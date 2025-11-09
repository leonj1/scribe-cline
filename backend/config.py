from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    MYSQL_URL: str = "mysql+pymysql://root:rootpassword@mysql:3306/transcription_db"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google/callback"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # LLM Provider
    LLM_API_KEY: str = ""
    LLM_PROVIDER: str = "requestyai"
    
    # Storage
    AUDIO_STORAGE_PATH: str = "/app/audio_storage"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()