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
    StreamingICFWorkflow,
    generate_icf_sections,
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

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        # Mock the LangChain service and its similarity search method
        mock_langchain_service = MagicMock()
        mock_doc1 = MagicMock(page_content="Protocol inclusion criteria", metadata={})
        mock_doc2 = MagicMock(page_content="Study procedures description", metadata={})

        mock_langchain_service.similarity_search_with_score.return_value = [
            (mock_doc1, 0.9),
            (mock_doc2, 0.8),
        ]

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
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




class TestRAGContextRetrieval:
    """Test cases for RAG context retrieval."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_rag_context_for_icf(self, mock_qdrant_client, sample_protocol_metadata):
        """Test RAG context retrieval for ICF generation."""
        document_id = sample_protocol_metadata["document_id"]

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        # Mock the LangChain service
        mock_langchain_service = MagicMock()

        # Set up different return values for different queries
        def mock_search_side_effect(collection_name, query, k):
            if "title" in query.lower():
                return [
                    (
                        MagicMock(page_content="Study title and acronym", metadata={}),
                        0.95,
                    )
                ]
            elif "objectives" in query.lower():
                return [
                    (
                        MagicMock(
                            page_content="Primary and secondary objectives", metadata={}
                        ),
                        0.90,
                    )
                ]
            elif "procedures" in query.lower():
                return [
                    (
                        MagicMock(
                            page_content="Study procedures and visits", metadata={}
                        ),
                        0.88,
                    )
                ]
            return []

        mock_langchain_service.similarity_search_with_score.side_effect = (
            mock_search_side_effect
        )

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
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

        generator = DocumentGenerator(mock_qdrant_client, None, None)

        # Mock the LangChain service with low-score results
        mock_langchain_service = MagicMock()
        mock_langchain_service.similarity_search_with_score.return_value = [
            (MagicMock(page_content="Irrelevant content", metadata={}), 0.3)
        ]

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
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
        """Test StreamingICFWorkflow initialization."""
        workflow = StreamingICFWorkflow()

        assert workflow.name == "icf_generation"



class TestIntegrationScenarios:
    """Integration test scenarios for document generation."""

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_end_to_end_icf_generation(
        self, memory_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test end-to-end ICF generation process."""
        # First store protocol in Qdrant
        # Create a protocol collection for testing
        from app.services.qdrant_service import QdrantService

        qdrant_service = QdrantService()
        qdrant_service.client = memory_qdrant_client  # Use test client

        collection_name = qdrant_service.create_protocol_collection(
            study_acronym="TEST",
            protocol_title=sample_protocol_metadata["protocol_title"],
        )
        sample_protocol_metadata["collection_name"] = collection_name

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
        # Mock the LangChain service for context retrieval
        mock_langchain_service = MagicMock()
        mock_langchain_service.similarity_search_with_score.return_value = [
            (MagicMock(page_content="Relevant protocol content", metadata={}), 0.9)
        ]

        with patch(
            "app.services.langchain_qdrant_service.get_langchain_qdrant_service",
            return_value=mock_langchain_service,
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
