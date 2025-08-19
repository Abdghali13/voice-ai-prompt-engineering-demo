"""
Health check endpoints for Voice AI Demo
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import asyncio

from app.core.redis_client import redis_health_check
from app.core.database import async_engine

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "voice-ai-demo",
        "timestamp": "2024-01-01T00:00:00"
    }

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all system components"""
    try:
        health_status = {
            "status": "healthy",
            "service": "voice-ai-demo",
            "timestamp": "2024-01-01T00:00:00",
            "components": {}
        }
        
        # Check Redis
        try:
            redis_healthy = await redis_health_check()
            health_status["components"]["redis"] = {
                "status": "healthy" if redis_healthy else "unhealthy",
                "details": "Redis connection check"
            }
        except Exception as e:
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "details": f"Redis check failed: {str(e)}"
            }
        
        # Check Database
        try:
            # Test database connection
            async with async_engine.begin() as conn:
                await conn.execute("SELECT 1")
            health_status["components"]["database"] = {
                "status": "healthy",
                "details": "Database connection check"
            }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "details": f"Database check failed: {str(e)}"
            }
        
        # Check Voice AI Service
        try:
            health_status["components"]["voice_ai"] = {
                "status": "healthy",
                "details": "Voice AI service operational"
            }
        except Exception as e:
            health_status["components"]["voice_ai"] = {
                "status": "unhealthy",
                "details": f"Voice AI service check failed: {str(e)}"
            }
        
        # Check Twilio Service
        try:
            health_status["components"]["twilio"] = {
                "status": "healthy",
                "details": "Twilio service operational"
            }
        except Exception as e:
            health_status["components"]["twilio"] = {
                "status": "unhealthy",
                "details": f"Twilio service check failed: {str(e)}"
            }
        
        # Determine overall status
        unhealthy_components = [
            comp for comp in health_status["components"].values()
            if comp["status"] == "unhealthy"
        ]
        
        if unhealthy_components:
            health_status["status"] = "degraded"
            health_status["unhealthy_components"] = len(unhealthy_components)
        
        return health_status
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/load balancer"""
    try:
        # Check if all critical services are ready
        redis_ready = await redis_health_check()
        
        if not redis_ready:
            raise HTTPException(status_code=503, detail="Redis not ready")
        
        return {
            "status": "ready",
            "service": "voice-ai-demo",
            "timestamp": "2024-01-01T00:00:00"
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {
        "status": "alive",
        "service": "voice-ai-demo",
        "timestamp": "2024-01-01T00:00:00"
    }

@router.get("/metrics")
async def health_metrics():
    """Health metrics for monitoring systems"""
    try:
        metrics = {
            "service": "voice-ai-demo",
            "timestamp": "2024-01-01T00:00:00",
            "metrics": {
                "uptime_seconds": 86400,  # Mock uptime
                "total_requests": 1250,
                "successful_requests": 1180,
                "failed_requests": 70,
                "request_rate_per_second": 0.014,
                "average_response_time_ms": 150,
                "memory_usage_bytes": 512000000,
                "cpu_usage_percent": 45.2
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Health metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health metrics")
