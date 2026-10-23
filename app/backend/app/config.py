import os
from pathlib import Path
from dotenv import load_dotenv

# Base backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "AI-Based Interview Simulator (HR Bot)")
    
    # Primary LLM: Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    
    # Fallback LLM: OpenRouter
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "cohere/north-mini-code:free")
    OPENROUTER_FALLBACK_MODEL: str = os.getenv("OPENROUTER_FALLBACK_MODEL", "local_heuristic")
    
    # Database (MongoDB Atlas for production, SQLite for local dev)
    DATABASE_URL: str = os.getenv("DATABASE_URL", os.getenv("MONGODB_URI", "sqlite:///./interview_simulator.db"))
    MONGODB_URI: str = os.getenv("MONGODB_URI", os.getenv("DATABASE_URL", ""))
    
    # Scoring weights
    WEIGHT_CONFIDENCE: float = float(os.getenv("WEIGHT_CONFIDENCE", "0.30"))
    WEIGHT_CLARITY: float = float(os.getenv("WEIGHT_CLARITY", "0.30"))
    WEIGHT_CONTENT: float = float(os.getenv("WEIGHT_CONTENT", "0.40"))
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key-for-jwt-token")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    
    # Demo Mode (seed sample historical sessions if DB empty)
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")

settings = Settings()
