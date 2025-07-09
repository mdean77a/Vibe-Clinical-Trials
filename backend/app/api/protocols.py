"""
FastAPI router for protocol management endpoints.

This module defines all HTTP endpoints for protocol operations including:
- Creating new protocols
- Retrieving protocols
- Updating protocol status
- Listing all protocols

Now using Qdrant-only architecture (migrated from SQLite).
"""

import logging
import os
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from ..models import ProtocolCreate, ProtocolResponse, ProtocolUpdate
from ..services.qdrant_service import QdrantError, get_qdrant_service

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/protocols", tags=["protocols"])

# Initialize services
qdrant_service = get_qdrant_service()


def extract_and_chunk_pdf(pdf_content: bytes, filename: str) -> List[str]:
    """
    Extract text from PDF using PyMuPDF and chunk using RecursiveCharacterTextSplitter.

    Standard protocol upload and processing endpoint.

    Args:
        pdf_content: Raw PDF bytes
        filename: Original filename for logging

    Returns:
        List of text chunks ready for embedding
    """
    pdf_document = None
    try:
        import fitz  # PyMuPDF
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        page_count = pdf_document.page_count

        # Extract text from all pages
        full_text = ""
        for page_num in range(page_count):
            page = pdf_document[page_num]
            page_text = page.get_text()
            full_text += f"\n\n--- Page {page_num + 1} ---\n\n"
            full_text += page_text

        # Close document after text extraction is complete
        pdf_document.close()
        pdf_document = None  # Clear reference

        if not full_text.strip():
            raise ValueError("No text content extracted from PDF")

        # Chunk the text using RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Good size for clinical protocols
            chunk_overlap=200,  # Preserve context across chunks
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],  # Try semantic breaks first
        )

        chunks = text_splitter.split_text(full_text)

        # Filter out very short chunks
        meaningful_chunks = [
            chunk.strip() for chunk in chunks if len(chunk.strip()) > 50
        ]

        if not meaningful_chunks:
            # Fallback: return the full text as one chunk if splitting failed
            meaningful_chunks = [full_text.strip()]

        logger.info(
            f"PDF {filename}: extracted {len(meaningful_chunks)} chunks from {page_count} pages"
        )
        return meaningful_chunks

    except ImportError as e:
        logger.error(f"Missing dependencies for PDF processing: {e}")
        raise ValueError("PDF processing dependencies not available")
    except Exception as e:
        logger.error(f"PDF text extraction failed for {filename}: {e}")
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    finally:
        # Ensure document is closed even if an error occurs
        if pdf_document is not None:
            try:
                pdf_document.close()
            except:
                pass


