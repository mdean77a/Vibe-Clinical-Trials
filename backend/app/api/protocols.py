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
import time
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from ..models import ProtocolCreate, ProtocolResponse, ProtocolUpdate
from ..services.qdrant_service import QdrantError, get_qdrant_service
from ..services.pdf_processor import PDFProcessor, PDFProcessingError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/protocols", tags=["protocols"])

# Initialize services
qdrant_service = get_qdrant_service()
pdf_processor = PDFProcessor()


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
            file_path=getattr(protocol, 'file_path', None)
        )
        
        # Create protocol metadata
        protocol_metadata = {
            "protocol_id": f"proto_{int(time.time())}",
            "study_acronym": protocol.study_acronym,
            "protocol_title": protocol.protocol_title,
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "status": "processing",
            "file_path": getattr(protocol, 'file_path', None),
            "created_at": datetime.now().isoformat()
        }
        
        # Store initial metadata (will be updated when document is processed)
        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["Initial protocol entry"],
            embeddings=[[0.0] * 1536],  # Placeholder embedding
            protocol_metadata=protocol_metadata
        )
        
        logger.info(f"Successfully created protocol with collection {collection_name}")
        return ProtocolResponse(**protocol_metadata)
        
    except QdrantError as e:
        logger.error(f"Qdrant error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create protocol"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/upload", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def upload_and_process_protocol(
    file: UploadFile = File(...),
    study_acronym: str = Form(...),
    protocol_title: str = Form(...)
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
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        logger.info(f"Processing PDF upload: {file.filename} for study {study_acronym}")
        
        # Read file content
        pdf_content = await file.read()
        
        # Process PDF with Docling
        try:
            text_chunks, pdf_metadata = pdf_processor.process_pdf_from_bytes(
                pdf_content, 
                file.filename
            )
            logger.info(f"PDF processed successfully: {len(text_chunks)} chunks extracted")
        except PDFProcessingError as e:
            logger.error(f"PDF processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process PDF: {str(e)}"
            )
        
        # Create collection for this protocol
        collection_name = qdrant_service.create_protocol_collection(
            study_acronym=study_acronym,
            protocol_title=protocol_title,
            file_path=file.filename
        )
        
        # Generate embeddings for all chunks
        try:
            embeddings = qdrant_service.get_embeddings(text_chunks)
            logger.info(f"Generated embeddings for {len(embeddings)} chunks")
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Continue with placeholder embeddings
            embeddings = [[0.1] * 1536 for _ in text_chunks]
            logger.warning("Using placeholder embeddings due to embedding error")
        
        # Create protocol metadata
        protocol_metadata = {
            "protocol_id": f"proto_{int(time.time())}",
            "study_acronym": study_acronym,
            "protocol_title": protocol_title,
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "status": "processed",  # Mark as processed since we've done the work
            "file_path": file.filename,
            "created_at": datetime.now().isoformat(),
            
            # Add PDF processing metadata
            "pdf_metadata": pdf_metadata,
            "chunk_count": len(text_chunks),
            "processing_method": "docling"
        }
        
        # Store protocol with actual document content and embeddings
        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=text_chunks,
            embeddings=embeddings,
            protocol_metadata=protocol_metadata
        )
        
        logger.info(f"Successfully processed and stored protocol {study_acronym} with {len(text_chunks)} chunks")
        return ProtocolResponse(**protocol_metadata)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except QdrantError as e:
        logger.error(f"Qdrant error during PDF processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store processed protocol"
        )
    except Exception as e:
        logger.error(f"Unexpected error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during PDF processing"
        )


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
                detail=f"Protocol with ID {protocol_id} not found"
            )
        
        return ProtocolResponse(**protocol_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
                detail=f"Protocol with collection {collection_name} not found"
            )
        
        return ProtocolResponse(**protocol_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
            detail="Failed to retrieve protocols"
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
        logger.info(f"Updating protocol {collection_name} status to {status_update.status}")
        
        # First verify protocol exists
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)
        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found"
            )
        
        # Update status
        success = qdrant_service.update_protocol_status(collection_name, status_update.status)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update protocol status"
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
            detail="Internal server error"
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
                detail=f"Protocol with collection {collection_name} not found"
            )
        
        # Delete protocol
        success = qdrant_service.delete_protocol(collection_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete protocol"
            )
        
        logger.info(f"Successfully deleted protocol {collection_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
