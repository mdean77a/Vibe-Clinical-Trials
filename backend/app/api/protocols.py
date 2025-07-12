"""
FastAPI router for protocol management endpoints.

This module defines all HTTP endpoints for protocol operations including:
- Creating new protocols
- Retrieving protocols
- Updating protocol status
- Listing all protocols

Now using Qdrant-only architecture (migrated from SQLite).
"""

import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from ..models import ProtocolCreate, ProtocolResponse
from ..services.qdrant_service import QdrantError, get_qdrant_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/protocols", tags=["protocols"])

# Initialize services
qdrant_service = get_qdrant_service()


@router.post("/", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_new_protocol(protocol: ProtocolCreate) -> ProtocolResponse:
    """
    Create a new protocol using Qdrant storage.

    Args:
        protocol: Protocol data to create

    Returns:
        ProtocolResponse: Created protocol with metadata

    Raises:
        HTTPException: 500 for creation errors
    """
    try:
        logger.info(f"Creating new protocol: {protocol.study_acronym}")

        # Create collection and get collection name
        collection_name = qdrant_service.create_protocol_collection(
            study_acronym=protocol.study_acronym,
            protocol_title=protocol.protocol_title,
            file_path=getattr(protocol, "file_path", None),
        )

        # Create protocol metadata
        protocol_metadata = {
            "protocol_id": f"proto_{int(time.time() * 1000)}",  # Use milliseconds for uniqueness
            "study_acronym": protocol.study_acronym,
            "protocol_title": protocol.protocol_title,
            "collection_name": collection_name,
            "upload_date": datetime.now(timezone.utc).isoformat(),
            "file_path": getattr(protocol, "file_path", None),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Store initial metadata (will be updated when document is processed)
        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["Initial protocol entry"],
            embeddings=[[0.0] * 1536],  # Placeholder embedding
            protocol_metadata=protocol_metadata,
        )

        logger.info(f"Successfully created protocol with collection {collection_name}")
        return ProtocolResponse.model_validate(protocol_metadata)

    except QdrantError as e:
        logger.error(f"Qdrant error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create protocol",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


# Legacy PyMuPDF upload endpoint removed - application now uses client-side PDF.js extraction
# See /upload-text endpoint below for the current implementation


@router.get("/diagnostics")
async def get_diagnostics() -> dict:
    """
    Get diagnostic information about the Qdrant connection and protocols.

    Returns:
        dict: Diagnostic information
    """
    try:
        diagnostics = {
            "qdrant_connection": False,
            "total_collections": 0,
            "protocol_collections": 0,
            "environment": {
                "qdrant_url": "SET" if os.getenv("QDRANT_URL") else "NOT SET",
                "qdrant_api_key": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
                "openai_api_key": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET",
            },
            "error": None,
        }

        # Test Qdrant connection
        connection_ok = qdrant_service.test_connection()
        diagnostics["qdrant_connection"] = connection_ok

        if connection_ok:
            # Get collection counts
            collections = qdrant_service.client.get_collections()
            diagnostics["total_collections"] = len(collections.collections)

            protocol_collections = [
                col.name
                for col in collections.collections
                if qdrant_service._is_protocol_collection(col.name)
            ]
            diagnostics["protocol_collections"] = len(protocol_collections)
            diagnostics["protocol_collection_names"] = protocol_collections

        return diagnostics

    except Exception as e:
        logger.error(f"Error in diagnostics: {e}")
        return {
            "qdrant_connection": False,
            "total_collections": 0,
            "protocol_collections": 0,
            "environment": {
                "qdrant_url": "SET" if os.getenv("QDRANT_URL") else "NOT SET",
                "qdrant_api_key": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
                "openai_api_key": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET",
            },
            "error": str(e),
        }


@router.get("/{protocol_id}", response_model=ProtocolResponse)
async def get_protocol(protocol_id: str) -> ProtocolResponse:
    """
    Retrieve a protocol by its ID.

    Args:
        protocol_id: Protocol ID to retrieve

    Returns:
        ProtocolResponse: Protocol data

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Retrieving protocol with ID {protocol_id}")
        protocol_data = qdrant_service.get_protocol_by_id(protocol_id)

        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with ID {protocol_id} not found",
            )

        return ProtocolResponse.model_validate(protocol_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/collection/{collection_name}", response_model=ProtocolResponse)
async def get_protocol_by_collection(collection_name: str) -> ProtocolResponse:
    """
    Retrieve a protocol by its collection name.

    Args:
        collection_name: Collection name to search for

    Returns:
        ProtocolResponse: Protocol data

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Retrieving protocol with collection name {collection_name}")
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)

        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found",
            )

        return ProtocolResponse.model_validate(protocol_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=List[ProtocolResponse])