@router.post("/", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_new_protocol(protocol: ProtocolCreate) -> ProtocolResponse:
    """
    Create a new protocol using Qdrant storage.

    Args:
        protocol: Protocol data to create

    Returns:
        ProtocolResponse: Created protocol with metadata

    Raises:
        HTTPException: 500 for creation errors
    """
    try:
        logger.info(f"Creating new protocol: {protocol.study_acronym}")

        # Create collection and get collection name
        collection_name = qdrant_service.create_protocol_collection(
            study_acronym=protocol.study_acronym,
            protocol_title=protocol.protocol_title,
            file_path=getattr(protocol, "file_path", None),
        )

        # Create protocol metadata
        protocol_metadata = {
            "protocol_id": f"proto_{int(time.time() * 1000)}",  # Use milliseconds for uniqueness
            "study_acronym": protocol.study_acronym,
            "protocol_title": protocol.protocol_title,
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "status": "processing",
            "file_path": getattr(protocol, "file_path", None),
            "created_at": datetime.now().isoformat(),
        }

        # Store initial metadata (will be updated when document is processed)
        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["Initial protocol entry"],
            embeddings=[[0.0] * 1536],  # Placeholder embedding
            protocol_metadata=protocol_metadata,
        )

        logger.info(f"Successfully created protocol with collection {collection_name}")
        return ProtocolResponse(**protocol_metadata)

    except QdrantError as e:
        logger.error(f"Qdrant error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create protocol",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post(
    "/upload", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED
)
async def upload_and_process_protocol(
    file: UploadFile = File(...),
    study_acronym: str = Form(...),
    protocol_title: str = Form(...),
) -> ProtocolResponse:
    """
    Upload and process a protocol PDF with full text extraction and embedding generation.

    Args:
        file: PDF file to upload
        study_acronym: Study acronym (e.g., 'STUDY-123')
        protocol_title: Full protocol title

    Returns:
        ProtocolResponse: Created protocol with processed content

    Raises:
        HTTPException: 400 for invalid files, 500 for processing errors
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported",
            )

        logger.info(f"Processing PDF upload: {file.filename} for study {study_acronym}")

        # Read file content
        pdf_content = await file.read()

        # Process PDF with PyMuPDF
        try:
            text_chunks = extract_and_chunk_pdf(pdf_content, file.filename)
            logger.info(
                f"PDF processed successfully: {len(text_chunks)} chunks extracted"
            )
        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process PDF: {str(e)}",
            )

        # Store protocol using LangChain integration
        try:
            from langchain_core.documents import Document

            from ..services.langchain_qdrant_service import get_langchain_qdrant_service

            # Initialize LangChain service
            langchain_service = get_langchain_qdrant_service()

            # Create protocol metadata (collection_name will be generated by LangChain)
            protocol_metadata = {
                "protocol_id": f"proto_{int(time.time() * 1000)}",
                "study_acronym": study_acronym,
                "protocol_title": protocol_title,
                "upload_date": datetime.now().isoformat(),
                "status": "processed",
                "file_path": file.filename,
                "created_at": datetime.now().isoformat(),
                "chunk_count": len(text_chunks),
                "processing_method": "pymupdf",
            }

            # Convert text chunks to LangChain Documents
            documents = []
            for i, chunk in enumerate(text_chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        **protocol_metadata,
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "embedding_model": "text-embedding-ada-002",
                        "processing_version": "1.0",
                        "last_updated": datetime.now().isoformat(),
                    },
                )
                documents.append(doc)

            # Store documents using LangChain (this will generate collection name)
            doc_ids, collection_name = langchain_service.store_documents(
                documents=documents,
                study_acronym=study_acronym,
            )

            # Add collection_name to protocol metadata after it's generated
            protocol_metadata["collection_name"] = collection_name

            logger.info(
                f"Stored {len(documents)} documents using LangChain with IDs: {len(doc_ids)}"
            )

        except Exception as e:
            logger.error(f"LangChain storage failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store protocol with LangChain: {str(e)}",
            )

        logger.info(
            f"Successfully processed and stored protocol {study_acronym} with {len(text_chunks)} chunks"
        )
        return ProtocolResponse(**protocol_metadata)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except QdrantError as e:
        logger.error(f"Qdrant error during PDF processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store processed protocol",
        )
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during PDF processing",
        )


@router.get("/diagnostics")
async def get_diagnostics() -> dict:
    """
    Get diagnostic information about the Qdrant connection and protocols.

    Returns:
        dict: Diagnostic information
    """
    try:
        diagnostics = {
            "qdrant_connection": False,
            "total_collections": 0,
            "protocol_collections": 0,
            "environment": {
                "qdrant_url": "SET" if os.getenv("QDRANT_URL") else "NOT SET",
                "qdrant_api_key": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
                "openai_api_key": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET",
            },
            "error": None,
        }

        # Test Qdrant connection
        connection_ok = qdrant_service.test_connection()
        diagnostics["qdrant_connection"] = connection_ok

        if connection_ok:
            # Get collection counts
            collections = qdrant_service.client.get_collections()
            diagnostics["total_collections"] = len(collections.collections)

            protocol_collections = [
                col.name
                for col in collections.collections
                if qdrant_service._is_protocol_collection(col.name)
            ]
            diagnostics["protocol_collections"] = len(protocol_collections)
            diagnostics["protocol_collection_names"] = protocol_collections

        return diagnostics

    except Exception as e:
        logger.error(f"Error in diagnostics: {e}")
        return {
            "qdrant_connection": False,
            "total_collections": 0,
            "protocol_collections": 0,
            "environment": {
                "qdrant_url": "SET" if os.getenv("QDRANT_URL") else "NOT SET",
                "qdrant_api_key": "SET" if os.getenv("QDRANT_API_KEY") else "NOT SET",
                "openai_api_key": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET",
            },
            "error": str(e),
        }


@router.get("/{protocol_id}", response_model=ProtocolResponse)
async def get_protocol(protocol_id: str) -> ProtocolResponse:
    """
    Retrieve a protocol by its ID.

    Args:
        protocol_id: Protocol ID to retrieve

    Returns:
        ProtocolResponse: Protocol data

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Retrieving protocol with ID {protocol_id}")
        protocol_data = qdrant_service.get_protocol_by_id(protocol_id)

        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with ID {protocol_id} not found",
            )

        return ProtocolResponse(**protocol_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/collection/{collection_name}", response_model=ProtocolResponse)
async def get_protocol_by_collection(collection_name: str) -> ProtocolResponse:
    """
    Retrieve a protocol by its collection name.

    Args:
        collection_name: Collection name to search for

    Returns:
        ProtocolResponse: Protocol data

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Retrieving protocol with collection name {collection_name}")
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)

        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found",
            )

        return ProtocolResponse(**protocol_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/", response_model=List[ProtocolResponse])
async def list_protocols(
    status_filter: Optional[str] = Query(None, description="Filter protocols by status")
) -> List[ProtocolResponse]:
    """
    List all protocols from Qdrant collections.

    Args:
        status_filter: Optional status to filter by

    Returns:
        List[ProtocolResponse]: List of protocols

    Raises:
        HTTPException: 500 for retrieval errors
    """
    try:
        logger.info(f"Listing protocols with status filter: {status_filter}")
        protocols = qdrant_service.list_all_protocols()

        if status_filter:
            protocols = [p for p in protocols if p.get("status") == status_filter]

        logger.info(f"Retrieved {len(protocols)} protocols")
        return [ProtocolResponse(**protocol) for protocol in protocols]

    except Exception as e:
        logger.error(f"Error listing protocols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocols",
        )


@router.patch("/collection/{collection_name}/status", response_model=ProtocolResponse)
async def update_protocol_status_endpoint(
    collection_name: str, status_update: ProtocolUpdate
) -> ProtocolResponse:
    """
    Update a protocol's status by collection name.

    Args:
        collection_name: Collection name to update
        status_update: New status data

    Returns:
        ProtocolResponse: Updated protocol data

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(
            f"Updating protocol {collection_name} status to {status_update.status}"
        )

        # First verify protocol exists
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)
        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found",
            )

        # Update status
        success = qdrant_service.update_protocol_status(
            collection_name, status_update.status
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update protocol status",
            )

        # Return updated protocol data
        updated_protocol = qdrant_service.get_protocol_by_collection(collection_name)
        logger.info(f"Successfully updated protocol {collection_name}")
        return ProtocolResponse(**updated_protocol)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/collection/{collection_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_protocol_endpoint(collection_name: str) -> None:
    """
    Delete a protocol from Qdrant by collection name.

    Args:
        collection_name: Collection name to delete

    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Deleting protocol with collection {collection_name}")

        # First verify protocol exists
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)
        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found",
            )

        # Delete protocol
        success = qdrant_service.delete_protocol(collection_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete protocol",
            )

        logger.info(f"Successfully deleted protocol {collection_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
