"""
Pytest configuration and fixtures for Clinical Trial Accelerator tests.

This module provides shared fixtures for testing including:
- In-memory Qdrant setup
- Test client configuration
- Data factories for test data generation
- Qdrant-only test infrastructure (migrated from SQLite)
"""

import uuid
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from factory import Factory, Faker, LazyAttribute
from fastapi.testclient import TestClient
from freezegun import freeze_time
from qdrant_client import QdrantClient

from app.main import app
from app.models import ProtocolCreate, ProtocolInDB
from app.services.qdrant_service import QdrantService


class ProtocolCreateFactory(Factory):
    """Factory for creating ProtocolCreate test instances."""

    class Meta:
        model = ProtocolCreate

    study_acronym = Faker("lexify", text="STUDY-???")
    protocol_title = Faker("sentence", nb_words=6)
    file_path = LazyAttribute(lambda obj: f"/uploads/{obj.study_acronym.lower()}.pdf")


class ProtocolInDBFactory(Factory):
    """Factory for creating ProtocolInDB test instances."""

    class Meta:
        model = ProtocolInDB

    protocol_id = LazyAttribute(lambda obj: f"proto_{int(datetime.now().timestamp())}")
    study_acronym = Faker("lexify", text="STUDY-???")
    protocol_title = Faker("sentence", nb_words=6)
    collection_name = LazyAttribute(
        lambda obj: f"{obj.study_acronym.lower()}_20241201_120000"
    )
    upload_date = LazyAttribute(lambda obj: datetime.now().isoformat())
    status = "processing"
    file_path = LazyAttribute(lambda obj: f"/uploads/{obj.study_acronym.lower()}.pdf")
    created_at = LazyAttribute(lambda obj: datetime.now().isoformat())


@pytest.fixture
def qdrant_client() -> QdrantClient:
    """
    Create an in-memory Qdrant client for testing.

    Returns:
        QdrantClient: In-memory Qdrant client instance
    """
    return QdrantClient(":memory:")


@pytest.fixture
def qdrant_service(qdrant_client: QdrantClient) -> QdrantService:
    """
    Create a Qdrant service with in-memory client for testing.

    Args:
        qdrant_client: In-memory Qdrant client

    Returns:
        QdrantService: Service instance for testing
    """
    return QdrantService(client=qdrant_client)


@pytest.fixture
def sample_protocol_data() -> dict:
    """
    Sample protocol data for testing.

    Returns:
        dict: Protocol data dictionary
    """
    return {
        "study_acronym": "TEST-001",
        "protocol_title": "Test Protocol for Unit Testing",
        "file_path": "/test/protocol.pdf",
    }


