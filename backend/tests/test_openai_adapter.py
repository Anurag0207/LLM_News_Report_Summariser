import json
import pytest
from unittest.mock import patch
from app.adapters.openai_adapter import OpenAIAdapter


@pytest.mark.asyncio
async def test_openai_adapter_generate_tool_calls():
    with patch.object(OpenAIAdapter, "_call_openai") as mock_call:
        mock_call.return_value = {
            "choices": [{"message": {"function_call": {"name": "search_internet", "arguments": "{\"query\":\"test\"}"}}}]
        }
        adapter = OpenAIAdapter("test-key")
        result = adapter.generate("prompt", "gpt-4", temperature=0.7)
        assert isinstance(result, str)
        assert result.startswith('{"tool_calls":')
        payload = json.loads(result)
        assert payload["tool_calls"][0]["function"]["name"] == "search_internet"


@pytest.mark.asyncio
async def test_openai_adapter_stream_no_tool_calls():
    with patch.object(OpenAIAdapter, "_call_openai") as mock_call:
        mock_call.return_value = [
            {"choices": [{"delta": {"content": "Hello"}}]}
        ]
        adapter = OpenAIAdapter("test-key")
        chunks = []
        async for chunk in adapter.generate_stream("prompt", "gpt-4"):
            chunks.append(chunk)
        assert chunks == ["Hello"]
