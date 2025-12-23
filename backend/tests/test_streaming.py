"""Tests for streaming functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.adapters.gemini_adapter import GeminiAdapter
from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_gemini_streaming():
    """Test Gemini adapter streaming."""
    with patch('app.adapters.gemini_adapter.genai') as mock_genai:
        # Mock the GenerativeModel
        mock_model = MagicMock()
        mock_chunk1 = MagicMock()
        mock_chunk1.text = "Hello "
        mock_chunk2 = MagicMock()
        mock_chunk2.text = "world"
        mock_chunk3 = MagicMock()
        mock_chunk3.text = "!"
        
        mock_model.generate_content.return_value = [
            mock_chunk1,
            mock_chunk2,
            mock_chunk3
        ]
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        adapter = GeminiAdapter("test-key")
        chunks = []
        async for chunk in adapter.generate_stream("test prompt", "gemini-pro"):
            chunks.append(chunk)
        
        assert chunks == ["Hello ", "world", "!"]
        mock_model.generate_content.assert_called_once()
        assert mock_model.generate_content.call_args[1]['stream'] is True


@pytest.mark.asyncio
async def test_gemini_streaming_error_handling():
    """Test Gemini streaming error handling."""
    with patch('app.adapters.gemini_adapter.genai') as mock_genai:
        mock_model = MagicMock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_genai.GenerativeModel.return_value = mock_model
        mock_genai.configure = MagicMock()
        
        adapter = GeminiAdapter("test-key")
        chunks = []
        with pytest.raises(Exception) as exc_info:
            async for chunk in adapter.generate_stream("test", "gemini-pro"):
                chunks.append(chunk)
        
        assert "API Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_llm_service_streaming():
    """Test LLM service streaming wrapper."""
    with patch('app.services.llm_service.get_adapter') as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.generate_stream = AsyncMock()
        mock_adapter.generate_stream.return_value = async_generator(["chunk1", "chunk2"])
        mock_get_adapter.return_value = mock_adapter
        
        chunks = []
        async for chunk in LLMService.generate_stream(
            "gemini", "key", "prompt", "model"
        ):
            chunks.append(chunk)
        
        assert chunks == ["chunk1", "chunk2"]


async def async_generator(items):
    """Helper to create async generator."""
    for item in items:
        yield item


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

