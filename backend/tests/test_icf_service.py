"""
Tests for ICF generation service.

This module contains tests for the ICF generation service that handles
streaming ICF document generation using LangGraph workflows.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.document_generator import DocumentGenerationError
from app.services.icf_service import ICFGenerationService


class TestICFGenerationService:
    """Test cases for ICFGenerationService class."""

    @pytest.fixture
    def mock_qdrant_client(self):
        """Mock Qdrant client for testing."""
        return MagicMock()

    @pytest.fixture
    def sample_protocol_metadata(self):
        """Sample protocol metadata for testing."""
        return {
            "protocol_title": "Test Clinical Trial",
            "sponsor": "Test Pharma",
            "indication": "Test Indication",
        }

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_init_service(self, mock_qdrant_client):
        """Test ICFGenerationService initialization."""
        service = ICFGenerationService(mock_qdrant_client)

        assert service.qdrant_client == mock_qdrant_client
        assert service.llm_config is not None  # Empty dict but should exist
        assert service.document_generator is not None

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_format_context_for_llm(self, mock_qdrant_client):
        """Test context formatting for LLM consumption."""
        service = ICFGenerationService(mock_qdrant_client)

        context = [
            {"text": "First context item", "score": 0.9},
            {"text": "Second context item", "score": 0.8},
            {"text": "Third context item", "score": 0.7},
        ]

        formatted = service._format_context_for_llm(context)

        assert "[Relevance: 0.90]" in formatted
        assert "First context item" in formatted
        assert "Second context item" in formatted
        assert "Third context item" in formatted

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_format_context_empty(self, mock_qdrant_client):
        """Test context formatting with empty context."""
        service = ICFGenerationService(mock_qdrant_client)

        formatted = service._format_context_for_llm([])

        assert formatted == "No specific protocol context available."

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_get_section_prompt(self, mock_qdrant_client):
        """Test section prompt retrieval."""
        service = ICFGenerationService(mock_qdrant_client)

        prompt = service._get_section_prompt("summary")

        assert isinstance(prompt, str)
        assert len(prompt) > 0

        # Test unknown section fallback
        unknown_prompt = service._get_section_prompt("unknown_section")
        assert "Generate an appropriate ICF section" in unknown_prompt

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_get_generation_status(self, mock_qdrant_client):
        """Test generation status retrieval."""
        service = ICFGenerationService(mock_qdrant_client)

        status = service.get_generation_status("test_task_id")

        assert status["task_id"] == "test_task_id"
        assert status["status"] == "not_implemented"
        assert "message" in status

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_validate_collection_exists_true(self, mock_qdrant_client):
        """Test collection validation when collection exists."""
        service = ICFGenerationService(mock_qdrant_client)

        # Mock successful collection retrieval
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        mock_collections_response = MagicMock()
        mock_collections_response.collections = [mock_collection]
        mock_qdrant_client.get_collections.return_value = mock_collections_response

        exists = await service.validate_collection_exists("test_collection")

        assert exists is True

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_validate_collection_exists_false(self, mock_qdrant_client):
        """Test collection validation when collection doesn't exist."""
        service = ICFGenerationService(mock_qdrant_client)

        # Mock empty collections
        mock_collections_response = MagicMock()
        mock_collections_response.collections = []
        mock_qdrant_client.get_collections.return_value = mock_collections_response

        exists = await service.validate_collection_exists("nonexistent_collection")

        assert exists is False

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_validate_collection_error(self, mock_qdrant_client):
        """Test collection validation with error."""
        service = ICFGenerationService(mock_qdrant_client)

        # Mock error during collection retrieval
        mock_qdrant_client.get_collections.side_effect = Exception("Connection failed")

        exists = await service.validate_collection_exists("test_collection")

        assert exists is False

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_get_protocol_summary_success(self, mock_qdrant_client):
        """Test successful protocol summary retrieval."""
        service = ICFGenerationService(mock_qdrant_client)

        # Mock successful scroll response
        mock_point = MagicMock()
        mock_point.payload = {
            "protocol_title": "Test Protocol",
            "filename": "test.pdf",
            "document_id": "test_doc_id",
        }
        mock_qdrant_client.scroll.return_value = ([mock_point], None)

        summary = await service.get_protocol_summary("test_collection")

        assert summary["collection_name"] == "test_collection"
        assert summary["status"] == "ready"
        assert summary["protocol_metadata"]["title"] == "Test Protocol"

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_get_protocol_summary_empty(self, mock_qdrant_client):
        """Test protocol summary retrieval with empty collection."""
        service = ICFGenerationService(mock_qdrant_client)

        # Mock empty scroll response
        mock_qdrant_client.scroll.return_value = ([], None)

        summary = await service.get_protocol_summary("empty_collection")

        assert summary["collection_name"] == "empty_collection"
        assert summary["status"] == "empty"
        assert "No protocol content found" in summary["message"]
