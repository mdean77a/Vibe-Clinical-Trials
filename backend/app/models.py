"""
Pydantic models for Clinical Trial Accelerator.

This module defines the data models used throughout the application,
including Protocol models for database operations and API responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProtocolBase(BaseModel):
    """Base protocol model with common fields."""

    study_acronym: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Study acronym (e.g., 'STUDY-123')",
    )
    protocol_title: str = Field(
        ..., min_length=1, max_length=500, description="Full protocol title"
    )

    @field_validator("study_acronym")
    @classmethod
    def validate_study_acronym(cls, v: str) -> str:
        """Validate study acronym format."""
        if not v.strip():
            raise ValueError("Study acronym cannot be empty or whitespace")
        return v.strip().upper()

    @field_validator("protocol_title")
    @classmethod
    def validate_protocol_title(cls, v: str) -> str:
        """Validate protocol title."""
        if not v.strip():
            raise ValueError("Protocol title cannot be empty or whitespace")
        return v.strip()


class ProtocolCreate(ProtocolBase):
    """Model for creating a new protocol."""

    file_path: Optional[str] = Field(
        None, description="Path to the uploaded protocol PDF file"
    )


class ProtocolInDB(ProtocolBase):
    """Model representing a protocol as stored in Qdrant."""

    protocol_id: str = Field(..., description="Unique protocol identifier")
    collection_name: str = Field(
        ...,
        min_length=1,
        description="Unique collection name for Qdrant vector storage",
    )
    upload_date: str = Field(
        ..., description="ISO timestamp when protocol was uploaded"
    )
    file_path: Optional[str] = Field(
        None, description="Path to the uploaded protocol PDF file"
    )
    created_at: str = Field(..., description="ISO timestamp when record was created")

    model_config = ConfigDict(from_attributes=True)


class ProtocolResponse(ProtocolInDB):
    """Model for protocol API responses."""

    pass


# ProtocolUpdate model removed - status updates no longer needed
# since protocols in Qdrant are always active by definition
