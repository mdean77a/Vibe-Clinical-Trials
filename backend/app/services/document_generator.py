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
from typing import Any, Dict, List, Optional, Union, Annotated, TypedDict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


def merge_sections(left: Dict[str, str], right: Dict[str, str]) -> Dict[str, str]:
    """Custom reducer to merge sections dictionaries safely."""
    result = left.copy() if left else {}
    if right:
        result.update(right)
    return result


def merge_errors(left: List[str], right: List[str]) -> List[str]:
    """Custom reducer to merge error lists safely."""
    result = left.copy() if left else []
    if right:
        result.extend(right)
    return result


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
        self, qdrant_client: QdrantClient, icf_workflow=None, checklist_workflow=None
    ):
        self.qdrant_client = qdrant_client
        self.icf_workflow = icf_workflow
        self.checklist_workflow = checklist_workflow

    def get_protocol_context(
        self, protocol_collection_name: str, query: str, min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant protocol context for document generation."""
        try:
            from .qdrant_service import QdrantService

            # Initialize QdrantService to get embeddings
            qdrant_service = QdrantService()
            
            # Generate query embedding
            query_embedding = qdrant_service.get_embeddings([query])[0]

            # Search for relevant context in the specific protocol collection
            search_results = self.qdrant_client.search(
                collection_name=protocol_collection_name,
                query_vector=query_embedding,
                limit=10,
            )

            # Filter by minimum score
            context = []
            for hit in search_results:
                if hit.score >= min_score:
                    context.append(
                        {
                            "text": hit.payload.get("chunk_text", hit.payload.get("text", "")),
                            "score": hit.score,
                            "chunk_index": hit.payload.get("chunk_index", 0),
                        }
                    )

            return context

        except Exception as e:
            raise DocumentGenerationError(f"Failed to retrieve context: {str(e)}")


class WorkflowBase(ABC):
    """Base class for LangGraph workflows."""

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.name = "base_workflow"
        self.llm_config = llm_config or {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 8192,
            "temperature": 0.1,
        }
        self._compiled_graph: Optional[CompiledStateGraph] = None
        self._initialize_llm()

    def _initialize_llm(self) -> None:
        """Initialize the LLM for the workflow."""
        try:
            self.llm = ChatAnthropic(
                model=self.llm_config["model"],
                max_tokens=self.llm_config["max_tokens"],
                temperature=self.llm_config["temperature"],
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            # Fallback to GPT-4o
            try:
                from langchain_openai import ChatOpenAI
                self.llm = ChatOpenAI(
                    model="gpt-4o",
                    max_tokens=self.llm_config["max_tokens"],
                    temperature=self.llm_config["temperature"],
                )
                logger.info("Using GPT-4o as fallback LLM")
            except Exception as fallback_error:
                logger.error(f"Fallback LLM initialization failed: {fallback_error}")
                raise DocumentGenerationError(
                    f"Failed to initialize any LLM: {e}, fallback: {fallback_error}"
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
            workflow_state = {
                "summary": [],
                "background": [],
                "participants": [],
                "procedures": [],
                "alternatives": [],
                "risks": [],
                "benefits": [],
                "document_generator": document_generator
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
                    if hasattr(latest_item, 'content'):
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
                    **inputs.get("metadata", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise DocumentGenerationError(f"Workflow execution failed: {str(e)}")

    def _generate_section_with_llm(
        self, section_name: str, context: str, section_prompt: str
    ) -> str:
        """Generate a section using the LLM."""
        try:
            messages = [
                SystemMessage(content=section_prompt),
                HumanMessage(content=f"Context: {context}\n\nGenerate the {section_name} section."),
            ]
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate {section_name} section: {e}")
            raise DocumentGenerationError(f"Failed to generate {section_name}: {str(e)}")


class ICFWorkflow(WorkflowBase):
    """Workflow for Informed Consent Form generation."""

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        super().__init__(llm_config)
        self.name = "icf_generation"
        self.sections = [
            "summary", "background", "participants", "procedures", 
            "alternatives", "risks", "benefits"
        ]

    def build_graph(self) -> StateGraph:
        """Build the ICF generation workflow graph with true parallel execution."""
        workflow = StateGraph(AgentState)
        
        # Add parallel section generation nodes (like your prototype)
        for section in self.sections:
            workflow.add_node(f"generate_{section}", self._create_section_generator(section))
        
        # TRUE PARALLEL EXECUTION: All nodes start from START and go directly to END
        for section in self.sections:
            workflow.add_edge(START, f"generate_{section}")
            workflow.add_edge(f"generate_{section}", END)
        
        return workflow

    def _get_section_query(self, section_name: str) -> str:
        """Get section-specific queries like your prototype."""
        queries = {
            "summary": "study purpose objectives overview participants intervention primary endpoints summary",
            "background": "background rationale medical condition disease previous studies literature review justification",
            "participants": "eligibility criteria inclusion exclusion participants enrollment target population demographics",
            "procedures": "study procedures visits tests treatments interventions timeline schedule follow-up assessments",
            "alternatives": "alternative treatments standard care options therapy comparisons current practice",
            "risks": "risks side effects adverse events safety monitoring toxicity complications contraindications",
            "benefits": "benefits outcomes efficacy potential improvements therapeutic effects clinical benefits"
        }
        return queries.get(section_name, "informed consent form requirements")

    def generate_title(self, context: str) -> str:
        """Generate title section - kept for backward compatibility."""
        return self._generate_section_with_llm("title", context, self._get_section_prompt("summary"))

    def generate_purpose(self, context: str) -> str:
        """Generate purpose section - kept for backward compatibility."""
        return self._generate_section_with_llm("purpose", context, self._get_section_prompt("background"))

    def generate_procedures(self, context: str) -> str:
        """Generate procedures section - kept for backward compatibility."""
        return self._generate_section_with_llm("procedures", context, self._get_section_prompt("procedures"))

    def _create_section_generator(self, section_name: str):
        """Create a section generator function with individual RAG retrieval like the prototype."""
        def generate_section(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Get the document generator for this state
                document_generator = state.get("document_generator")
                if not document_generator:
                    raise ValueError("Document generator not found in state")
                
                # Get document_id from the workflow inputs (passed via document_generator)
                document_id = getattr(document_generator, '_current_document_id', None)
                if not document_id:
                    raise ValueError("Document ID not found in document_generator")
                
                # SECTION-SPECIFIC RAG RETRIEVAL (like your prototype)
                section_query = self._get_section_query(section_name)
                logger.info(f"Retrieving context for {section_name} with query: '{section_query}'")
                
                # Individual retrieval for this specific section
                context = document_generator.get_protocol_context(
                    document_id, 
                    section_query,
                    min_score=0.2  # Lower threshold for section-specific content
                )
                
                logger.info(f"Retrieved {len(context)} context items for {section_name}")
                if context:
                    total_text_length = sum(len(item.get("text", "")) for item in context)
                    logger.info(f"{section_name} context total text length: {total_text_length}")
                
                context_text = self._format_context(context)
                prompt = self._get_section_prompt(section_name)
                
                section_content = self._generate_section_with_llm(
                    section_name, context_text, prompt
                )
                
                # Return the specific section field in a list (like your prototype: {"summary": [summary]})
                # This allows for revision history - initial generation appends first item
                return {section_name: [section_content]}
                
            except Exception as e:
                logger.error(f"Failed to generate {section_name}: {e}")
                # Return empty result - error handling done outside workflow
                return {}
        
        return generate_section


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

    def _get_section_prompt(self, section_name: str) -> str:
        """Get the prompt for a specific ICF section."""
        prompts = {
            "summary": """
You are an expert clinical trial specialist creating an ICF Summary section.
Generate a clear, concise summary (2-3 paragraphs) that:
- Explains what the study is about in plain language
- States the main purpose and what participants will do
- Mentions key time commitments
- Uses language appropriate for general public (8th grade reading level)
- Follows FDA 21 CFR 50 guidelines
""",
            "background": """
You are an expert clinical trial specialist creating an ICF Background section.
Generate a comprehensive background section that:
- Explains the medical condition or research question
- Describes why this study is needed
- Summarizes relevant previous research
- Explains how this study will advance knowledge
- Uses clear, non-technical language when possible
- Follows FDA 21 CFR 50 guidelines
""",
            "participants": """
You are an expert clinical trial specialist creating an ICF Participants section.
Generate a clear participants section that:
- States the total number of participants expected
- Explains who can participate (inclusion criteria in plain language)
- Explains who cannot participate (exclusion criteria in plain language)
- Mentions study locations if relevant
- Uses accessible language for general public
- Follows FDA 21 CFR 50 guidelines
""",
            "procedures": """
You are an expert clinical trial specialist creating an ICF Study Procedures section.
Generate a detailed procedures section that:
- Lists all study visits and procedures chronologically
- Explains what happens at each visit
- Describes any tests, treatments, or interventions
- Mentions time commitments for each procedure
- Explains any follow-up requirements
- Uses step-by-step format for clarity
- Follows FDA 21 CFR 50 guidelines
""",
            "alternatives": """
You are an expert clinical trial specialist creating an ICF Alternative Procedures section.
Generate a comprehensive alternatives section that:
- Lists available alternative treatments outside the study
- Explains standard care options
- Describes pros and cons of alternatives vs. study participation
- Mentions that choosing not to participate is an alternative
- Uses balanced, non-coercive language
- Follows FDA 21 CFR 50 guidelines
""",
            "risks": """
You are an expert clinical trial specialist creating an ICF Risks section.
Generate a thorough risks section that:
- Lists all known and potential risks
- Explains likelihood and severity of each risk
- Describes how risks will be monitored and managed
- Mentions unknown risks may exist
- Uses clear, honest language without minimizing risks
- Groups risks by category (common, serious, unknown)
- Follows FDA 21 CFR 50 guidelines
""",
            "benefits": """
You are an expert clinical trial specialist creating an ICF Benefits section.
Generate a balanced benefits section that:
- Lists potential direct benefits to participants
- Explains potential benefits to society/future patients
- Clearly states that benefits are not guaranteed
- Avoids overstating or promising benefits
- Uses realistic, evidence-based language
- Balances hope with scientific uncertainty
- Follows FDA 21 CFR 50 guidelines
""",
        }
        
        return prompts.get(section_name, "Generate an appropriate ICF section based on the context.")


class SiteChecklistWorkflow(WorkflowBase):
    """Workflow for Site Initiation Checklist generation."""

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        super().__init__(llm_config)
        self.name = "site_checklist_generation"
        self.sections = [
            "regulatory", "training", "equipment", 
            "documentation", "preparation", "timeline"
        ]

    def build_graph(self) -> StateGraph:
        """Build the site checklist generation workflow graph."""
        workflow = StateGraph(dict)
        
        # Add parallel section generation nodes
        for section in self.sections:
            workflow.add_node(f"generate_{section}", self._create_section_generator(section))
        
        # Add compilation node
        workflow.add_node("compile_checklist", self._compile_checklist)
        
        # Set entry point
        workflow.set_entry_point("generate_regulatory")
        
        # Connect nodes in parallel execution pattern
        for i, section in enumerate(self.sections):
            if i < len(self.sections) - 1:
                workflow.add_edge(f"generate_{section}", f"generate_{self.sections[i+1]}")
            else:
                workflow.add_edge(f"generate_{section}", "compile_checklist")
        
        # Connect compilation to end
        workflow.add_edge("compile_checklist", END)
        
        return workflow

    def generate_regulatory(self, context: str) -> str:
        """Generate regulatory requirements section - kept for backward compatibility."""
        return self._generate_section_with_llm("regulatory", context, self._get_section_prompt("regulatory"))

    def generate_training(self, context: str) -> str:
        """Generate training requirements section - kept for backward compatibility."""
        return self._generate_section_with_llm("training", context, self._get_section_prompt("training"))

    def generate_equipment(self, context: str) -> str:
        """Generate equipment requirements section - kept for backward compatibility."""
        return self._generate_section_with_llm("equipment", context, self._get_section_prompt("equipment"))


class StreamingICFWorkflow(ICFWorkflow):
    """Streaming version of ICF workflow that sends tokens to a queue."""
    
    def __init__(self, llm_config: Optional[Dict[str, Any]] = None, event_queue=None, document_generator=None, document_id=None, main_loop=None):
        super().__init__(llm_config)
        self.event_queue = event_queue
        self.document_generator = document_generator
        self.document_id = document_id
        self.main_loop = main_loop
        
    def _create_section_generator(self, section_name: str):
        """Create a section generator that streams tokens via the event queue."""
        
        def generate_section(state: AgentState) -> AgentState:
            try:
                logger.info(f"Section {section_name} using document_id: '{self.document_id}'")
                
                if not self.document_id:
                    raise ValueError(f"document_id is empty for section {section_name}")
                
                if not self.document_generator:
                    raise ValueError(f"document_generator is missing for section {section_name}")
                
                query = self._get_section_query(section_name)
                
                # Get section-specific context
                context_items = self.document_generator.get_protocol_context(
                    self.document_id, query, min_score=0.3
                )
                
                context_text = "\n\n".join([
                    item.get("text", "") for item in context_items[:3]  # Top 3 items
                ]) if context_items else f"No specific context for {section_name}"
                
                # Generate section WITH token streaming
                section_prompt = self._get_section_prompt(section_name)
                
                # Create messages for the LLM
                from langchain_core.messages import HumanMessage, SystemMessage
                messages = [
                    SystemMessage(content=section_prompt),
                    HumanMessage(content=f"Context: {context_text}\n\nGenerate the {section_name} section."),
                ]
                
                # Send section start event
                if self.event_queue and self.main_loop:
                    try:
                        import asyncio
                        if not self.main_loop.is_closed():
                            future = asyncio.run_coroutine_threadsafe(
                                self.event_queue.put({
                                    "type": "section_start",
                                    "section_name": section_name
                                }),
                                self.main_loop
                            )
                            future.result(timeout=1.0)  # Wait up to 1 second for section start
                    except Exception as e:
                        logger.error(f"Failed to queue section start for {section_name}: {e}")
                
                # Stream tokens from the LLM
                section_content = ""
                try:
                    for chunk in self.llm.stream(messages):
                        if hasattr(chunk, 'content') and chunk.content:
                            section_content += chunk.content
                            
                            # Send each token to the queue
                            if self.event_queue and self.main_loop:
                                try:
                                    import asyncio
                                    # Check if the event loop is still running
                                    if not self.main_loop.is_closed():
                                        future = asyncio.run_coroutine_threadsafe(
                                            self.event_queue.put({
                                                "type": "token",
                                                "section_name": section_name,
                                                "content": chunk.content,
                                                "accumulated_content": section_content
                                            }),
                                            self.main_loop
                                        )
                                        # Wait briefly for the future to complete to avoid overwhelming the queue
                                        future.result(timeout=0.1)
                                    else:
                                        logger.warning(f"Event loop closed, cannot send token for {section_name}")
                                        break  # Stop streaming if event loop is closed
                                except asyncio.TimeoutError:
                                    # Token queuing timeout - continue but log it
                                    logger.debug(f"Token queuing timeout for {section_name}")
                                except Exception as e:
                                    logger.error(f"Failed to queue token for {section_name}: {e}")
                                    # Continue streaming even if we can't queue individual tokens
                
                except Exception as e:
                    logger.error(f"Failed to stream {section_name}: {e}")
                    # Fallback to non-streaming generation
                    section_content = self._generate_section_with_llm(
                        section_name, context_text, section_prompt
                    )
                
                # Send section complete event
                if self.event_queue and self.main_loop:
                    try:
                        import asyncio
                        if not self.main_loop.is_closed():
                            future = asyncio.run_coroutine_threadsafe(
                                self.event_queue.put({
                                    "type": "section_complete",
                                    "section_name": section_name,
                                    "content": section_content
                                }),
                                self.main_loop
                            )
                            future.result(timeout=1.0)  # Wait up to 1 second for section complete
                    except Exception as queue_error:
                        logger.error(f"Failed to queue section complete for {section_name}: {queue_error}")
                elif self.event_queue:
                    logger.warning(f"No main loop available for {section_name}")
                
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
                if self.event_queue and self.main_loop:
                    try:
                        import asyncio
                        if not self.main_loop.is_closed():
                            future = asyncio.run_coroutine_threadsafe(
                                self.event_queue.put({
                                    "type": "section_error",
                                    "section_name": section_name,
                                    "error": str(e)
                                }),
                                self.main_loop
                            )
                            future.result(timeout=1.0)
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

    def _get_section_prompt(self, section_name: str) -> str:
        """Get the prompt for a specific checklist section."""
        prompts = {
            "regulatory": """
You are an expert clinical operations specialist creating regulatory requirements for site initiation.
Generate a comprehensive regulatory checklist that includes:
- IRB/IEC approval requirements and timelines
- Regulatory submissions and documentation
- Protocol amendments and notifications
- Investigator qualifications and CVs
- Site licensing and certification requirements
- Regulatory compliance monitoring setup
Format as actionable checklist items with clear deadlines.
""",
            "training": """
You are an expert clinical operations specialist creating training requirements for site initiation.
Generate a comprehensive training checklist that includes:
- GCP (Good Clinical Practice) training requirements
- Protocol-specific training modules
- Investigator and staff training documentation
- Training verification and competency assessment
- Ongoing training requirements
- Training record maintenance
Format as actionable checklist items with clear completion criteria.
""",
            "equipment": """
You are an expert clinical operations specialist creating equipment requirements for site initiation.
Generate a comprehensive equipment checklist that includes:
- Study-specific equipment and supplies
- Calibration and maintenance requirements
- Installation and setup procedures
- User training for equipment
- Backup and contingency equipment
- Equipment qualification documentation
Format as actionable checklist items with specifications.
""",
            "documentation": """
You are an expert clinical operations specialist creating documentation requirements for site initiation.
Generate a comprehensive documentation checklist that includes:
- Essential document preparation and filing
- Site file organization and maintenance
- Source document templates and guidelines
- Data collection forms and eCRF setup
- Document version control procedures
- Archival and retention requirements
Format as actionable checklist items with clear deliverables.
""",
            "preparation": """
You are an expert clinical operations specialist creating site preparation tasks for study initiation.
Generate a comprehensive preparation checklist that includes:
- Physical site preparation and setup
- Staff role assignments and responsibilities
- Communication protocols and contacts
- Emergency procedures and safety protocols
- Participant recruitment preparation
- Site visit scheduling and logistics
Format as actionable checklist items with clear timelines.
""",
            "timeline": """
You are an expert clinical operations specialist creating timeline and milestones for site initiation.
Generate a comprehensive timeline that includes:
- Key milestone dates and dependencies
- Critical path activities and deadlines
- Regulatory submission timelines
- Training completion schedules
- Equipment delivery and installation dates
- Study start and recruitment timelines
Format as actionable timeline with clear milestones and deadlines.
""",
        }
        
        return prompts.get(section_name, "Generate an appropriate checklist section based on the context.")


def get_langgraph_workflow(workflow_type: str, llm_config: Optional[Dict[str, Any]] = None):
    """Get LangGraph workflow instance."""
    if workflow_type == "icf":
        return ICFWorkflow(llm_config)
    elif workflow_type == "site_checklist":
        return SiteChecklistWorkflow(llm_config)
    else:
        raise DocumentGenerationError(f"Unknown workflow type: {workflow_type}")


def generate_icf_sections(
    document_id: str, qdrant_client: QdrantClient, workflow=None
) -> Dict[str, str]:
    """Generate ICF sections for a protocol."""
    try:
        if workflow is None:
            workflow = ICFWorkflow()

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
    document_id: str, qdrant_client: QdrantClient, workflow=None
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
