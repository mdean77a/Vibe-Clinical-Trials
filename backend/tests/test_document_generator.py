"""
Unit tests for AI document generation pipeline.

This module tests LangGraph workflows for:
- ICF (Informed Consent Form) generation
- Site Initiation Checklist generation
- RAG context retrieval
- Section-based generation
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.document_generator import (
    DocumentGenerationError,
    DocumentGenerator,
    ICFWorkflow,
    SiteChecklistWorkflow,
    generate_icf_sections,
    generate_site_checklist_sections,
)


class TestDocumentGenerator:
    """Test cases for DocumentGenerator class."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_init_generator(self, mock_qdrant_client, mock_langgraph_workflow):
        """Test DocumentGenerator initialization."""
        generator = DocumentGenerator(
            qdrant_client=mock_qdrant_client,
            icf_workflow=mock_langgraph_workflow,
            checklist_workflow=mock_langgraph_workflow,
        )

        assert generator.qdrant_client == mock_qdrant_client
        assert generator.icf_workflow == mock_langgraph_workflow
        assert generator.checklist_workflow == mock_langgraph_workflow

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_get_protocol_context_success(
        self, mock_qdrant_client, sample_protocol_metadata
    ):
        """Test successful protocol context retrieval."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock Qdrant search results
        mock_qdrant_client.search.return_value = [
            MagicMock(payload={"text": "Protocol inclusion criteria"}, score=0.9),
            MagicMock(payload={"text": "Study procedures description"}, score=0.8),
        ]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        with patch(
            "app.services.qdrant_service.QdrantService.get_embeddings", return_value=[[0.1] * 1536]
        ):
            context = generator.get_protocol_context(document_id, "inclusion criteria")

        assert len(context) == 2
        assert "Protocol inclusion criteria" in context[0]["text"]
        assert context[0]["score"] == 0.9


class TestICFGeneration:
    """Test cases for ICF (Informed Consent Form) generation."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_icf_sections_success(
        self, mock_qdrant_client, mock_langgraph_workflow, sample_protocol_metadata
    ):
        """Test successful ICF generation."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock workflow response
        mock_langgraph_workflow.invoke.return_value = {
            "summary": "Study Summary: Safety and Efficacy Trial",
            "background": "The background of this study is to evaluate...",
            "participants": "We will enroll 100 participants...",
            "procedures": "Participants will undergo the following procedures...",
            "alternatives": "Alternative treatments include...",
            "risks": "Potential risks include mild side effects...",
            "benefits": "Potential benefits include symptom improvement...",
        }

        # Mock context retrieval
        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=["Relevant protocol context"],
        ):

            result = generate_icf_sections(
                document_id=document_id,
                qdrant_client=mock_qdrant_client,
                workflow=mock_langgraph_workflow,
            )

        assert "summary" in result
        assert "background" in result
        assert "participants" in result
        assert "procedures" in result
        assert "alternatives" in result
        assert "risks" in result
        assert "benefits" in result

        assert result["summary"].startswith("Study Summary:")
        mock_langgraph_workflow.invoke.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_icf_sections_workflow_error(
        self, mock_qdrant_client, mock_langgraph_workflow, sample_protocol_metadata
    ):
        """Test ICF generation with workflow error."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock workflow error
        mock_langgraph_workflow.invoke.side_effect = Exception(
            "LangGraph execution failed"
        )

        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=["Context"],
        ):

            with pytest.raises(DocumentGenerationError, match="Failed to generate ICF"):
                generate_icf_sections(
                    document_id, mock_qdrant_client, mock_langgraph_workflow
                )


