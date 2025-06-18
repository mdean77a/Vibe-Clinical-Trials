"""
Unit tests for Pydantic models.

This module tests all Pydantic model validation, serialization,
and business logic including edge cases and error scenarios.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import (
    ProtocolBase,
    ProtocolCreate,
    ProtocolInDB,
    ProtocolResponse,
    ProtocolUpdate,
)


class TestProtocolBase:
    """Test cases for ProtocolBase model."""

    @pytest.mark.unit
    def test_valid_protocol_base(self):
        """Test creating a valid ProtocolBase instance."""
        protocol = ProtocolBase(
            study_acronym="STUDY-123", protocol_title="Test Clinical Trial Protocol"
        )

        assert protocol.study_acronym == "STUDY-123"
        assert protocol.protocol_title == "Test Clinical Trial Protocol"

    @pytest.mark.unit
    def test_study_acronym_validation_strips_whitespace(self):
        """Test that study acronym validation strips whitespace."""
        protocol = ProtocolBase(
            study_acronym="  study-123  ", protocol_title="Test Protocol"
        )

        assert protocol.study_acronym == "STUDY-123"

    @pytest.mark.unit
    def test_study_acronym_validation_converts_to_uppercase(self):
        """Test that study acronym is converted to uppercase."""
        protocol = ProtocolBase(
            study_acronym="study-123", protocol_title="Test Protocol"
        )

        assert protocol.study_acronym == "STUDY-123"

    @pytest.mark.unit
    def test_protocol_title_validation_strips_whitespace(self):
        """Test that protocol title validation strips whitespace."""
        protocol = ProtocolBase(
            study_acronym="STUDY-123", protocol_title="  Test Protocol  "
        )

        assert protocol.protocol_title == "Test Protocol"

    @pytest.mark.unit
    def test_empty_study_acronym_raises_validation_error(self):
        """Test that empty study acronym raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolBase(study_acronym="", protocol_title="Test Protocol")

        assert "String should have at least 1 character" in str(exc_info.value)

    @pytest.mark.unit
    def test_whitespace_only_study_acronym_raises_validation_error(self):
        """Test that whitespace-only study acronym raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolBase(study_acronym="   ", protocol_title="Test Protocol")

        assert "Study acronym cannot be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_empty_protocol_title_raises_validation_error(self):
        """Test that empty protocol title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolBase(study_acronym="STUDY-123", protocol_title="")

        assert "String should have at least 1 character" in str(exc_info.value)

    @pytest.mark.unit
    def test_whitespace_only_protocol_title_raises_validation_error(self):
        """Test that whitespace-only protocol title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolBase(study_acronym="STUDY-123", protocol_title="   ")

        assert "Protocol title cannot be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_study_acronym_too_long_raises_validation_error(self):
        """Test that study acronym longer than 50 chars raises ValidationError."""
        long_acronym = "A" * 51

        with pytest.raises(ValidationError) as exc_info:
            ProtocolBase(study_acronym=long_acronym, protocol_title="Test Protocol")

        assert "String should have at most 50 characters" in str(exc_info.value)

    @pytest.mark.unit
    def test_protocol_title_too_long_raises_validation_error(self):
        """Test that protocol title longer than 500 chars raises ValidationError."""
        long_title = "A" * 501

        with pytest.raises(ValidationError) as exc_info:
            ProtocolBase(study_acronym="STUDY-123", protocol_title=long_title)

        assert "String should have at most 500 characters" in str(exc_info.value)


class TestProtocolCreate:
    """Test cases for ProtocolCreate model."""

    @pytest.mark.unit
    def test_valid_protocol_create_with_file_path(self):
        """Test creating a valid ProtocolCreate with file path."""
        protocol = ProtocolCreate(
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            file_path="/uploads/test.pdf",
        )

        assert protocol.study_acronym == "STUDY-123"
        assert protocol.protocol_title == "Test Protocol"
        assert protocol.file_path == "/uploads/test.pdf"

    @pytest.mark.unit
    def test_valid_protocol_create_without_file_path(self):
        """Test creating a valid ProtocolCreate without file path."""
        protocol = ProtocolCreate(
            study_acronym="STUDY-123", protocol_title="Test Protocol"
        )

        assert protocol.study_acronym == "STUDY-123"
        assert protocol.protocol_title == "Test Protocol"
        assert protocol.file_path is None

    @pytest.mark.unit
    def test_protocol_create_inherits_base_validation(self):
        """Test that ProtocolCreate inherits validation from ProtocolBase."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolCreate(study_acronym="", protocol_title="Test Protocol")

        assert "String should have at least 1 character" in str(exc_info.value)


