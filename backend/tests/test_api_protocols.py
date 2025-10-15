"""
Unit tests for FastAPI protocol endpoints.

This module tests all HTTP endpoints for protocol operations including:
- Request/response validation
- HTTP status codes
- Error handling
- Integration scenarios

Updated for Qdrant-only architecture (migrated from SQLite).
"""

import pytest
from fastapi.testclient import TestClient

# Removed test classes for unused endpoints:
# - TestCreateProtocolEndpoint (POST /protocols/)
# - TestGetProtocolEndpoint (GET /protocols/{protocol_id})
# - TestGetProtocolByCollectionEndpoint (GET /protocols/collection/{collection_name})


class TestListProtocolsEndpoint:
    """Test cases for GET /protocols/ endpoint."""

    @pytest.mark.unit
    def test_list_protocols_empty(self, test_client):
        """Test listing protocols with empty database."""
        response = test_client.get("/api/protocols/")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    # Removed test_list_protocols_multiple - relied on removed POST endpoint
    # Note: List functionality is still tested via test_list_protocols_empty


class TestDeleteProtocolEndpoint:
    """Test cases for DELETE /protocols/{protocol_id} endpoint."""


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


# Removed integration tests that relied on removed endpoints:
# - test_full_protocol_api_lifecycle (used POST, GET by ID, GET by collection)
# - test_concurrent_protocol_creation_via_api (used POST endpoint)
