import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "InterviewAce AI Backend"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./interview_ace.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "interview_ace_secret_key_extremely_secure_128bit")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 1 day
    
    # GROQ API Configurations
    GROQ_API_KEY: str = os.getenv(
        "GROQ_API_KEY", 
        "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"
    )
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    
    class Config:
        case_sensitive = True

settings = Settings()
