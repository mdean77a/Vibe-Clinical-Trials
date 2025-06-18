"""
Pytest configuration and fixtures for Qdrant-based Clinical Trial Accelerator tests.

This module provides shared fixtures for testing including:
- In-memory Qdrant setup
- Test client configuration
- Data factories for test data generation
- Mock AI services (OpenAI, LangGraph)
"""

import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from factory import Factory, Faker, LazyAttribute
from fastapi.testclient import TestClient
from freezegun import freeze_time
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.main import app


class ProtocolMetadataFactory(Factory):
    """Factory for creating protocol metadata test instances."""

    class Meta:
        model = dict

    study_acronym = Faker("lexify", text="STUDY-???")
    protocol_title = Faker("sentence", nb_words=6)
    filename = LazyAttribute(lambda obj: f"{obj.study_acronym.lower()}.pdf")
    upload_date = Faker("date_time")
    status = "processing"
    document_id = LazyAttribute(lambda obj: str(uuid.uuid4()))


@pytest.fixture
def mock_qdrant_client():
    """
    Create a mock Qdrant client for testing.

    Returns:
        MagicMock: Mocked Qdrant client
    """
    mock_client = MagicMock(spec=QdrantClient)

    # Configure mock methods
    mock_client.create_collection.return_value = True
    mock_client.upsert.return_value = True
    mock_client.search.return_value = []
    mock_client.scroll.return_value = ([], None)
    mock_client.get_collection.return_value = True

    return mock_client


@pytest.fixture
def memory_qdrant_client():
    """
    Create an in-memory Qdrant client for integration testing.

    Returns:
        QdrantClient: In-memory Qdrant client
    """
    client = QdrantClient(":memory:")

    # Create test collection
    client.create_collection(
        collection_name="test_protocols",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

    return client


@pytest.fixture
def mock_openai_client():
    """
    Mock OpenAI client for testing embeddings.

    Returns:
        MagicMock: Mocked OpenAI client
    """
    mock_client = MagicMock()

    # Mock embedding response
    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1] * 1536  # Mock 1536-dimensional embedding
    mock_client.embeddings.create.return_value.data = [mock_embedding]

    return mock_client


@pytest.fixture
def mock_langgraph_workflow():
    """
    Mock LangGraph workflow for testing document generation.

    Returns:
        MagicMock: Mocked LangGraph workflow
    """
    mock_workflow = MagicMock()

    # Mock workflow execution
    mock_workflow.invoke.return_value = {
        "sections": {
            "title": "Generated Title",
            "purpose": "Generated Purpose",
            "procedures": "Generated Procedures",
            "risks": "Generated Risks and Benefits",
        }
    }

    return mock_workflow


@pytest.fixture
def sample_pdf_content():
    """
    Sample PDF content for testing.

    Returns:
        bytes: Sample PDF file content
    """
    return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n178\n%%EOF"


@pytest.fixture
def sample_protocol_chunks():
    """
    Sample protocol text chunks for testing.

    Returns:
        list[str]: List of text chunks
    """
    return [
        "PROTOCOL TITLE: Test Clinical Trial for New Drug",
        "STUDY OBJECTIVES: To evaluate the safety and efficacy of the new drug",
        "INCLUSION CRITERIA: Patients aged 18-65 with diagnosed condition",
        "EXCLUSION CRITERIA: Pregnant women, patients with severe comorbidities",
        "PROCEDURES: Patients will receive study drug for 12 weeks",
        "RISKS: Potential side effects include nausea, headache, fatigue",
        "BENEFITS: Potential improvement in symptoms and quality of life",
    ]


@pytest.fixture
def test_client_with_mocks(
    mock_qdrant_client, mock_openai_client, mock_langgraph_workflow
):
    """
    Create a test client with all AI services mocked.

    Args:
        mock_qdrant_client: Mocked Qdrant client
        mock_openai_client: Mocked OpenAI client
        mock_langgraph_workflow: Mocked LangGraph workflow

    Returns:
        TestClient: FastAPI test client with mocked dependencies
    """
    with (
        patch(
            "app.services.qdrant_service.get_qdrant_client",
            return_value=mock_qdrant_client,
        ),
        patch(
            "app.services.embedding_service.get_openai_client",
            return_value=mock_openai_client,
        ),
        patch(
            "app.services.document_generator.get_langgraph_workflow",
            return_value=mock_langgraph_workflow,
        ),
    ):
        return TestClient(app)


@pytest.fixture
def frozen_time():
    """
    Freeze time for consistent timestamp testing.

    Yields:
        datetime: Frozen datetime
    """
    frozen_datetime = datetime(2024, 12, 15, 12, 0, 0)
    with freeze_time(frozen_datetime):
        yield frozen_datetime


@pytest.fixture
def temp_upload_dir():
    """
    Create temporary upload directory for testing.

    Yields:
        Path: Temporary upload directory path
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        upload_path = Path(temp_dir) / "uploads"
        upload_path.mkdir()
        yield upload_path


# Test data factories
@pytest.fixture
def sample_protocol_metadata():
    """Create sample protocol metadata."""
    return ProtocolMetadataFactory()


@pytest.fixture
def multiple_protocols_metadata():
    """Create multiple protocol metadata instances."""
    return [ProtocolMetadataFactory() for _ in range(3)]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers for new architecture."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "ai_service: mark test as AI service test")
    config.addinivalue_line("markers", "qdrant: mark test as Qdrant-related test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
