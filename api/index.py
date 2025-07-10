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
        elif parsed_url.path == '/api/icf/sections/requirements':
            response = self._get_icf_section_requirements()
        elif parsed_url.path.startswith('/api/protocols'):
            response = self._handle_protocols_get(parsed_url.path)
        else:
            response = {"error": "Endpoint not found", "path": parsed_url.path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
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
            response = {"error": str(e), "type": type(e).__name__}
        
        # Send headers after response code
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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
        try:
            # Validate required fields
            required_fields = ['study_acronym', 'protocol_title', 'extracted_text']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"{field} is required")
            
            # Mock response for now (replace with actual logic later)
            return {
                "protocol": {
                    "protocol_id": f"proto_{data['study_acronym'].lower()}",
                    "study_acronym": data['study_acronym'],
                    "protocol_title": data['protocol_title'],
                    "status": "processed",
                    "processing_method": "client-side-extraction",
                    "collection_name": f"protocol_{data['study_acronym'].lower()}",
                    "chunk_count": len(data['extracted_text']) // 1000,  # Rough estimate
                    "created_at": "2025-01-01T00:00:00Z"
                },
                "message": "Protocol uploaded successfully"
            }
        except Exception as e:
            # Log the error details
            print(f"Error in _handle_text_upload: {e}")
            print(f"Data received: {data}")
            raise
    
    def _get_icf_section_requirements(self):
        """Return ICF section requirements"""
        return {
            "sections": [
                {
                    "name": "introduction",
                    "title": "Introduction",
                    "required": True,
                    "description": "Introduction to the study"
                },
                {
                    "name": "purpose",
                    "title": "Purpose of Research",
                    "required": True,
                    "description": "Why the research is being done"
                },
                {
                    "name": "procedures",
                    "title": "Study Procedures",
                    "required": True,
                    "description": "What will happen during the study"
                },
                {
                    "name": "risks",
                    "title": "Risks and Discomforts",
                    "required": True,
                    "description": "Potential risks of participation"
                },
                {
                    "name": "benefits",
                    "title": "Benefits",
                    "required": True,
                    "description": "Potential benefits of participation"
                },
                {
                    "name": "confidentiality",
                    "title": "Confidentiality",
                    "required": True,
                    "description": "How data will be protected"
                }
            ]
        }
    
    def _handle_protocols_get(self, path):
        """Handle GET requests to protocols endpoints"""
        if path == '/api/protocols':
            # Return empty list for now
            return {"protocols": []}
        else:
            return {"error": "Protocol endpoint not implemented", "path": path}