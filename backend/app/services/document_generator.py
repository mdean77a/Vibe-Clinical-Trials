"""
Document generation service using LangGraph workflows.

This module handles:
- ICF (Informed Consent Form) generation
- Site Initiation Checklist generation
- RAG context retrieval
- Section-based document assembly
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient


class DocumentGenerationError(Exception):
    """Exception raised for document generation errors."""

    pass


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
            from .qdrant_service import get_embeddings

            # Generate query embedding
            query_embedding = get_embeddings([query])[0]

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
                            "text": hit.payload.get("text", ""),
                            "score": hit.score,
                            "chunk_index": hit.payload.get("chunk_index", 0),
                        }
                    )

            return context

        except Exception as e:
            raise DocumentGenerationError(f"Failed to retrieve context: {str(e)}")


class WorkflowBase(ABC):
    """Base class for LangGraph workflows."""

    def __init__(self):
        self.name = "base_workflow"

    @abstractmethod
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow with given inputs."""
        pass


class ICFWorkflow(WorkflowBase):
    """Workflow for Informed Consent Form generation."""

    def __init__(self):
        super().__init__()
        self.name = "icf_generation"

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ICF sections."""
        # TODO: Implement actual LangGraph workflow
        # This is a placeholder for testing
        return {
            "title": "Generated ICF Title",
            "purpose": "Generated Purpose",
            "procedures": "Generated Procedures",
            "risks": "Generated Risks",
            "benefits": "Generated Benefits",
            "rights": "Generated Rights",
            "contact": "Generated Contact Info",
        }

    def generate_title(self, context: str) -> str:
        """Generate title section."""
        return f"Study Title: {context}"

    def generate_purpose(self, context: str) -> str:
        """Generate purpose section."""
        return f"Purpose: {context}"

    def generate_procedures(self, context: str) -> str:
        """Generate procedures section."""
        return f"Procedures: {context}"


class SiteChecklistWorkflow(WorkflowBase):
    """Workflow for Site Initiation Checklist generation."""

    def __init__(self):
        super().__init__()
        self.name = "site_checklist_generation"

    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate site checklist sections."""
        # TODO: Implement actual LangGraph workflow
        # This is a placeholder for testing
        return {
            "regulatory": "Generated Regulatory Requirements",
            "training": "Generated Training Requirements",
            "equipment": "Generated Equipment List",
            "documentation": "Generated Documentation Requirements",
            "preparation": "Generated Site Preparation Tasks",
            "timeline": "Generated Timeline and Milestones",
        }

    def generate_regulatory(self, context: str) -> str:
        """Generate regulatory requirements section."""
        return f"Regulatory: {context}"

    def generate_training(self, context: str) -> str:
        """Generate training requirements section."""
        return f"Training: {context}"

    def generate_equipment(self, context: str) -> str:
        """Generate equipment requirements section."""
        return f"Equipment: {context}"


def get_langgraph_workflow(workflow_type: str):
    """Get LangGraph workflow instance."""
    if workflow_type == "icf":
        return ICFWorkflow()
    elif workflow_type == "site_checklist":
        return SiteChecklistWorkflow()
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
            "title",
            "purpose",
            "procedures",
            "risks",
            "benefits",
            "rights",
            "contact",
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
