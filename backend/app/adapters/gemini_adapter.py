"""Google Gemini adapter implementation."""
from typing import List, Dict, Optional, AsyncIterator
import asyncio
import json
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
from .base import BaseLLMAdapter


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini API."""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package is required for Gemini support")
        genai.configure(api_key=api_key)
    
    def validate_key(self) -> bool:
        """Validate Gemini API key."""
        try:
            list(genai.list_models())
            return True
        except Exception:
            return False
    
    def list_models(self) -> List[Dict[str, str]]:
        """List available Gemini models."""
        try:
            models = genai.list_models()
            return [
                {
                    "id": model.name.split("/")[-1],
                    "name": model.display_name or model.name.split("/")[-1],
                    "provider": "gemini",
                    "description": f"Google {model.display_name or model.name}"
                }
                for model in models
                if "generateContent" in model.supported_generation_methods
            ]
        except Exception:
            return [
                {
                    "id": "gemini-pro",
                    "name": "Gemini Pro",
                    "provider": "gemini",
                    "description": "Google Gemini Pro"
                },
                {
                    "id": "gemini-pro-vision",
                    "name": "Gemini Pro Vision",
                    "provider": "gemini",
                    "description": "Google Gemini Pro Vision"
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
        """Generate text using Gemini."""
        try:
            model_instance = genai.GenerativeModel(model)
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Note: Gemini function calling support varies by SDK version
            # For now, we'll skip tools in non-streaming mode to avoid errors
            # Tools can be added later when SDK support is confirmed
            generate_kwargs = {"generation_config": generation_config, **kwargs}
            # Skip tools for now - Gemini SDK may not support it in this version
            # if tools:
            #     # Convert OpenAI-style tools to Gemini format
            #     gemini_tools = []
            #     for tool in tools:
            #         if tool.get("type") == "function":
            #             func_def = tool.get("function", {})
            #             gemini_tools.append({
            #                 "function_declarations": [{
            #                     "name": func_def.get("name"),
            #                     "description": func_def.get("description"),
            #                     "parameters": func_def.get("parameters", {})
            #                 }]
            #             })
            #     if gemini_tools:
            #         generate_kwargs["tools"] = gemini_tools
            
            response = model_instance.generate_content(
                prompt,
                **generate_kwargs
            )
            
            # Check for function calls
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    parts = candidate.content.parts
                    for part in parts:
                        if hasattr(part, 'function_call'):
                            # Return function call info
                            return json.dumps({
                                "tool_calls": [{
                                    "id": "gemini_call",
                                    "function": {
                                        "name": part.function_call.name,
                                        "arguments": json.dumps(dict(part.function_call.args))
                                    }
                                }]
                            })
            
            return response.text
        except Exception as e:
            raise Exception(f"Gemini generation error: {str(e)}")
    
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
        """Generate streaming text using Gemini."""
        try:
            model_instance = genai.GenerativeModel(model)
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Note: Gemini function calling support varies by SDK version
            # For now, we'll skip tools in streaming mode to avoid errors
            # Tools can be added later when SDK support is confirmed
            generate_kwargs = {
                "generation_config": generation_config,
                "stream": True,
                **kwargs
            }
            # Skip tools for streaming - Gemini SDK may not support it yet
            # if tools:
            #     # Convert OpenAI-style tools to Gemini format
            #     gemini_tools = []
            #     for tool in tools:
            #         if tool.get("type") == "function":
            #             func_def = tool.get("function", {})
            #             gemini_tools.append({
            #                 "function_declarations": [{
            #                     "name": func_def.get("name"),
            #                     "description": func_def.get("description"),
            #                     "parameters": func_def.get("parameters", {})
            #                 }]
            #             })
            #     if gemini_tools:
            #         generate_kwargs["tools"] = gemini_tools
            
            response = model_instance.generate_content(
                prompt,
                **generate_kwargs
            )
            
            # Yield chunks as they arrive
            for chunk in response:
                if chunk.text:
                    text = chunk.text
                    if text is not None:
                        yield str(text)  # Ensure it's a string
        except Exception as e:
            # Log error and yield error message
            error_msg = f"Gemini streaming error: {str(e)}"
            yield f"\n\n[Error: {error_msg}]"
            raise Exception(error_msg)
    
    @property
    def provider_name(self) -> str:
        return "gemini"

