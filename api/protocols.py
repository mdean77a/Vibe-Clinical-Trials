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

from app.services.qdrant_service_vercel import QdrantServiceVercel as QdrantService, QdrantError
import time
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize Qdrant service
            qdrant_service = QdrantService()
            
            # Get all protocols from Qdrant
            protocols = qdrant_service.list_all_protocols()
            
            # Convert to frontend format
            protocol_list = []
            for protocol in protocols:
                protocol_list.append({
                    "id": protocol.get("protocol_id", ""),
                    "study_acronym": protocol.get("study_acronym", ""),
                    "protocol_title": protocol.get("protocol_title", ""),
                    "upload_date": protocol.get("upload_date", "") + ("Z" if protocol.get("upload_date") and not protocol.get("upload_date").endswith("Z") else ""),
                    "status": protocol.get("status", "processing")
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
            # Initialize Qdrant service
            qdrant_service = QdrantService()
            
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
            
            # Create protocol collection
            collection_name = qdrant_service.create_protocol_collection(
                study_acronym=study_acronym,
                protocol_title=protocol_title,
                file_path=file_path
            )
            
            # Create protocol metadata
            protocol_metadata = {
                "protocol_id": f"proto_{int(time.time())}",
                "study_acronym": study_acronym,
                "protocol_title": protocol_title,
                "collection_name": collection_name,
                "upload_date": datetime.now().isoformat(),
                "status": "processing",
                "file_path": file_path,
                "created_at": datetime.now().isoformat()
            }
            
            # Store initial metadata so the protocol can be discovered
            qdrant_service.store_protocol_with_metadata(
                collection_name=collection_name,
                chunks=["Initial protocol entry"],
                embeddings=[[0.0] * 1536],  # Placeholder embedding
                protocol_metadata=protocol_metadata
            )
            
            # Convert to frontend format
            created_protocol = {
                "id": protocol_metadata["protocol_id"],
                "study_acronym": protocol_metadata["study_acronym"],
                "protocol_title": protocol_metadata["protocol_title"],
                "upload_date": protocol_metadata["upload_date"] + "Z",
                "status": protocol_metadata["status"]
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

 