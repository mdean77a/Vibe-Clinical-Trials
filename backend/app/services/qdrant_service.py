"""
Qdrant service for protocol metadata and collection management.

This service provides low-level Qdrant operations for protocol management:
- Protocol collection creation and deletion
- Protocol metadata retrieval and listing
- Collection name generation
- Direct Qdrant client operations

NOTE: For document storage and RAG operations, use langchain_qdrant_service.py
which provides LangChain-integrated document chunking, embedding, and retrieval.
"""

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from ..config import EMBEDDING_DIMENSION

# Load environment variables for local development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available (e.g., in production), skip loading
    pass

logger = logging.getLogger(__name__)


class QdrantError(Exception):
    """Exception raised for Qdrant-related errors."""

    pass


class QdrantService:
    """Service class for Qdrant operations - handles all protocol metadata and vector operations."""

    def __init__(
        self,
        client: Optional[QdrantClient] = None,
    ):
        """Initialize Qdrant service with appropriate client for environment."""
        if client:
            self.client = client
        else:
            # Use environment variables for Qdrant configuration
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")

            # Debug logging
            logger.info(
                f"Environment check - QDRANT_URL: {'SET' if qdrant_url else 'NOT SET'}"
            )
            logger.info(
                f"Environment check - QDRANT_API_KEY: {'SET' if qdrant_api_key else 'NOT SET'}"
            )

            if qdrant_url:
                if qdrant_api_key:
                    # Qdrant Cloud with API key
                    self.client = QdrantClient(
                        url=qdrant_url, api_key=qdrant_api_key, timeout=60
                    )
                    logger.info(f"Connected to Qdrant Cloud at {qdrant_url}")
                else:
                    # Local Qdrant server without API key
                    self.client = QdrantClient(url=qdrant_url)
                    logger.info(f"Connected to local Qdrant at {qdrant_url}")
            else:
                # Fallback to memory for testing
                self.client = QdrantClient(":memory:")
                logger.warning("Using in-memory Qdrant - data will not persist")

        # No need to ensure protocols collection - we'll use collection listing instead

    def generate_collection_name(self, study_acronym: str) -> str:
        """Generate unique collection name for protocol using acronym + 8-char UUID."""
        # Clean acronym to only include alphanumeric characters
        clean_acronym = "".join(c for c in study_acronym if c.isalnum()).upper()

        # Generate 8-character UUID
        uuid_str = str(uuid.uuid4()).replace("-", "")[:8].lower()

        # Format: ACRONYM-8charuuid (e.g., THAPCA-08ndfes)
        return f"{clean_acronym}-{uuid_str}"

    def create_protocol_collection(
        self, study_acronym: str, protocol_title: str, file_path: Optional[str] = None
    ) -> str:
        """Create a new collection for a protocol's vector embeddings.

        Args:
            study_acronym: The study acronym for the protocol
            protocol_title: The title of the protocol (kept for backward compatibility)
            file_path: Optional file path (kept for backward compatibility)

        Returns:
            str: The generated collection name
        """
        collection_name = self.generate_collection_name(study_acronym)

        try:
            # Actually create the individual collection for this protocol
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION, distance=Distance.COSINE
                ),
            )
            logger.info(f"Created protocol collection: {collection_name}")
            return collection_name
        except Exception as e:
            raise QdrantError(f"Failed to create protocol collection: {str(e)}")

    def list_all_protocols(self) -> List[dict]:
        """List all protocols by querying Qdrant collections and extracting metadata."""
        try:
            # Test connection first
            if not self.test_connection():
                raise QdrantError("Cannot connect to Qdrant database")

            # Get all collections from Qdrant
            collections = self.client.get_collections()
            protocols = []

            logger.info(f"Found {len(collections.collections)} total collections")

            for collection_info in collections.collections:
                collection_name = collection_info.name

                # Skip non-protocol collections (protocol collections have format: ACRONYM-8chars)
                if not self._is_protocol_collection(collection_name):
                    logger.debug(f"Skipping non-protocol collection: {collection_name}")
                    continue

                # Get metadata from the first point in the collection
                try:
                    result = self.client.scroll(
                        collection_name=collection_name, limit=1, with_payload=True
                    )

                    points, _ = result
                    if points:
                        payload = points[0].payload

                        # Get collection info for chunk count
                        collection_info_detail = self.client.get_collection(
                            collection_name
                        )
                        point_count = collection_info_detail.points_count

                        # Handle different payload structures (LangChain vs raw Qdrant)
                        if payload and "metadata" in payload:
                            # LangChain structure: metadata is nested
                            metadata = payload["metadata"]
                        else:
                            # Raw Qdrant structure: metadata is at top level
                            metadata = payload or {}

                        protocol_data = {
                            "protocol_id": metadata.get("protocol_id"),
                            "study_acronym": metadata.get("study_acronym"),
                            "protocol_title": metadata.get("protocol_title"),
                            "collection_name": collection_name,
                            "upload_date": metadata.get("upload_date"),
                            "file_path": metadata.get("file_path"),
                            "created_at": metadata.get("created_at")
                            or metadata.get("upload_date")
                            or datetime.now(timezone.utc).isoformat(),
                            "chunk_count": point_count,
                        }

                        protocols.append(protocol_data)
                        logger.debug(
                            f"Added protocol: {metadata.get('study_acronym', 'UNKNOWN')}"
                        )

                    else:
                        logger.warning(f"Collection {collection_name} has no points")

                except Exception as collection_error:
                    logger.warning(
                        f"Could not read metadata from collection {collection_name}: {collection_error}"
                    )
                    continue

            # Sort protocols by upload_date (newest first)
            # Use created_at as fallback if upload_date is missing
            protocols.sort(
                key=lambda p: p.get("upload_date")
                or p.get("created_at")
                or "1970-01-01",
                reverse=True,
            )

            logger.info(f"Successfully retrieved {len(protocols)} protocols")
            return protocols

        except Exception as e:
            logger.error(f"Error listing protocols: {e}")
            raise QdrantError(f"Failed to list protocols: {str(e)}")

    def _is_protocol_collection(self, collection_name: str) -> bool:
        """Check if a collection name matches our protocol naming pattern (ACRONYM-8chars)."""
        import re

        # Pattern: one or more alphanumeric chars, dash, exactly 8 alphanumeric chars
        pattern = r"^[A-Z0-9]+-[a-z0-9]{8}$"
        return bool(re.match(pattern, collection_name))

    def get_protocol_by_collection(self, collection_name: str) -> Optional[dict]:
        """Get protocol metadata from collection by reading first point."""
        try:
            result = self.client.scroll(
                collection_name=collection_name, limit=1, with_payload=True
            )

            points, _ = result
            if points:
                payload = points[0].payload

                # Get collection info for chunk count
                collection_info = self.client.get_collection(collection_name)

                # Handle different payload structures (LangChain vs raw Qdrant)
                if payload and "metadata" in payload:
                    # LangChain structure: metadata is nested
                    metadata = payload["metadata"]
                else:
                    # Raw Qdrant structure: metadata is at top level
                    metadata = payload or {}

                return {
                    "protocol_id": metadata.get("protocol_id"),
                    "study_acronym": metadata.get("study_acronym"),
                    "protocol_title": metadata.get("protocol_title"),
                    "collection_name": collection_name,
                    "upload_date": metadata.get("upload_date"),
                    "file_path": metadata.get("file_path"),
                    "created_at": metadata.get("created_at")
                    or metadata.get("upload_date")
                    or datetime.now(timezone.utc).isoformat(),
                    "chunk_count": collection_info.points_count,
                }
            return None

        except Exception as e:
            logger.error(
                f"Error retrieving protocol from collection {collection_name}: {e}"
            )
            return None

    def get_protocol_by_id(self, protocol_id: str) -> Optional[dict]:
        """Get protocol by protocol ID by searching across all protocol collections."""
        try:
            protocols = self.list_all_protocols()
            for protocol in protocols:
                if protocol.get("protocol_id") == protocol_id:
                    return protocol
            return None

        except Exception as e:
            logger.error(f"Error retrieving protocol {protocol_id}: {e}")
            return None

    def get_collection_name_for_protocol(self, protocol_id: str) -> Optional[str]:
        """Get the collection name for a specific protocol ID - useful for retrieval."""
        try:
            protocol = self.get_protocol_by_id(protocol_id)
            return protocol.get("collection_name") if protocol else None
        except Exception as e:
            logger.error(
                f"Error getting collection name for protocol {protocol_id}: {e}"
            )
            return None

    # update_protocol_status method removed - protocols in Qdrant are always active

    def delete_protocol(self, collection_name: str) -> bool:
        """Delete an entire protocol collection."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted protocol collection {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False

    def create_collection(self, collection_name: str) -> bool:
        """Create a new Qdrant collection."""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION, distance=Distance.COSINE
                ),
            )
            return True
        except Exception as e:
            raise QdrantError(f"Failed to create collection: {str(e)}")

    def test_connection(self) -> bool:
        """Test Qdrant connection and log results."""
        try:
            collections = self.client.get_collections()
            logger.info(
                f"Connection test successful - found {len(collections.collections)} collections"
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance - using in-memory for migration."""
    return QdrantClient(":memory:")


def get_qdrant_service() -> QdrantService:
    """Get configured Qdrant service instance."""
    return QdrantService()
