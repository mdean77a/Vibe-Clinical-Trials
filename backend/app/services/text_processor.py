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
        # Log input text statistics
        total_tokens = tiktoken_len(extracted_text)
        total_chars = len(extracted_text)
        logger.info(f"Input text: {total_tokens} tokens, {total_chars} characters")
        logger.info(f"Chunking config: chunk_size={TEXT_CHUNK_SIZE}, overlap={TEXT_CHUNK_OVERLAP}")
        
        # Create text splitter with token-based configuration
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=TEXT_CHUNK_SIZE,
            chunk_overlap=TEXT_CHUNK_OVERLAP,
            length_function=tiktoken_len,
        )

        # Split the text
        text_chunks = text_splitter.split_text(extracted_text)
        
        logger.info(f"Initial split produced {len(text_chunks)} chunks")

        # Filter out very short chunks and log statistics
        meaningful_chunks = [
            chunk.strip()
            for chunk in text_chunks
            if len(chunk.strip()) > MIN_CHUNK_LENGTH
        ]

        # Fallback to full text if no meaningful chunks
        if not meaningful_chunks:
            meaningful_chunks = [extracted_text.strip()]

        # Log detailed chunk statistics
        logger.info(f"Text processed: {len(meaningful_chunks)} chunks using token-based splitting")
        
        # Log statistics for each chunk
        token_counts = []
        for i, chunk in enumerate(meaningful_chunks):
            token_count = tiktoken_len(chunk)
            char_count = len(chunk)
            token_counts.append(token_count)
            logger.info(f"  Chunk {i+1}: {token_count} tokens, {char_count} chars")
        
        # Log summary statistics
        if token_counts:
            avg_tokens = sum(token_counts) / len(token_counts)
            min_tokens = min(token_counts)
            max_tokens = max(token_counts)
            over_limit = sum(1 for t in token_counts if t > TEXT_CHUNK_SIZE)
            
            logger.info(f"Chunk statistics:")
            logger.info(f"  Average: {avg_tokens:.0f} tokens")
            logger.info(f"  Min: {min_tokens} tokens")
            logger.info(f"  Max: {max_tokens} tokens")
            logger.info(f"  Chunks over {TEXT_CHUNK_SIZE} limit: {over_limit}/{len(token_counts)}")
            
            if max_tokens > TEXT_CHUNK_SIZE:
                logger.warning(
                    f"WARNING: Largest chunk ({max_tokens} tokens) exceeds configured "
                    f"TEXT_CHUNK_SIZE ({TEXT_CHUNK_SIZE} tokens) by {max_tokens - TEXT_CHUNK_SIZE} tokens"
                )

        return meaningful_chunks

    except Exception as e:
        logger.error(f"Text processing failed: {e}")
        raise
