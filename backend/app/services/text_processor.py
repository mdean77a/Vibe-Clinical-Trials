"""
Shared text processing utilities for protocol document chunking.

This module provides common text splitting and processing functions used by both
the FastAPI backend and Vercel serverless functions to ensure consistent
chunking behavior across deployments.
"""

import logging
from typing import List

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import MIN_CHUNK_LENGTH, TEXT_CHUNK_OVERLAP, TEXT_CHUNK_SIZE

logger = logging.getLogger(__name__)


def tiktoken_len(text: str) -> int:
    """
    Calculate token length using GPT-4o tokenizer.

    Args:
        text: Text to count tokens for

    Returns:
        Number of tokens in the text
    """
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(text)
    return len(tokens)


def chunk_protocol_text(extracted_text: str) -> List[str]:
    """
    Split protocol text into chunks using token-based splitting.

    Args:
        extracted_text: Raw text extracted from protocol PDF

    Returns:
        List of meaningful text chunks

    Raises:
        Exception: If text processing fails
    """
    try:
        # Create text splitter with token-based configuration
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=TEXT_CHUNK_SIZE,
            chunk_overlap=TEXT_CHUNK_OVERLAP,
            length_function=tiktoken_len,
        )

        # Split the text
        text_chunks = text_splitter.split_text(extracted_text)

        # Filter out very short chunks
        meaningful_chunks = [
            chunk.strip()
            for chunk in text_chunks
            if len(chunk.strip()) > MIN_CHUNK_LENGTH
        ]

        # Fallback to full text if no meaningful chunks
        if not meaningful_chunks:
            meaningful_chunks = [extracted_text.strip()]

        logger.info(
            f"Text processed: {len(meaningful_chunks)} chunks using token-based splitting"
        )

        return meaningful_chunks

    except Exception as e:
        logger.error(f"Text processing failed: {e}")
        raise
