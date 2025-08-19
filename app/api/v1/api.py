"""
Main API router for Voice AI Demo
Includes all voice AI, telephony, and healthcare endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import voice_ai, twilio, calls, analytics, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(voice_ai.router, prefix="/voice-ai", tags=["voice-ai"])
api_router.include_router(twilio.router, prefix="/twilio", tags=["twilio"])
api_router.include_router(calls.router, prefix="/calls", tags=["calls"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
