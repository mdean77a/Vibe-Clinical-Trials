"""
ICF Generation API endpoints.

This module provides REST API endpoints for generating Informed Consent Forms
using LangGraph workflows and RAG context retrieval.
"""

import json
import logging
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..services.document_generator import DocumentGenerationError
from ..services.icf_service import ICFGenerationService, get_icf_service

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/icf", tags=["ICF Generation"])


# Request/Response Models
class ICFGenerationRequest(BaseModel):
    """Request model for ICF generation."""

    protocol_collection_name: str = Field(
        ...,
        description="The Qdrant collection name containing the protocol document",
        json_schema_extra={"example": "ABCD1234-efgh-5678-ijkl-9012mnopqrst-a1b2c3d4"},
    )
    protocol_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional metadata about the protocol",
        json_schema_extra={
            "example": {
                "protocol_title": "Safety and Efficacy Study",
                "sponsor": "Example Pharma",
                "indication": "Oncology",
            }
        },
    )


class SectionRegenerationRequest(BaseModel):
    """Request model for section-specific regeneration."""

    protocol_collection_name: str = Field(
        ..., description="The Qdrant collection name containing the protocol document"
    )
    section_name: str = Field(
        ...,
        description="The specific section to regenerate",
        json_schema_extra={"example": "summary"},
    )
    protocol_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata about the protocol"
    )


class ICFSection(BaseModel):
    """Model for an individual ICF section."""

    name: str = Field(..., description="Section name")
    content: str = Field(..., description="Generated section content")
    word_count: int = Field(..., description="Number of words in the section")


class ICFGenerationResponse(BaseModel):
    """Response model for ICF generation."""

    collection_name: str = Field(..., description="Protocol collection name")
    sections: Dict[str, str] = Field(..., description="Generated ICF sections")
    metadata: Dict[str, Any] = Field(..., description="Generation metadata")
    errors: list[str] = Field(
        default_factory=list, description="Any errors encountered"
    )
    status: str = Field(..., description="Generation status")


class ProtocolSummaryResponse(BaseModel):
    """Response model for protocol summary."""

    collection_name: str = Field(..., description="Collection name")
    status: str = Field(..., description="Collection status")
    protocol_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Protocol metadata"
    )
    message: Optional[str] = Field(None, description="Status message")


class GenerationStatusResponse(BaseModel):
    """Response model for generation status check."""

    task_id: str = Field(..., description="Generation task ID")
    status: str = Field(..., description="Task status")
    message: Optional[str] = Field(None, description="Status message")


