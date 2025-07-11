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
        """Handle text upload with actual backend logic"""
        try:
            # Validate required fields
            required_fields = ['study_acronym', 'protocol_title', 'extracted_text']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"{field} is required")
            
            # Import and use the actual backend logic
            from datetime import datetime
            import time
            
            study_acronym = data['study_acronym'].strip().upper()
            protocol_title = data['protocol_title'].strip()
            extracted_text = data['extracted_text'].strip()
            original_filename = data.get('original_filename', '')
            page_count = data.get('page_count', 0)
            
            print(f"Processing text upload for study {study_acronym}")
            
            # Process the extracted text using the same chunking logic
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            # Use the same text splitter configuration as extract_and_chunk_pdf
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            
            text_chunks = text_splitter.split_text(extracted_text)
            
            # Filter out very short chunks
            meaningful_chunks = [
                chunk.strip() for chunk in text_chunks if len(chunk.strip()) > 50
            ]
            
            if not meaningful_chunks:
                meaningful_chunks = [extracted_text.strip()]
                
            print(f"Text processed: {len(meaningful_chunks)} chunks from {page_count} pages")
            
            # Store protocol using LangChain integration (same as file upload)
            from langchain_core.documents import Document
            from app.services.langchain_qdrant_service import get_langchain_qdrant_service
            
            # Initialize LangChain service
            langchain_service = get_langchain_qdrant_service()
            
            # Create protocol metadata
            protocol_metadata = {
                "protocol_id": f"proto_{int(time.time() * 1000)}",
                "study_acronym": study_acronym,
                "protocol_title": protocol_title,
                "upload_date": datetime.now().isoformat(),
                "status": "processed",
                "file_path": original_filename,
                "created_at": datetime.now().isoformat(),
                "chunk_count": len(meaningful_chunks),
                "processing_method": "client-side-extraction",
                "page_count": page_count,
            }
            
            # Convert text chunks to LangChain Documents
            documents = []
            for i, chunk in enumerate(meaningful_chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        **protocol_metadata,
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "embedding_model": "text-embedding-ada-002",
                        "processing_version": "1.0",
                        "last_updated": datetime.now().isoformat(),
                    },
                )
                documents.append(doc)
                
            # Store documents using LangChain
            doc_ids, collection_name = langchain_service.store_documents(
                documents=documents,
                study_acronym=study_acronym,
            )
            
            # Add collection_name to protocol metadata
            protocol_metadata["collection_name"] = collection_name
            
            print(f"Stored {len(documents)} documents using LangChain with collection: {collection_name}")
            
            # Return the protocol response
            return protocol_metadata
            
        except Exception as e:
            # Log the error details
            print(f"Error in _handle_text_upload: {e}")
            print(f"Data received: {data}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _get_icf_section_requirements(self):
        """Return ICF section requirements"""
        return {
            "required_sections": [
                {
                    "name": "summary",
                    "title": "Study Summary",
                    "description": "A clear, concise overview of the study purpose and participant involvement",
                    "estimated_length": "2-3 paragraphs"
                },
                {
                    "name": "background",
                    "title": "Background and Purpose",
                    "description": "Medical/scientific background explaining why the study is needed",
                    "estimated_length": "3-4 paragraphs"
                },
                {
                    "name": "participants",
                    "title": "Number of Participants",
                    "description": "Total participants and eligibility criteria",
                    "estimated_length": "2-3 paragraphs"
                },
                {
                    "name": "procedures",
                    "title": "Study Procedures",
                    "description": "Detailed description of all study procedures and timeline",
                    "estimated_length": "4-6 paragraphs"
                },
                {
                    "name": "alternatives",
                    "title": "Alternative Procedures",
                    "description": "Alternative treatments available outside the study",
                    "estimated_length": "2-3 paragraphs"
                },
                {
                    "name": "risks",
                    "title": "Risks and Discomforts",
                    "description": "Comprehensive list of potential risks and side effects",
                    "estimated_length": "3-5 paragraphs"
                },
                {
                    "name": "benefits",
                    "title": "Benefits",
                    "description": "Potential benefits to participants and society",
                    "estimated_length": "2-3 paragraphs"
                }
            ],
            "total_sections": 7,
            "compliance": "FDA 21 CFR 50 - Protection of Human Subjects",
            "generation_method": "LangGraph parallel processing with RAG context retrieval"
        }
    
    def _handle_protocols_get(self, path):
        """Handle GET requests to protocols endpoints"""
        if path == '/api/protocols':
            try:
                # Import necessary dependencies
                from qdrant_client import QdrantClient
                import os
                import re
                
                # Initialize Qdrant client
                qdrant_url = os.getenv("QDRANT_URL")
                qdrant_api_key = os.getenv("QDRANT_API_KEY")
                
                if not qdrant_url:
                    print("Warning: QDRANT_URL not set")
                    return {"protocols": []}
                
                client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
                
                # Get all collections
                collections = client.get_collections()
                protocols = []
                
                # Pattern to identify protocol collections
                protocol_pattern = re.compile(r'^[A-Z0-9]+-[a-z0-9]{8}$')
                
                for collection_info in collections.collections:
                    collection_name = collection_info.name
                    
                    # Check if this is a protocol collection
                    if not protocol_pattern.match(collection_name):
                        continue
                    
                    try:
                        # Get the first point to extract metadata
                        result = client.scroll(
                            collection_name=collection_name,
                            limit=1,
                            with_payload=True
                        )
                        
                        if result[0]:  # If points exist
                            point = result[0][0]  # Get first point
                            payload = point.payload or {}
                            
                            # Extract metadata (handle both LangChain and raw structures)
                            if "metadata" in payload:
                                metadata = payload["metadata"]
                            else:
                                metadata = payload
                            
                            # Get collection details for point count
                            collection_detail = client.get_collection(collection_name)
                            
                            # Build protocol data
                            protocol_data = {
                                "protocol_id": metadata.get("protocol_id", ""),
                                "study_acronym": metadata.get("study_acronym", ""),
                                "protocol_title": metadata.get("protocol_title", ""),
                                "collection_name": collection_name,
                                "upload_date": metadata.get("upload_date", ""),
                                "status": metadata.get("status", "processed"),
                                "file_path": metadata.get("file_path", ""),
                                "created_at": metadata.get("created_at", ""),
                                "chunk_count": collection_detail.points_count,
                            }
                            
                            protocols.append(protocol_data)
                    except Exception as e:
                        print(f"Error processing collection {collection_name}: {e}")
                        continue
                
                return {"protocols": protocols}
                
            except Exception as e:
                print(f"Error listing protocols: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return {"protocols": [], "error": str(e)}
        else:
            return {"error": "Protocol endpoint not implemented", "path": path}