"""
Unit tests for Qdrant service operations.

This module tests all Qdrant operations including:
- Collection management
- Document storage and retrieval
- Metadata operations
- Vector search functionality
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from qdrant_client.models import PointStruct, ScoredPoint

from app.services.qdrant_service import (
    QdrantError,
    QdrantService,
)


class TestQdrantService:
    """Test cases for QdrantService class."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_init_service(self, mock_qdrant_client):
        """Test QdrantService initialization."""
        service = QdrantService(client=mock_qdrant_client)
        assert service.client == mock_qdrant_client

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_create_collection_success(self, mock_qdrant_client):
        """Test successful collection creation."""
        service = QdrantService(client=mock_qdrant_client)

        result = service.create_collection("test_collection")

        assert result is True
        mock_qdrant_client.create_collection.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_create_collection_error(self, mock_qdrant_client):
        """Test collection creation error handling."""
        mock_qdrant_client.create_collection.side_effect = Exception(
            "Connection failed"
        )
        service = QdrantService(client=mock_qdrant_client)

        with pytest.raises(QdrantError, match="Failed to create collection"):
            service.create_collection("test_collection")


class TestStoreProtocolWithMetadata:
    """Test cases for storing protocol with metadata."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_store_protocol_success(
        self, mock_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test successful protocol storage with metadata."""
        # Mock embeddings
        mock_embeddings = [[0.1] * 1536 for _ in sample_protocol_chunks]

        service = QdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_embeddings", return_value=mock_embeddings):
            result = service.store_protocol_with_metadata(
                collection_name="test-collection",
                chunks=sample_protocol_chunks,
                embeddings=mock_embeddings,
                protocol_metadata=sample_protocol_metadata,
            )

        assert result is True
        mock_qdrant_client.upsert.assert_called()

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_store_protocol_embedding_error(
        self, mock_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test protocol storage with invalid embeddings."""
        service = QdrantService(client=mock_qdrant_client)
        # Invalid embeddings - wrong dimensions
        invalid_embeddings = [[0.1] * 10 for _ in sample_protocol_chunks]  # Wrong size

        mock_qdrant_client.upsert.side_effect = Exception("Invalid vector dimension")

        with pytest.raises(QdrantError, match="Failed to store protocol"):
            service.store_protocol_with_metadata(
                collection_name="test-collection",
                chunks=sample_protocol_chunks,
                embeddings=invalid_embeddings,
                protocol_metadata=sample_protocol_metadata,
            )

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_store_protocol_qdrant_error(
        self, mock_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test protocol storage with Qdrant error."""
        mock_qdrant_client.upsert.side_effect = Exception("Qdrant connection failed")
        service = QdrantService(client=mock_qdrant_client)
        mock_embeddings = [[0.1] * 1536 for _ in sample_protocol_chunks]

        with pytest.raises(QdrantError, match="Failed to store protocol"):
            service.store_protocol_with_metadata(
                collection_name="test-collection",
                chunks=sample_protocol_chunks,
                embeddings=mock_embeddings,
                protocol_metadata=sample_protocol_metadata,
            )


class TestSearchProtocols:
    """Test cases for protocol search functionality."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_search_protocols_success(self, mock_qdrant_client):
        """Test successful protocol search."""
        # Mock search results with MagicMock to avoid validation issues
        mock_point = MagicMock()
        mock_point.score = 0.95
        mock_point.payload = {
            "study_acronym": "STUDY-001",
            "protocol_title": "Test Protocol",
        }
        mock_points = [mock_point]
        mock_qdrant_client.search.return_value = mock_points

        service = QdrantService(client=mock_qdrant_client)
        with patch.object(service, "get_embeddings", return_value=[[0.1] * 1536]):
            results = service.search_protocol_documents(
                protocol_collection_name="test-collection",
                query="clinical trial safety",
                limit=5,
            )

        assert len(results) == 1
        assert results[0]["study_acronym"] == "STUDY-001"
        assert results[0]["score"] == 0.95

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_search_protocols_no_results(self, mock_qdrant_client):
        """Test protocol search with no results."""
        mock_qdrant_client.search.return_value = []

        service = QdrantService(client=mock_qdrant_client)
        with patch.object(service, "get_embeddings", return_value=[[0.1] * 1536]):
            results = service.search_protocol_documents(
                protocol_collection_name="test-collection", query="nonexistent protocol"
            )

        assert results == []


class TestGetProtocolById:
    """Test cases for getting protocol by ID."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_id_success(
        self, mock_qdrant_client, sample_protocol_metadata
    ):
        """Test successful protocol retrieval by ID."""
        document_id = sample_protocol_metadata["document_id"]

        service = QdrantService(client=mock_qdrant_client)

        # Mock list_all_protocols to return our test protocol
        test_protocol = {
            "protocol_id": document_id,
            "study_acronym": sample_protocol_metadata["study_acronym"],
            **sample_protocol_metadata,
        }

        with patch.object(service, "list_all_protocols", return_value=[test_protocol]):
            result = service.get_protocol_by_id(document_id)

        assert result is not None
        assert result["study_acronym"] == sample_protocol_metadata["study_acronym"]

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_id_not_found(self, mock_qdrant_client):
        """Test protocol retrieval with non-existent ID."""
        mock_qdrant_client.scroll.return_value = ([], None)

        service = QdrantService(client=mock_qdrant_client)
        result = service.get_protocol_by_id("nonexistent-id")

        assert result is None


