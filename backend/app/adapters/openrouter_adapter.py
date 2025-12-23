"""OpenRouter adapter implementation."""
from typing import List, Dict, Optional, AsyncIterator
import requests
import json
import asyncio
from .base import BaseLLMAdapter


class OpenRouterAdapter(BaseLLMAdapter):
    """Adapter for OpenRouter API."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_key(self) -> bool:
        """Validate OpenRouter API key."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[Dict[str, str]]:
        """List available OpenRouter models."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "id": model["id"],
                        "name": model.get("name", model["id"]),
                        "provider": "openrouter",
                        "description": model.get("description", f"OpenRouter {model['id']}")
                    }
                    for model in data.get("data", [])
                ]
            return []
        except Exception:
            # Return some common models as fallback
            return [
                {
                    "id": "openai/gpt-4",
                    "name": "GPT-4 (via OpenRouter)",
                    "provider": "openrouter",
                    "description": "OpenAI GPT-4 via OpenRouter"
                },
                {
                    "id": "anthropic/claude-3-opus",
                    "name": "Claude 3 Opus (via OpenRouter)",
                    "provider": "openrouter",
                    "description": "Anthropic Claude 3 Opus via OpenRouter"
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
        """Generate text using OpenRouter."""
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            if tools:
                payload["tools"] = tools
                if tool_choice:
                    payload["tool_choice"] = tool_choice
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            
            message = data["choices"][0]["message"]
            
            # Handle tool calls
            if "tool_calls" in message:
                import json
                return json.dumps({
                    "tool_calls": message["tool_calls"]
                })
            
            return message.get("content", "")
        except Exception as e:
            raise Exception(f"OpenRouter generation error: {str(e)}")
    
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
        """Generate streaming text using OpenRouter."""
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "stream": True,
            }
            if max_tokens:
                payload["max_tokens"] = max_tokens
            if tools:
                payload["tools"] = tools
                if tool_choice:
                    payload["tool_choice"] = tool_choice
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60,
                stream=True
            )
            response.raise_for_status()
            
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:].strip()
                        if data_str == '[DONE]':
                            break
                        if not data_str:
                            continue
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and data['choices']:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content')
                                if content is not None:
                                    chunk_count += 1
                                    yield str(content)  # Ensure it's a string
                        except json.JSONDecodeError as e:
                            # Log but continue - might be malformed JSON
                            import logging
                            logging.getLogger(__name__).debug(f"JSON decode error: {e}, line: {data_str[:100]}")
                            continue
            
            if chunk_count == 0:
                import logging
                logging.getLogger(__name__).warning(f"No chunks received from OpenRouter for model {model}")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"OpenRouter streaming error: {str(e)}", exc_info=True)
            raise Exception(f"OpenRouter streaming error: {str(e)}")
    
    @property
    def provider_name(self) -> str:
        return "openrouter"

