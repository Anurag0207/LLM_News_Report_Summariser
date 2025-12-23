"""Base adapter interface for LLM providers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator


class BaseLLMAdapter(ABC):
    """Base class for LLM provider adapters."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    def validate_key(self) -> bool:
        """Validate the API key."""
        pass
    
    @abstractmethod
    def list_models(self) -> List[Dict[str, str]]:
        """List available models for this provider."""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text using the specified model."""
        pass
    
    async def generate_stream(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate text stream. Default implementation falls back to chunked non-streaming."""
        # Default: fallback to non-streaming with chunking simulation
        response = self.generate(prompt, model, temperature, max_tokens, **kwargs)
        # Simulate streaming by yielding chunks
        chunk_size = 10
        for i in range(0, len(response), chunk_size):
            yield response[i:i + chunk_size]
            # Small delay to simulate streaming
            import asyncio
            await asyncio.sleep(0.01)
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass

