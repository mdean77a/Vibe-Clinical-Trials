"""
Simple Vercel Function handler for health check endpoints.
"""

import json


def handler(request):
    """
    Simple Vercel Function handler for health check endpoints.
    
    Args:
        request: Vercel function request object
        
    Returns:
        Vercel function response object
    """
    try:
        method = request.get("httpMethod", "GET")
        path = request.get("path", "/")
        
        # Handle CORS preflight
        if method == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "access-control-allow-origin": "*",
                    "access-control-allow-methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "access-control-allow-headers": "Content-Type, Authorization",
                    "access-control-max-age": "86400"
                },
                "body": ""
            }
        
        # Route to appropriate handler
        if method == "GET" and path == "/":
            return {
                "statusCode": 200,
                "headers": {
                    "content-type": "application/json",
                    "access-control-allow-origin": "*"
                },
                "body": json.dumps({
                    "message": "Clinical Trial Accelerator API",
                    "version": "0.1.0",
                    "status": "healthy"
                })
            }
        elif method == "GET" and path == "/health":
            return {
                "statusCode": 200,
                "headers": {
                    "content-type": "application/json",
                    "access-control-allow-origin": "*"
                },
                "body": json.dumps({"status": "healthy"})
            }
        
        # Route not found
        return {
            "statusCode": 404,
            "headers": {
                "content-type": "application/json",
                "access-control-allow-origin": "*"
            },
            "body": json.dumps({"detail": "Not found"})
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "content-type": "application/json",
                "access-control-allow-origin": "*"
            },
            "body": json.dumps({"detail": f"Internal server error: {str(e)}"})
        } 