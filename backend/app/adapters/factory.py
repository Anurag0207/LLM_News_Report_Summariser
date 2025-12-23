"""Factory for creating LLM adapters."""
from typing import Optional
from .base import BaseLLMAdapter
from .openai_adapter import OpenAIAdapter
from .gemini_adapter import GeminiAdapter
from .openrouter_adapter import OpenRouterAdapter


def get_adapter(provider: str, api_key: str) -> BaseLLMAdapter:
    """Get the appropriate adapter for a provider."""
    adapters = {
        "openai": OpenAIAdapter,
        "gemini": GeminiAdapter,
        "openrouter": OpenRouterAdapter,
    }
    
    adapter_class = adapters.get(provider.lower())
    if not adapter_class:
        raise ValueError(f"Unknown provider: {provider}")
    
    return adapter_class(api_key)

