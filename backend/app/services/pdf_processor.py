"""
PDF processing service using Docling for semantic document parsing.

This module handles:
- PDF text extraction with semantic structure preservation
- Intelligent text chunking based on document sections
- Metadata extraction for clinical trial protocols
- Integration with Qdrant for vector storage
"""

import logging
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult

logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Exception raised for PDF processing errors."""
    pass


class PDFProcessor:
    """Service class for processing PDF documents using Docling."""
    
    def __init__(self):
        """Initialize the PDF processor with Docling converter."""
        try:
            # Initialize Docling converter with optimized settings for clinical documents
            self.converter = DocumentConverter()
            logger.info("PDF processor initialized with Docling")
        except Exception as e:
            logger.error(f"Failed to initialize PDF processor: {e}")
            raise PDFProcessingError(f"Failed to initialize PDF processor: {str(e)}")
    
    def process_pdf_from_bytes(
        self, 
        pdf_bytes: bytes, 
        filename: str = "document.pdf"
    ) -> Tuple[List[str], Dict[str, Any]]:
        """
        Process PDF from bytes and return chunks with metadata.
        
        Args:
            pdf_bytes: Raw PDF file bytes
            filename: Original filename for metadata
            
        Returns:
            Tuple of (text_chunks, document_metadata)
        """
        try:
            # Create temporary file for Docling processing
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_bytes)
                temp_path = Path(temp_file.name)
            
            try:
                # Process with Docling
                result = self.converter.convert(temp_path)
                
                # Extract chunks and metadata
                chunks = self._extract_semantic_chunks(result)
                metadata = self._extract_document_metadata(result, filename)
                
                logger.info(f"Successfully processed PDF: {len(chunks)} chunks extracted")
                return chunks, metadata
                
            finally:
                # Clean up temporary file
                temp_path.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Error processing PDF from bytes: {e}")
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}")
    
    def process_pdf_from_path(self, file_path: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Process PDF from file path and return chunks with metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (text_chunks, document_metadata)
        """
        try:
            # Process with Docling
            result = self.converter.convert(Path(file_path))
            
            # Extract chunks and metadata
            chunks = self._extract_semantic_chunks(result)
            metadata = self._extract_document_metadata(result, Path(file_path).name)
            
            logger.info(f"Successfully processed PDF: {len(chunks)} chunks extracted")
            return chunks, metadata
            
        except Exception as e:
            logger.error(f"Error processing PDF from path {file_path}: {e}")
            raise PDFProcessingError(f"Failed to process PDF: {str(e)}")
    
    def _extract_semantic_chunks(self, result: ConversionResult) -> List[str]:
        """
        Extract semantically meaningful chunks from Docling conversion result.
        
        Args:
            result: Docling conversion result
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        try:
            # Get the document
            doc = result.document
            
            # Extract chunks based on document structure
            # Docling provides semantic structure we can leverage
            
            # Method 1: Use document sections if available
            if hasattr(doc, 'texts') and doc.texts:
                # Group texts by semantic meaning
                current_chunk = ""
                chunk_size_limit = 1000  # Target chunk size
                
                for text_element in doc.texts:
                    text_content = text_element.text.strip()
                    
                    if not text_content:
                        continue
                    
                    # If adding this text would exceed limit, finalize current chunk
                    if current_chunk and len(current_chunk) + len(text_content) > chunk_size_limit:
                        chunks.append(current_chunk.strip())
                        current_chunk = text_content
                    else:
                        if current_chunk:
                            current_chunk += "\n\n" + text_content
                        else:
                            current_chunk = text_content
                
                # Add final chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
            
            # Method 2: Fallback to page-based chunking if structure extraction fails
            if not chunks and hasattr(doc, 'pages'):
                for page in doc.pages:
                    page_text = ""
                    # Extract text from page elements
                    if hasattr(page, 'texts'):
                        page_text = "\n".join([t.text for t in page.texts if t.text.strip()])
                    
                    if page_text.strip():
                        # Split large pages into smaller chunks
                        page_chunks = self._split_text_into_chunks(page_text, max_size=1000)
                        chunks.extend(page_chunks)
            
            # Method 3: Ultimate fallback - convert entire document to markdown and chunk
            if not chunks:
                try:
                    markdown_content = doc.export_to_markdown()
                    if markdown_content:
                        chunks = self._split_text_into_chunks(markdown_content, max_size=1000)
                except Exception as markdown_error:
                    logger.warning(f"Markdown export failed: {markdown_error}")
                    # Final fallback - use raw text if available
                    if hasattr(result, 'document') and hasattr(result.document, 'get_text'):
                        raw_text = result.document.get_text()
                        if raw_text:
                            chunks = self._split_text_into_chunks(raw_text, max_size=1000)
            
            # Filter out very short chunks
            chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
            
            if not chunks:
                logger.warning("No meaningful text chunks extracted from PDF")
                chunks = ["Document processed but no extractable text found."]
            
            logger.info(f"Extracted {len(chunks)} semantic chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error extracting semantic chunks: {e}")
            # Return a single chunk with error info
            return [f"Error extracting text from document: {str(e)}"]
    
    def _split_text_into_chunks(self, text: str, max_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks of specified size.
        
        Args:
            text: Text to split
            max_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the target break point
                sentence_break = text.rfind('.', start + max_size - 200, end)
                if sentence_break > start:
                    end = sentence_break + 1
                else:
                    # Look for paragraph breaks
                    para_break = text.rfind('\n\n', start + max_size - 200, end)
                    if para_break > start:
                        end = para_break + 2
                    else:
                        # Look for any newline
                        line_break = text.rfind('\n', start + max_size - 100, end)
                        if line_break > start:
                            end = line_break + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - overlap)
        
        return chunks
    
    def _extract_document_metadata(self, result: ConversionResult, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from Docling conversion result.
        
        Args:
            result: Docling conversion result
            filename: Original filename
            
        Returns:
            Document metadata dictionary
        """
        metadata = {
            "filename": filename,
            "processing_engine": "docling",
            "conversion_status": "success" if result else "failed"
        }
        
        try:
            doc = result.document
            
            # Extract basic document info
            if hasattr(doc, 'pages'):
                metadata["page_count"] = len(doc.pages)
            
            # Extract document structure info
            if hasattr(doc, 'texts'):
                metadata["text_elements_count"] = len(doc.texts)
                # Calculate total character count
                total_chars = sum(len(t.text) for t in doc.texts if hasattr(t, 'text'))
                metadata["total_characters"] = total_chars
            
            # Extract any document-level metadata Docling provides
            if hasattr(doc, 'metadata'):
                for key, value in doc.metadata.items():
                    if key not in metadata:  # Don't override our metadata
                        metadata[f"doc_{key}"] = value
            
            # Try to identify document type based on content
            metadata["document_type"] = self._identify_document_type(result)
            
        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
            metadata["metadata_extraction_error"] = str(e)
        
        return metadata
    
    def _identify_document_type(self, result: ConversionResult) -> str:
        """
        Attempt to identify the type of clinical trial document.
        
        Args:
            result: Docling conversion result
            
        Returns:
            Identified document type
        """
        try:
            # Get text content for analysis
            text_content = ""
            if hasattr(result.document, 'texts'):
                text_content = " ".join([t.text.lower() for t in result.document.texts[:10]])  # First 10 text elements
            
            # Look for common clinical trial document indicators
            if any(term in text_content for term in ["protocol", "clinical trial", "study protocol"]):
                return "clinical_trial_protocol"
            elif any(term in text_content for term in ["informed consent", "consent form"]):
                return "informed_consent"
            elif any(term in text_content for term in ["investigator brochure", "ib"]):
                return "investigator_brochure"
            elif any(term in text_content for term in ["case report form", "crf"]):
                return "case_report_form"
            else:
                return "clinical_document"
                
        except Exception as e:
            logger.warning(f"Error identifying document type: {e}")
            return "unknown"


def create_pdf_processor() -> PDFProcessor:
    """Factory function to create a PDF processor instance."""
    return PDFProcessor()