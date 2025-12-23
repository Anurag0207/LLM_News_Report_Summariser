# Research Assistant - Full-Stack Application

A modern, full-stack research assistant application with support for multiple LLM providers (OpenAI, Google Gemini, OpenRouter). Built with React (TypeScript) frontend and FastAPI backend.

## Features

- **Multi-LLM Support**: Unified interface for OpenAI, Google Gemini, and OpenRouter
- **Dynamic Model Discovery**: Automatically fetch available models from each provider
- **Chat Interface**: Clean, modern chat UI with session management
- **Session Tabs**: Organize conversations into multiple sessions
- **News Processing**: Extract and process text from URLs
- **Extensible Architecture**: Modular design ready for future features (citations, summaries, exports, collaboration)

## Architecture

### Backend (FastAPI)
- **Modular Adapter Pattern**: Clean separation of LLM providers
- **SQLite Database**: Session and message storage
- **RESTful API**: Well-structured endpoints for all operations
- **Extensible Services**: Easy to add new features

### Frontend (React + TypeScript)
- **Component-Based**: Reusable, maintainable components
- **Type Safety**: Full TypeScript support
- **Modern UI**: Clean, responsive design
- **State Management**: Efficient React state handling

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py           # Database configuration
│   │   ├── models/               # Database models
│   │   │   ├── session.py
│   │   │   └── api_key.py
│   │   ├── adapters/            # LLM provider adapters
│   │   │   ├── base.py
│   │   │   ├── openai_adapter.py
│   │   │   ├── gemini_adapter.py
│   │   │   ├── openrouter_adapter.py
│   │   │   └── factory.py
│   │   ├── services/            # Business logic
│   │   │   ├── llm_service.py
│   │   │   ├── session_service.py
│   │   │   └── news_service.py
│   │   └── api/                 # API routes
│   │       ├── auth.py
│   │       ├── models.py
│   │       ├── sessions.py
│   │       ├── chat.py
│   │       └── news.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── APIKeyManager.tsx
│   │   │   ├── ModelSelector.tsx
│   │   │   ├── SessionTabs.tsx
│   │   │   └── ChatInterface.tsx
│   │   ├── services/            # API services
│   │   │   └── api.ts
│   │   ├── types/               # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation (Swagger UI) at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## Usage

1. **Configure API Key**:
   - Expand the "API Key Configuration" section in the sidebar
   - Select a provider (OpenAI, Gemini, or OpenRouter)
   - Enter your API key
   - Click "Validate & Load Models"

2. **Select Model**:
   - Expand the "Model Selection" section
   - Search for models using the search bar
   - Click on a model to select it
   - Selected model is highlighted and shown in the status bar

3. **Start Chatting**:
   - Create a new session using the "+" button or select an existing one
   - Type your message in the expandable input box
   - Press Enter to send (Shift+Enter for new line)
   - Watch responses stream in real-time
   - Use copy and regenerate buttons on messages

4. **Manage Sessions**:
   - **Rename**: Click the ✏️ icon on a session tab
   - **Duplicate**: Click the 📋 icon to copy a session with all messages
   - **Delete**: Click the × icon to remove a session
   - Switch between sessions by clicking tabs

5. **Theme & Settings**:
   - Toggle between light/dark themes using the 🌙/☀️ button in the top nav
   - Access settings via the ⚙️ button (future feature)

6. **Resize Panels**:
   - Drag the vertical divider between sidebar and main content
   - Drag the divider in the chat area to show/hide context panel

## API Endpoints

### Authentication
- `POST /api/auth/validate` - Validate API key

### Models
- `POST /api/models/list` - List available models

### Sessions
- `GET /api/sessions` - List all sessions
- `POST /api/sessions` - Create a new session
- `GET /api/sessions/{id}` - Get a specific session
- `GET /api/sessions/{id}/messages` - Get messages for a session
- `DELETE /api/sessions/{id}` - Delete a session

### Chat
- `POST /api/chat` - Send a chat message

### News Processing
- `POST /api/news/process-urls` - Process URLs and extract text
- `POST /api/news/chunk-text` - Split text into chunks

## Environment Variables

### Backend
- `DATABASE_URL` - Database connection string (default: `sqlite:///./research_assistant.db`)

### Frontend
- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

## Database

The application uses SQLite by default for development. The database file (`research_assistant.db`) will be created automatically on first run.

### Tables
- `sessions` - Chat sessions
- `messages` - Chat messages
- `api_keys` - API key storage (for future use)

## Development

### Adding a New LLM Provider

1. Create a new adapter in `backend/app/adapters/`:
   ```python
   from .base import BaseLLMAdapter
   
   class NewProviderAdapter(BaseLLMAdapter):
       # Implement required methods
   ```

2. Register it in `backend/app/adapters/factory.py`

3. Add provider option to frontend `APIKeyManager` component

### Extending Features

The architecture is designed for easy extension:
- **Citations**: Add citation tracking to messages
- **Summaries**: Implement summarization service
- **Exports**: Add export endpoints and UI
- **Collaboration**: Extend session model with sharing

## Streaming

The application supports real-time streaming of LLM responses. See [STREAMING.md](STREAMING.md) for detailed information about:
- How streaming is implemented
- Testing streaming locally
- Troubleshooting streaming issues
- Future enhancements

### Quick Streaming Test

```bash
# Test Gemini streaming
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "gemini",
    "api_key": "YOUR_KEY",
    "model": "gemini-pro",
    "prompt": "Hello"
  }' --no-buffer
```

## Troubleshooting

### Backend Issues
- Ensure Python 3.9+ is installed
- Check that all dependencies are installed
- Verify database file permissions
- Check backend logs for streaming errors

### Frontend Issues
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check that backend is running on port 8000
- Verify CORS settings in `backend/app/main.py`
- Check browser console for streaming errors

### Streaming Issues
- **Stuck in loading**: Check browser console and backend logs
- **No chunks appearing**: Verify SSE events in Network tab
- **Timeout errors**: Check API key validity and network connection
- See [STREAMING.md](STREAMING.md) for detailed troubleshooting

### API Key Issues
- Verify API key is correct for the selected provider
- Check provider API status
- Ensure API key has necessary permissions
- For Gemini, ensure `google-generativeai` package is installed

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
