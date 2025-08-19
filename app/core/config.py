"""
Configuration settings for Voice AI Demo
HIPAA compliance and environment configuration
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings with HIPAA compliance"""
    
    # Application
    APP_NAME: str = "Voice AI Prompt Engineering Demo"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    PRODUCTION: bool = False
    
    # Security & HIPAA
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS & Hosts
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/voice_ai_demo"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 1000
    OPENAI_TEMPERATURE: float = 0.7
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "voice-ai-demo-audio"
    AWS_TRANSCRIBE_LANGUAGE: str = "en-US"
    AWS_POLLY_VOICE_ID: str = "Joanna"
    
    # HIPAA Compliance
    HIPAA_ENABLED: bool = True
    ENCRYPTION_KEY: str = "your-encryption-key-change-in-production"
    AUDIT_LOG_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 2555  # 7 years for HIPAA
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    METRICS_ENABLED: bool = True
    
    # Call Settings
    MAX_CALL_DURATION: int = 1800  # 30 minutes
    SILENCE_TIMEOUT: int = 5  # seconds
    HOLD_DETECTION_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "production":
    settings.PRODUCTION = True
    settings.ALLOWED_HOSTS = ["your-domain.com"]
    settings.ALLOWED_ORIGINS = ["https://your-domain.com"]
    settings.LOG_LEVEL = "WARNING"
