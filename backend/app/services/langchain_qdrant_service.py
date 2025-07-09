"""
LangChain-based Qdrant service for vector operations.

This module provides a LangChain-integrated approach to Qdrant operations:
- Uses QdrantVectorStore for document storage and retrieval
- Implements LangChain retriever patterns for RAG operations
- Maintains raw client access for collection management
- Provides unified interface for document operations
"""

import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Load environment variables for local development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)


class LangChainQdrantError(Exception):
    """Exception raised for LangChain Qdrant-related errors."""

    pass


class LangChainQdrantService:
    """Service class for LangChain-integrated Qdrant operations."""

    def __init__(
        self,
        client: Optional[QdrantClient] = None,
        embeddings: Optional[OpenAIEmbeddings] = None,
    ):
        """Initialize LangChain Qdrant service with appropriate clients."""
        # Initialize raw Qdrant client for collection management
        if client:
            self.client = client
        else:
            qdrant_url = os.getenv("QDRANT_URL")
            qdrant_api_key = os.getenv("QDRANT_API_KEY")

            logger.info(
                f"Environment check - QDRANT_URL: {'SET' if qdrant_url else 'NOT SET'}"
            )
            logger.info(
                f"Environment check - QDRANT_API_KEY: {'SET' if qdrant_api_key else 'NOT SET'}"
            )

            if qdrant_url:
                if qdrant_api_key:
                    self.client = QdrantClient(
                        url=qdrant_url, api_key=qdrant_api_key, timeout=60
                    )
                    logger.info(f"Connected to Qdrant Cloud at {qdrant_url}")
                else:
                    self.client = QdrantClient(url=qdrant_url)
                    logger.info(f"Connected to local Qdrant at {qdrant_url}")
            else:
                self.client = QdrantClient(":memory:")
                logger.warning("Using in-memory Qdrant - data will not persist")

        # Initialize OpenAI embeddings
        if embeddings:
            self.embeddings = embeddings
        else:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                embedding_model = os.getenv(
                    "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
                )
                self.embeddings = OpenAIEmbeddings(
                    model=embedding_model,
                    openai_api_key=openai_api_key,
                )
                logger.info(
                    f"OpenAI embeddings initialized successfully with model: {embedding_model}"
                )
            else:
                self.embeddings = None
                logger.warning("OpenAI API key not found - embeddings will not work")

    def generate_collection_name(self, study_acronym: str) -> str:
        """Generate unique collection name for protocol using acronym + 8-char UUID."""
        # Clean acronym to only include alphanumeric characters
        clean_acronym = "".join(c for c in study_acronym if c.isalnum()).upper()

        # Generate 8-character UUID
        uuid_str = str(uuid.uuid4()).replace("-", "")[:8].lower()

        # Format: ACRONYM-8charuuid (e.g., THAPCA-08ndfes)
        return f"{clean_acronym}-{uuid_str}"

    def get_vector_store(self, collection_name: str) -> QdrantVectorStore:
        """Get LangChain QdrantVectorStore for a specific collection."""
        if not self.embeddings:
            raise LangChainQdrantError("Embeddings not initialized")

        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.embeddings,
        )

    def store_documents(
        self,
        documents: List[Document],
        study_acronym: str,
        ids: Optional[List[str]] = None,
    ) -> tuple[List[str], str]:
        """Store documents in a Qdrant collection using LangChain."""
        try:
            # Generate collection name
            collection_name = self.generate_collection_name(study_acronym)
            logger.info(
                f"Generated collection name: {collection_name} for study: {study_acronym}"
            )

            # Use from_documents to create collection and store documents
            logger.info(
                f"Creating collection and storing {len(documents)} documents with embeddings model: {self.embeddings}"
            )
            vector_store = QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )

            # Get the document IDs (they're auto-generated by from_documents)
            doc_ids = [
                str(i) for i in range(len(documents))
            ]  # from_documents doesn't return IDs
            logger.info(
                f"Created collection and stored {len(documents)} documents in {collection_name}"
            )

            return doc_ids, collection_name
        except Exception as e:
            logger.error(f"Error storing documents in {collection_name}: {e}")
            raise LangChainQdrantError(f"Failed to store documents: {str(e)}")

    def get_retriever(
        self,
        collection_name: str,
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,
    ) -> BaseRetriever:
        """Get a LangChain retriever for a specific collection."""
        try:
            vector_store = self.get_vector_store(collection_name)

            if search_kwargs is None:
                search_kwargs = {"k": 5}

            return vector_store.as_retriever(
                search_type=search_type,
                search_kwargs=search_kwargs,
            )
        except Exception as e:
            logger.error(f"Error creating retriever for {collection_name}: {e}")
            raise LangChainQdrantError(f"Failed to create retriever: {str(e)}")

    def similarity_search(
        self,
        collection_name: str,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Document]:
        """Perform similarity search using LangChain."""
        try:
            vector_store = self.get_vector_store(collection_name)

            if score_threshold is not None:
                return vector_store.similarity_search_with_score_threshold(
                    query, k=k, score_threshold=score_threshold
                )
            else:
                return vector_store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error in similarity search for {collection_name}: {e}")
            raise LangChainQdrantError(f"Failed to perform similarity search: {str(e)}")

    def similarity_search_with_score(
        self,
        collection_name: str,
        query: str,
        k: int = 5,
    ) -> List[tuple[Document, float]]:
        """Perform similarity search with scores using LangChain."""
        try:
            vector_store = self.get_vector_store(collection_name)
            results = vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(
                f"Error in similarity search with score for {collection_name}: {e}"
            )
            raise LangChainQdrantError(
                f"Failed to perform similarity search with score: {str(e)}"
            )

    def list_collections(self) -> List[str]:
        """List all collections using raw Qdrant client."""
        try:
            collections = self.client.get_collections()
            return [col.name for col in collections.collections]
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            raise LangChainQdrantError(f"Failed to list collections: {str(e)}")

    def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection using raw Qdrant client."""
        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a collection."""
        try:
            collection_info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status,
            }
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            return None

    def test_connection(self) -> bool:
        """Test Qdrant connection."""
        try:
            collections = self.client.get_collections()
            logger.info(
                f"Connection test successful - found {len(collections.collections)} collections"
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def get_langchain_qdrant_service() -> LangChainQdrantService:
    """Get configured LangChain Qdrant service instance."""
    return LangChainQdrantService()
