"""
Configuration constants for the Clinical Trial Accelerator backend.
"""

from typing import Union

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# LLM configuration
LLM_MODEL = "gpt-4.1"  # Can be any OpenAI or Anthropic model
LLM_MAX_TOKENS = 8192
LLM_TEMPERATURE = 1


def get_llm_chat_model(
    model: str = LLM_MODEL,
    max_tokens: int = LLM_MAX_TOKENS,
    temperature: float = LLM_TEMPERATURE,
) -> Union[ChatOpenAI, ChatAnthropic]:
    """
    Get the appropriate chat model based on the model name.

    Automatically detects the provider based on model name:
    - Models starting with 'gpt' or 'o1' use OpenAI
    - Models starting with 'claude' use Anthropic

    Args:
        model: The model name
        max_tokens: Maximum tokens for generation
        temperature: Temperature for generation

    Returns:
        Configured chat model instance

    Raises:
        ValueError: If model type cannot be determined
    """
    if model.startswith("gpt") or model.startswith("o1"):
        # OpenAI models (gpt-4, gpt-3.5, o1-preview, etc.)
        return ChatOpenAI(
            model=model,
            # max_tokens=max_tokens,
            temperature=temperature,
        )
    elif model.startswith("claude"):
        # Anthropic models
        return ChatAnthropic(  # type: ignore[call-arg]
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        raise ValueError(
            f"Unknown model type: {model}. Must start with 'gpt', 'o1', or 'claude'"
        )


# Text splitting configuration for document chunking
TEXT_CHUNK_SIZE = 2000
TEXT_CHUNK_OVERLAP = 200
MIN_CHUNK_LENGTH = 50