class TestListAllProtocols:
    """Test cases for listing all protocols."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_success(
        self, mock_qdrant_client, multiple_protocols_metadata
    ):
        """Test successful listing of all protocols."""
        # Mock get_collections to return protocol collections
        mock_collection_info = MagicMock()
        mock_collection_info.name = "TEST-12345678"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection_info]
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock scroll results for the collection
        mock_points = [MagicMock(payload=multiple_protocols_metadata[0])]
        mock_qdrant_client.scroll.return_value = (mock_points, None)

        # Mock get_collection for point count
        mock_collection_detail = MagicMock()
        mock_collection_detail.points_count = 5
        mock_qdrant_client.get_collection.return_value = mock_collection_detail

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        assert len(results) == 1
        assert "study_acronym" in results[0]
        assert results[0]["chunk_count"] == 5

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_empty(self, mock_qdrant_client):
        """Test listing protocols with no protocol collections."""
        # Mock empty collections
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_qdrant_client.get_collections.return_value = mock_collections

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        assert results == []

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_protocols_with_status_filter(
        self, mock_qdrant_client, multiple_protocols_metadata
    ):
        """Test listing protocols with status filter."""
        # Set one protocol to 'completed' status
        completed_metadata = multiple_protocols_metadata[0].copy()
        completed_metadata["status"] = "completed"

        # Mock collections
        mock_collection_info = MagicMock()
        mock_collection_info.name = "TEST-12345678"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection_info]
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock scroll returning the completed protocol
        mock_points = [MagicMock(payload=completed_metadata)]
        mock_qdrant_client.scroll.return_value = (mock_points, None)

        # Mock collection detail
        mock_collection_detail = MagicMock()
        mock_collection_detail.points_count = 1
        mock_qdrant_client.get_collection.return_value = mock_collection_detail

        service = QdrantService(client=mock_qdrant_client)
        protocols = service.list_all_protocols()
        results = [p for p in protocols if p.get("status") == "completed"]

        assert len(results) == 1
        assert results[0]["status"] == "completed"

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_protocols_sorted_by_date(self, mock_qdrant_client):
        """Test that protocols are sorted by upload_date with newest first."""
        # Create protocols with different upload dates
        protocols_data = [
            {
                "protocol_id": "proto_1",
                "study_acronym": "OLD",
                "protocol_title": "Old Protocol",
                "upload_date": "2024-01-01T10:00:00",
                "status": "active",
            },
            {
                "protocol_id": "proto_2",
                "study_acronym": "NEW",
                "protocol_title": "New Protocol",
                "upload_date": "2024-12-01T10:00:00",
                "status": "active",
            },
            {
                "protocol_id": "proto_3",
                "study_acronym": "MIDDLE",
                "protocol_title": "Middle Protocol",
                "upload_date": "2024-06-15T10:00:00",
                "status": "active",
            },
        ]

        # Mock collections with multiple protocol collections
        mock_collections = MagicMock()
        mock_collections.collections = []
        for i, data in enumerate(protocols_data):
            mock_collection = MagicMock()
            mock_collection.name = f"{data['study_acronym']}-1234567{i}"
            mock_collections.collections.append(mock_collection)
        
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock scroll results for each collection
        def mock_scroll_side_effect(collection_name, **kwargs):
            for i, data in enumerate(protocols_data):
                if f"{data['study_acronym']}-1234567{i}" == collection_name:
                    return ([MagicMock(payload=data)], None)
            return ([], None)

        mock_qdrant_client.scroll.side_effect = mock_scroll_side_effect

        # Mock get_collection for point counts
        mock_collection_detail = MagicMock()
        mock_collection_detail.points_count = 10
        mock_qdrant_client.get_collection.return_value = mock_collection_detail

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        # Verify sorting - newest first
        assert len(results) == 3
        assert results[0]["study_acronym"] == "NEW"  # Dec 2024
        assert results[1]["study_acronym"] == "MIDDLE"  # June 2024
        assert results[2]["study_acronym"] == "OLD"  # Jan 2024


class TestIntegrationScenarios:
    """Integration test scenarios for Qdrant service."""

    @pytest.mark.integration
    @pytest.mark.qdrant
    def test_full_protocol_lifecycle_qdrant(
        self, memory_qdrant_client, sample_protocol_chunks, sample_protocol_metadata
    ):
        """Test complete protocol lifecycle with new QdrantService."""
        service = QdrantService(client=memory_qdrant_client)

        # Create protocol collection
        collection_name = service.create_protocol_collection(
            study_acronym="TEST", protocol_title="Test Protocol"
        )

        # Store protocol with metadata
        mock_embeddings = [[0.1] * 1536 for _ in sample_protocol_chunks]
        with patch.object(
            service,
            "get_embeddings",
            return_value=mock_embeddings,
        ):
            success = service.store_protocol_with_metadata(
                collection_name=collection_name,
                chunks=sample_protocol_chunks,
                embeddings=mock_embeddings,
                protocol_metadata=sample_protocol_metadata,
            )

        assert success is True

        # Retrieve by collection name
        retrieved = service.get_protocol_by_collection(collection_name)
        assert retrieved is not None
        assert retrieved["study_acronym"] == sample_protocol_metadata["study_acronym"]

        # List all protocols (should find our new collection)
        all_protocols = service.list_all_protocols()
        assert len(all_protocols) >= 1

        # Search within the protocol collection
        with patch.object(service, "get_embeddings", return_value=[[0.1] * 1536]):
            search_results = service.search_protocol_documents(
                protocol_collection_name=collection_name, query="clinical trial"
            )
            assert len(search_results) >= 1
