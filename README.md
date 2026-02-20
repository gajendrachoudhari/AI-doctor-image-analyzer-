# CHATBOT PYTHON - Medical Image Analysis App

A FastAPI-based web application for analyzing medical images and providing health information.

## Quick Start

### Option 1: Run via Batch File (Windows)
Double-click `start.bat` to launch the server on port 8001.

### Option 2: Command Line
```powershell
python -m uvicorn app:app --host 127.0.0.1 --port 8001
```

### Option 3: Python Script
```powershell
python run_at_7pm.py --now
```

## Access the App
- **Web UI:** http://127.0.0.1:8001
- **Health Check:** http://127.0.0.1:8001/health
- **API Endpoint:** POST http://127.0.0.1:8001/upload_and_query

## Configuration

The `.env` file controls behavior:

- `GROQ_API_KEY` - Your GROQ API key (if using real API)
- `MOCK_MODE=true` (current) - Uses local mock responses (no API call)
- `MOCK_MODE=false` - Uses GROQ API (requires valid GROQ_API_KEY)
- `GROQ_MODEL` - Model name (default: `mixtral-8x7b-32768`)
- `GROQ_ALT_MODEL` - Fallback model if primary fails (optional)

## Features

✅ **Image Upload** - Upload medical images for analysis  
✅ **Hinglish Support** - Understands English, Hindi-English (Hinglish), and typos  
✅ **Dual Responses** - Condition analysis + medicine/treatment suggestions  
✅ **Mock Mode** - Works offline with pre-configured responses  
✅ **Health Endpoint** - Check server status and configuration  

## Current Status

✅ **Everything Working** - App is in MOCK_MODE (no external API dependency)
- Upload & query endpoint: Ready
- Web UI: Ready
- All responses: Working perfectly
