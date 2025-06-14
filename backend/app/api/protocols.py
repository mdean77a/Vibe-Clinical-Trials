"""
FastAPI router for protocol management endpoints.

This module defines all HTTP endpoints for protocol operations including:
- Creating new protocols
- Retrieving protocols
- Updating protocol status
- Listing all protocols
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
import logging

from ..models import ProtocolCreate, ProtocolResponse, ProtocolUpdate
from ..database import (
    create_protocol,
    get_protocol_by_id,
    get_protocol_by_collection_name,
    get_all_protocols,
    update_protocol_status,
    delete_protocol,
    ProtocolNotFoundError,
    DuplicateProtocolError,
    DatabaseError
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/protocols", tags=["protocols"])


@router.post("/", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_new_protocol(protocol: ProtocolCreate) -> ProtocolResponse:
    """
    Create a new protocol record.
    
    Args:
        protocol: Protocol data to create
        
    Returns:
        ProtocolResponse: Created protocol with database fields
        
    Raises:
        HTTPException: 409 if protocol already exists, 500 for other errors
    """
    try:
        logger.info(f"Creating new protocol: {protocol.study_acronym}")
        created_protocol = create_protocol(protocol)
        logger.info(f"Successfully created protocol with ID {created_protocol.id}")
        return created_protocol
        
    except DuplicateProtocolError as e:
        logger.warning(f"Duplicate protocol creation attempt: {e}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error creating protocol: {e}")
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


@router.get("/{protocol_id}", response_model=ProtocolResponse)
async def get_protocol(protocol_id: int) -> ProtocolResponse:
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
        protocol = get_protocol_by_id(protocol_id)
        return protocol
        
    except ProtocolNotFoundError as e:
        logger.warning(f"Protocol not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocol"
        )
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
        protocol = get_protocol_by_collection_name(collection_name)
        return protocol
        
    except ProtocolNotFoundError as e:
        logger.warning(f"Protocol not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocol"
        )
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
    List all protocols, optionally filtered by status.
    
    Args:
        status_filter: Optional status to filter by
        
    Returns:
        List[ProtocolResponse]: List of protocols
        
    Raises:
        HTTPException: 500 for database errors
    """
    try:
        logger.info(f"Listing protocols with status filter: {status_filter}")
        protocols = get_all_protocols(status_filter)
        logger.info(f"Retrieved {len(protocols)} protocols")
        return protocols
        
    except DatabaseError as e:
        logger.error(f"Database error listing protocols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocols"
        )
    except Exception as e:
        logger.error(f"Unexpected error listing protocols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/{protocol_id}/status", response_model=ProtocolResponse)
async def update_protocol_status_endpoint(
    protocol_id: int, 
    status_update: ProtocolUpdate
) -> ProtocolResponse:
    """
    Update a protocol's status.
    
    Args:
        protocol_id: Protocol ID to update
        status_update: New status data
        
    Returns:
        ProtocolResponse: Updated protocol data
        
    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Updating protocol {protocol_id} status to {status_update.status}")
        updated_protocol = update_protocol_status(protocol_id, status_update)
        logger.info(f"Successfully updated protocol {protocol_id}")
        return updated_protocol
        
    except ProtocolNotFoundError as e:
        logger.warning(f"Protocol not found for update: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error updating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update protocol"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{protocol_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_protocol_endpoint(protocol_id: int) -> None:
    """
    Delete a protocol from the database.
    
    Args:
        protocol_id: Protocol ID to delete
        
    Raises:
        HTTPException: 404 if protocol not found, 500 for other errors
    """
    try:
        logger.info(f"Deleting protocol with ID {protocol_id}")
        delete_protocol(protocol_id)
        logger.info(f"Successfully deleted protocol {protocol_id}")
        
    except ProtocolNotFoundError as e:
        logger.warning(f"Protocol not found for deletion: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error deleting protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete protocol"
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) 