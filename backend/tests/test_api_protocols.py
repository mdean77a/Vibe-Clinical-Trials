"""
Unit tests for FastAPI protocol endpoints.

This module tests all HTTP endpoints for protocol operations including:
- Request/response validation
- HTTP status codes
- Error handling
- Integration scenarios

Updated for Qdrant-only architecture (migrated from SQLite).
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models import ProtocolCreate
from app.services.qdrant_service import QdrantError, QdrantService


class TestCreateProtocolEndpoint:
    """Test cases for POST /protocols/ endpoint."""

    @pytest.mark.unit
    def test_create_protocol_success(self, test_client, sample_protocol_create_data):
        """Test successful protocol creation via API."""
        response = test_client.post("/api/protocols/", json=sample_protocol_create_data)

        assert response.status_code == 201
        data = response.json()

        assert data["study_acronym"] == sample_protocol_create_data["study_acronym"]
        assert data["protocol_title"] == sample_protocol_create_data["protocol_title"]
        assert data["file_path"] == sample_protocol_create_data["file_path"]
        assert "protocol_id" in data
        assert "collection_name" in data
        assert "upload_date" in data
        assert "created_at" in data

    @pytest.mark.unit
    def test_create_protocol_without_file_path(self, test_client):
        """Test creating protocol without file path."""
        protocol_data = {
            "study_acronym": "STUDY-123",
            "protocol_title": "Test Protocol",
        }

        response = test_client.post("/api/protocols/", json=protocol_data)

        assert response.status_code == 201
        data = response.json()
        assert data["file_path"] is None

    @pytest.mark.unit
    def test_create_protocol_invalid_data(self, test_client):
        """Test creating protocol with invalid data."""
        invalid_data = {
            "study_acronym": "",  # Empty acronym
            "protocol_title": "Test Protocol",
        }

        response = test_client.post("/api/protocols/", json=invalid_data)

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()

    @pytest.mark.unit
    def test_create_protocol_missing_required_fields(self, test_client):
        """Test creating protocol with missing required fields."""
        incomplete_data = {
            "study_acronym": "STUDY-123"
            # Missing protocol_title
        }

        response = test_client.post("/api/protocols/", json=incomplete_data)

        assert response.status_code == 422

    @pytest.mark.unit
    def test_create_protocol_database_error(
        self, test_client, sample_protocol_create_data
    ):
        """Test create protocol endpoint with database error."""
        with patch(
            "app.api.protocols.qdrant_service.create_protocol_collection"
        ) as mock_create:
            mock_create.side_effect = QdrantError("Database connection failed")

            response = test_client.post(
                "/api/protocols/", json=sample_protocol_create_data
            )

            assert response.status_code == 500
            assert "Failed to create protocol" in response.json()["detail"]


class TestGetProtocolEndpoint:
    """Test cases for GET /protocols/{protocol_id} endpoint."""

    @pytest.mark.unit
    def test_get_protocol_success(self, test_client, sample_protocol_create_data):
        """Test successful protocol retrieval by ID."""
        # Create a protocol first
        create_response = test_client.post(
            "/api/protocols/", json=sample_protocol_create_data
        )
        created_protocol = create_response.json()
        protocol_id = created_protocol["protocol_id"]

        # Retrieve it
        response = test_client.get(f"/api/protocols/{protocol_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["protocol_id"] == protocol_id
        assert data["study_acronym"] == sample_protocol_create_data["study_acronym"]
        assert data["protocol_title"] == sample_protocol_create_data["protocol_title"]

    @pytest.mark.unit
    def test_get_protocol_not_found(self, test_client):
        """Test get protocol with non-existent ID."""
        response = test_client.get("/api/protocols/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetProtocolByCollectionEndpoint:
    """Test cases for GET /protocols/collection/{collection_name} endpoint."""

    @pytest.mark.unit
    def test_get_protocol_by_collection_success(
        self, test_client, sample_protocol_create_data
    ):
        """Test successful protocol retrieval by collection name."""
        # Create a protocol first
        create_response = test_client.post(
            "/api/protocols/", json=sample_protocol_create_data
        )
        created_protocol = create_response.json()
        collection_name = created_protocol["collection_name"]

        # Retrieve by collection name
        response = test_client.get(f"/api/protocols/collection/{collection_name}")

        assert response.status_code == 200
        data = response.json()

        assert data["collection_name"] == collection_name
        assert data["study_acronym"] == sample_protocol_create_data["study_acronym"]

    @pytest.mark.unit
    def test_get_protocol_by_collection_not_found(self, test_client):
        """Test get protocol by collection name with non-existent collection."""
        response = test_client.get("/api/protocols/collection/nonexistent_collection")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestListProtocolsEndpoint:
    """Test cases for GET /protocols/ endpoint."""

    @pytest.mark.unit
    def test_list_protocols_empty(self, test_client):
        """Test listing protocols with empty database."""
        response = test_client.get("/api/protocols/")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.unit
    def test_list_protocols_multiple(self, test_client, multiple_protocols_data):
        """Test listing multiple protocols."""
        # Create multiple protocols
        created_protocols = []
        for protocol_data in multiple_protocols_data:
            create_response = test_client.post("/api/protocols/", json=protocol_data)
            created_protocols.append(create_response.json())

        # List all protocols
        response = test_client.get("/api/protocols/")

        assert response.status_code == 200
        data = response.json()

        assert len(data) == 3
        # Should be ordered by upload_date DESC (most recent first)
        for i in range(len(data) - 1):
            assert data[i]["upload_date"] >= data[i + 1]["upload_date"]


class TestDeleteProtocolEndpoint:
    """Test cases for DELETE /protocols/{protocol_id} endpoint."""

    @pytest.mark.unit
    def test_delete_protocol_success(self, test_client, sample_protocol_create_data):
        """Test successful protocol deletion."""
        # Create a protocol first
        create_response = test_client.post(
            "/api/protocols/", json=sample_protocol_create_data
        )
        created_protocol = create_response.json()
        protocol_id = created_protocol["protocol_id"]

        # Delete it using collection name endpoint
        response = test_client.delete(
            f"/api/protocols/collection/{created_protocol['collection_name']}"
        )

        assert response.status_code == 204
        assert response.content == b""  # No content for 204

        # Verify it's deleted
        get_response = test_client.get(f"/api/protocols/{protocol_id}")
        assert get_response.status_code == 404

    @pytest.mark.unit
    def test_delete_protocol_not_found(self, test_client):
        """Test delete protocol with non-existent protocol."""
        response = test_client.delete(
            "/api/protocols/collection/nonexistent_collection"
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    @pytest.mark.unit
    def test_root_endpoint(self, test_client):
        """Test root endpoint."""
        response = test_client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.unit
    def test_health_check_endpoint(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestIntegrationScenarios:
    """Integration test scenarios for API endpoints."""

    @pytest.mark.integration
    def test_full_protocol_api_lifecycle(self, test_client):
        """Test complete protocol lifecycle via API."""
        protocol_data = {
            "study_acronym": "STUDY-LIFECYCLE",
            "protocol_title": "API Lifecycle Test Protocol",
            "file_path": "/uploads/lifecycle.pdf",
        }

        # Create
        create_response = test_client.post("/api/protocols/", json=protocol_data)
        assert create_response.status_code == 201
        created_protocol = create_response.json()
        protocol_id = created_protocol["protocol_id"]

        # Read by ID
        get_response = test_client.get(f"/api/protocols/{protocol_id}")
        assert get_response.status_code == 200
        retrieved_protocol = get_response.json()
        assert retrieved_protocol["study_acronym"] == "STUDY-LIFECYCLE"

        # Read by collection name
        collection_name = created_protocol["collection_name"]
        collection_response = test_client.get(
            f"/api/protocols/collection/{collection_name}"
        )
        assert collection_response.status_code == 200

        # Verify in list
        list_response = test_client.get("/api/protocols/")
        assert list_response.status_code == 200
        all_protocols = list_response.json()
        assert len(all_protocols) == 1

        # Delete using collection name endpoint
        delete_response = test_client.delete(
            f"/api/protocols/collection/{collection_name}"
        )
        assert delete_response.status_code == 204

        # Verify deleted
        get_deleted_response = test_client.get(f"/api/protocols/{protocol_id}")
        assert get_deleted_response.status_code == 404

        # Verify empty list
        final_list_response = test_client.get("/api/protocols/")
        assert final_list_response.status_code == 200
        final_protocols = final_list_response.json()
        assert len(final_protocols) == 0

    @pytest.mark.integration
    def test_concurrent_protocol_creation_via_api(self, test_client):
        """Test creating multiple protocols via API."""
        protocols_data = [
            {
                "study_acronym": f"STUDY-{i:03d}",
                "protocol_title": f"API Protocol {i}",
                "file_path": f"/uploads/protocol_{i}.pdf",
            }
            for i in range(1, 6)
        ]

        created_protocols = []
        for protocol_data in protocols_data:
            response = test_client.post("/api/protocols/", json=protocol_data)
            assert response.status_code == 201
            created_protocols.append(response.json())

        # Verify all protocols created with unique collection names
        collection_names = [p["collection_name"] for p in created_protocols]
        assert len(set(collection_names)) == 5  # All unique

        # Verify all can be retrieved via list endpoint
        list_response = test_client.get("/api/protocols/")
        assert list_response.status_code == 200
        all_protocols = list_response.json()
        assert len(all_protocols) == 5
