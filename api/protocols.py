"""
Vercel Function handler for protocols endpoints.

This module provides the serverless function handler that wraps our FastAPI
protocols router for deployment on Vercel.
"""

import sys
import os
import json
import logging
from typing import Dict, Any

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.vercel_adapter import convert_vercel_request, convert_fastapi_response, handle_cors_preflight
from app.database import init_database
from app.api.protocols import router
from app.models import ProtocolCreate, ProtocolUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on cold start
try:
    init_database()
    logger.info("Database initialized for Vercel Function")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")


def handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Vercel Function handler for protocols endpoints.
    
    Args:
        request: Vercel function request object
        
    Returns:
        Vercel function response object
    """
    try:
        # Handle CORS preflight
        if request.get("httpMethod") == "OPTIONS":
            return handle_cors_preflight()
        
        # Convert Vercel request to FastAPI format
        fastapi_request = convert_vercel_request(request)
        method = fastapi_request["method"]
        path = fastapi_request["path"]
        
        logger.info(f"Processing {method} {path}")
        
        # Route to appropriate handler based on method and path
        if method == "POST" and path == "/protocols/":
            return handle_create_protocol(fastapi_request)
        elif method == "GET" and path.startswith("/protocols/"):
            if "/collection/" in path:
                collection_name = path.split("/collection/")[1]
                return handle_get_protocol_by_collection(collection_name)
            else:
                protocol_id = path.split("/protocols/")[1]
                if protocol_id.isdigit():
                    return handle_get_protocol(int(protocol_id))
        elif method == "GET" and path == "/protocols/":
            return handle_list_protocols(fastapi_request)
        elif method == "PATCH" and "/status" in path:
            protocol_id = int(path.split("/protocols/")[1].split("/status")[0])
            return handle_update_protocol_status(protocol_id, fastapi_request)
        elif method == "DELETE" and path.startswith("/protocols/"):
            protocol_id = int(path.split("/protocols/")[1])
            return handle_delete_protocol(protocol_id)
        
        # Route not found
        return convert_fastapi_response(404, {"detail": "Not found"})
        
    except Exception as e:
        logger.error(f"Error in protocols handler: {e}")
        return convert_fastapi_response(500, {"detail": "Internal server error"})


def handle_create_protocol(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle POST /protocols/"""
    try:
        from app.database import create_protocol
        
        protocol_data = ProtocolCreate(**request["body"])
        created_protocol = create_protocol(protocol_data)
        
        return convert_fastapi_response(201, created_protocol.model_dump())
        
    except Exception as e:
        logger.error(f"Error creating protocol: {e}")
        return convert_fastapi_response(500, {"detail": "Failed to create protocol"})


def handle_get_protocol(protocol_id: int) -> Dict[str, Any]:
    """Handle GET /protocols/{id}"""
    try:
        from app.database import get_protocol_by_id, ProtocolNotFoundError
        
        protocol = get_protocol_by_id(protocol_id)
        return convert_fastapi_response(200, protocol.model_dump())
        
    except ProtocolNotFoundError:
        return convert_fastapi_response(404, {"detail": "Protocol not found"})
    except Exception as e:
        logger.error(f"Error getting protocol: {e}")
        return convert_fastapi_response(500, {"detail": "Failed to retrieve protocol"})


def handle_get_protocol_by_collection(collection_name: str) -> Dict[str, Any]:
    """Handle GET /protocols/collection/{name}"""
    try:
        from app.database import get_protocol_by_collection_name, ProtocolNotFoundError
        
        protocol = get_protocol_by_collection_name(collection_name)
        return convert_fastapi_response(200, protocol.model_dump())
        
    except ProtocolNotFoundError:
        return convert_fastapi_response(404, {"detail": "Protocol not found"})
    except Exception as e:
        logger.error(f"Error getting protocol by collection: {e}")
        return convert_fastapi_response(500, {"detail": "Failed to retrieve protocol"})


def handle_list_protocols(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GET /protocols/"""
    try:
        from app.database import get_all_protocols
        
        status_filter = request["query_params"].get("status_filter")
        protocols = get_all_protocols(status_filter)
        
        return convert_fastapi_response(200, [p.model_dump() for p in protocols])
        
    except Exception as e:
        logger.error(f"Error listing protocols: {e}")
        return convert_fastapi_response(500, {"detail": "Failed to retrieve protocols"})


def handle_update_protocol_status(protocol_id: int, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle PATCH /protocols/{id}/status"""
    try:
        from app.database import update_protocol_status, ProtocolNotFoundError
        
        status_update = ProtocolUpdate(**request["body"])
        updated_protocol = update_protocol_status(protocol_id, status_update.status)
        
        return convert_fastapi_response(200, updated_protocol.model_dump())
        
    except ProtocolNotFoundError:
        return convert_fastapi_response(404, {"detail": "Protocol not found"})
    except Exception as e:
        logger.error(f"Error updating protocol status: {e}")
        return convert_fastapi_response(500, {"detail": "Failed to update protocol"})


def handle_delete_protocol(protocol_id: int) -> Dict[str, Any]:
    """Handle DELETE /protocols/{id}"""
    try:
        from app.database import delete_protocol, ProtocolNotFoundError
        
        delete_protocol(protocol_id)
        return convert_fastapi_response(204, None)
        
    except ProtocolNotFoundError:
        return convert_fastapi_response(404, {"detail": "Protocol not found"})
    except Exception as e:
        logger.error(f"Error deleting protocol: {e}")
        return convert_fastapi_response(500, {"detail": "Failed to delete protocol"}) 