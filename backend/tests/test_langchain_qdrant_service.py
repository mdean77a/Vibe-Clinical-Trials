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
        mock_qdrant_client.delete_collection.assert_called_once_with(
            collection_name="test_collection"
        )

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


class TestStoreDocuments:
    """Test store_documents method."""

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    @patch("app.services.langchain_qdrant_service.get_qdrant_service")
    @patch("app.services.langchain_qdrant_service.QdrantVectorStore")
    def test_store_documents_success(
        self,
        mock_vector_store,
        mock_get_qdrant,
        mock_embeddings_class,
        mock_qdrant_client,
    ):
        """Test successful document storage."""
        # Setup mocks
        mock_qdrant_service = MagicMock()
        mock_qdrant_service.generate_collection_name.return_value = (
            "test-collection-123"
        )
        mock_get_qdrant.return_value = mock_qdrant_service

        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        # Create service and documents
        service = LangChainQdrantService(client=mock_qdrant_client)

        mock_doc1 = MagicMock()
        mock_doc1.page_content = "Test content 1"
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "Test content 2"
        documents = [mock_doc1, mock_doc2]

        # Call method
        doc_ids, collection_name = service.store_documents(
            documents=documents, study_acronym="TEST001"
        )

        # Verify results
        assert collection_name == "test-collection-123"
        assert len(doc_ids) == 2
        mock_vector_store.from_documents.assert_called_once()

    @pytest.mark.unit
    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
            "QDRANT_URL": "http://localhost:6333",
            "QDRANT_API_KEY": "test-api-key",
        },
    )
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    @patch("app.services.langchain_qdrant_service.get_qdrant_service")
    @patch("app.services.langchain_qdrant_service.QdrantVectorStore")
    def test_store_documents_with_url_and_api_key(
        self,
        mock_vector_store,
        mock_get_qdrant,
        mock_embeddings_class,
        mock_qdrant_client,
    ):
        """Test document storage with URL and API key."""
        mock_qdrant_service = MagicMock()
        mock_qdrant_service.generate_collection_name.return_value = "test-collection"
        mock_get_qdrant.return_value = mock_qdrant_service

        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)
        documents = [MagicMock()]

        doc_ids, collection_name = service.store_documents(documents, "TEST001")

        # Verify from_documents was called with url and api_key
        call_kwargs = mock_vector_store.from_documents.call_args[1]
        assert "url" in call_kwargs
        assert "api_key" in call_kwargs

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    @patch("app.services.langchain_qdrant_service.get_qdrant_service")
    @patch("app.services.langchain_qdrant_service.QdrantVectorStore")
    def test_store_documents_error(
        self,
        mock_vector_store,
        mock_get_qdrant,
        mock_embeddings_class,
        mock_qdrant_client,
    ):
        """Test document storage with error."""
        mock_qdrant_service = MagicMock()
        mock_qdrant_service.generate_collection_name.return_value = "test-collection"
        mock_get_qdrant.return_value = mock_qdrant_service

        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        # Make from_documents raise an error
        mock_vector_store.from_documents.side_effect = Exception("Storage failed")

        service = LangChainQdrantService(client=mock_qdrant_client)
        documents = [MagicMock()]

        with pytest.raises(LangChainQdrantError, match="Failed to store documents"):
            service.store_documents(documents, "TEST001")


