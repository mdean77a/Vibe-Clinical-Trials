"""
Configuration constants for the Clinical Trial Accelerator backend.
"""

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Text splitting configuration for document chunking
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 200
MIN_CHUNK_LENGTH = 50