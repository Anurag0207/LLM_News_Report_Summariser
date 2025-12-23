"""OpenAI adapter implementation (SDK-compliant).
"""
from typing import List, Dict, Optional, AsyncIterator
import openai
import json
from .base import BaseLLMAdapter


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI API."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # Configure the OpenAI client with the provided API key
        openai.api_key = api_key
        # No persistent client object is strictly required; we use openai.* calls directly
        # self.client = openai
        
    def _call_openai(self, request_params: Dict, **kwargs):
        """Internal helper to call OpenAI API in a way compatible with multiple SDK versions."""
        # Try modern ChatCompletion path if available
        try:
            if hasattr(openai, "ChatCompletion"):
                return openai.ChatCompletion.create(**request_params, **kwargs)
        except Exception:
            pass
        # Fallback to legacy path if present
        try:
            if hasattr(openai, "chat") and hasattr(openai.chat, "completions"):
                return openai.chat.completions.create(**request_params, **kwargs)
        except Exception:
            pass
        raise RuntimeError("OpenAI API endpoint not available under current OpenAI SDK version")
        
    def validate_key(self) -> bool:
        """Validate OpenAI API key."""
        try:
            openai.Model.list()
            return True
        except Exception:
            return False
    
    def list_models(self) -> List[Dict[str, str]]:
        """List available OpenAI models."""
        try:
            models = openai.Model.list()
            return [
                {
                    "id": m["id"],
                    "name": m["id"],
                    "provider": "openai",
                    "description": f"OpenAI {m.get('id', '')}"
                }
                for m in models.get("data", [])
                if "gpt" in str(m.get("id", "")).lower() or "davinci" in str(m.get("id", "")).lower()
            ]
        except Exception:
            return [
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "provider": "openai",
                    "description": "OpenAI GPT-4"
                },
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "openai",
                    "description": "OpenAI GPT-3.5 Turbo"
                }
            ]
    
    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate text using OpenAI."""
        try:
            messages = [{"role": "user", "content": prompt}]
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            if tools:
                # Map our tools to OpenAI function_call structure
                request_params["functions"] = tools
                if tool_choice:
                    request_params["function_call"] = {"name": tool_choice}
            
            response = self._call_openai(request_params, **kwargs)
            # Normalize access to response content across SDK versions
            message = None
            if isinstance(response, dict):
                choices = response.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
            else:
                # SDK may return a SimpleNamespace-like object
                choices = getattr(response, "choices", None)
                if choices:
                    message = choices[0].message
            
            # If the model used function calling, there will be a function_call payload
            func_call = None
            if isinstance(message, dict):
                func_call = message.get("function_call")
            else:
                func_call = getattr(message, "function_call", None)
            if func_call:
                return json.dumps({
                    "tool_calls": [
                        {
                            "id": "openai_call",
                            "function": {
                                "name": func_call.get("name"),
                                "arguments": func_call.get("arguments")
                            }
                        }
                    ]
                })
            # Fallback to plain content
            if isinstance(message, dict):
                content = message.get("content")
            else:
                content = getattr(message, "content", None)
            return content or ""
        except Exception as e:
            raise Exception(f"OpenAI generation error: {str(e)}")
    
    async def generate_stream(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming text using OpenAI."""
        try:
            messages = [{"role": "user", "content": prompt}]
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            if tools:
                request_params["functions"] = tools
                if tool_choice:
                    request_params["function_call"] = {"name": tool_choice}
            
            response = self._call_openai(request_params, **kwargs)
            # Some SDKs return a generator/stream-like object for streaming; handle accordingly
            for chunk in response:
                # chunk is a dict with 'choices'; delta content is under delta.content
                if isinstance(chunk, dict):
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield str(content)
                else:
                    try:
                        content = getattr(chunk, "choices")[0].get("delta", {}).get("content")
                        if content:
                            yield str(content)
                    except Exception:
                        continue
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")
    
    @property
    def provider_name(self) -> str:
        return "openai"
