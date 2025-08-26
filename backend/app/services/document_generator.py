"""
Document generation service using LangGraph workflows.

This module handles:
- ICF (Informed Consent Form) generation
- Site Initiation Checklist generation
- RAG context retrieval
- Section-based document assembly
"""

import logging
from abc import ABC, abstractmethod
from typing import Annotated, Any, Dict, List, Optional, TypedDict, Union

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

from ..config import get_llm_chat_model
from ..prompts.generation_prompts import SECTION_GENERATION_PROMPT
from ..prompts.icf_prompts import ICF_PROMPTS, ICF_SECTION_QUERIES

logger = logging.getLogger(__name__)


class DocumentGenerationError(Exception):
    """Exception raised for document generation errors."""

    pass


class AgentState(TypedDict):
    """State for LangGraph workflows with revision support."""

    # Individual section fields as lists for revision history
    summary: Annotated[List[str], add_messages]
    background: Annotated[List[str], add_messages]
    participants: Annotated[List[str], add_messages]
    procedures: Annotated[List[str], add_messages]
    alternatives: Annotated[List[str], add_messages]
    risks: Annotated[List[str], add_messages]
    benefits: Annotated[List[str], add_messages]


class DocumentGenerator:
    """Main document generator service."""

    def __init__(
        self,
        qdrant_client: QdrantClient,
        icf_workflow: Optional[Any] = None,
        checklist_workflow: Optional[Any] = None,
    ) -> None:
        self.qdrant_client = qdrant_client
        self.icf_workflow = icf_workflow
        self.checklist_workflow = checklist_workflow

    def get_protocol_context(
        self, protocol_collection_name: str, query: str, min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant protocol context for document generation using LangChain."""
        try:
            from .langchain_qdrant_service import get_langchain_qdrant_service

            # Initialize LangChain Qdrant service
            langchain_service = get_langchain_qdrant_service()

            # Use similarity search with score to get scored results
            docs_with_scores = langchain_service.similarity_search_with_score(
                collection_name=protocol_collection_name,
                query=query,
                k=10,
            )

            # Filter by minimum score and format results
            context = []
            for i, (doc, score) in enumerate(docs_with_scores):
                if score >= min_score:
                    context.append(
                        {
                            "text": doc.page_content,
                            "metadata": doc.metadata,
                            "score": score,
                        }
                    )

                    # Log chunk with relevance score
                    logger.info(f"Chunk {i+1} (relevance: {score:.3f})")

            logger.info(
                f"Retrieved {len(context)} relevant documents for query: {query[:50]}..."
            )
            return context

        except Exception as e:
            logger.error(f"Error retrieving protocol context: {e}")
            raise DocumentGenerationError(
                f"Failed to retrieve context using LangChain: {str(e)}"
            )


class WorkflowBase(ABC):
    """Base class for LangGraph workflows."""

    sections: List[str] = []  # Will be overridden by child classes

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.name = "base_workflow"
        self.llm_config = llm_config or {}
        self._compiled_graph: Optional[CompiledStateGraph] = None
        self._initialize_llm()

    def _initialize_llm(self) -> None:
        """Initialize the LLM for the workflow using centralized configuration."""
        try:
            # Pass any custom config to get_llm_chat_model, it will use defaults for missing values
            self.llm = get_llm_chat_model(**self.llm_config)
            from ..config import LLM_MODEL

            model_name = self.llm_config.get("model", LLM_MODEL)
            logger.info(f"Successfully initialized LLM: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise DocumentGenerationError(
                f"Failed to initialize LLM. Text generation cannot proceed: {e}"
            )

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        pass

    def compile_workflow(self) -> CompiledStateGraph:
        """Compile the workflow graph."""
        if self._compiled_graph is None:
            graph = self.build_graph()
            self._compiled_graph = graph.compile()
        return self._compiled_graph

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with given inputs."""
        try:
            # Get document generator and set the current document ID
            document_generator = inputs.get("document_generator")
            document_id = inputs.get("document_id")

            if document_generator and document_id:
                # Store document_id on the generator for section access
                document_generator._current_document_id = document_id

            # Initialize only the section fields and document_generator - no conflicting fields
            workflow_state: Dict[str, Any] = {
                "summary": [],
                "background": [],
                "participants": [],
                "procedures": [],
                "alternatives": [],
                "risks": [],
                "benefits": [],
                "document_generator": document_generator,
            }

            # Get compiled workflow
            workflow = self.compile_workflow()

            # Execute workflow with simplified state
            result = workflow.invoke(workflow_state)

            # Construct final response from individual section results
            sections = {}
            errors = []

            for section_name in self.sections:
                section_list = result.get(section_name, [])
                if section_list:
                    # Extract content from HumanMessage objects (add_messages creates these)
                    latest_item = section_list[-1]  # Latest version
                    if hasattr(latest_item, "content"):
                        sections[section_name] = latest_item.content
                    else:
                        sections[section_name] = str(latest_item)
                else:
                    errors.append(f"Missing section: {section_name}")

            # Build final response outside of workflow state
            return {
                "sections": sections,
                "errors": errors,
                "metadata": {
                    "generated_sections": list(sections.keys()),
                    "workflow_name": self.name,
                    **inputs.get("metadata", {}),
                },
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise DocumentGenerationError(f"Workflow execution failed: {str(e)}")

    def _generate_section_with_llm(
        self, section_name: str, context: str, section_prompt: str
    ) -> str:
        """Generate a section using the initialized working model."""
        messages = [
            SystemMessage(content=section_prompt),
            HumanMessage(
                content=SECTION_GENERATION_PROMPT.format(
                    context=context, section_name=section_name
                )
            ),
        ]

        try:
            response = self.llm.invoke(messages)
            return str(response.content)
        except Exception as e:
            logger.error(
                f"Failed to generate {section_name} section with working LLM: {e}"
            )
            raise DocumentGenerationError(
                f"Failed to generate {section_name}: {str(e)}"
            )


class SiteChecklistWorkflow(WorkflowBase):
    """Workflow for Site Initiation Checklist generation."""

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        super().__init__(llm_config)
        self.name = "site_checklist_generation"
        self.sections = [
            "regulatory",
            "training",
            "equipment",
            "documentation",
            "preparation",
            "timeline",
        ]

    def build_graph(self) -> StateGraph:
        """Build the site checklist generation workflow graph."""
        workflow = StateGraph(AgentState)

        # Add parallel section generation nodes
        for section in self.sections:
            workflow.add_node(
                f"generate_{section}", self._create_section_generator(section)  # type: ignore[attr-defined]
            )

        # Add compilation node
        workflow.add_node("compile_checklist", self._compile_checklist)  # type: ignore[attr-defined]

        # Set entry point
        workflow.set_entry_point("generate_regulatory")

        # Connect nodes in parallel execution pattern
        for i, section in enumerate(self.sections):
            if i < len(self.sections) - 1:
                workflow.add_edge(
                    f"generate_{section}", f"generate_{self.sections[i+1]}"
                )
            else:
                workflow.add_edge(f"generate_{section}", "compile_checklist")

        # Connect compilation to end
        workflow.add_edge("compile_checklist", END)

        return workflow


class StreamingICFWorkflow(WorkflowBase):
    """Streaming version of ICF workflow that sends tokens to a queue."""

    def __init__(
        self,
        llm_config: Optional[Dict[str, Any]] = None,
        event_queue: Optional[Any] = None,
        document_generator: Optional[Any] = None,
        document_id: Optional[str] = None,
        main_loop: Optional[Any] = None,
        sections_filter: Optional[List[str]] = None,
    ):
        super().__init__(llm_config)
        self.name = "streaming_icf_generation"
        self.sections = [
            "summary",
            "background",
            "participants",
            "procedures",
            "alternatives",
            "risks",
            "benefits",
        ]
        self.event_queue = event_queue
        self.document_generator = document_generator
        self.document_id = document_id
        self.main_loop = main_loop
        self.sections_filter = sections_filter

        # Override sections if filter is provided
        if sections_filter:
            self.sections = sections_filter

    def _create_section_generator(self, section_name: str) -> Any:
        """Create a section generator that streams tokens via the event queue."""

        def generate_section(state: AgentState) -> AgentState:
            try:
                logger.info(
                    f"Section {section_name} using document_id: '{self.document_id}'"
                )

                if not self.document_id:
                    raise ValueError(f"document_id is empty for section {section_name}")

                if not self.document_generator:
                    raise ValueError(
                        f"document_generator is missing for section {section_name}"
                    )

                query = self._get_section_query(section_name)

                # Get section-specific context
                context_items = self.document_generator.get_protocol_context(
                    self.document_id, query, min_score=0.3
                )

                # Log context items for this section
                if context_items:
                    logger.info(
                        f"Context for section '{section_name}' with query '{query}':"
                    )
                    for i, item in enumerate(context_items[:3]):  # Top 3 items
                        score = item.get("score", 0)
                        logger.info(f"  Section chunk {i+1} (relevance: {score:.3f})")

                context_text = (
                    "\n\n".join(
                        [
                            item.get("text", "")
                            for item in context_items[:3]  # Top 3 items
                        ]
                    )
                    if context_items
                    else f"No specific context for {section_name}"
                )

                # Generate section WITH token streaming
                section_prompt = self._get_section_prompt(section_name)

                # Create messages for the LLM
                from langchain_core.messages import HumanMessage, SystemMessage

                messages = [
                    SystemMessage(content=section_prompt),
                    HumanMessage(
                        content=SECTION_GENERATION_PROMPT.format(
                            context=context_text, section_name=section_name
                        )
                    ),
                ]

                # Send section start event (thread-safe)
                if self.event_queue:
                    try:
                        # Use thread-safe queue directly (no asyncio needed)
                        self.event_queue.put({
                            "type": "section_start",
                            "section_name": section_name,
                        })
                        logger.debug(f"Queued section start for {section_name}")
                    except Exception as e:
                        logger.error(
                            f"Failed to queue section start for {section_name}: {type(e).__name__}: {e}"
                        )

                # Stream tokens from the working LLM
                section_content = ""

                try:
                    for chunk in self.llm.stream(messages):
                        if hasattr(chunk, "content") and chunk.content:
                            # Ensure content is a string for concatenation
                            content = chunk.content
                            if isinstance(content, str):
                                section_content += content
                            else:
                                # Handle non-string content (convert to string)
                                section_content += str(content)

                            # Send each token to the queue (thread-safe)
                            if self.event_queue:
                                try:
                                    # Use thread-safe queue directly (no asyncio needed)
                                    self.event_queue.put({
                                        "type": "token",
                                        "section_name": section_name,
                                        "content": chunk.content,
                                        "accumulated_content": section_content,
                                    })
                                except Exception as e:
                                    logger.debug(
                                        f"Failed to queue token for {section_name}: {type(e).__name__}: {e}"
                                    )
                                    # Continue streaming even if we can't queue individual tokens

                except Exception as e:
                    logger.error(
                        f"Failed to stream {section_name} with working LLM: {e}"
                    )
                    # Fall back to non-streaming generation
                    section_content = self._generate_section_with_llm(
                        section_name, context_text, section_prompt
                    )

                # Send section complete event (thread-safe)
                if self.event_queue:
                    try:
                        # Use thread-safe queue directly (no asyncio needed)
                        self.event_queue.put({
                            "type": "section_complete",
                            "section_name": section_name,
                            "content": section_content,
                        })
                        logger.debug(f"Queued section complete for {section_name}")
                    except Exception as queue_error:
                        logger.error(
                            f"Failed to queue section complete for {section_name}: {type(queue_error).__name__}: {queue_error}"
                        )

                # Update state with the generated content
                if section_name == "summary":
                    return {**state, "summary": [section_content]}
                elif section_name == "background":
                    return {**state, "background": [section_content]}
                elif section_name == "participants":
                    return {**state, "participants": [section_content]}
                elif section_name == "procedures":
                    return {**state, "procedures": [section_content]}
                elif section_name == "alternatives":
                    return {**state, "alternatives": [section_content]}
                elif section_name == "risks":
                    return {**state, "risks": [section_content]}
                elif section_name == "benefits":
                    return {**state, "benefits": [section_content]}
                else:
                    return state

            except Exception as e:
                logger.error(f"Failed to generate {section_name}: {e}")
                if self.event_queue:
                    try:
                        # Use thread-safe queue directly (no asyncio needed)
                        self.event_queue.put({
                            "type": "section_error",
                            "section_name": section_name,
                            "error": str(e),
                        })
                    except:
                        pass  # Ignore queue errors during error handling

                # Return state with empty content on error
                return state

        return generate_section

    def _compile_checklist(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Compile all sections into final checklist."""
        sections = state.get("sections", {})
        errors = state.get("errors", [])

        # Check if all required sections are present
        missing_sections = [s for s in self.sections if s not in sections]
        if missing_sections:
            error_msg = f"Missing sections: {', '.join(missing_sections)}"
            errors.append(error_msg)
            state["errors"] = errors

        # Add metadata
        metadata = state.get("metadata", {})
        metadata["generated_sections"] = list(sections.keys())
        metadata["workflow_name"] = self.name
        state["metadata"] = metadata

        logger.info(f"Compiled checklist with {len(sections)} sections")
        return state

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """Format context for LLM consumption."""
        if not context:
            return "No specific protocol context available."

        formatted = []
        for item in context[:5]:  # Limit to top 5 most relevant
            text = item.get("text", "")
            score = item.get("score", 0)
            formatted.append(f"[Relevance: {score:.2f}] {text}")

        return "\n\n".join(formatted)

    def _get_section_query(self, section_name: str) -> str:
        """Get section-specific queries for RAG retrieval."""
        return ICF_SECTION_QUERIES.get(
            section_name, "informed consent form requirements"
        )

    def _get_section_prompt(self, section_name: str) -> str:
        """Get the prompt for a specific ICF section."""
        return ICF_PROMPTS.get(
            section_name, "Generate an appropriate ICF section based on the context."
        )

    def build_graph(self) -> StateGraph:
        """Build the ICF generation workflow graph with parallel execution for efficiency."""
        workflow = StateGraph(AgentState)

        # Add parallel section generation nodes
        for section in self.sections:
            workflow.add_node(
                f"generate_{section}", self._create_section_generator(section)
            )

        # PARALLEL EXECUTION: All sections run simultaneously for efficiency
        for section in self.sections:
            workflow.add_edge(START, f"generate_{section}")
            workflow.add_edge(f"generate_{section}", END)

        return workflow


def get_langgraph_workflow(
    workflow_type: str, llm_config: Optional[Dict[str, Any]] = None
) -> Union[StreamingICFWorkflow, SiteChecklistWorkflow]:
    """Get LangGraph workflow instance."""
    if workflow_type == "icf":
        return StreamingICFWorkflow(llm_config)
    elif workflow_type == "site_checklist":
        return SiteChecklistWorkflow(llm_config)
    else:
        raise DocumentGenerationError(f"Unknown workflow type: {workflow_type}")


def generate_icf_sections(
    document_id: str, qdrant_client: QdrantClient, workflow: Optional[Any] = None
) -> Dict[str, str]:
    """Generate ICF sections for a protocol."""
    try:
        if workflow is None:
            workflow = StreamingICFWorkflow()

        # Get protocol context
        generator = DocumentGenerator(qdrant_client)
        context = generator.get_protocol_context(
            document_id, "informed consent requirements"
        )

        # Prepare workflow inputs
        workflow_inputs = {
            "document_id": document_id,
            "context": context,
            "document_type": "icf",
        }

        # Execute workflow
        result = workflow.invoke(workflow_inputs)

        # Validate required sections
        required_sections = [
            "summary",
            "background",
            "participants",
            "procedures",
            "alternatives",
            "risks",
            "benefits",
        ]
        for section in required_sections:
            if section not in result:
                raise DocumentGenerationError(
                    f"Missing required ICF section: {section}"
                )

        return result

    except Exception as e:
        raise DocumentGenerationError(f"Failed to generate ICF: {str(e)}")


def generate_site_checklist_sections(
    document_id: str, qdrant_client: QdrantClient, workflow: Optional[Any] = None
) -> Dict[str, str]:
    """Generate Site Initiation Checklist sections for a protocol."""
    try:
        if workflow is None:
            workflow = SiteChecklistWorkflow()

        # Get protocol context
        generator = DocumentGenerator(qdrant_client)
        context = generator.get_protocol_context(
            document_id, "site initiation requirements"
        )

        # Prepare workflow inputs
        workflow_inputs = {
            "document_id": document_id,
            "context": context,
            "document_type": "site_checklist",
        }

        # Execute workflow
        result = workflow.invoke(workflow_inputs)

        # Validate required sections
        required_sections = ["regulatory", "training", "equipment", "documentation"]
        for section in required_sections:
            if section not in result:
                raise DocumentGenerationError(
                    f"Missing required sections: {', '.join(required_sections)}"
                )

        return result

    except Exception as e:
        raise DocumentGenerationError(f"Failed to generate site checklist: {str(e)}")
