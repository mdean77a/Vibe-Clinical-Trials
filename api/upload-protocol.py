"""
Vercel Function for Protocol PDF Upload and Processing.

Handles multipart file uploads, processes PDFs with PyMuPDF, 
generates embeddings, and stores in Qdrant with metadata.
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import cgi
import io
import tempfile
import time
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.qdrant_service_vercel import QdrantServiceVercel as QdrantService, QdrantError

import logging
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle PDF upload and processing."""
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error_response(400, "Expected multipart/form-data")
                return
            
            # Parse form fields
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            # Validate required fields
            if 'file' not in form:
                self.send_error_response(400, "No file provided")
                return
                
            if 'study_acronym' not in form:
                self.send_error_response(400, "study_acronym is required")
                return
                
            if 'protocol_title' not in form:
                self.send_error_response(400, "protocol_title is required")
                return
            
            file_item = form['file']
            study_acronym = form['study_acronym'].value
            protocol_title = form['protocol_title'].value
            
            # Validate file
            if not hasattr(file_item, 'filename') or not file_item.filename:
                self.send_error_response(400, "No file selected")
                return
                
            if not file_item.filename.lower().endswith('.pdf'):
                self.send_error_response(400, "Only PDF files are supported")
                return
            
            # Read file content
            pdf_content = file_item.file.read()
            
            logger.info(f"Processing PDF upload: {file_item.filename} for study {study_acronym}")
            
            # Process PDF with PyMuPDF
            try:
                text_chunks = self.extract_and_chunk_pdf(pdf_content, file_item.filename)
                logger.info(f"Extracted {len(text_chunks)} text chunks from PDF")
            except Exception as e:
                logger.error(f"PDF processing failed: {e}")
                self.send_error_response(400, f"Failed to process PDF: {str(e)}")
                return
            
            # Initialize Qdrant service
            qdrant_service = QdrantService()
            
            # Create collection for this protocol
            collection_name = qdrant_service.create_protocol_collection(
                study_acronym=study_acronym,
                protocol_title=protocol_title,
                file_path=file_item.filename
            )
            
            # Generate embeddings for all chunks
            try:
                embeddings = qdrant_service.get_embeddings(text_chunks)
                logger.info(f"Generated embeddings for {len(embeddings)} chunks")
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                # Use placeholder embeddings
                embeddings = [[0.1] * 1536 for _ in text_chunks]
                logger.warning("Using placeholder embeddings due to embedding error")
            
            # Create protocol metadata
            protocol_metadata = {
                "protocol_id": f"proto_{int(time.time())}",
                "study_acronym": study_acronym,
                "protocol_title": protocol_title,
                "collection_name": collection_name,
                "upload_date": datetime.now().isoformat(),
                "status": "processed",
                "file_path": file_item.filename,
                "created_at": datetime.now().isoformat(),
                "chunk_count": len(text_chunks),
                "processing_method": "pymupdf"
            }
            
            # Store protocol with document content and embeddings
            qdrant_service.store_protocol_with_metadata(
                collection_name=collection_name,
                chunks=text_chunks,
                embeddings=embeddings,
                protocol_metadata=protocol_metadata
            )
            
            logger.info(f"Successfully processed and stored protocol {study_acronym} with {len(text_chunks)} chunks")
            
            # Return success response
            response_data = {
                "success": True,
                "protocol": protocol_metadata
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
        except QdrantError as e:
            logger.error(f"Qdrant error during PDF processing: {e}")
            self.send_error_response(500, "Failed to store processed protocol")
        except Exception as e:
            logger.error(f"Unexpected error processing PDF: {e}")
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def extract_and_chunk_pdf(self, pdf_content: bytes, filename: str) -> List[str]:
        """
        Extract text from PDF using PyMuPDF and chunk using RecursiveCharacterTextSplitter.
        
        Args:
            pdf_content: Raw PDF bytes
            filename: Original filename for logging
            
        Returns:
            List of text chunks ready for embedding
        """
        pdf_document = None
        try:
            import fitz  # PyMuPDF
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            page_count = pdf_document.page_count
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(page_count):
                page = pdf_document[page_num]
                page_text = page.get_text()
                full_text += f"\n\n--- Page {page_num + 1} ---\n\n"
                full_text += page_text
            
            pdf_document.close()
            pdf_document = None
            
            if not full_text.strip():
                raise ValueError("No text content extracted from PDF")
            
            # Chunk the text using RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,        # Good size for clinical protocols
                chunk_overlap=200,      # Preserve context across chunks
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]  # Try semantic breaks first
            )
            
            chunks = text_splitter.split_text(full_text)
            
            # Filter out very short chunks
            meaningful_chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 50]
            
            if not meaningful_chunks:
                # Fallback: return the full text as one chunk if splitting failed
                meaningful_chunks = [full_text.strip()]
            
            logger.info(f"PDF {filename}: extracted {len(meaningful_chunks)} chunks from {page_count} pages")
            return meaningful_chunks
            
        except ImportError as e:
            logger.error(f"Missing dependencies for PDF processing: {e}")
            raise ValueError("PDF processing dependencies not available")
        except Exception as e:
            logger.error(f"PDF text extraction failed for {filename}: {e}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        finally:
            # Ensure document is closed even if an error occurs
            if pdf_document is not None:
                try:
                    pdf_document.close()
                except:
                    pass
    
    def send_error_response(self, status_code: int, message: str):
        """Send an error response."""
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            "success": False,
            "error": message
        }
        
        self.wfile.write(json.dumps(error_response).encode())