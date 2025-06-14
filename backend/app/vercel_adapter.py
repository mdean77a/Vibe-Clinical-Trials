"""
Vercel Functions adapter for FastAPI integration.

This module provides utilities to convert between Vercel's serverless function
request/response format and FastAPI's expected format.
"""

import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


def convert_vercel_request(vercel_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Vercel request format to FastAPI-compatible format.
    
    Args:
        vercel_request: Vercel function request object
        
    Returns:
        Dict containing FastAPI-compatible request data
    """
    # Extract path and query parameters
    path = vercel_request.get("path", "/")
    query_params = vercel_request.get("queryStringParameters") or {}
    
    # Convert headers to lowercase (FastAPI expects lowercase)
    headers = {}
    for key, value in (vercel_request.get("headers") or {}).items():
        headers[key.lower()] = value
    
    # Parse body if present
    body = None
    if vercel_request.get("body"):
        try:
            body = json.loads(vercel_request["body"])
        except json.JSONDecodeError:
            body = vercel_request["body"]
    
    return {
        "method": vercel_request.get("httpMethod", "GET"),
        "path": path,
        "query_params": query_params,
        "headers": headers,
        "body": body
    }


def convert_fastapi_response(
    status_code: int,
    content: Any,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Convert FastAPI response to Vercel function response format.
    
    Args:
        status_code: HTTP status code
        content: Response content (will be JSON serialized)
        headers: Optional response headers
        
    Returns:
        Dict in Vercel function response format
    """
    # Default headers
    response_headers = {
        "content-type": "application/json",
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
        "access-control-allow-headers": "Content-Type, Authorization"
    }
    
    # Add custom headers
    if headers:
        response_headers.update(headers)
    
    # Serialize content
    if isinstance(content, (dict, list)):
        body = json.dumps(content)
    elif content is None:
        body = ""
    else:
        body = str(content)
    
    return {
        "statusCode": status_code,
        "headers": response_headers,
        "body": body
    }


def handle_cors_preflight() -> Dict[str, Any]:
    """
    Handle CORS preflight requests.
    
    Returns:
        Vercel response for CORS preflight
    """
    return convert_fastapi_response(
        status_code=200,
        content=None,
        headers={
            "access-control-allow-origin": "*",
            "access-control-allow-methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "access-control-allow-headers": "Content-Type, Authorization",
            "access-control-max-age": "86400"
        }
    ) 