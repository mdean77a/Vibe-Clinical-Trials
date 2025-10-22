"""
Unit tests for ICF Generation API endpoints.

This module tests all HTTP endpoints for ICF generation operations including:
- Streaming ICF generation
- Section regeneration
- Protocol summary retrieval
- Generation status tracking
- Health check endpoint
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.icf_service import get_icf_service


@pytest.fixture(autouse=True)
def cleanup_overrides():
    """Clean up dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


class TestGenerateICFStreamEndpoint:
    """Test cases for POST /api/icf/generate-stream endpoint."""

    @pytest.mark.unit
    def test_generate_stream_success(self):
        """Test successful ICF generation with streaming."""
        mock_service = MagicMock()

        async def mock_stream():
            yield {"type": "section_start", "section_name": "summary"}
            yield {
                "type": "token",
                "section_name": "summary",
                "content": "This is ",
                "accumulated_content": "This is ",
            }
            yield {
                "type": "section_complete",
                "section_name": "summary",
                "content": "This is a test summary section.",
            }
            yield {
                "type": "complete",
                "total_sections": 7,
                "completed_sections": 7,
                "errors": [],
            }

        mock_service.generate_icf_streaming.return_value = mock_stream()
        mock_service.validate_collection_exists = AsyncMock(return_value=True)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {
            "protocol_collection_name": "test-collection-123",
            "protocol_metadata": {"protocol_title": "Test Protocol"},
        }

        response = client.post("/api/icf/generate-stream", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        assert len(events) >= 2
        assert events[0]["event"] == "section_start"
        assert events[-1]["event"] == "complete"

    @pytest.mark.unit
    def test_generate_stream_collection_not_found(self):
        """Test streaming generation fails when collection doesn't exist."""
        mock_service = MagicMock()
        mock_service.validate_collection_exists = AsyncMock(return_value=False)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {"protocol_collection_name": "nonexistent-collection"}

        response = client.post("/api/icf/generate-stream", json=request_data)

        assert response.status_code == 200
        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        assert len(events) >= 1
        assert events[0]["event"] == "error"
        assert "not found" in events[0]["data"]["error"]

    @pytest.mark.unit
    def test_generate_stream_section_error(self):
        """Test streaming handles section generation errors."""
        mock_service = MagicMock()

        async def mock_stream():
            yield {"type": "section_start", "section_name": "summary"}
            yield {
                "type": "section_error",
                "section_name": "summary",
                "error": "Failed to generate summary section",
            }

        mock_service.generate_icf_streaming.return_value = mock_stream()
        mock_service.validate_collection_exists = AsyncMock(return_value=True)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {"protocol_collection_name": "test-collection-123"}

        response = client.post("/api/icf/generate-stream", json=request_data)

        assert response.status_code == 200
        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        assert any(e["event"] == "section_error" for e in events)

    @pytest.mark.unit
    def test_generate_stream_missing_collection_name(self):
        """Test streaming fails with missing collection name."""
        client = TestClient(app)
        request_data = {}

        response = client.post("/api/icf/generate-stream", json=request_data)

        assert response.status_code == 422


class TestRegenerateICFSectionEndpoint:
    """Test cases for POST /api/icf/regenerate-section endpoint."""

    @pytest.mark.unit
    def test_regenerate_section_success(self):
        """Test successful section regeneration with streaming."""
        mock_service = MagicMock()

        async def mock_stream():
            yield {"type": "section_start", "section_name": "risks"}
            yield {
                "type": "section_complete",
                "section_name": "risks",
                "content": "Regenerated risks section content.",
            }
            yield {
                "type": "complete",
                "total_sections": 1,
                "completed_sections": 1,
                "errors": [],
            }

        mock_service.generate_icf_streaming.return_value = mock_stream()
        mock_service.validate_collection_exists = AsyncMock(return_value=True)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {
            "protocol_collection_name": "test-collection-123",
            "section_name": "risks",
        }

        response = client.post("/api/icf/regenerate-section", json=request_data)

        assert response.status_code == 200
        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        assert len(events) >= 2
        assert any(e["event"] == "section_start" for e in events)

    @pytest.mark.unit
    def test_regenerate_section_invalid_section_name(self):
        """Test regeneration fails with invalid section name."""
        mock_service = MagicMock()
        mock_service.validate_collection_exists = AsyncMock(return_value=True)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {
            "protocol_collection_name": "test-collection-123",
            "section_name": "invalid_section",
        }

        response = client.post("/api/icf/regenerate-section", json=request_data)

        assert response.status_code == 200
        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        assert len(events) >= 1
        assert events[0]["event"] == "error"
        assert "Invalid section name" in events[0]["data"]["error"]

    @pytest.mark.unit
    def test_regenerate_section_valid_sections(self):
        """Test all valid section names are accepted."""
        valid_sections = [
            "summary",
            "background",
            "participants",
            "procedures",
            "alternatives",
            "risks",
            "benefits",
        ]

        mock_service = MagicMock()

        async def mock_stream():
            yield {"type": "section_complete", "section_name": "test", "content": "Test"}

        mock_service.generate_icf_streaming.return_value = mock_stream()
        mock_service.validate_collection_exists = AsyncMock(return_value=True)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)

        for section in valid_sections:
            request_data = {
                "protocol_collection_name": "test-collection-123",
                "section_name": section,
            }
            response = client.post("/api/icf/regenerate-section", json=request_data)
            assert response.status_code == 200

    @pytest.mark.unit
    def test_regenerate_section_collection_not_found(self):
        """Test regeneration fails when collection doesn't exist."""
        mock_service = MagicMock()
        mock_service.validate_collection_exists = AsyncMock(return_value=False)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {
            "protocol_collection_name": "nonexistent-collection",
            "section_name": "summary",
        }

        response = client.post("/api/icf/regenerate-section", json=request_data)

        assert response.status_code == 200
        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        assert events[0]["event"] == "error"


