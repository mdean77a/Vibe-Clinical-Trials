"""
Configuration constants for the Clinical Trial Accelerator backend.
"""

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# LLM configuration
PRIMARY_LLM_MODEL = "gpt-4o-mini"  # OpenAI primary model
FALLBACK_LLM_MODEL = "claude-sonnet-4-20250514"  # Anthropic fallback model
LLM_MAX_TOKENS = 8192
LLM_TEMPERATURE = 0.1

# Text splitting configuration for document chunking
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 200
MIN_CHUNK_LENGTH = 50