class TestGetRetriever:
    """Test get_retriever method."""

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_get_retriever_success(self, mock_embeddings_class, mock_qdrant_client):
        """Test successful retriever creation."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        # Mock the vector store
        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_vector_store = MagicMock()
            mock_retriever = MagicMock()
            mock_vector_store.as_retriever.return_value = mock_retriever
            mock_get_vs.return_value = mock_vector_store

            retriever = service.get_retriever("test-collection")

            assert retriever == mock_retriever
            mock_vector_store.as_retriever.assert_called_once()

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_get_retriever_with_custom_kwargs(
        self, mock_embeddings_class, mock_qdrant_client
    ):
        """Test retriever creation with custom search kwargs."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_vector_store = MagicMock()
            mock_get_vs.return_value = mock_vector_store

            service.get_retriever(
                "test-collection",
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 20},
            )

            call_kwargs = mock_vector_store.as_retriever.call_args[1]
            assert call_kwargs["search_type"] == "mmr"
            assert call_kwargs["search_kwargs"]["k"] == 5

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_get_retriever_error(self, mock_embeddings_class, mock_qdrant_client):
        """Test retriever creation with error."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_get_vs.side_effect = Exception("Vector store error")

            with pytest.raises(
                LangChainQdrantError, match="Failed to create retriever"
            ):
                service.get_retriever("test-collection")


class TestSimilaritySearch:
    """Test similarity search methods."""

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_similarity_search_success(self, mock_embeddings_class, mock_qdrant_client):
        """Test successful similarity search."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_vector_store = MagicMock()
            mock_doc = MagicMock()
            mock_vector_store.similarity_search.return_value = [mock_doc]
            mock_get_vs.return_value = mock_vector_store

            results = service.similarity_search("test-collection", "test query", k=3)

            assert len(results) == 1
            mock_vector_store.similarity_search.assert_called_once_with(
                "test query", k=3
            )

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_similarity_search_with_score_threshold(
        self, mock_embeddings_class, mock_qdrant_client
    ):
        """Test similarity search with score threshold."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_vector_store = MagicMock()
            mock_doc1 = MagicMock()
            mock_doc2 = MagicMock()
            # Return docs with scores
            mock_vector_store.similarity_search_with_score.return_value = [
                (mock_doc1, 0.9),
                (mock_doc2, 0.6),
            ]
            mock_get_vs.return_value = mock_vector_store

            results = service.similarity_search(
                "test-collection", "test query", k=5, score_threshold=0.7
            )

            # Only doc1 should be returned (score 0.9 >= 0.7)
            assert len(results) == 1
            assert results[0] == mock_doc1

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_similarity_search_error(self, mock_embeddings_class, mock_qdrant_client):
        """Test similarity search with error."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_get_vs.side_effect = Exception("Search error")

            with pytest.raises(
                LangChainQdrantError, match="Failed to perform similarity search"
            ):
                service.similarity_search("test-collection", "query")

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_similarity_search_with_score_success(
        self, mock_embeddings_class, mock_qdrant_client
    ):
        """Test similarity search with scores."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_vector_store = MagicMock()
            mock_doc = MagicMock()
            mock_vector_store.similarity_search_with_score.return_value = [
                (mock_doc, 0.95)
            ]
            mock_get_vs.return_value = mock_vector_store

            results = service.similarity_search_with_score(
                "test-collection", "query", k=3
            )

            assert len(results) == 1
            assert results[0][0] == mock_doc
            assert results[0][1] == 0.95

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    def test_similarity_search_with_score_error(
        self, mock_embeddings_class, mock_qdrant_client
    ):
        """Test similarity search with score error handling."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        service = LangChainQdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_vector_store") as mock_get_vs:
            mock_get_vs.side_effect = Exception("Search failed")

            with pytest.raises(
                LangChainQdrantError,
                match="Failed to perform similarity search with score",
            ):
                service.similarity_search_with_score("test-collection", "query")


class TestGetVectorStore:
    """Test get_vector_store method."""

    @pytest.mark.unit
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("app.services.langchain_qdrant_service.OpenAIEmbeddings")
    @patch("app.services.langchain_qdrant_service.QdrantVectorStore")
    def test_get_vector_store_success(
        self, mock_vector_store_class, mock_embeddings_class, mock_qdrant_client
    ):
        """Test successful vector store creation."""
        mock_embeddings = MagicMock()
        mock_embeddings_class.return_value = mock_embeddings

        mock_vector_store = MagicMock()
        mock_vector_store_class.return_value = mock_vector_store

        service = LangChainQdrantService(client=mock_qdrant_client)
        vector_store = service.get_vector_store("test-collection")

        assert vector_store == mock_vector_store
        mock_vector_store_class.assert_called_once()

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)  # Clear all env vars
    def test_get_vector_store_no_embeddings(self, mock_qdrant_client):
        """Test vector store creation without embeddings."""
        # Ensure OPENAI_API_KEY is not set
        os.environ.pop("OPENAI_API_KEY", None)

        service = LangChainQdrantService(client=mock_qdrant_client)
        # service.embeddings should be None

        with pytest.raises(LangChainQdrantError, match="Embeddings not initialized"):
            service.get_vector_store("test-collection")


class TestGetCollectionInfo:
    """Test get_collection_info method."""

    @pytest.mark.unit
    def test_get_collection_info_success(self, mock_qdrant_client):
        """Test successful collection info retrieval."""
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 100
        mock_collection_info.vectors_count = 100
        mock_collection_info.status = "green"
        mock_qdrant_client.get_collection.return_value = mock_collection_info

        service = LangChainQdrantService(client=mock_qdrant_client)
        info = service.get_collection_info("test-collection")

        assert info is not None
        assert info["name"] == "test-collection"
        assert info["points_count"] == 100
        assert info["vectors_count"] == 100
        assert info["status"] == "green"

    @pytest.mark.unit
    def test_get_collection_info_error(self, mock_qdrant_client):
        """Test collection info retrieval with error."""
        mock_qdrant_client.get_collection.side_effect = Exception(
            "Collection not found"
        )

        service = LangChainQdrantService(client=mock_qdrant_client)
        info = service.get_collection_info("nonexistent-collection")

        assert info is None
