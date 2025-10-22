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
    def test_create_protocol_collection_success(self, mock_qdrant_client):
        """Test successful protocol collection creation."""
        service = QdrantService(client=mock_qdrant_client)

        result = service.create_protocol_collection("TEST123", "Test Protocol")

        assert result  # Returns collection name
        assert result.startswith("TEST123-")
        mock_qdrant_client.create_collection.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_create_protocol_collection_error(self, mock_qdrant_client):
        """Test protocol collection creation error handling."""
        mock_qdrant_client.create_collection.side_effect = Exception(
            "Connection failed"
        )
        service = QdrantService(client=mock_qdrant_client)

        with pytest.raises(QdrantError, match="Failed to create protocol collection"):
            service.create_protocol_collection("TEST123", "Test Protocol")


class TestSearchProtocols:
    """Test cases for protocol search functionality."""

    # Note: search_protocol_documents method has been removed from QdrantService
    # as part of the embedding consolidation. Search functionality is now
    # handled through LangChain's vector store search capabilities.


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

    # Status filter test removed - protocols in Qdrant are always active

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
            },
            {
                "protocol_id": "proto_2",
                "study_acronym": "NEW",
                "protocol_title": "New Protocol",
                "upload_date": "2024-12-01T10:00:00",
            },
            {
                "protocol_id": "proto_3",
                "study_acronym": "MIDDLE",
                "protocol_title": "Middle Protocol",
                "upload_date": "2024-06-15T10:00:00",
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


class TestGetProtocolByCollection:
    """Test cases for getting protocol by collection name."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_collection_success(self, mock_qdrant_client):
        """Test successful protocol retrieval by collection name."""
        # Mock scroll response with payload
        mock_payload = {
            "protocol_id": "test-proto-123",
            "study_acronym": "TEST",
            "protocol_title": "Test Protocol",
            "upload_date": "2024-01-01T10:00:00",
            "file_path": "/path/to/test.pdf",
        }
        mock_point = MagicMock(payload=mock_payload)
        mock_qdrant_client.scroll.return_value = ([mock_point], None)

        # Mock collection info
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 42
        mock_qdrant_client.get_collection.return_value = mock_collection_info

        service = QdrantService(client=mock_qdrant_client)
        result = service.get_protocol_by_collection("TEST-12345678")

        assert result is not None
        assert result["protocol_id"] == "test-proto-123"
        assert result["study_acronym"] == "TEST"
        assert result["chunk_count"] == 42
        assert result["collection_name"] == "TEST-12345678"

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_collection_langchain_structure(self, mock_qdrant_client):
        """Test protocol retrieval with LangChain nested metadata structure."""
        # Mock scroll response with LangChain nested metadata
        mock_payload = {
            "metadata": {
                "protocol_id": "langchain-proto-456",
                "study_acronym": "LANG",
                "protocol_title": "LangChain Protocol",
                "upload_date": "2024-02-01T10:00:00",
            }
        }
        mock_point = MagicMock(payload=mock_payload)
        mock_qdrant_client.scroll.return_value = ([mock_point], None)

        # Mock collection info
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 15
        mock_qdrant_client.get_collection.return_value = mock_collection_info

        service = QdrantService(client=mock_qdrant_client)
        result = service.get_protocol_by_collection("LANG-abcdef12")

        assert result is not None
        assert result["protocol_id"] == "langchain-proto-456"
        assert result["study_acronym"] == "LANG"

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_collection_not_found(self, mock_qdrant_client):
        """Test protocol retrieval when collection is empty."""
        mock_qdrant_client.scroll.return_value = ([], None)

        service = QdrantService(client=mock_qdrant_client)
        result = service.get_protocol_by_collection("EMPTY-12345678")

        assert result is None

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_collection_error(self, mock_qdrant_client):
        """Test protocol retrieval error handling."""
        mock_qdrant_client.scroll.side_effect = Exception("Database error")

        service = QdrantService(client=mock_qdrant_client)
        result = service.get_protocol_by_collection("ERROR-12345678")

        assert result is None


class TestGetCollectionNameForProtocol:
    """Test cases for getting collection name by protocol ID."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_collection_name_success(self, mock_qdrant_client):
        """Test successful collection name retrieval."""
        service = QdrantService(client=mock_qdrant_client)

        # Mock get_protocol_by_id to return protocol with collection name
        test_protocol = {
            "protocol_id": "proto-123",
            "collection_name": "TEST-12345678",
        }

        with patch.object(service, "get_protocol_by_id", return_value=test_protocol):
            result = service.get_collection_name_for_protocol("proto-123")

        assert result == "TEST-12345678"

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_collection_name_not_found(self, mock_qdrant_client):
        """Test collection name retrieval when protocol not found."""
        service = QdrantService(client=mock_qdrant_client)

        with patch.object(service, "get_protocol_by_id", return_value=None):
            result = service.get_collection_name_for_protocol("nonexistent-id")

        assert result is None

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_collection_name_error(self, mock_qdrant_client):
        """Test collection name retrieval error handling."""
        service = QdrantService(client=mock_qdrant_client)

        with patch.object(
            service, "get_protocol_by_id", side_effect=Exception("Database error")
        ):
            result = service.get_collection_name_for_protocol("error-id")

        assert result is None


class TestDeleteCollection:
    """Test cases for collection deletion."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_delete_collection_success(self, mock_qdrant_client):
        """Test successful collection deletion."""
        service = QdrantService(client=mock_qdrant_client)
        result = service.delete_collection("TEST-12345678")

        assert result is True
        mock_qdrant_client.delete_collection.assert_called_once_with(
            collection_name="TEST-12345678"
        )

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_delete_collection_error(self, mock_qdrant_client):
        """Test collection deletion error handling."""
        mock_qdrant_client.delete_collection.side_effect = Exception("Deletion failed")

        service = QdrantService(client=mock_qdrant_client)
        result = service.delete_collection("ERROR-12345678")

        assert result is False


class TestIsProtocolCollection:
    """Test cases for protocol collection name validation."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_is_protocol_collection_valid(self, mock_qdrant_client):
        """Test valid protocol collection names."""
        service = QdrantService(client=mock_qdrant_client)

        valid_names = [
            "TEST-12345678",
            "STUDY-abcdef12",
            "A-1234567a",
            "ABC123-9876fedc",
        ]

        for name in valid_names:
            assert service._is_protocol_collection(name) is True

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_is_protocol_collection_invalid(self, mock_qdrant_client):
        """Test invalid protocol collection names."""
        service = QdrantService(client=mock_qdrant_client)

        invalid_names = [
            "test-12345678",  # lowercase acronym
            "TEST-1234567",  # only 7 chars
            "TEST-123456789",  # 9 chars
            "TEST",  # no UUID
            "metadata_collection",  # underscore format
            "TEST-ABCDEF12",  # uppercase UUID
        ]

        for name in invalid_names:
            assert service._is_protocol_collection(name) is False


class TestListAllProtocolsEdgeCases:
    """Test edge cases for list_all_protocols method."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_connection_failure(self, mock_qdrant_client):
        """Test list protocols when connection test fails."""
        mock_qdrant_client.get_collections.side_effect = Exception("Connection failed")

        service = QdrantService(client=mock_qdrant_client)

        with pytest.raises(QdrantError, match="Failed to list protocols"):
            service.list_all_protocols()

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_skips_non_protocol_collections(
        self, mock_qdrant_client
    ):
        """Test that non-protocol collections are skipped."""
        # Mock collections with both protocol and non-protocol collections
        mock_collection_1 = MagicMock()
        mock_collection_1.name = "TEST-12345678"  # Valid protocol
        mock_collection_2 = MagicMock()
        mock_collection_2.name = "metadata_store"  # Invalid - should skip
        mock_collection_3 = MagicMock()
        mock_collection_3.name = "system-cache"  # Invalid - should skip

        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection_1, mock_collection_2, mock_collection_3]
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock scroll for valid collection
        mock_payload = {
            "protocol_id": "test-123",
            "study_acronym": "TEST",
            "protocol_title": "Test Protocol",
        }
        mock_point = MagicMock(payload=mock_payload)
        mock_qdrant_client.scroll.return_value = ([mock_point], None)

        # Mock collection info
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 5
        mock_qdrant_client.get_collection.return_value = mock_collection_info

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        # Only the valid protocol collection should be included
        assert len(results) == 1
        assert results[0]["study_acronym"] == "TEST"

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_empty_collection(self, mock_qdrant_client):
        """Test handling of protocol collection with no points."""
        mock_collection = MagicMock()
        mock_collection.name = "EMPTY-12345678"

        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock empty scroll response
        mock_qdrant_client.scroll.return_value = ([], None)

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        # Empty collection should not be included in results
        assert len(results) == 0

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_collection_read_error(self, mock_qdrant_client):
        """Test handling of error when reading collection metadata."""
        mock_collection = MagicMock()
        mock_collection.name = "ERROR-12345678"

        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock scroll to raise exception
        mock_qdrant_client.scroll.side_effect = Exception("Read error")

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        # Collection with read error should be skipped
        assert len(results) == 0

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_list_all_protocols_langchain_metadata_structure(self, mock_qdrant_client):
        """Test list protocols with LangChain nested metadata structure."""
        mock_collection = MagicMock()
        mock_collection.name = "LANG-12345678"

        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_qdrant_client.get_collections.return_value = mock_collections

        # Mock scroll with LangChain nested metadata
        mock_payload = {
            "metadata": {
                "protocol_id": "lang-123",
                "study_acronym": "LANG",
                "protocol_title": "LangChain Test",
                "upload_date": "2024-01-15T10:00:00",
            }
        }
        mock_point = MagicMock(payload=mock_payload)
        mock_qdrant_client.scroll.return_value = ([mock_point], None)

        # Mock collection info
        mock_collection_info = MagicMock()
        mock_collection_info.points_count = 20
        mock_qdrant_client.get_collection.return_value = mock_collection_info

        service = QdrantService(client=mock_qdrant_client)
        results = service.list_all_protocols()

        assert len(results) == 1
        assert results[0]["study_acronym"] == "LANG"
        assert results[0]["protocol_id"] == "lang-123"


class TestGetProtocolByIdEdgeCases:
    """Test edge cases for get_protocol_by_id method."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_get_protocol_by_id_error(self, mock_qdrant_client):
        """Test error handling in get_protocol_by_id."""
        service = QdrantService(client=mock_qdrant_client)

        with patch.object(
            service, "list_all_protocols", side_effect=Exception("Database error")
        ):
            result = service.get_protocol_by_id("error-id")

        assert result is None


class TestQdrantServiceInitialization:
    """Test cases for QdrantService initialization variations."""

    @pytest.mark.unit
    @pytest.mark.qdrant
    def test_init_with_url_no_api_key(self):
        """Test initialization with URL but no API key (local Qdrant)."""
        with patch.dict("os.environ", {"QDRANT_URL": "http://localhost:6333"}):
            with patch("app.services.qdrant_service.QdrantClient") as mock_client_class:
                service = QdrantService()
                # Should call QdrantClient with URL only (no api_key)
                mock_client_class.assert_called_once_with(url="http://localhost:6333")


class TestIntegrationScenarios:
    """Integration test scenarios for Qdrant service."""

    @pytest.mark.integration
    @pytest.mark.qdrant
    def test_protocol_collection_lifecycle(self, memory_qdrant_client):
        """Test protocol collection creation and management."""
        service = QdrantService(client=memory_qdrant_client)

        # Create protocol collection
        collection_name = service.create_protocol_collection(
            study_acronym="TEST", protocol_title="Test Protocol"
        )

        # Verify collection was created with proper format
        assert collection_name.startswith("TEST-")
        assert len(collection_name.split("-")[1]) == 8  # 8-char UUID

        # Test connection
        assert service.test_connection() is True
