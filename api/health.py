"""
Vercel Function handler for health check endpoints.

This module provides the serverless function handler for health check
and root endpoints.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.vercel_adapter import convert_vercel_request, convert_fastapi_response, handle_cors_preflight

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Vercel Function handler for health check endpoints.
    
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
        
        # Route to appropriate handler
        if method == "GET" and path == "/":
            return handle_root()
        elif method == "GET" and path == "/health":
            return handle_health_check()
        
        # Route not found
        return convert_fastapi_response(404, {"detail": "Not found"})
        
    except Exception as e:
        logger.error(f"Error in health handler: {e}")
        return convert_fastapi_response(500, {"detail": "Internal server error"})


def handle_root() -> Dict[str, Any]:
    """Handle GET /"""
    return convert_fastapi_response(200, {
        "message": "Clinical Trial Accelerator API",
        "version": "0.1.0",
        "status": "healthy"
    })


def handle_health_check() -> Dict[str, Any]:
    """Handle GET /health"""
    return convert_fastapi_response(200, {"status": "healthy"}) 