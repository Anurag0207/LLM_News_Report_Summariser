# Streaming Implementation Guide

## Overview

The Research Assistant application supports real-time streaming of LLM responses using Server-Sent Events (SSE). This provides a better user experience by displaying partial responses as they are generated, rather than waiting for the complete response.

## Architecture

### Backend

1. **Adapter Layer**: Each LLM adapter (OpenAI, Gemini, OpenRouter) implements a `generate_stream()` method that yields text chunks as they arrive.

2. **Service Layer**: The `LLMService.generate_stream()` method wraps adapter streaming and provides a unified interface.

3. **API Endpoint**: The `/api/chat/stream` endpoint uses FastAPI's `StreamingResponse` to send SSE events to the frontend.

### Frontend

1. **API Service**: The `chatAPI.sendMessageStream()` method uses the Fetch API with `ReadableStream` to consume SSE events.

2. **Chat Interface**: The `ChatInterface` component updates the UI in real-time as chunks arrive, showing a streaming indicator and appending text progressively.

## Gemini Streaming

Gemini streaming is implemented using the `google-generativeai` SDK's native streaming support:

```python
response = model_instance.generate_content(
    prompt,
    generation_config=generation_config,
    stream=True,  # Enable streaming
    **kwargs
)

for chunk in response:
    if chunk.text:
        yield chunk.text
```

### Error Handling

- If streaming fails, the adapter yields an error message and raises an exception
- The backend logs all streaming errors with full stack traces
- The frontend displays user-friendly error messages

## Testing Streaming

### Backend Tests

Run the streaming tests:

```bash
cd backend
pytest tests/test_streaming.py -v
```

### Manual Testing with curl

Test the streaming endpoint directly:

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "api_key": "YOUR_API_KEY",
    "model": "gemini-pro",
    "prompt": "Tell me a short story",
    "temperature": 0.7
  }' \
  --no-buffer
```

You should see SSE events like:

```
data: {"type": "chunk", "content": "Once "}

data: {"type": "chunk", "content": "upon "}

data: {"type": "chunk", "content": "a time"}

data: {"type": "done", "content": "Once upon a time..."}
```

### Testing in Browser

1. Open browser DevTools (F12)
2. Go to Network tab
3. Send a message in the chat
4. Look for the `/api/chat/stream` request
5. Check the Response tab to see streaming events

### WebSocket Alternative (Future)

For even better real-time performance, WebSocket support could be added:

```python
from fastapi import WebSocket

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    # Stream chunks via WebSocket
```

## Troubleshooting

### Streaming Stuck in Loading State

1. Check browser console for errors
2. Verify backend logs for adapter errors
3. Ensure API key is valid
4. Check network tab for failed requests

### Chunks Not Appearing

1. Verify SSE events are being sent (check Network tab)
2. Check frontend console for parsing errors
3. Ensure `ReadableStream` is supported (modern browsers)

### Timeout Issues

- Default timeout is handled by the browser
- For long responses, consider implementing a heartbeat mechanism
- Add timeout handling in the frontend:

```typescript
const controller = new AbortController();
setTimeout(() => controller.abort(), 60000); // 60s timeout
```

## Logging

Streaming events are logged on the backend:

- Success: Logged at INFO level
- Errors: Logged at ERROR level with full stack traces
- Performance: Consider adding metrics for streaming duration and chunk count

## Future Enhancements

1. **WebSocket Support**: For bidirectional communication
2. **Chunk Batching**: Combine small chunks for better performance
3. **Streaming Metrics**: Track streaming performance and success rates
4. **Retry Logic**: Automatic retry for failed streams
5. **Stream Cancellation**: Allow users to stop streaming mid-response

