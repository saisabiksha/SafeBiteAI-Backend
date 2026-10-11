"""Configuration settings for SafeBiteAI Backend."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Directory paths
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR / "data"

# Load environment variables from the backend root .env file
ENV_FILE = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)

PROJECT_NAME = "SafeBiteAI Backend"
PROJECT_DESCRIPTION = "Backend API for SafeBiteAI"
PROJECT_VERSION = "1.0.0"

# Database configuration (Dedicated backend data directory)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'safebiteai.db'}"

# Gemini configuration (Loaded securely without logging or exposing)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Allowed origins for Cross-Origin Resource Sharing (CORS)
# Strictly restricted to local Vite frontend development servers
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
