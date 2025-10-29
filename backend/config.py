import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-2.0-flash")
    CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    TOP_K = int(os.getenv("TOP_K", "6"))
    MAX_REWRITE_ATTEMPTS = int(os.getenv("MAX_REWRITE_ATTEMPTS", "2"))
    MAX_REFINEMENT_ROUNDS = int(os.getenv("MAX_REFINEMENT_ROUNDS", "2"))
    CRITIQUE_CONFIDENCE_THRESHOLD = float(os.getenv("CRITIQUE_CONFIDENCE_THRESHOLD", "0.9"))
    TRACE_LOG = os.getenv("TRACE_LOG", "./logs/reasoning_traces.jsonl")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))      # Increased for fewer, better chunks
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200")) # ~12.5% overlap
    EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))  # Increased from 4
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///./data/users.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

settings = Settings()