class TestGetProtocolSummaryEndpoint:
    """Test cases for GET /api/icf/protocol/{collection_name}/summary endpoint."""

    @pytest.mark.unit
    def test_get_protocol_summary_success(self):
        """Test successful protocol summary retrieval."""
        mock_service = MagicMock()
        mock_service.get_protocol_summary = AsyncMock(
            return_value={
                "collection_name": "test-collection-123",
                "status": "ready",
                "protocol_metadata": {
                    "title": "Test Protocol",
                    "filename": "test.pdf",
                    "document_id": "doc-123",
                    "total_chunks": 50,
                },
            }
        )
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        response = client.get("/api/icf/protocol/test-collection-123/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["collection_name"] == "test-collection-123"
        assert data["status"] == "ready"
        assert "protocol_metadata" in data

    @pytest.mark.unit
    def test_get_protocol_summary_empty_collection(self):
        """Test protocol summary when collection is empty."""
        mock_service = MagicMock()
        mock_service.get_protocol_summary = AsyncMock(
            return_value={
                "collection_name": "empty-collection",
                "status": "empty",
                "message": "No protocol content found",
            }
        )
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        response = client.get("/api/icf/protocol/empty-collection/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "empty"
        assert "message" in data

    @pytest.mark.unit
    def test_get_protocol_summary_error(self):
        """Test protocol summary handles errors."""
        mock_service = MagicMock()
        mock_service.get_protocol_summary = AsyncMock(
            side_effect=Exception("Database connection error")
        )
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        response = client.get("/api/icf/protocol/test-collection/summary")

        assert response.status_code == 500
        assert "Failed to retrieve protocol summary" in response.json()["detail"]

    @pytest.mark.unit
    def test_get_protocol_summary_special_characters_in_name(self):
        """Test protocol summary with special characters in collection name."""
        mock_service = MagicMock()
        mock_service.get_protocol_summary = AsyncMock(
            return_value={
                "collection_name": "test-collection_with-special.chars",
                "status": "ready",
            }
        )
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        response = client.get(
            "/api/icf/protocol/test-collection_with-special.chars/summary"
        )

        assert response.status_code == 200


class TestGetGenerationStatusEndpoint:
    """Test cases for GET /api/icf/status/{task_id} endpoint."""

    @pytest.mark.unit
    def test_get_generation_status_success(self):
        """Test successful generation status retrieval."""
        mock_service = MagicMock()
        mock_service.get_generation_status.return_value = {
            "task_id": "task-123",
            "status": "not_implemented",
            "message": "Task tracking not yet implemented",
        }
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        response = client.get("/api/icf/status/task-123")

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "task-123"
        assert data["status"] == "not_implemented"

    @pytest.mark.unit
    def test_get_generation_status_error(self):
        """Test generation status handles errors."""
        mock_service = MagicMock()
        mock_service.get_generation_status.side_effect = Exception(
            "Status lookup failed"
        )
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        response = client.get("/api/icf/status/task-123")

        assert response.status_code == 500
        assert "Failed to retrieve generation status" in response.json()["detail"]


class TestICFHealthCheckEndpoint:
    """Test cases for GET /api/icf/health endpoint."""

    @pytest.mark.unit
    def test_health_check_success(self):
        """Test successful health check."""
        with patch("app.api.icf_generation.get_icf_service") as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service

            client = TestClient(app)
            response = client.get("/api/icf/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "ICF Generation"
            assert data["workflow"] == "StreamingICFWorkflow"
            assert "llm_model" in data

    @pytest.mark.unit
    def test_health_check_service_failure(self):
        """Test health check when service fails to initialize."""
        with patch("app.api.icf_generation.get_icf_service") as mock_get_service:
            mock_get_service.side_effect = Exception("Service initialization failed")

            client = TestClient(app)
            response = client.get("/api/icf/health")

            assert response.status_code == 500
            assert "ICF service unhealthy" in response.json()["detail"]


class TestICFGenerationIntegration:
    """Integration test scenarios for ICF generation API."""

    @pytest.mark.unit
    def test_full_icf_generation_flow(self):
        """Test complete ICF generation flow from start to finish."""
        mock_service = MagicMock()

        async def mock_stream():
            sections = ["summary", "background", "participants", "procedures"]
            for section in sections:
                yield {"type": "section_start", "section_name": section}
                yield {
                    "type": "section_complete",
                    "section_name": section,
                    "content": f"Content for {section}",
                }
            yield {
                "type": "complete",
                "total_sections": 4,
                "completed_sections": 4,
                "errors": [],
            }

        mock_service.generate_icf_streaming.return_value = mock_stream()
        mock_service.validate_collection_exists = AsyncMock(return_value=True)
        app.dependency_overrides[get_icf_service] = lambda: mock_service

        client = TestClient(app)
        request_data = {
            "protocol_collection_name": "test-protocol-full",
            "protocol_metadata": {"protocol_title": "Full Test Protocol"},
        }

        response = client.post("/api/icf/generate-stream", json=request_data)

        assert response.status_code == 200
        events = []
        for line in response.text.strip().split("\n"):
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                events.append(event_data)

        section_starts = [e for e in events if e["event"] == "section_start"]
        section_completes = [e for e in events if e["event"] == "section_complete"]
        complete_events = [e for e in events if e["event"] == "complete"]

        assert len(section_starts) == 4
        assert len(section_completes) == 4
        assert len(complete_events) == 1
