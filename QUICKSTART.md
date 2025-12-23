# Quick Start Guide

## Quick Setup (Windows)

### Backend
```bash
# Option 1: Use the batch script
start_backend.bat

# Option 2: Manual setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
# Option 1: Use the batch script
start_frontend.bat

# Option 2: Manual setup
cd frontend
npm install
npm run dev
```

## Quick Setup (macOS/Linux)

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## First Steps

1. **Start Backend**: Run the backend server (port 8000)
2. **Start Frontend**: Run the frontend dev server (port 5173)
3. **Open Browser**: Navigate to `http://localhost:5173`
4. **Configure API Key**: 
   - Select a provider (OpenAI, Gemini, or OpenRouter)
   - Enter your API key
   - Click "Validate & Load Models"
5. **Select Model**: Choose a model from the list
6. **Start Chatting**: Type a message and press Enter

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

- **Backend won't start**: Check Python version (3.9+), ensure dependencies are installed
- **Frontend won't start**: Check Node.js version (18+), delete `node_modules` and reinstall
- **CORS errors**: Ensure backend is running and CORS settings in `backend/app/main.py` are correct
- **API key validation fails**: Verify the key is correct and the provider service is accessible