async def list_protocols() -> List[ProtocolResponse]:
    """
    List all protocols from Qdrant collections.

    Returns:
        List[ProtocolResponse]: List of protocols (all protocols are active by definition)

    Raises:
        HTTPException: 500 for retrieval errors
    """
    try:
        logger.info("Listing protocols")
        protocols = qdrant_service.list_all_protocols()

        logger.info(f"Retrieved {len(protocols)} protocols")
        return [ProtocolResponse.model_validate(protocol) for protocol in protocols]

    except Exception as e:
        logger.error(f"Error listing protocols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocols",
        )


# Status update endpoint removed - protocols in Qdrant are always active


@router.delete("/collection/{collection_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_protocol_endpoint(collection_name: str) -> None:
    """
    Delete a protocol from Qdrant by collection name.

    Args:
        collection_name: Collection name to delete

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Deleting protocol with collection {collection_name}")

        # First verify protocol exists
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)
        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found",
            )

        # Delete protocol
        success = qdrant_service.delete_protocol(collection_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete protocol",
            )

        logger.info(f"Successfully deleted protocol {collection_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/upload-text", response_model=ProtocolResponse)
async def upload_protocol_text(request: dict) -> ProtocolResponse:
    """
    Upload protocol with pre-extracted text (for client-side PDF processing).

    This endpoint is used when PDF text extraction is done on the client side
    using PDF.js, allowing deployment on platforms with size restrictions.

    Args:
        request: JSON body containing:
            - study_acronym: Study identifier
            - protocol_title: Protocol title
            - extracted_text: Pre-extracted text from PDF
            - original_filename: Original PDF filename
            - page_count: Number of pages in the original PDF

    Returns:
        ProtocolResponse with created protocol details
    """
    try:
        # Extract request data
        study_acronym = request.get("study_acronym", "").strip().upper()
        protocol_title = request.get("protocol_title", "").strip()
        extracted_text = request.get("extracted_text", "").strip()
        original_filename = request.get("original_filename", "")
        page_count = request.get("page_count", 0)

        # Validate required fields
        if not study_acronym:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="study_acronym is required",
            )
        if not protocol_title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="protocol_title is required",
            )
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="extracted_text is required",
            )

        logger.info(f"Processing text upload for study {study_acronym}")

        # Process the extracted text using the same chunking logic
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            # Use the same text splitter configuration as extract_and_chunk_pdf
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )

            text_chunks = text_splitter.split_text(extracted_text)

            # Filter out very short chunks
            meaningful_chunks = [
                chunk.strip() for chunk in text_chunks if len(chunk.strip()) > 50
            ]

            if not meaningful_chunks:
                meaningful_chunks = [extracted_text.strip()]

            logger.info(
                f"Text processed: {len(meaningful_chunks)} chunks from {page_count} pages"
            )

        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process text: {str(e)}",
            )

        # Store protocol using LangChain integration (same as file upload)
        try:
            from langchain_core.documents import Document

            from ..services.langchain_qdrant_service import get_langchain_qdrant_service

            # Initialize LangChain service
            langchain_service = get_langchain_qdrant_service()

            # Create protocol metadata
            protocol_metadata = {
                "protocol_id": f"proto_{int(time.time() * 1000)}",
                "study_acronym": study_acronym,
                "protocol_title": protocol_title,
                "upload_date": datetime.now(timezone.utc).isoformat(),
                "file_path": original_filename,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "chunk_count": len(meaningful_chunks),
                "processing_method": "client-side-extraction",
                "page_count": page_count,
            }

            # Convert text chunks to LangChain Documents
            documents = []
            for i, chunk in enumerate(meaningful_chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        **protocol_metadata,
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "embedding_model": "text-embedding-ada-002",
                        "processing_version": "1.0",
                        "last_updated": datetime.now().isoformat(),
                    },
                )
                documents.append(doc)

            # Store documents using LangChain
            doc_ids, collection_name = langchain_service.store_documents(
                documents=documents,
                study_acronym=study_acronym,
            )

            # Add collection_name to protocol metadata
            protocol_metadata["collection_name"] = collection_name

            logger.info(
                f"Stored {len(documents)} documents using LangChain with collection: {collection_name}"
            )

        except Exception as e:
            logger.error(f"LangChain storage failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store protocol: {str(e)}",
            )

        logger.info(
            f"Successfully processed and stored protocol {study_acronym} from client text"
        )
        return ProtocolResponse.model_validate(protocol_metadata)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing text upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during text processing",
        )
