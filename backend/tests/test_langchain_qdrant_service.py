"""
Tests for LangChain Qdrant service.

Covers initialization, collection management, and basic operations.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from qdrant_client import QdrantClient

from app.services.langchain_qdrant_service import (
    LangChainQdrantError,
    LangChainQdrantService,
    get_langchain_qdrant_service,
)


class TestLangChainQdrantServiceInit:
    """Test LangChainQdrantService initialization."""

    @pytest.mark.unit
    def test_init_with_provided_client(self, mock_qdrant_client):
        """Test initialization with provided Qdrant client."""
        service = LangChainQdrantService(client=mock_qdrant_client)
        assert service.client == mock_qdrant_client

    @pytest.mark.unit
    @patch("app.services.langchain_qdrant_service.get_qdrant_service")
    def test_init_without_client_reuses_qdrant_service(
        self, mock_get_qdrant_service, mock_qdrant_client
    ):
        """Test that initialization without client reuses qdrant_service client."""
        mock_qdrant_service = MagicMock()
        mock_qdrant_service.client = mock_qdrant_client
        mock_get_qdrant_service.return_value = mock_qdrant_service

        service = LangChainQdrantService()

        assert service.client == mock_qdrant_client
        mock_get_qdrant_service.assert_called_once()

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_init_with_openai_api_key(self, mock_embeddings_class, mock_qdrant_client):
        """Test initialization with OPENAI_API_KEY set."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        assert service.embeddings == mock_embeddings
        mock_embeddings_class.assert_called_once()

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)  # Clear OPENAI_API_KEY
    def test_init_without_openai_api_key(self, mock_qdrant_client):
        """Test initialization without OPENAI_API_KEY warns appropriately."""
        # Remove OPENAI_API_KEY if it exists
        os.environ.pop("OPENAI_API_KEY", None)

        service = LangChainQdrantService(client=mock_qdrant_client)

        assert service.embeddings is None

    @pytest.mark.unit
    def test_init_with_provided_embeddings(self, mock_qdrant_client):
        """Test initialization with provided embeddings."""
        mock_embeddings = MagicMock()
        service = LangChainQdrantService(
            client=mock_qdrant_client, embeddings=mock_embeddings
        )

        assert service.embeddings == mock_embeddings


class TestLangChainQdrantServiceMethods:
    """Test LangChainQdrantService methods."""

    @pytest.mark.unit
    @patch("app.services.langchain_qdrant_service.get_qdrant_service")
    def test_test_connection_success(self, mock_get_qdrant_service, mock_qdrant_client):
        """Test connection test with successful connection."""
        mock_qdrant_service = MagicMock()
        mock_qdrant_service.test_connection.return_value = True
        mock_get_qdrant_service.return_value = mock_qdrant_service

        service = LangChainQdrantService(client=mock_qdrant_client)
        result = service.test_connection()

        assert result is True
        mock_qdrant_service.test_connection.assert_called_once()

    @pytest.mark.unit
    @patch("app.services.langchain_qdrant_service.get_qdrant_service")
    def test_test_connection_failure(self, mock_get_qdrant_service, mock_qdrant_client):
        """Test connection test with failed connection."""
        mock_qdrant_service = MagicMock()
        mock_qdrant_service.test_connection.return_value = False
        mock_get_qdrant_service.return_value = mock_qdrant_service

        service = LangChainQdrantService(client=mock_qdrant_client)
        result = service.test_connection()

        assert result is False

    @pytest.mark.unit
    def test_list_collections(self, mock_qdrant_client):
        """Test listing collections."""
        mock_collection1 = MagicMock()
        mock_collection1.name = "collection1"
        mock_collection2 = MagicMock()
        mock_collection2.name = "collection2"

        mock_response = MagicMock()
        mock_response.collections = [mock_collection1, mock_collection2]
        mock_qdrant_client.get_collections.return_value = mock_response

        service = LangChainQdrantService(client=mock_qdrant_client)
        collections = service.list_collections()

        assert collections == ["collection1", "collection2"]
        mock_qdrant_client.get_collections.assert_called_once()

    @pytest.mark.unit
    def test_delete_collection_success(self, mock_qdrant_client):
        """Test successful collection deletion."""
        mock_qdrant_client.delete_collection.return_value = True
        service = LangChainQdrantService(client=mock_qdrant_client)

        result = service.delete_collection("test_collection")

        assert result is True
        mock_qdrant_client.delete_collection.assert_called_once_with(collection_name="test_collection")

    @pytest.mark.unit
    def test_delete_collection_failure(self, mock_qdrant_client):
        """Test collection deletion failure."""
        mock_qdrant_client.delete_collection.side_effect = Exception("Delete failed")
        service = LangChainQdrantService(client=mock_qdrant_client)

        result = service.delete_collection("test_collection")

        assert result is False


class TestGetLangChainQdrantService:
    """Test module-level get_langchain_qdrant_service function."""

    @pytest.mark.unit
    def test_get_langchain_qdrant_service_returns_instance(self):
        """Test that get_langchain_qdrant_service returns a service instance."""
        service = get_langchain_qdrant_service()

        assert isinstance(service, LangChainQdrantService)
        assert service.client is not None

    @pytest.mark.unit
    def test_get_langchain_qdrant_service_caches_instance(self):
        """Test that get_langchain_qdrant_service returns cached instance."""
        service1 = get_langchain_qdrant_service()
        service2 = get_langchain_qdrant_service()

        # Should return the same instance (cached)
        assert service1 is service2


class TestLangChainQdrantError:
    """Test LangChainQdrantError exception."""

    @pytest.mark.unit
    def test_langchain_qdrant_error_can_be_raised(self):
        """Test that LangChainQdrantError can be raised."""
        with pytest.raises(LangChainQdrantError) as exc_info:
            raise LangChainQdrantError("Test error message")

        assert "Test error message" in str(exc_info.value)

    @pytest.mark.unit
    def test_langchain_qdrant_error_is_exception(self):
        """Test that LangChainQdrantError inherits from Exception."""
        assert issubclass(LangChainQdrantError, Exception)
