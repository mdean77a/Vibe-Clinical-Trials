"""
Tests for protocol collection management using Qdrant.

This module tests collection creation and management functionality
in the qdrant_service. Document storage tests are in test_langchain_qdrant.py.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.services.qdrant_service import QdrantError, QdrantService


class TestQdrantProtocolService:
    """Test suite for Qdrant protocol collection management."""

    def test_create_protocol_collection(self, qdrant_service, sample_protocol_data):
        """Test creating a protocol collection."""
        collection_name = qdrant_service.create_protocol_collection(
            **sample_protocol_data
        )

        # Verify collection name format (special chars are cleaned)
        expected_prefix = "".join(
            c for c in sample_protocol_data["study_acronym"] if c.isalnum()
        ).upper()
        assert collection_name.startswith(expected_prefix)
        assert "-" in collection_name
        assert len(collection_name.split("-")[1]) == 8  # 8-char UUID

    def test_generate_collection_name(self, qdrant_service):
        """Test collection name generation."""
        # Test with simple acronym
        name1 = qdrant_service.generate_collection_name("TEST")
        assert name1.startswith("TEST-")
        assert len(name1.split("-")[1]) == 8

        # Test with special characters (should be cleaned)
        name2 = qdrant_service.generate_collection_name("TEST-123")
        assert name2.startswith("TEST123-")

        # Test uniqueness
        name3 = qdrant_service.generate_collection_name("TEST")
        assert name1 != name3  # Should generate different UUIDs

    def test_list_all_protocols_empty(self, qdrant_service):
        """Test listing protocols when none exist."""
        # Mock the client to return empty collections
        qdrant_service.client.get_collections = MagicMock()
        qdrant_service.client.get_collections.return_value.collections = []

        protocols = qdrant_service.list_all_protocols()
        assert protocols == []

    def test_test_connection(self, qdrant_service):
        """Test connection testing."""
        # Mock successful connection
        qdrant_service.client.get_collections = MagicMock()
        assert qdrant_service.test_connection() is True

        # Mock failed connection
        qdrant_service.client.get_collections.side_effect = Exception(
            "Connection failed"
        )
        assert qdrant_service.test_connection() is False

    def test_get_nonexistent_protocol_by_collection(self, qdrant_service):
        """Test retrieving non-existent protocol by collection name."""
        result = qdrant_service.get_protocol_by_collection("nonexistent-collection")
        assert result is None


    @pytest.mark.integration
    def test_collection_creation_error_handling(self, qdrant_service):
        """Test error handling during collection creation."""
        # Mock collection creation to fail
        qdrant_service.client.create_collection = MagicMock(
            side_effect=Exception("Collection already exists")
        )

        with pytest.raises(QdrantError, match="Failed to create protocol collection"):
            qdrant_service.create_protocol_collection(
                study_acronym="TEST", protocol_title="Test Protocol"
            )
