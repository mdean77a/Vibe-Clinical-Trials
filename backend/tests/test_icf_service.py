"""
Unit tests for ICF generation service.

This module tests the ICF service layer that integrates LangGraph workflows
with the API endpoints for ICF document generation.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.services.icf_service import ICFGenerationService, get_icf_service
from app.services.document_generator import DocumentGenerationError
from app.main import app


class TestICFGenerationService:
    """Test cases for ICFGenerationService class."""

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_init_service(self, mock_qdrant_client):
        """Test ICFGenerationService initialization."""
        service = ICFGenerationService(mock_qdrant_client)
        
        assert service.qdrant_client == mock_qdrant_client
        assert service.llm_config["model"] == "claude-4-sonnet"
        assert service.llm_config["max_tokens"] == 32000
        assert service.llm_config["temperature"] == 0.1
        assert service.icf_workflow is not None

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_generate_icf_async_success(self, mock_qdrant_client, sample_protocol_metadata):
        """Test successful async ICF generation."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "TEST_COLLECTION_12345"
        
        # Mock the synchronous generation method
        expected_result = {
            "collection_name": collection_name,
            "sections": {
                "summary": "Generated summary",
                "background": "Generated background",
                "participants": "Generated participants",
                "procedures": "Generated procedures",
                "alternatives": "Generated alternatives",
                "risks": "Generated risks",
                "benefits": "Generated benefits",
            },
            "metadata": {"generation_timestamp": 123456.789},
            "errors": [],
            "status": "completed"
        }
        
        with patch.object(service, '_generate_icf_sync', return_value=expected_result):
            result = await service.generate_icf_async(collection_name, sample_protocol_metadata)
            
            assert result["collection_name"] == collection_name
            assert len(result["sections"]) == 7
            assert result["status"] == "completed"
            assert "summary" in result["sections"]

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_generate_icf_async_error(self, mock_qdrant_client):
        """Test async ICF generation with error."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "TEST_COLLECTION_ERROR"
        
        # Mock the synchronous method to raise an error
        with patch.object(service, '_generate_icf_sync', side_effect=Exception("Generation failed")):
            with pytest.raises(DocumentGenerationError, match="Failed to generate ICF"):
                await service.generate_icf_async(collection_name)

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_icf_sync_success(self, mock_qdrant_client):
        """Test successful synchronous ICF generation."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "TEST_COLLECTION_SYNC"
        
        # Mock document generator context retrieval
        mock_context = [
            {"text": "Protocol inclusion criteria", "score": 0.9},
            {"text": "Study procedures description", "score": 0.8},
        ]
        
        with patch.object(service.document_generator, 'get_protocol_context', return_value=mock_context), \
             patch.object(service.icf_workflow, 'invoke') as mock_invoke:
            
            # Mock workflow response
            mock_invoke.return_value = {
                "sections": {
                    "summary": "Generated summary",
                    "background": "Generated background", 
                    "participants": "Generated participants",
                    "procedures": "Generated procedures",
                    "alternatives": "Generated alternatives",
                    "risks": "Generated risks",
                    "benefits": "Generated benefits",
                },
                "errors": [],
                "metadata": {"workflow_name": "icf_generation"}
            }
            
            result = service._generate_icf_sync(collection_name)
            
            assert result["collection_name"] == collection_name
            assert len(result["sections"]) == 7
            assert result["status"] == "completed"
            mock_invoke.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_generate_icf_sync_missing_sections(self, mock_qdrant_client):
        """Test sync ICF generation with missing required sections."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "TEST_COLLECTION_INCOMPLETE"
        
        mock_context = [{"text": "Limited context", "score": 0.5}]
        
        with patch.object(service.document_generator, 'get_protocol_context', return_value=mock_context), \
             patch.object(service.icf_workflow, 'invoke') as mock_invoke:
            
            # Mock incomplete workflow response
            mock_invoke.return_value = {
                "sections": {
                    "summary": "Generated summary",
                    "background": "Generated background",
                    # Missing other required sections
                },
                "errors": [],
                "metadata": {}
            }
            
            with pytest.raises(DocumentGenerationError, match="Missing required ICF sections"):
                service._generate_icf_sync(collection_name)

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_validate_collection_exists_true(self, mock_qdrant_client):
        """Test collection validation when collection exists."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "EXISTING_COLLECTION"
        
        # Mock Qdrant collections response
        mock_collection = MagicMock()
        mock_collection.name = collection_name
        mock_collections_response = MagicMock()
        mock_collections_response.collections = [mock_collection]
        
        mock_qdrant_client.get_collections.return_value = mock_collections_response
        
        result = await service.validate_collection_exists(collection_name)
        assert result is True

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_validate_collection_exists_false(self, mock_qdrant_client):
        """Test collection validation when collection doesn't exist."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "NONEXISTENT_COLLECTION"
        
        # Mock empty collections response
        mock_collections_response = MagicMock()
        mock_collections_response.collections = []
        
        mock_qdrant_client.get_collections.return_value = mock_collections_response
        
        result = await service.validate_collection_exists(collection_name)
        assert result is False

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_get_protocol_summary_success(self, mock_qdrant_client):
        """Test successful protocol summary retrieval."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "TEST_PROTOCOL_SUMMARY"
        
        # Mock Qdrant scroll response
        mock_point = MagicMock()
        mock_point.payload = {
            "protocol_title": "Test Clinical Trial",
            "filename": "protocol.pdf",
            "document_id": "test-doc-123"
        }
        mock_scroll_response = ([mock_point], None)
        
        mock_qdrant_client.scroll.return_value = mock_scroll_response
        
        result = await service.get_protocol_summary(collection_name)
        
        assert result["collection_name"] == collection_name
        assert result["status"] == "ready"
        assert result["protocol_metadata"]["title"] == "Test Clinical Trial"

    @pytest.mark.unit
    @pytest.mark.ai_service
    async def test_get_protocol_summary_empty(self, mock_qdrant_client):
        """Test protocol summary for empty collection."""
        service = ICFGenerationService(mock_qdrant_client)
        collection_name = "EMPTY_COLLECTION"
        
        # Mock empty scroll response
        mock_scroll_response = ([], None)
        mock_qdrant_client.scroll.return_value = mock_scroll_response
        
        result = await service.get_protocol_summary(collection_name)
        
        assert result["collection_name"] == collection_name
        assert result["status"] == "empty"

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_get_generation_status(self, mock_qdrant_client):
        """Test generation status retrieval."""
        service = ICFGenerationService(mock_qdrant_client)
        task_id = "test-task-123"
        
        result = service.get_generation_status(task_id)
        
        assert result["task_id"] == task_id
        assert result["status"] == "not_implemented"

    @pytest.mark.unit
    @pytest.mark.ai_service
    def test_get_icf_service_singleton(self):
        """Test singleton service retrieval."""
        service1 = get_icf_service()
        service2 = get_icf_service()
        
        assert service1 is service2
        assert isinstance(service1, ICFGenerationService)


