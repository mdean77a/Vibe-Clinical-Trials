"""
Vercel Function handler for protocols endpoints.

This module provides the serverless function handler that wraps our FastAPI
protocols router for deployment on Vercel.
"""

from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Mock protocol data
        protocols = [
            {
                "id": "NCT12345678",
                "title": "Phase II Study of Novel Cancer Treatment",
                "status": "Recruiting",
                "phase": "Phase 2",
                "condition": "Breast Cancer",
                "sponsor": "University Medical Center",
                "location": "Multiple Sites",
                "enrollment": 150
            },
            {
                "id": "NCT87654321", 
                "title": "Cardiovascular Prevention Trial",
                "status": "Active",
                "phase": "Phase 3",
                "condition": "Heart Disease",
                "sponsor": "Pharma Corp",
                "location": "US & Canada",
                "enrollment": 500
            }
        ]
        
        response = {
            "protocols": protocols,
            "total": len(protocols),
            "status": "success"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return

    def do_POST(self):
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract protocol data
            study_acronym = data.get('study_acronym', '')
            protocol_title = data.get('protocol_title', '')
            file_path = data.get('file_path', '')
            
            # Validate required fields
            if not study_acronym or not protocol_title:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "detail": "study_acronym and protocol_title are required"
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                return
            
            # Create mock protocol response
            import time
            protocol_id = int(time.time())  # Simple ID generation
            
            created_protocol = {
                "id": protocol_id,
                "study_acronym": study_acronym.upper(),
                "protocol_title": protocol_title,
                "collection_name": f"{study_acronym.lower().replace('-', '').replace('_', '')}_{int(time.time())}",
                "upload_date": "2024-12-01T12:00:00Z",
                "status": "processed",
                "file_path": file_path,
                "created_at": "2024-12-01T12:00:00Z"
            }
            
            # Send success response
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(created_protocol).encode('utf-8'))
            return
            
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "detail": "Invalid JSON in request body"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "detail": f"Internal server error: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
        return

 