class TestProtocolInDB:
    """Test cases for ProtocolInDB model."""

    @pytest.mark.unit
    def test_valid_protocol_in_db(self):
        """Test creating a valid ProtocolInDB instance."""
        now = datetime.now().isoformat()
        protocol = ProtocolInDB(
            protocol_id="proto_123",
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            collection_name="study_123_20241201_120000",
            upload_date=now,
            status="processing",
            file_path="/uploads/test.pdf",
            created_at=now,
        )

        assert protocol.protocol_id == "proto_123"
        assert protocol.study_acronym == "STUDY-123"
        assert protocol.protocol_title == "Test Protocol"
        assert protocol.collection_name == "study_123_20241201_120000"
        assert protocol.upload_date == now
        assert protocol.status == "processing"
        assert protocol.file_path == "/uploads/test.pdf"
        assert protocol.created_at == now

    @pytest.mark.unit
    def test_protocol_in_db_with_default_status(self):
        """Test ProtocolInDB with default status."""
        now = datetime.now().isoformat()
        protocol = ProtocolInDB(
            protocol_id="proto_123",
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            collection_name="study_123_20241201_120000",
            upload_date=now,
            created_at=now,
        )

        assert protocol.status == "processing"

    @pytest.mark.unit
    def test_protocol_in_db_without_file_path(self):
        """Test ProtocolInDB without file path."""
        now = datetime.now().isoformat()
        protocol = ProtocolInDB(
            protocol_id="proto_123",
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            collection_name="study_123_20241201_120000",
            upload_date=now,
            created_at=now,
        )

        assert protocol.file_path is None

    @pytest.mark.unit
    def test_empty_collection_name_raises_validation_error(self):
        """Test that empty collection name raises ValidationError."""
        now = datetime.now().isoformat()

        with pytest.raises(ValidationError) as exc_info:
            ProtocolInDB(
                protocol_id="proto_123",
                study_acronym="STUDY-123",
                protocol_title="Test Protocol",
                collection_name="",
                upload_date=now,
                created_at=now,
            )

        assert "String should have at least 1 character" in str(exc_info.value)


class TestProtocolResponse:
    """Test cases for ProtocolResponse model."""

    @pytest.mark.unit
    def test_protocol_response_inherits_from_protocol_in_db(self):
        """Test that ProtocolResponse inherits from ProtocolInDB."""
        now = datetime.now().isoformat()
        protocol = ProtocolResponse(
            protocol_id="proto_123",
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            collection_name="study_123_20241201_120000",
            upload_date=now,
            created_at=now,
        )

        assert isinstance(protocol, ProtocolInDB)
        assert protocol.protocol_id == "proto_123"
        assert protocol.study_acronym == "STUDY-123"


class TestProtocolUpdate:
    """Test cases for ProtocolUpdate model."""

    @pytest.mark.unit
    def test_valid_protocol_update_processing(self):
        """Test creating a valid ProtocolUpdate with processing status."""
        update = ProtocolUpdate(status="processing")
        assert update.status == "processing"

    @pytest.mark.unit
    def test_valid_protocol_update_processed(self):
        """Test creating a valid ProtocolUpdate with processed status."""
        update = ProtocolUpdate(status="processed")
        assert update.status == "processed"

    @pytest.mark.unit
    def test_valid_protocol_update_failed(self):
        """Test creating a valid ProtocolUpdate with failed status."""
        update = ProtocolUpdate(status="failed")
        assert update.status == "failed"

    @pytest.mark.unit
    def test_invalid_status_raises_validation_error(self):
        """Test that invalid status raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolUpdate(status="invalid_status")

        assert "Status must be one of" in str(exc_info.value)
        assert "processing" in str(exc_info.value)
        assert "processed" in str(exc_info.value)
        assert "failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_empty_status_raises_validation_error(self):
        """Test that empty status raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProtocolUpdate(status="")

        assert "Status must be one of" in str(exc_info.value)


class TestModelSerialization:
    """Test cases for model serialization and deserialization."""

    @pytest.mark.unit
    def test_protocol_create_to_dict(self):
        """Test ProtocolCreate serialization to dictionary."""
        protocol = ProtocolCreate(
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            file_path="/uploads/test.pdf",
        )

        data = protocol.model_dump()

        assert data["study_acronym"] == "STUDY-123"
        assert data["protocol_title"] == "Test Protocol"
        assert data["file_path"] == "/uploads/test.pdf"

    @pytest.mark.unit
    def test_protocol_create_from_dict(self):
        """Test ProtocolCreate deserialization from dictionary."""
        data = {
            "study_acronym": "study-123",
            "protocol_title": "  Test Protocol  ",
            "file_path": "/uploads/test.pdf",
        }

        protocol = ProtocolCreate(**data)

        assert protocol.study_acronym == "STUDY-123"
        assert protocol.protocol_title == "Test Protocol"
        assert protocol.file_path == "/uploads/test.pdf"

    @pytest.mark.unit
    def test_protocol_in_db_to_json(self):
        """Test ProtocolInDB serialization to JSON."""
        now = datetime(2024, 12, 1, 12, 0, 0).isoformat()
        protocol = ProtocolInDB(
            protocol_id="proto_123",
            study_acronym="STUDY-123",
            protocol_title="Test Protocol",
            collection_name="study_123_20241201_120000",
            upload_date=now,
            created_at=now,
        )

        json_data = protocol.model_dump_json()

        assert '"protocol_id":"proto_123"' in json_data
        assert '"study_acronym":"STUDY-123"' in json_data
        assert '"status":"processing"' in json_data