class TestICFGenerationAPI:
    """Test cases for ICF Generation API endpoints."""

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_generate_icf_endpoint_success(self, mock_qdrant_client):
        """Test successful ICF generation API endpoint."""
        
        request_data = {
            "protocol_collection_name": "TEST_COLLECTION_API",
            "protocol_metadata": {
                "protocol_title": "Test Protocol",
                "sponsor": "Test Sponsor"
            }
        }
        
        # Mock the service dependencies at module level
        with patch('app.services.icf_service.get_qdrant_service') as mock_get_qdrant_service, \
             patch('app.api.icf_generation.get_icf_service') as mock_get_service:
            
            # Mock qdrant service
            mock_qdrant_service = MagicMock()
            mock_qdrant_service.client = mock_qdrant_client
            mock_get_qdrant_service.return_value = mock_qdrant_service
            
            # Mock ICF service
            mock_service = MagicMock()
            mock_service.validate_collection_exists = AsyncMock(return_value=True)
            mock_service.generate_icf_async = AsyncMock(return_value={
                "collection_name": "TEST_COLLECTION_API",
                "sections": {
                    "summary": "Generated summary",
                    "background": "Generated background",
                    "participants": "Generated participants",
                    "procedures": "Generated procedures",
                    "alternatives": "Generated alternatives",
                    "risks": "Generated risks",
                    "benefits": "Generated benefits",
                },
                "metadata": {"timestamp": 123456.789},
                "errors": [],
                "status": "completed"
            })
            mock_get_service.return_value = mock_service
            
            client = TestClient(app)
            response = client.post("/api/icf/generate", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["collection_name"] == "TEST_COLLECTION_API"
            assert len(data["sections"]) == 7
            assert data["status"] == "completed"

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_generate_icf_endpoint_collection_not_found(self, mock_qdrant_client):
        """Test ICF generation API with non-existent collection."""
        
        request_data = {
            "protocol_collection_name": "NONEXISTENT_COLLECTION"
        }
        
        with patch('app.services.icf_service.get_qdrant_service') as mock_get_qdrant_service, \
             patch('app.api.icf_generation.get_icf_service') as mock_get_service:
            
            # Mock qdrant service
            mock_qdrant_service = MagicMock()
            mock_qdrant_service.client = mock_qdrant_client
            mock_get_qdrant_service.return_value = mock_qdrant_service
            
            # Mock ICF service
            mock_service = MagicMock()
            mock_service.validate_collection_exists = AsyncMock(return_value=False)
            mock_get_service.return_value = mock_service
            
            client = TestClient(app)
            response = client.post("/api/icf/generate", json=request_data)
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_get_protocol_summary_endpoint(self, mock_qdrant_client):
        """Test protocol summary API endpoint."""
        collection_name = "TEST_SUMMARY_COLLECTION"
        
        with patch('app.services.icf_service.get_qdrant_service') as mock_get_qdrant_service, \
             patch('app.api.icf_generation.get_icf_service') as mock_get_service:
            
            # Mock qdrant service
            mock_qdrant_service = MagicMock()
            mock_qdrant_service.client = mock_qdrant_client
            mock_get_qdrant_service.return_value = mock_qdrant_service
            
            # Mock ICF service
            mock_service = MagicMock()
            mock_service.get_protocol_summary = AsyncMock(return_value={
                "collection_name": collection_name,
                "status": "ready",
                "protocol_metadata": {
                    "title": "Test Protocol",
                    "filename": "test.pdf"
                }
            })
            mock_get_service.return_value = mock_service
            
            client = TestClient(app)
            response = client.get(f"/api/icf/protocol/{collection_name}/summary")
            
            assert response.status_code == 200
            data = response.json()
            assert data["collection_name"] == collection_name
            assert data["status"] == "ready"

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_get_icf_section_requirements_endpoint(self):
        """Test ICF section requirements API endpoint."""
        client = TestClient(app)
        
        response = client.get("/api/icf/sections/requirements")
        
        assert response.status_code == 200
        data = response.json()
        assert "required_sections" in data
        assert data["total_sections"] == 7
        assert len(data["required_sections"]) == 7

    @pytest.mark.integration
    @pytest.mark.ai_service
    def test_icf_health_check_endpoint(self, mock_qdrant_client):
        """Test ICF health check API endpoint."""
        
        with patch('app.services.icf_service.get_qdrant_service') as mock_get_qdrant_service, \
             patch('app.api.icf_generation.get_icf_service') as mock_get_service:
            
            # Mock qdrant service
            mock_qdrant_service = MagicMock()
            mock_qdrant_service.client = mock_qdrant_client
            mock_get_qdrant_service.return_value = mock_qdrant_service
            
            # Mock ICF service
            mock_service = MagicMock()
            mock_service.icf_workflow.name = "icf_generation"
            mock_service.llm_config = {"model": "claude-4-sonnet"}
            mock_get_service.return_value = mock_service
            
            client = TestClient(app)
            response = client.get("/api/icf/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "ICF Generation"
            assert data["llm_model"] == "claude-4-sonnet"