@pytest.fixture
def test_client() -> TestClient:
    """
    Create a test client for FastAPI application.

    Returns:
        TestClient: FastAPI test client
    """
    # Patch the Qdrant service to use in-memory client with proper mock configuration
    with patch("app.api.protocols.qdrant_service") as mock_service:
        # Storage for created protocols to maintain consistency
        # Reset for each test to ensure clean state
        created_protocols = {}

        # Protocol creation methods with unique collection names
        import time

        def create_protocol_collection(study_acronym, protocol_title, file_path=None):
            timestamp = int(time.time() * 1000)  # More precise timestamp
            collection_name = f"{study_acronym.lower()}_{timestamp}"

            # Store basic protocol metadata for API tests
            protocol_id = f"proto_{timestamp}"
            protocol_metadata = {
                "protocol_id": protocol_id,
                "study_acronym": study_acronym,
                "protocol_title": protocol_title,
                "collection_name": collection_name,
                "upload_date": f"{timestamp}",
                "file_path": file_path,
                "created_at": f"{timestamp}",
            }
            created_protocols[protocol_id] = protocol_metadata

            return collection_name

        mock_service.create_protocol_collection.side_effect = create_protocol_collection

        # Protocol retrieval methods with dynamic responses
        def get_protocol_by_id(protocol_id):
            if protocol_id in created_protocols:
                return created_protocols[protocol_id]
            # Return None if not found
            return None

        def get_protocol_by_collection(collection_name):
            for protocol_data in created_protocols.values():
                if protocol_data.get("collection_name") == collection_name:
                    return protocol_data
            # Return None if not found
            return None

        mock_service.get_protocol_by_id.side_effect = get_protocol_by_id
        mock_service.get_protocol_by_collection.side_effect = get_protocol_by_collection
        mock_service.get_protocol.side_effect = get_protocol_by_id

        # Protocol listing methods
        def list_all_protocols():
            # Return protocols sorted by upload_date DESC (most recent first)
            protocols = list(created_protocols.values())
            return sorted(
                protocols, key=lambda p: p.get("upload_date", ""), reverse=True
            )

        mock_service.list_all_protocols.side_effect = list_all_protocols
        mock_service.list_protocols.return_value = []
        mock_service.search_protocols.return_value = []

        # Protocol update/delete methods
        def update_protocol_status(collection_name, new_status):
            for protocol_id, protocol_data in created_protocols.items():
                if protocol_data.get("collection_name") == collection_name:
                    protocol_data["status"] = new_status
                    return True
            return False

        mock_service.update_protocol_status.side_effect = update_protocol_status
        mock_service.update_protocol.return_value = True

        yield TestClient(app)


@pytest.fixture
def sample_protocol_create() -> ProtocolCreate:
    """
    Create a sample ProtocolCreate instance for testing.

    Returns:
        ProtocolCreate: Sample protocol data
    """
    return ProtocolCreateFactory()


@pytest.fixture
def sample_protocol_create_data() -> dict:
    """
    Create sample protocol data as dictionary.

    Returns:
        dict: Sample protocol data
    """
    protocol = ProtocolCreateFactory()
    return {
        "study_acronym": protocol.study_acronym,
        "protocol_title": protocol.protocol_title,
        "file_path": protocol.file_path,
    }


@pytest.fixture
def multiple_protocols_data() -> list[dict]:
    """
    Create multiple protocol data instances for testing.

    Returns:
        list[dict]: List of protocol data dictionaries
    """
    return [
        {
            "study_acronym": "STUDY-001",
            "protocol_title": "First Clinical Trial Protocol",
            "file_path": "/uploads/study-001.pdf",
        },
        {
            "study_acronym": "STUDY-002",
            "protocol_title": "Second Clinical Trial Protocol",
            "file_path": "/uploads/study-002.pdf",
        },
        {
            "study_acronym": "STUDY-003",
            "protocol_title": "Third Clinical Trial Protocol",
            "file_path": "/uploads/study-003.pdf",
        },
    ]


@pytest.fixture
def frozen_time():
    """
    Freeze time for consistent timestamp testing.

    Yields:
        datetime: Frozen datetime
    """
    frozen_datetime = datetime(2024, 12, 1, 12, 0, 0)
    with freeze_time(frozen_datetime):
        yield frozen_datetime


@pytest.fixture
def mock_logger():
    """
    Mock logger for testing log messages.

    Yields:
        Mock: Mocked logger
    """
    with patch("app.services.qdrant_service.logger") as mock_log:
        yield mock_log


# Qdrant fixtures for new architecture tests
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
    from qdrant_client.models import Distance, VectorParams

    client = QdrantClient(":memory:")
    # No longer create a protocols collection - using individual collections now
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
def sample_protocol_metadata():
    """Create sample protocol metadata."""
    return ProtocolMetadataFactory()


@pytest.fixture
def multiple_protocols_metadata():
    """Create multiple protocol metadata instances."""
    return [ProtocolMetadataFactory() for _ in range(3)]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "ai_service: mark test as AI service test")
    config.addinivalue_line("markers", "qdrant: mark test as Qdrant-related test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
