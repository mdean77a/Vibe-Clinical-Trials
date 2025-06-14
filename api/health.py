"""
Simple Vercel Function handler for health check endpoints.
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Test if we can import backend modules
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from app.database import init_database
    backend_available = True
    backend_error = None
except Exception as e:
    backend_available = False
    backend_error = str(e)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "backend_available": backend_available,
            "backend_error": backend_error,
            "python_path": sys.path[:3]  # Show first 3 paths for debugging
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
        return 