# API Endpoints
@router.post("/generate-stream")
async def generate_icf_stream(
    request: ICFGenerationRequest,
    icf_service: ICFGenerationService = Depends(get_icf_service),
) -> StreamingResponse:
    """
    Generate an ICF with streaming section results.

    This endpoint streams each section as it's generated, allowing the frontend
    to show progress and populate sections in real-time.

    Returns Server-Sent Events (SSE) stream with the following event types:
    - section_complete: When a section finishes generating
    - error: When a section fails to generate
    - complete: When all sections are finished
    """

    async def stream_generator() -> Any:
        try:
            logger.info(
                f"Streaming ICF generation for collection: {request.protocol_collection_name}"
            )

            # Validate collection exists
            collection_exists = await icf_service.validate_collection_exists(
                request.protocol_collection_name
            )

            if not collection_exists:
                error_data = {
                    "event": "error",
                    "data": {
                        "error": f"Protocol collection '{request.protocol_collection_name}' not found"
                    },
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            # Stream sections as they complete
            async for section_result in icf_service.generate_icf_streaming(
                protocol_collection_name=request.protocol_collection_name,
                protocol_metadata=request.protocol_metadata,
            ):
                if section_result["type"] == "section_start":
                    event_data = {
                        "event": "section_start",
                        "data": {"section_name": section_result["section_name"]},
                    }
                elif section_result["type"] == "token":
                    event_data = {
                        "event": "token",
                        "data": {
                            "section_name": section_result["section_name"],
                            "content": section_result["content"],
                            "accumulated_content": section_result[
                                "accumulated_content"
                            ],
                        },
                    }
                elif section_result["type"] == "section_complete":
                    event_data = {
                        "event": "section_complete",
                        "data": {
                            "section_name": section_result["section_name"],
                            "content": section_result["content"],
                            "word_count": len(section_result["content"].split()),
                        },
                    }
                elif section_result["type"] == "section_error":
                    event_data = {
                        "event": "section_error",
                        "data": {
                            "section_name": section_result["section_name"],
                            "error": section_result["error"],
                        },
                    }
                elif section_result["type"] == "complete":
                    event_data = {
                        "event": "complete",
                        "data": {
                            "total_sections": section_result["total_sections"],
                            "completed_sections": section_result["completed_sections"],
                            "errors": section_result["errors"],
                        },
                    }
                elif section_result["type"] == "error":
                    event_data = {
                        "event": "error",
                        "data": {"error": section_result["error"]},
                    }
                else:
                    # Skip unknown event types
                    continue

                yield f"data: {json.dumps(event_data)}\n\n"

        except Exception as e:
            error_data = {
                "event": "error",
                "data": {"error": f"Generation failed: {str(e)}"},
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.post("/regenerate-section")
async def regenerate_icf_section(
    request: SectionRegenerationRequest,
    icf_service: ICFGenerationService = Depends(get_icf_service),
) -> StreamingResponse:
    """
    Regenerate a specific ICF section with streaming.

    This endpoint regenerates only the specified section with real-time streaming,
    providing immediate feedback during generation.
    """

    async def stream_generator() -> Any:
        try:
            logger.info(
                f"Streaming section regeneration for: {request.section_name} in collection: {request.protocol_collection_name}"
            )

            # Validate collection exists
            collection_exists = await icf_service.validate_collection_exists(
                request.protocol_collection_name
            )

            if not collection_exists:
                error_data = {
                    "event": "error",
                    "data": {
                        "error": f"Protocol collection '{request.protocol_collection_name}' not found"
                    },
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            # Validate section name
            valid_sections = [
                "summary",
                "background",
                "participants",
                "procedures",
                "alternatives",
                "risks",
                "benefits",
            ]
            if request.section_name not in valid_sections:
                error_data = {
                    "event": "error",
                    "data": {
                        "error": f"Invalid section name. Must be one of: {', '.join(valid_sections)}"
                    },
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return

            # Stream sections as they complete using existing streaming infrastructure
            async for section_result in icf_service.generate_icf_streaming(
                protocol_collection_name=request.protocol_collection_name,
                protocol_metadata=request.protocol_metadata,
                sections_filter=[
                    request.section_name
                ],  # Only regenerate the specified section
            ):
                if section_result["type"] == "section_start":
                    event_data = {
                        "event": "section_start",
                        "data": {"section_name": section_result["section_name"]},
                    }
                elif section_result["type"] == "token":
                    event_data = {
                        "event": "token",
                        "data": {
                            "section_name": section_result["section_name"],
                            "content": section_result["content"],
                            "accumulated_content": section_result[
                                "accumulated_content"
                            ],
                        },
                    }
                elif section_result["type"] == "section_complete":
                    event_data = {
                        "event": "section_complete",
                        "data": {
                            "section_name": section_result["section_name"],
                            "content": section_result["content"],
                            "word_count": len(section_result["content"].split()),
                        },
                    }
                elif section_result["type"] == "section_error":
                    event_data = {
                        "event": "section_error",
                        "data": {
                            "section_name": section_result["section_name"],
                            "error": section_result["error"],
                        },
                    }
                elif section_result["type"] == "complete":
                    event_data = {
                        "event": "complete",
                        "data": {
                            "total_sections": section_result["total_sections"],
                            "completed_sections": section_result["completed_sections"],
                            "errors": section_result["errors"],
                        },
                    }
                elif section_result["type"] == "error":
                    event_data = {
                        "event": "error",
                        "data": {"error": section_result["error"]},
                    }
                else:
                    # Skip unknown event types
                    continue

                yield f"data: {json.dumps(event_data)}\n\n"

        except Exception as e:
            error_data = {
                "event": "error",
                "data": {"error": f"Generation failed: {str(e)}"},
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get(
    "/protocol/{collection_name}/summary", response_model=ProtocolSummaryResponse
)
async def get_protocol_summary(
    collection_name: str, icf_service: ICFGenerationService = Depends(get_icf_service)
) -> ProtocolSummaryResponse:
    """
    Get a summary of a protocol collection.

    This endpoint provides basic information about a protocol collection
    including metadata and readiness for ICF generation.
    """
    try:
        logger.info(f"Protocol summary requested for collection: {collection_name}")

        summary = await icf_service.get_protocol_summary(collection_name)

        return ProtocolSummaryResponse(**summary)

    except Exception as e:
        logger.error(f"Failed to get protocol summary: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve protocol summary"
        )


@router.get("/status/{task_id}", response_model=GenerationStatusResponse)
async def get_generation_status(
    task_id: str, icf_service: ICFGenerationService = Depends(get_icf_service)
) -> GenerationStatusResponse:
    """
    Get the status of an ICF generation task.

    This endpoint allows checking the progress of long-running ICF generation tasks.
    Currently returns a placeholder response as generation is synchronous.
    """
    try:
        logger.info(f"Generation status requested for task: {task_id}")

        status = icf_service.get_generation_status(task_id)

        return GenerationStatusResponse(**status)

    except Exception as e:
        logger.error(f"Failed to get generation status: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve generation status"
        )


@router.get("/sections/requirements")
async def get_icf_section_requirements() -> Dict[str, Any]:
    """
    Get the required ICF sections and their descriptions.

    This endpoint provides information about the ICF sections that will be generated,
    useful for frontend display and validation.
    """
    return {
        "required_sections": [
            {
                "name": "summary",
                "title": "Study Summary",
                "description": "A clear, concise overview of the study purpose and participant involvement",
                "estimated_length": "2-3 paragraphs",
            },
            {
                "name": "background",
                "title": "Background and Purpose",
                "description": "Medical/scientific background explaining why the study is needed",
                "estimated_length": "3-4 paragraphs",
            },
            {
                "name": "participants",
                "title": "Number of Participants",
                "description": "Total participants and eligibility criteria",
                "estimated_length": "2-3 paragraphs",
            },
            {
                "name": "procedures",
                "title": "Study Procedures",
                "description": "Detailed description of all study procedures and timeline",
                "estimated_length": "4-6 paragraphs",
            },
            {
                "name": "alternatives",
                "title": "Alternative Procedures",
                "description": "Alternative treatments available outside the study",
                "estimated_length": "2-3 paragraphs",
            },
            {
                "name": "risks",
                "title": "Risks and Discomforts",
                "description": "Comprehensive list of potential risks and side effects",
                "estimated_length": "3-5 paragraphs",
            },
            {
                "name": "benefits",
                "title": "Benefits",
                "description": "Potential benefits to participants and society",
                "estimated_length": "2-3 paragraphs",
            },
        ],
        "total_sections": 7,
        "compliance": "FDA 21 CFR 50 - Protection of Human Subjects",
        "generation_method": "LangGraph parallel processing with RAG context retrieval",
    }


@router.get("/health")
async def icf_health_check() -> Dict[str, str]:
    """Health check endpoint for ICF generation service."""
    try:
        # Test service initialization
        icf_service = get_icf_service()

        # Get current LLM model from centralized config
        from ..config import LLM_MODEL
        
        return {
            "status": "healthy",
            "service": "ICF Generation",
            "workflow": "StreamingICFWorkflow",
            "llm_model": LLM_MODEL,
        }
    except Exception as e:
        logger.error(f"ICF service health check failed: {e}")
        raise HTTPException(status_code=500, detail="ICF service unhealthy")
