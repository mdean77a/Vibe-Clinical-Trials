"""
Vercel Function handler for protocols endpoints.

This module provides the serverless function handler that wraps our FastAPI
protocols router for deployment on Vercel.
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import (
    init_database, 
    create_protocol, 
    get_all_protocols,
    ProtocolNotFoundError,
    DatabaseError
)
from app.models import ProtocolCreate
from app.vercel_adapter import convert_fastapi_response, handle_cors_preflight

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize database if needed
            init_database()
            
            # Get all protocols from database
            protocols = get_all_protocols()
            
            # Convert to frontend format
            protocol_list = []
            for protocol in protocols:
                protocol_list.append({
                    "id": str(protocol.id),
                    "study_acronym": protocol.study_acronym,
                    "protocol_title": protocol.protocol_title,
                    "upload_date": protocol.upload_date.isoformat() + "Z",
                    "status": protocol.status
                })
            
            response = {
                "protocols": protocol_list,
                "total": len(protocol_list),
                "status": "success"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return
            
        except Exception as e:
            # Return error response
            error_response = {
                "detail": f"Failed to fetch protocols: {str(e)}",
                "status": "error"
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
            return

    def do_POST(self):
        try:
            # Initialize database if needed
            init_database()
            
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
            
            # Create protocol in database
            protocol_data = ProtocolCreate(
                study_acronym=study_acronym,
                protocol_title=protocol_title,
                file_path=file_path
            )
            
            created_protocol_db = create_protocol(protocol_data)
            
            # Convert to frontend format
            created_protocol = {
                "id": str(created_protocol_db.id),
                "study_acronym": created_protocol_db.study_acronym,
                "protocol_title": created_protocol_db.protocol_title,
                "upload_date": created_protocol_db.upload_date.isoformat() + "Z",
                "status": created_protocol_db.status
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

 