class TestSiteChecklistGeneration:
    """Test cases for Site Initiation Checklist generation."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_site_checklist_success(
        self, mock_qdrant_client, mock_langgraph_workflow, sample_protocol_metadata
    ):
        """Test successful Site Initiation Checklist generation."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock workflow response
        mock_langgraph_workflow.invoke.return_value = {
            "regulatory": "IRB approval required before study initiation...",
            "training": "All study staff must complete GCP training...",
            "equipment": "Required equipment includes centrifuge, freezer...",
            "documentation": "Essential documents checklist includes...",
            "preparation": "Site preparation tasks include...",
            "timeline": "Study timeline and milestones...",
        }

        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=["Site requirements context"],
        ):

            result = generate_site_checklist_sections(
                document_id=document_id,
                qdrant_client=mock_qdrant_client,
                workflow=mock_langgraph_workflow,
            )

        assert "regulatory" in result
        assert "training" in result
        assert "equipment" in result
        assert "documentation" in result
        assert "preparation" in result
        assert "timeline" in result

        assert "IRB approval" in result["regulatory"]
        mock_langgraph_workflow.invoke.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_site_checklist_missing_sections(
        self, mock_qdrant_client, mock_langgraph_workflow, sample_protocol_metadata
    ):
        """Test site checklist generation with missing sections."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock incomplete workflow response
        mock_langgraph_workflow.invoke.return_value = {
            "regulatory": "IRB approval required...",
            "training": "GCP training required...",
            # Missing other required sections
        }

        with patch(
            "app.services.document_generator.DocumentGenerator.get_protocol_context",
            return_value=["Context"],
        ):

            with pytest.raises(
                DocumentGenerationError, match="Missing required sections"
            ):
                generate_site_checklist_sections(
                    document_id, mock_qdrant_client, mock_langgraph_workflow
                )


class TestRAGContextRetrieval:
    """Test cases for RAG context retrieval."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_rag_context_for_icf(self, mock_qdrant_client, sample_protocol_metadata):
        """Test RAG context retrieval for ICF generation."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock context retrieval for different ICF sections
        mock_qdrant_client.search.side_effect = [
            # Title context
            [MagicMock(payload={"text": "Study title and acronym"}, score=0.95)],
            # Purpose context
            [
                MagicMock(
                    payload={"text": "Primary and secondary objectives"}, score=0.90
                )
            ],
            # Procedures context
            [MagicMock(payload={"text": "Study procedures and visits"}, score=0.88)],
        ]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        with patch(
            "app.services.qdrant_service.QdrantService.get_embeddings", return_value=[[0.1] * 1536]
        ):
            # Test different section contexts
            title_context = generator.get_protocol_context(document_id, "study title")
            purpose_context = generator.get_protocol_context(
                document_id, "study objectives"
            )
            procedures_context = generator.get_protocol_context(
                document_id, "study procedures"
            )

        assert len(title_context) == 1
        assert "Study title" in title_context[0]["text"]

        assert len(purpose_context) == 1
        assert "objectives" in purpose_context[0]["text"]

        assert len(procedures_context) == 1
        assert "procedures" in procedures_context[0]["text"]

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_rag_context_insufficient_results(
        self, mock_qdrant_client, sample_protocol_metadata
    ):
        """Test RAG context retrieval with insufficient results."""
        document_id = sample_protocol_metadata["document_id"]

        # Mock low-score results
        mock_qdrant_client.search.return_value = [
            MagicMock(payload={"text": "Irrelevant content"}, score=0.3)
        ]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        with patch(
            "app.services.qdrant_service.QdrantService.get_embeddings", return_value=[[0.1] * 1536]
        ):
            context = generator.get_protocol_context(
                document_id,
                "specific medical procedure",
                min_score=0.7,  # Higher threshold
            )

        assert len(context) == 0  # No results above threshold


class TestWorkflowClasses:
    """Test cases for workflow classes."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_icf_workflow_init(self):
        """Test ICFWorkflow initialization."""
        workflow = ICFWorkflow()

        assert workflow.name == "icf_generation"
        assert hasattr(workflow, "generate_title")
        assert hasattr(workflow, "generate_purpose")
        assert hasattr(workflow, "generate_procedures")

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_site_checklist_workflow_init(self):
        """Test SiteChecklistWorkflow initialization."""
        workflow = SiteChecklistWorkflow()

        assert workflow.name == "site_checklist_generation"
        assert hasattr(workflow, "generate_regulatory")
        assert hasattr(workflow, "generate_training")
        assert hasattr(workflow, "generate_equipment")


class TestIntegrationScenarios:
    """Integration test scenarios for document generation."""

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_end_to_end_icf_generation(
        self, memory_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test end-to-end ICF generation process."""
        # First store protocol in Qdrant
        with patch(
            "app.services.qdrant_service.QdrantService.get_embeddings",
            return_value=[[0.1] * 1536 for _ in sample_protocol_chunks],
        ):
            from app.services.qdrant_service import QdrantService

            qdrant_service = QdrantService()
            qdrant_service.client = memory_qdrant_client  # Use test client
            
            embeddings = [[0.1] * 1536 for _ in sample_protocol_chunks]
            collection_name = qdrant_service.create_protocol_collection(
                sample_protocol_metadata["document_id"],
                sample_protocol_metadata["protocol_title"]
            )
            
            qdrant_service.store_protocol_with_metadata(
                collection_name=collection_name,
                chunks=sample_protocol_chunks,
                embeddings=embeddings,
                protocol_metadata=sample_protocol_metadata,
            )

        # Mock ICF workflow
        mock_workflow = MagicMock()
        mock_workflow.invoke.return_value = {
            "summary": "Generated ICF Summary",
            "background": "Generated Background",
            "participants": "Generated Participants",
            "procedures": "Generated Procedures",
            "alternatives": "Generated Alternatives",
            "risks": "Generated Risks",
            "benefits": "Generated Benefits",
        }

        # Generate ICF using the collection name that was actually created
        with patch(
            "app.services.qdrant_service.QdrantService.get_embeddings", return_value=[[0.1] * 1536]
        ):
            icf_sections = generate_icf_sections(
                document_id=collection_name,  # Use the actual collection name
                qdrant_client=memory_qdrant_client,
                workflow=mock_workflow,
            )

        assert len(icf_sections) == 7
        assert all(
            section in icf_sections
            for section in [
                "summary",
                "background", 
                "participants",
                "procedures",
                "alternatives",
                "risks",
                "benefits",
            ]
        )
        mock_workflow.invoke.assert_called_once()
