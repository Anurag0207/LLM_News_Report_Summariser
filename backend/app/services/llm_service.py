"""LLM service for managing model interactions."""
from typing import Dict, List, Optional, AsyncIterator, Tuple
from ..adapters.factory import get_adapter
from ..adapters.base import BaseLLMAdapter
from .tool_service import ToolService
import json
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations."""
    
    @staticmethod
    def validate_api_key(provider: str, api_key: str) -> bool:
        """Validate an API key for a provider."""
        try:
            adapter = get_adapter(provider, api_key)
            return adapter.validate_key()
        except Exception:
            return False
    
    @staticmethod
    def list_models(provider: str, api_key: str) -> List[Dict[str, str]]:
        """List available models for a provider."""
        try:
            adapter = get_adapter(provider, api_key)
            return adapter.list_models()
        except Exception as e:
            return []
    
    @staticmethod
    def generate_text(
        provider: str,
        api_key: str,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        enable_search: bool = True,
        search_api_key: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using the specified model with optional tool calls."""
        adapter = get_adapter(provider, api_key)
        # Skip tool calling for Gemini as it's not fully supported yet
        tools = ToolService.get_tools() if (enable_search and provider != "gemini") else None
        
        messages = [{"role": "user", "content": prompt}]
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Generate response
            response = adapter.generate(
                prompt=prompt if iteration == 1 else "\n".join([m.get("content", "") for m in messages if m.get("role") != "system"]),
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools if iteration == 1 else None,  # Only send tools on first call
                **kwargs
            )
            
            # Check if response contains tool calls
            try:
                tool_data = json.loads(response)
                if "tool_calls" in tool_data:
                    # Execute tool calls
                    tool_results = ToolService.process_tool_calls(
                        tool_data["tool_calls"],
                        search_api_key=search_api_key
                    )
                    
                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": tool_data["tool_calls"]
                    })
                    
                    # Add tool results
                    messages.extend(tool_results)
                    
                    # Continue loop to get final response
                    # Update prompt for next iteration
                    prompt = f"Based on the search results, please provide a comprehensive answer to: {prompt}"
                    continue
            except (json.JSONDecodeError, KeyError):
                # Not a tool call, return the response
                return response
        
        # Fallback if we hit max iterations
        return response
    
    @staticmethod
    async def generate_stream(
        provider: str,
        api_key: str,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        enable_search: bool = True,
        search_api_key: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming text using the specified model with optional tool calls.
        Yields strings (chunks) streamed from the LLM provider.
        """
        adapter = get_adapter(provider, api_key)
        tools = ToolService.get_tools() if enable_search else None
        
        generator = adapter.generate_stream(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            **kwargs
        )
        # Support both awaitable and direct async iterators
        try:
            async_iter = await generator  # type: ignore
        except TypeError:
            async_iter = generator  # type: ignore
        
        async for chunk in async_iter:  # type: ignore
            yield chunk
