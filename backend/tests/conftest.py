"""
Pytest configuration and fixtures for Clinical Trial Accelerator tests.

This module provides shared fixtures for testing including:
- In-memory database setup
- Test client configuration
- Data factories for test data generation
"""

import pytest
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import patch

from fastapi.testclient import TestClient
from factory import Factory, Faker, LazyAttribute
from freezegun import freeze_time

from app.main import app
from app.database import get_db_connection, init_database, DATABASE_PATH
from app.models import ProtocolCreate, ProtocolInDB


class ProtocolCreateFactory(Factory):
    """Factory for creating ProtocolCreate test instances."""
    
    class Meta:
        model = ProtocolCreate
    
    study_acronym = Faker('lexify', text='STUDY-???')
    protocol_title = Faker('sentence', nb_words=6)
    file_path = LazyAttribute(lambda obj: f"/uploads/{obj.study_acronym.lower()}.pdf")


class ProtocolInDBFactory(Factory):
    """Factory for creating ProtocolInDB test instances."""
    
    class Meta:
        model = ProtocolInDB
    
    id = Faker('random_int', min=1, max=1000)
    study_acronym = Faker('lexify', text='STUDY-???')
    protocol_title = Faker('sentence', nb_words=6)
    collection_name = LazyAttribute(lambda obj: f"{obj.study_acronym.lower()}_20241201_120000")
    upload_date = Faker('date_time')
    status = "processing"
    file_path = LazyAttribute(lambda obj: f"/uploads/{obj.study_acronym.lower()}.pdf")
    created_at = Faker('date_time')


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """
    Create a temporary database file for testing.
    
    Yields:
        Path: Path to temporary database file
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def mock_database_path(temp_db_path: Path):
    """
    Mock the DATABASE_PATH to use temporary database.
    
    Args:
        temp_db_path: Path to temporary database file
    """
    with patch('app.database.DATABASE_PATH', temp_db_path):
        yield temp_db_path


@pytest.fixture
def init_test_db(mock_database_path: Path):
    """
    Initialize test database with schema.
    
    Args:
        mock_database_path: Path to test database
    """
    init_database()
    yield
    # Database cleanup handled by temp_db_path fixture


@pytest.fixture
def db_connection(init_test_db, mock_database_path: Path):
    """
    Provide a database connection for testing.
    
    Args:
        init_test_db: Initialized test database
        mock_database_path: Path to test database
        
    Yields:
        sqlite3.Connection: Database connection
    """
    conn = sqlite3.connect(mock_database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    yield conn
    
    conn.close()


@pytest.fixture
def test_client(init_test_db) -> TestClient:
    """
    Create a test client for FastAPI application.
    
    Args:
        init_test_db: Initialized test database
        
    Returns:
        TestClient: FastAPI test client
    """
    return TestClient(app)


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
        "file_path": protocol.file_path
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
            "file_path": "/uploads/study-001.pdf"
        },
        {
            "study_acronym": "STUDY-002", 
            "protocol_title": "Second Clinical Trial Protocol",
            "file_path": "/uploads/study-002.pdf"
        },
        {
            "study_acronym": "STUDY-003",
            "protocol_title": "Third Clinical Trial Protocol", 
            "file_path": "/uploads/study-003.pdf"
        }
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
    with patch('app.database.logger') as mock_log:
        yield mock_log


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    ) 