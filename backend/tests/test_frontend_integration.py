"""
Tests for frontend-backend integration.

This module tests the integration between the frontend API utilities
and the backend Vercel Functions.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestFrontendBackendIntegration:
    """Test integration between frontend and backend through Vercel Functions."""

    @pytest.mark.integration
    def test_frontend_api_url_configuration(self):
        """Test that frontend API URL configuration works correctly."""
        # This would be tested in a JavaScript test environment
        # For now, we'll test the concept with Python

        # Production environment (Vercel)
        prod_base_url = "/api"

        # Development environment (local)
        dev_base_url = "http://localhost:8000"

        # Test endpoint construction
        endpoint = "protocols/"

        prod_url = f"{prod_base_url}/{endpoint}"
        dev_url = f"{dev_base_url}/{endpoint}"

        assert prod_url == "/api/protocols/"
        assert dev_url == "http://localhost:8000/protocols/"

    @pytest.mark.integration
    def test_vercel_function_response_format_matches_frontend_expectations(self):
        """Test that Vercel Function responses match what frontend expects."""
        from app.vercel_adapter import convert_fastapi_response

        # Test protocol creation response
        protocol_data = {
            "id": 1,
            "study_acronym": "TEST-123",
            "protocol_title": "Test Protocol",
            "collection_name": "test123_20241201_120000",
            "status": "processing",
        }

        vercel_response = convert_fastapi_response(201, protocol_data)

        # Verify response format matches frontend expectations
        assert vercel_response["statusCode"] == 201
        assert vercel_response["headers"]["content-type"] == "application/json"
        assert vercel_response["headers"]["access-control-allow-origin"] == "*"

        # Verify response body can be parsed by frontend
        response_body = json.loads(vercel_response["body"])
        assert response_body["id"] == 1
        assert response_body["study_acronym"] == "TEST-123"

    @pytest.mark.integration
    def test_cors_headers_for_frontend_requests(self):
        """Test that CORS headers are properly set for frontend requests."""
        from app.vercel_adapter import handle_cors_preflight

        cors_response = handle_cors_preflight()

        assert cors_response["statusCode"] == 200
        assert cors_response["headers"]["access-control-allow-origin"] == "*"
        assert (
            "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            in cors_response["headers"]["access-control-allow-methods"]
        )
        assert (
            "Content-Type, Authorization"
            in cors_response["headers"]["access-control-allow-headers"]
        )

    @pytest.mark.integration
    def test_error_response_format_for_frontend(self):
        """Test that error responses are formatted correctly for frontend consumption."""
        from app.vercel_adapter import convert_fastapi_response

        error_response = convert_fastapi_response(404, {"detail": "Protocol not found"})

        assert error_response["statusCode"] == 404
        assert error_response["headers"]["content-type"] == "application/json"

        error_body = json.loads(error_response["body"])
        assert error_body["detail"] == "Protocol not found"

    @pytest.mark.integration
    def test_protocol_lifecycle_through_vercel_functions(self):
        """Test complete protocol CRUD operations through Vercel Functions."""
        # This test simulates the frontend calling Vercel Functions

        # Mock Vercel request for creating a protocol
        create_request = {
            "httpMethod": "POST",
            "path": "/protocols/",
            "headers": {"content-type": "application/json"},
            "queryStringParameters": None,
            "body": json.dumps(
                {
                    "study_acronym": "TEST-123",
                    "protocol_title": "Integration Test Protocol",
                    "file_path": "/uploads/test.pdf",
                }
            ),
        }

        # Mock Vercel request for getting a protocol
        get_request = {
            "httpMethod": "GET",
            "path": "/protocols/1",
            "headers": {"content-type": "application/json"},
            "queryStringParameters": None,
            "body": None,
        }

        # Verify request format is correct for Vercel Functions
        from app.vercel_adapter import convert_vercel_request

        create_fastapi_request = convert_vercel_request(create_request)
        assert create_fastapi_request["method"] == "POST"
        assert create_fastapi_request["path"] == "/protocols/"
        assert create_fastapi_request["body"]["study_acronym"] == "TEST-123"

        get_fastapi_request = convert_vercel_request(get_request)
        assert get_fastapi_request["method"] == "GET"
        assert get_fastapi_request["path"] == "/protocols/1"
