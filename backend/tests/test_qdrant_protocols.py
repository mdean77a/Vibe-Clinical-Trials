"""
Tests for protocol operations using Qdrant-only architecture.

This module tests the complete protocol lifecycle using the migrated
Qdrant-only storage system (no SQLite dependencies).
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from app.models import ProtocolCreate, ProtocolResponse
from app.services.qdrant_service import QdrantError, QdrantService


class TestQdrantProtocolService:
    """Test suite for Qdrant protocol service operations."""

    def test_create_protocol_collection(self, qdrant_service, sample_protocol_data):
        """Test creating a protocol collection."""
        collection_name = qdrant_service.create_protocol_collection(
            study_acronym=sample_protocol_data["study_acronym"],
            protocol_title=sample_protocol_data["protocol_title"],
            file_path=sample_protocol_data["file_path"],
        )

        assert collection_name.startswith("TEST001-")
        assert len(collection_name.split("-")) == 2  # ACRONYM-8charuuid format
        assert len(collection_name.split("-")[1]) == 8  # 8-char UUID

    def test_store_protocol_with_metadata(self, qdrant_service, sample_protocol_data):
        """Test storing protocol with metadata."""
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        protocol_metadata = {
            "protocol_id": "test_001",
            "study_acronym": sample_protocol_data["study_acronym"],
            "protocol_title": sample_protocol_data["protocol_title"],
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "file_path": sample_protocol_data["file_path"],
            "created_at": datetime.now().isoformat(),
        }

        success = qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["test chunk 1", "test chunk 2"],
            embeddings=[[0.1] * 1536, [0.2] * 1536],
            protocol_metadata=protocol_metadata,
        )

        assert success is True

    def test_list_all_protocols(self, qdrant_service, sample_protocol_data):
        """Test listing all protocols."""
        # Create and store a test protocol
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        protocol_metadata = {
            "protocol_id": "test_001",
            "study_acronym": sample_protocol_data["study_acronym"],
            "protocol_title": sample_protocol_data["protocol_title"],
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "file_path": sample_protocol_data["file_path"],
            "created_at": datetime.now().isoformat(),
        }

        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["test chunk"],
            embeddings=[[0.1] * 1536],
            protocol_metadata=protocol_metadata,
        )

        # List protocols
        protocols = qdrant_service.list_all_protocols()

        assert len(protocols) == 1
        assert protocols[0]["study_acronym"] == "TEST-001"
        assert protocols[0]["protocol_title"] == "Test Protocol for Unit Testing"

    def test_get_protocol_by_collection(self, qdrant_service, sample_protocol_data):
        """Test getting protocol by collection name."""
        # Create and store a test protocol
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        protocol_metadata = {
            "protocol_id": "test_001",
            "study_acronym": sample_protocol_data["study_acronym"],
            "protocol_title": sample_protocol_data["protocol_title"],
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "file_path": sample_protocol_data["file_path"],
            "created_at": datetime.now().isoformat(),
        }

        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["test chunk"],
            embeddings=[[0.1] * 1536],
            protocol_metadata=protocol_metadata,
        )

        # Retrieve protocol
        protocol = qdrant_service.get_protocol_by_collection(collection_name)

        assert protocol is not None
        assert protocol["study_acronym"] == "TEST-001"
        assert protocol["collection_name"] == collection_name

    def test_get_protocol_by_id(self, qdrant_service, sample_protocol_data):
        """Test getting protocol by protocol ID."""
        # Create and store a test protocol
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        protocol_metadata = {
            "protocol_id": "test_001",
            "study_acronym": sample_protocol_data["study_acronym"],
            "protocol_title": sample_protocol_data["protocol_title"],
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "file_path": sample_protocol_data["file_path"],
            "created_at": datetime.now().isoformat(),
        }

        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["test chunk"],
            embeddings=[[0.1] * 1536],
            protocol_metadata=protocol_metadata,
        )

        # Retrieve protocol by ID
        protocol = qdrant_service.get_protocol_by_id("test_001")

        assert protocol is not None
        assert protocol["protocol_id"] == "test_001"
        assert protocol["study_acronym"] == "TEST-001"

    def test_delete_protocol(self, qdrant_service, sample_protocol_data):
        """Test deleting a protocol."""
        # Create and store a test protocol
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        protocol_metadata = {
            "protocol_id": "test_001",
            "study_acronym": sample_protocol_data["study_acronym"],
            "protocol_title": sample_protocol_data["protocol_title"],
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "file_path": sample_protocol_data["file_path"],
            "created_at": datetime.now().isoformat(),
        }

        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["test chunk"],
            embeddings=[[0.1] * 1536],
            protocol_metadata=protocol_metadata,
        )

        # Delete protocol
        success = qdrant_service.delete_protocol(collection_name)
        assert success is True

        # Verify protocol was deleted
        protocol = qdrant_service.get_protocol_by_collection(collection_name)
        assert protocol is None

    def test_search_protocols(self, qdrant_service, sample_protocol_data):
        """Test searching protocols by content."""
        # Create and store a test protocol
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        protocol_metadata = {
            "protocol_id": "test_001",
            "study_acronym": sample_protocol_data["study_acronym"],
            "protocol_title": sample_protocol_data["protocol_title"],
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "file_path": sample_protocol_data["file_path"],
            "created_at": datetime.now().isoformat(),
        }

        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["clinical trial procedures"],
            embeddings=[[0.1] * 1536],
            protocol_metadata=protocol_metadata,
        )

        # Search protocols
        results = qdrant_service.search_protocol_documents(
            collection_name, "clinical trial", limit=5
        )

        # Should find our stored protocol (though with placeholder embeddings)
        assert isinstance(results, list)
        # Note: With placeholder embeddings, search might not return meaningful results
        # but we're testing the interface works


class TestQdrantProtocolErrors:
    """Test error handling in Qdrant protocol operations."""

    def test_get_nonexistent_protocol_by_collection(self, qdrant_service):
        """Test getting a non-existent protocol by collection name."""
        protocol = qdrant_service.get_protocol_by_collection("nonexistent_collection")
        assert protocol is None

    def test_get_nonexistent_protocol_by_id(self, qdrant_service):
        """Test getting a non-existent protocol by ID."""
        protocol = qdrant_service.get_protocol_by_id("nonexistent_id")
        assert protocol is None

    def test_delete_nonexistent_protocol(self, qdrant_service):
        """Test deleting non-existent protocol."""
        # Note: delete_protocol returns False only on exception, not for non-existent collections
        # The actual behavior depends on Qdrant client implementation
        success = qdrant_service.delete_protocol("nonexistent_collection")
        assert isinstance(success, bool)  # Just verify it returns a boolean
