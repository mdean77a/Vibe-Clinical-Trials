"""
ICF (Informed Consent Form) generation service.

This module provides high-level services for generating ICF documents
using LangGraph workflows and RAG context retrieval.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient

from .document_generator import (
    DocumentGenerationError,
    DocumentGenerator,
    ICFWorkflow,
    StreamingICFWorkflow,
    get_langgraph_workflow,
)
from ..prompts.icf_prompts import ICF_SECTION_QUERIES
from .qdrant_service import get_qdrant_service

logger = logging.getLogger(__name__)


class ICFGenerationService:
    """Service for generating ICF documents using LangGraph workflows."""

    def __init__(self, qdrant_client: Optional[QdrantClient] = None):
        """Initialize the ICF generation service."""
        self.qdrant_client = qdrant_client or get_qdrant_service().client
        self.document_generator = DocumentGenerator(self.qdrant_client)

        # LLM configuration for Claude Sonnet 4
        self.llm_config = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 8192,
            "temperature": 0.1,
        }

        # Initialize workflows
        self.icf_workflow = ICFWorkflow(self.llm_config)

        # Thread pool for async execution
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def generate_icf_async(
        self,
        protocol_collection_name: str,
        protocol_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate ICF sections asynchronously using LangGraph workflow.

        Args:
            protocol_collection_name: The Qdrant collection name for the protocol
            protocol_metadata: Optional metadata about the protocol

        Returns:
            Dict containing generated ICF sections and metadata
        """
        try:
            logger.info(
                f"Starting async ICF generation for collection: {protocol_collection_name}"
            )

            # Run the synchronous generation in a thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._generate_icf_sync,
                protocol_collection_name,
                protocol_metadata,
            )

            logger.info(
                f"Completed async ICF generation for collection: {protocol_collection_name}"
            )
            return result

        except Exception as e:
            logger.error(f"Async ICF generation failed: {e}")
            raise DocumentGenerationError(f"Failed to generate ICF: {str(e)}")

    async def generate_icf_streaming(
        self,
        protocol_collection_name: str,
        protocol_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Generate ICF sections using LangGraph with streaming tokens from each node.

        Each section is generated by a separate LangGraph node in parallel, and this
        method streams tokens from each LLM call to the frontend in real-time.

        Args:
            protocol_collection_name: The Qdrant collection name for the protocol
            protocol_metadata: Optional metadata about the protocol

        Yields:
            Dict with streaming events from parallel section generation
        """
        import asyncio
        import time
        from asyncio import Queue

        try:
            # Start timing the generation process
            generation_start_time = time.time()
            logger.info(
                f"🚀 Starting streaming ICF generation for collection: {protocol_collection_name} at {time.strftime('%H:%M:%S')}"
            )

            # Create a queue to collect streaming events from all sections
            event_queue = Queue()

            # Get the current event loop to pass to the workflow
            main_loop = asyncio.get_running_loop()

            # Create a modified ICF workflow that supports streaming
            streaming_workflow = StreamingICFWorkflow(
                self.llm_config,
                event_queue,
                self.document_generator,
                protocol_collection_name,
                main_loop,
            )

            # Prepare workflow inputs like the original implementation
            context = self.document_generator.get_protocol_context(
                protocol_collection_name,
                "informed consent form requirements eligibility procedures risks benefits",
                min_score=0.3,
            )

            if not context:
                logger.warning(
                    f"No context found for collection: {protocol_collection_name}"
                )
                context = [
                    {"text": "No specific protocol context available", "score": 0.0}
                ]

            logger.info(f"Using collection name: '{protocol_collection_name}'")

            # Initialize state with empty lists for all sections
            workflow_inputs = {
                "summary": [],
                "background": [],
                "participants": [],
                "procedures": [],
                "alternatives": [],
                "risks": [],
                "benefits": [],
            }

            # Start the workflow execution in a background task
            workflow_task = asyncio.create_task(
                self._execute_streaming_workflow(
                    streaming_workflow, workflow_inputs, event_queue
                )
            )

            # Stream events as they arrive from the queue
            sections_completed = 0
            total_sections = 7  # ICF has 7 sections

            while sections_completed < total_sections:
                try:
                    # Wait for the next event with a timeout
                    event = await asyncio.wait_for(event_queue.get(), timeout=60.0)

                    if event["type"] == "section_complete":
                        sections_completed += 1
                    elif event["type"] == "error":
                        sections_completed = total_sections  # Stop on error

                    yield event

                except asyncio.TimeoutError:
                    logger.error("Timeout waiting for streaming events")
                    yield {
                        "type": "error",
                        "error": "Generation timeout - LLM taking too long to respond",
                    }
                    break

            # Wait for workflow to complete and get final results
            try:
                await asyncio.wait_for(workflow_task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning("Workflow cleanup timeout")

            # Calculate total generation time
            generation_end_time = time.time()
            total_time = generation_end_time - generation_start_time

            # Log the completion with timing information
            logger.info(f"⏱️  ICF GENERATION COMPLETE!")
            logger.info(f"📊 Collection: {protocol_collection_name}")
            logger.info(
                f"⏰ Total Time: {total_time:.2f} seconds ({total_time/60:.1f} minutes)"
            )
            logger.info(f"📝 Sections: {sections_completed}/{total_sections} completed")
            logger.info(f"🏁 Finished at: {time.strftime('%H:%M:%S')}")

            # Send completion event
            yield {
                "type": "complete",
                "total_sections": total_sections,
                "completed_sections": sections_completed,
                "generation_time_seconds": round(total_time, 2),
                "errors": [],
            }

            logger.info(
                f"Streaming ICF generation completed for collection: {protocol_collection_name}"
            )

        except Exception as e:
            logger.error(f"Streaming ICF generation failed: {e}")
            yield {"type": "error", "error": f"Generation failed: {str(e)}"}

    async def _execute_streaming_workflow(self, workflow, inputs, event_queue):
        """Execute the streaming workflow in the background."""
        try:
            # Run the workflow (this will populate the event_queue via the streaming nodes)
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, workflow.invoke, inputs
            )
            return result
        except Exception as e:
            await event_queue.put(
                {"type": "error", "error": f"Workflow execution failed: {str(e)}"}
            )

    def _generate_section_streaming_sync(
        self,
        protocol_collection_name: str,
        section_name: str,
        protocol_metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Generate a single ICF section with token-by-token streaming.

        This is a synchronous method that returns an async generator for streaming.

        Args:
            protocol_collection_name: The Qdrant collection name for the protocol
            section_name: Name of the section to generate
            protocol_metadata: Optional metadata about the protocol

        Returns:
            Async generator yielding streaming tokens
        """

        async def stream_section():
            try:
                # Use the same section queries as initial generation for consistency
                query = ICF_SECTION_QUERIES.get(
                    section_name, f"{section_name} informed consent"
                )
                context = self.document_generator.get_protocol_context(
                    protocol_collection_name, query, min_score=0.3
                )

                if not context:
                    context = [
                        {
                            "text": f"No specific context available for {section_name}",
                            "score": 0.0,
                        }
                    ]

                # Generate the section with streaming using LangChain's streaming
                async for chunk in self._generate_section_with_streaming_llm(
                    section_name=section_name,
                    context="\n\n".join(
                        [item.get("text", "") for item in context[:3]]
                    ),  # Top 3 items
                    section_prompt=self.icf_workflow._get_section_prompt(section_name),
                ):
                    yield chunk

            except Exception as e:
                logger.error(f"Failed to stream section {section_name}: {e}")
                yield {
                    "type": "error",
                    "error": f"Failed to generate {section_name}: {str(e)}",
                }

        return stream_section()

    async def _generate_section_with_streaming_llm(
        self, section_name: str, context: str, section_prompt: str
    ):
        """
        Generate a section using the LLM with token streaming.

        Args:
            section_name: Name of the section being generated
            context: Protocol context for the section
            section_prompt: Section-specific prompt

        Yields:
            Dict with streaming tokens
        """
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            messages = [
                SystemMessage(content=section_prompt),
                HumanMessage(
                    content=f"Context: {context}\n\nGenerate the {section_name} section."
                ),
            ]

            # Stream tokens from the LLM
            async for chunk in self.icf_workflow.llm.astream(messages):
                if hasattr(chunk, "content") and chunk.content:
                    yield {"type": "token", "content": chunk.content}

        except Exception as e:
            logger.error(f"Failed to stream {section_name} section: {e}")
            yield {
                "type": "error",
                "error": f"Failed to generate {section_name}: {str(e)}",
            }

    def _generate_icf_sync(
        self,
        protocol_collection_name: str,
        protocol_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous ICF generation using LangGraph workflow.

        Args:
            protocol_collection_name: The Qdrant collection name for the protocol
            protocol_metadata: Optional metadata about the protocol

        Returns:
            Dict containing generated ICF sections and metadata
        """
        try:
            # Get protocol context for general ICF requirements
            context = self.document_generator.get_protocol_context(
                protocol_collection_name,
                "informed consent form requirements eligibility procedures risks benefits",
                min_score=0.3,  # Lower threshold for broader context
            )

            logger.info(
                f"Retrieved {len(context)} context items for {protocol_collection_name}"
            )
            for i, item in enumerate(context[:3]):
                text = item.get("text", "")
                score = item.get("score", 0)
                logger.info(
                    f"Context {i+1}: score={score:.3f}, length={len(text)}, preview='{text[:100]}...'"
                )

            if not context:
                logger.warning(
                    f"No context found for collection: {protocol_collection_name}"
                )
                context = [
                    {"text": "No specific protocol context available", "score": 0.0}
                ]

            # Prepare workflow inputs (like your prototype)
            workflow_inputs = {
                "document_id": protocol_collection_name,
                "document_generator": self.document_generator,  # Pass document generator for individual RAG
                "document_type": "icf",
                "context": context,  # Keep for backward compatibility, but each section will do its own retrieval
                "sections": {},
                "errors": [],
                "metadata": protocol_metadata or {},
            }

            logger.info(f"Executing ICF workflow with {len(context)} context items")

            # Execute the LangGraph workflow
            result = self.icf_workflow.invoke(workflow_inputs)

            # Extract sections from the result
            sections = result.get("sections", {})
            errors = result.get("errors", [])
            metadata = result.get("metadata", {})

            if errors:
                logger.warning(f"ICF generation completed with errors: {errors}")

            # Validate that all required sections are present
            required_sections = [
                "summary",
                "background",
                "participants",
                "procedures",
                "alternatives",
                "risks",
                "benefits",
            ]

            missing_sections = [s for s in required_sections if s not in sections]
            if missing_sections:
                error_msg = (
                    f"Missing required ICF sections: {', '.join(missing_sections)}"
                )
                logger.error(error_msg)
                raise DocumentGenerationError(error_msg)

            # Format response
            import time

            response = {
                "collection_name": protocol_collection_name,
                "sections": sections,
                "metadata": {
                    **metadata,
                    "generation_timestamp": time.time(),
                    "context_items": len(context),
                    "workflow_name": self.icf_workflow.name,
                    "llm_config": self.llm_config,
                },
                "errors": errors,
                "status": "completed" if not errors else "completed_with_warnings",
            }

            logger.info(
                f"ICF generation successful: {len(sections)} sections generated"
            )
            return response

        except Exception as e:
            logger.error(f"Synchronous ICF generation failed: {e}")
            raise DocumentGenerationError(f"Failed to generate ICF: {str(e)}")

    async def regenerate_section_async(
        self,
        protocol_collection_name: str,
        section_name: str,
        protocol_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Regenerate a specific ICF section asynchronously.

        Args:
            protocol_collection_name: The Qdrant collection name for the protocol
            section_name: The specific section to regenerate
            protocol_metadata: Optional metadata about the protocol

        Returns:
            Dict containing the regenerated section content
        """
        try:
            logger.info(
                f"Starting async section regeneration: {section_name} for collection: {protocol_collection_name}"
            )

            # Run the synchronous generation in a thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._regenerate_section_sync,
                protocol_collection_name,
                section_name,
                protocol_metadata,
            )

            logger.info(f"Completed async section regeneration: {section_name}")
            return result

        except Exception as e:
            logger.error(f"Async section regeneration failed: {e}")
            raise DocumentGenerationError(f"Failed to regenerate section: {str(e)}")

    def _regenerate_section_sync(
        self,
        protocol_collection_name: str,
        section_name: str,
        protocol_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synchronous section regeneration.

        Args:
            protocol_collection_name: The Qdrant collection name for the protocol
            section_name: The specific section to regenerate
            protocol_metadata: Optional metadata about the protocol

        Returns:
            Dict containing the regenerated section content
        """
        try:
            # Get protocol context for the specific section using the same queries as initial generation
            query = ICF_SECTION_QUERIES.get(
                section_name, f"informed consent form {section_name} requirements"
            )
            context = self.document_generator.get_protocol_context(
                protocol_collection_name,
                query,
                min_score=0.3,
            )

            if not context:
                logger.warning(
                    f"No context found for collection: {protocol_collection_name}"
                )
                context = [
                    {"text": "No specific protocol context available", "score": 0.0}
                ]

            # Format context for LLM consumption
            context_text = self._format_context_for_llm(context)

            # Get the section prompt
            prompt = self._get_section_prompt(section_name)

            # Generate the section using LLM
            section_content = self.icf_workflow._generate_section_with_llm(
                section_name, context_text, prompt
            )

            # Format response
            import time

            response = {
                "section_name": section_name,
                "content": section_content,
                "word_count": len(section_content.split()) if section_content else 0,
                "metadata": {
                    "regeneration_timestamp": time.time(),
                    "context_items": len(context),
                    "workflow_name": self.icf_workflow.name,
                    "llm_config": self.llm_config,
                    **(protocol_metadata or {}),
                },
                "status": "completed",
            }

            logger.info(f"Section regeneration successful: {section_name}")
            return response

        except Exception as e:
            logger.error(f"Synchronous section regeneration failed: {e}")
            raise DocumentGenerationError(f"Failed to regenerate section: {str(e)}")

    def _format_context_for_llm(self, context: List[Dict[str, Any]]) -> str:
        """Format context for LLM consumption."""
        if not context:
            return "No specific protocol context available."

        formatted = []
        for item in context[:5]:  # Limit to top 5 most relevant
            text = item.get("text", "")
            score = item.get("score", 0)
            formatted.append(f"[Relevance: {score:.2f}] {text}")

        return "\n\n".join(formatted)

    def _get_section_prompt(self, section_name: str) -> str:
        """Get the prompt for a specific ICF section."""
        # Use the same prompts as the workflow
        return self.icf_workflow._get_section_prompt(section_name)

    def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an ICF generation task.

        Note: This is a placeholder for future async task tracking.
        Currently returns a simple status since generation is synchronous.
        """
        return {
            "task_id": task_id,
            "status": "not_implemented",
            "message": "Task tracking not yet implemented",
        }

    async def validate_collection_exists(self, collection_name: str) -> bool:
        """
        Validate that a protocol collection exists in Qdrant.

        Args:
            collection_name: The collection name to validate

        Returns:
            True if collection exists, False otherwise
        """
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]

            exists = collection_name in collection_names
            logger.info(f"Collection {collection_name} exists: {exists}")
            return exists

        except Exception as e:
            logger.error(f"Failed to validate collection {collection_name}: {e}")
            return False

    async def get_protocol_summary(self, collection_name: str) -> Dict[str, Any]:
        """
        Get a summary of the protocol from the collection metadata.

        Args:
            collection_name: The collection name to get summary for

        Returns:
            Dict containing protocol summary information
        """
        try:
            # Get some sample content from the collection to create a summary
            search_results = self.qdrant_client.scroll(
                collection_name=collection_name, limit=5, with_payload=True
            )

            if not search_results[0]:  # No points found
                return {
                    "collection_name": collection_name,
                    "status": "empty",
                    "message": "No protocol content found",
                }

            # Extract metadata from the first point
            first_point = search_results[0][0]
            payload = first_point.payload

            summary = {
                "collection_name": collection_name,
                "status": "ready",
                "protocol_metadata": {
                    "title": payload.get("protocol_title", "Unknown"),
                    "filename": payload.get("filename", "Unknown"),
                    "document_id": payload.get("document_id", "Unknown"),
                    "total_chunks": len(search_results[0]),
                },
            }

            logger.info(f"Retrieved protocol summary for {collection_name}")
            return summary

        except Exception as e:
            logger.error(f"Failed to get protocol summary for {collection_name}: {e}")
            return {
                "collection_name": collection_name,
                "status": "error",
                "message": str(e),
            }


# Singleton service instance
_icf_service_instance: Optional[ICFGenerationService] = None


def get_icf_service() -> ICFGenerationService:
    """Get the singleton ICF generation service instance."""
    global _icf_service_instance
    if _icf_service_instance is None:
        _icf_service_instance = ICFGenerationService()
    return _icf_service_instance
