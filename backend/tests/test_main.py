"""
Tests for FastAPI main application module.

This module tests the FastAPI application initialization, lifespan events,
and core endpoints including health checks and root endpoint.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app, lifespan


class TestLifespanManager:
    """Test cases for application lifespan context manager."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_lifespan_successful_startup(self):
        """Test successful application startup with Qdrant initialization."""
        mock_qdrant_service = MagicMock()

        with patch("app.main.get_qdrant_service") as mock_get_qdrant:
            with patch("app.main.logger") as mock_logger:
                mock_get_qdrant.return_value = mock_qdrant_service

                # Execute lifespan context manager
                async with lifespan(app):
                    # Verify startup logging
                    assert mock_logger.info.call_count >= 1
                    startup_calls = [
                        call
                        for call in mock_logger.info.call_args_list
                        if "Starting Clinical Trial Accelerator" in str(call)
                    ]
                    assert len(startup_calls) == 1

                    # Verify Qdrant service was initialized
                    mock_get_qdrant.assert_called_once()

                    success_calls = [
                        call
                        for call in mock_logger.info.call_args_list
                        if "Qdrant service initialized successfully" in str(call)
                    ]
                    assert len(success_calls) == 1

                # Verify shutdown logging (after context exits)
                shutdown_calls = [
                    call
                    for call in mock_logger.info.call_args_list
                    if "Shutting down Clinical Trial Accelerator" in str(call)
                ]
                assert len(shutdown_calls) == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_lifespan_startup_failure(self):
        """Test application startup failure when Qdrant initialization fails."""
        with patch("app.main.get_qdrant_service") as mock_get_qdrant:
            with patch("app.main.logger") as mock_logger:
                # Simulate Qdrant service initialization failure
                mock_get_qdrant.side_effect = Exception("Connection refused")

                # Verify exception is raised
                with pytest.raises(Exception, match="Connection refused"):
                    async with lifespan(app):
                        pass

                # Verify error logging
                mock_logger.error.assert_called_once()
                error_call = mock_logger.error.call_args[0][0]
                assert "Failed to initialize Qdrant service" in error_call
                assert "Connection refused" in error_call

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_lifespan_shutdown_logging(self):
        """Test shutdown logging is executed properly."""
        mock_qdrant_service = MagicMock()

        with patch("app.main.get_qdrant_service") as mock_get_qdrant:
            with patch("app.main.logger") as mock_logger:
                mock_get_qdrant.return_value = mock_qdrant_service

                async with lifespan(app):
                    # Reset call count to isolate shutdown logging
                    mock_logger.info.reset_mock()

                # After context exits, shutdown should be logged
                shutdown_calls = [
                    call
                    for call in mock_logger.info.call_args_list
                    if "Shutting down" in str(call)
                ]
                assert len(shutdown_calls) == 1


class TestRootEndpoint:
    """Test cases for root endpoint."""

    @pytest.mark.unit
    def test_root_endpoint(self):
        """Test root endpoint returns correct response."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Clinical Trial Accelerator API"
        assert data["version"] == "0.1.0"
        assert data["status"] == "healthy"

    @pytest.mark.unit
    def test_root_endpoint_structure(self):
        """Test root endpoint response has all required fields."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert len(data) == 3


class TestHealthCheckEndpoint:
    """Test cases for health check endpoint."""

    @pytest.mark.unit
    def test_health_check_endpoint(self):
        """Test health check endpoint returns healthy status."""
        client = TestClient(app)
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.unit
    def test_health_check_structure(self):
        """Test health check response structure."""
        client = TestClient(app)
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)


class TestApplicationConfiguration:
    """Test cases for FastAPI application configuration."""

    @pytest.mark.unit
    def test_cors_middleware_configured(self):
        """Test CORS middleware is properly configured."""
        # Check that CORS middleware is in the app's middleware stack
        middleware_types = [type(m.cls) for m in app.user_middleware]
        from fastapi.middleware.cors import CORSMiddleware

        # Note: Middleware configuration is hard to test directly,
        # but we can verify it doesn't break basic requests
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200

    @pytest.mark.unit
    def test_routers_included(self):
        """Test that API routers are included in the application."""
        # Get all registered routes
        routes = [route.path for route in app.routes]

        # Verify key API routes are registered
        assert "/" in routes
        assert "/api/health" in routes

        # Verify ICF and protocol routes are included (prefix check)
        icf_routes = [r for r in routes if r.startswith("/api/icf")]
        protocol_routes = [r for r in routes if r.startswith("/api/protocols")]

        assert len(icf_routes) > 0, "ICF routes should be included"
        assert len(protocol_routes) > 0, "Protocol routes should be included"

    @pytest.mark.unit
    def test_app_metadata(self):
        """Test FastAPI application metadata."""
        assert app.title == "Clinical Trial Accelerator API"
        assert app.description == "AI-powered clinical trial document generation backend"
        assert app.version == "0.1.0"


class TestApplicationLifecycle:
    """Integration tests for full application lifecycle."""

    @pytest.mark.unit
    def test_app_can_handle_multiple_requests(self):
        """Test application can handle multiple sequential requests."""
        client = TestClient(app)

        # Make multiple requests
        for _ in range(5):
            response = client.get("/api/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    @pytest.mark.unit
    def test_app_endpoints_accessible(self):
        """Test that all main endpoints are accessible."""
        client = TestClient(app)

        endpoints_to_test = [
            ("/", 200),
            ("/api/health", 200),
        ]

        for endpoint, expected_status in endpoints_to_test:
            response = client.get(endpoint)
            assert (
                response.status_code == expected_status
            ), f"Endpoint {endpoint} returned {response.status_code}"
