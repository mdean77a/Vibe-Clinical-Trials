"""
Vercel serverless function entry point.
Simple HTTP handler without FastAPI for Vercel compatibility.
"""

import json
import sys
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Simple routing
        if parsed_url.path == '/api/health':
            response = {"status": "healthy", "environment": "vercel-serverless"}
        elif parsed_url.path == '/api':
            response = {
                "message": "Clinical Trial Accelerator API",
                "version": "0.1.0",
                "environment": "vercel-serverless"
            }
        else:
            response = {"error": "Endpoint not found", "path": parsed_url.path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            if parsed_url.path == '/api/protocols/upload-text':
                # Handle text upload
                data = json.loads(post_data.decode())
                response = self._handle_text_upload(data)
                self.send_response(200)
            else:
                self.send_response(404)
                response = {"error": "Endpoint not found", "path": parsed_url.path}
        except Exception as e:
            self.send_response(500)
            response = {"error": str(e)}
        
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _handle_text_upload(self, data):
        """Simple text upload handler"""
        # Validate required fields
        required_fields = ['study_acronym', 'protocol_title', 'extracted_text']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"{field} is required")
        
        # Mock response for now (replace with actual logic later)
        return {
            "protocol_id": f"proto_{data['study_acronym'].lower()}",
            "study_acronym": data['study_acronym'],
            "protocol_title": data['protocol_title'],
            "status": "processed",
            "processing_method": "client-side-extraction",
            "message": "Protocol uploaded successfully"
        }