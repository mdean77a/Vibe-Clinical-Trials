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


class TestUploadProtocolTextEndpoint:
    """Test cases for POST /api/protocols/upload-text endpoint."""

    @pytest.mark.unit
    def test_upload_text_success(self, test_client):
        """Test successful protocol upload with extracted text."""
        request_data = {
            "study_acronym": "TEST-001",
            "protocol_title": "Test Protocol Title",
            "extracted_text": "This is extracted protocol text with enough content to be meaningful. "
            * 20,
            "original_filename": "test_protocol.pdf",
            "page_count": 10,
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["study_acronym"] == "TEST-001"
        assert data["protocol_title"] == "Test Protocol Title"
        assert "protocol_id" in data
        assert "collection_name" in data
        assert "upload_date" in data
        assert data["file_path"] == "test_protocol.pdf"

    @pytest.mark.unit
    def test_upload_text_normalizes_acronym(self, test_client):
        """Test that study_acronym is normalized to uppercase and trimmed."""
        request_data = {
            "study_acronym": "  test-002  ",  # Lowercase with spaces
            "protocol_title": "Test Protocol",
            "extracted_text": "Protocol content here. " * 20,
            "original_filename": "test.pdf",
            "page_count": 5,
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["study_acronym"] == "TEST-002"  # Should be uppercase and trimmed

    @pytest.mark.unit
    def test_upload_text_missing_study_acronym(self, test_client):
        """Test upload fails when study_acronym is missing."""
        request_data = {
            "protocol_title": "Test Protocol",
            "extracted_text": "Protocol content",
            "original_filename": "test.pdf",
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 400
        assert "study_acronym is required" in response.json()["detail"]

    @pytest.mark.unit
    def test_upload_text_empty_study_acronym(self, test_client):
        """Test upload fails when study_acronym is empty."""
        request_data = {
            "study_acronym": "   ",  # Only whitespace
            "protocol_title": "Test Protocol",
            "extracted_text": "Protocol content",
            "original_filename": "test.pdf",
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 400
        assert "study_acronym is required" in response.json()["detail"]

    @pytest.mark.unit
    def test_upload_text_missing_protocol_title(self, test_client):
        """Test upload fails when protocol_title is missing."""
        request_data = {
            "study_acronym": "TEST-003",
            "extracted_text": "Protocol content",
            "original_filename": "test.pdf",
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 400
        assert "protocol_title is required" in response.json()["detail"]

    @pytest.mark.unit
    def test_upload_text_empty_protocol_title(self, test_client):
        """Test upload fails when protocol_title is empty."""
        request_data = {
            "study_acronym": "TEST-004",
            "protocol_title": "   ",  # Only whitespace
            "extracted_text": "Protocol content",
            "original_filename": "test.pdf",
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 400
        assert "protocol_title is required" in response.json()["detail"]

    @pytest.mark.unit
    def test_upload_text_missing_extracted_text(self, test_client):
        """Test upload fails when extracted_text is missing."""
        request_data = {"study_acronym": "TEST-005", "protocol_title": "Test Protocol"}

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 400
        assert "extracted_text is required" in response.json()["detail"]

    @pytest.mark.unit
    def test_upload_text_empty_extracted_text(self, test_client):
        """Test upload fails when extracted_text is empty."""
        request_data = {
            "study_acronym": "TEST-006",
            "protocol_title": "Test Protocol",
            "extracted_text": "   ",  # Only whitespace
            "original_filename": "test.pdf",
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 400
        assert "extracted_text is required" in response.json()["detail"]

    @pytest.mark.unit
    def test_upload_text_without_optional_fields(self, test_client):
        """Test upload succeeds without optional fields."""
        request_data = {
            "study_acronym": "TEST-007",
            "protocol_title": "Test Protocol",
            "extracted_text": "Minimal protocol content. " * 20,
            # No original_filename or page_count
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["study_acronym"] == "TEST-007"
        assert data["file_path"] == ""  # Should default to empty string
        # page_count not in response model

    @pytest.mark.unit
    def test_upload_text_with_large_text(self, test_client):
        """Test upload with large extracted text."""
        # Create large text (> 2000 tokens to ensure chunking)
        large_text = " ".join(["Protocol section content with details"] * 1000)
        request_data = {
            "study_acronym": "TEST-008",
            "protocol_title": "Large Protocol",
            "extracted_text": large_text,
            "original_filename": "large_protocol.pdf",
            "page_count": 100,
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["study_acronym"] == "TEST-008"

    @pytest.mark.unit
    def test_upload_text_with_special_characters(self, test_client):
        """Test upload with special characters in text."""
        request_data = {
            "study_acronym": "TEST-009",
            "protocol_title": "Protocol with Special Chars: @#$%",
            "extracted_text": "Protocol content with special chars: @#$% & * () [] {}. "
            * 20,
            "original_filename": "special_chars.pdf",
            "page_count": 5,
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "@#$%" in data["protocol_title"]

    @pytest.mark.unit
    def test_upload_text_with_unicode(self, test_client):
        """Test upload with unicode characters."""
        request_data = {
            "study_acronym": "TEST-010",
            "protocol_title": "Protocol 临床试验 🌍",
            "extracted_text": "Protocol content 临床试验方案 with unicode 世界. " * 20,
            "original_filename": "unicode.pdf",
            "page_count": 3,
        }

        response = test_client.post("/api/protocols/upload-text", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "临床试验" in data["protocol_title"]


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
