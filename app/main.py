"""
Voice AI Prompt Engineering Demo - Main Application
FastAPI backend with HIPAA compliance and voice AI integration
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import os
from typing import Dict, Any

from app.core.config import settings
from app.core.security import verify_token
from app.api.v1.api import api_router
from app.core.database import init_db
from app.core.redis_client import init_redis
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Voice AI application...")
    await init_db()
    await init_redis()
    logger.info("Voice AI application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Voice AI application...")

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Voice AI Prompt Engineering Demo",
        description="Healthcare billing automation with voice AI and HIPAA compliance",
        version="1.0.0",
        docs_url="/docs" if not settings.PRODUCTION else None,
        redoc_url="/redoc" if not settings.PRODUCTION else None,
        lifespan=lifespan
    )
    
    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "voice-ai-demo",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with service information"""
        return {
            "message": "Voice AI Prompt Engineering Demo",
            "description": "Healthcare billing automation with voice AI",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Protected endpoint example
    @app.get("/protected")
    async def protected_endpoint(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Example protected endpoint"""
        try:
            payload = verify_token(credentials.credentials)
            return {
                "message": "Access granted",
                "user_id": payload.get("sub"),
                "permissions": payload.get("permissions", [])
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    
    return app

# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
