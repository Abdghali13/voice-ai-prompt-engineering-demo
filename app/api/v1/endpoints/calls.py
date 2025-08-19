"""
Call management endpoints for Voice AI Demo
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.core.logging import get_hipaa_logger
from app.core.redis_client import get_call_session, get_conversation_state

logger = logging.getLogger(__name__)
hipaa_logger = get_hipaa_logger('calls_endpoints')

router = APIRouter()

@router.get("/active")
async def get_active_calls():
    """Get list of active calls"""
    try:
        # In a real implementation, this would query the database
        # For demo purposes, return mock data
        active_calls = [
            {
                "call_sid": "demo_call_001",
                "phone_number": "+1-555-0123",
                "status": "in-progress",
                "duration": 120,
                "scenario": "billing_inquiry",
                "start_time": "2024-01-01T10:00:00"
            },
            {
                "call_sid": "demo_call_002",
                "phone_number": "+1-555-0456",
                "status": "ringing",
                "duration": 0,
                "scenario": "insurance_verification",
                "start_time": "2024-01-01T10:05:00"
            }
        ]
        
        return {"active_calls": active_calls, "total": len(active_calls)}
        
    except Exception as e:
        logger.error(f"Failed to get active calls: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active calls")

@router.get("/{call_sid}")
async def get_call_details(call_sid: str):
    """Get detailed information about a specific call"""
    try:
        # Get call session data
        session_data = await get_call_session(call_sid)
        conversation_state = await get_conversation_state(call_sid)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Combine session and conversation data
        call_details = {
            "call_sid": call_sid,
            "session_data": session_data,
            "conversation_state": conversation_state,
            "metadata": {
                "retrieved_at": datetime.now().isoformat(),
                "data_source": "redis_cache"
            }
        }
        
        return call_details
        
    except Exception as e:
        logger.error(f"Failed to get call details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call details")

@router.get("/{call_sid}/transcript")
async def get_call_transcript(call_sid: str):
    """Get call transcript"""
    try:
        conversation_state = await get_conversation_state(call_sid)
        
        if not conversation_state:
            raise HTTPException(status_code=404, detail="Call transcript not found")
        
        transcript = {
            "call_sid": call_sid,
            "total_turns": conversation_state.get("turn_count", 0),
            "scenario": conversation_state.get("scenario", "unknown"),
            "segments": [
                {
                    "turn": 1,
                    "speaker": "patient",
                    "text": conversation_state.get("last_transcript", "No transcript available"),
                    "timestamp": conversation_state.get("start_time", "Unknown")
                },
                {
                    "turn": 1,
                    "speaker": "ai",
                    "text": conversation_state.get("last_ai_response", "No response available"),
                    "timestamp": conversation_state.get("start_time", "Unknown")
                }
            ]
        }
        
        return transcript
        
    except Exception as e:
        logger.error(f"Failed to get call transcript: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call transcript")

@router.get("/{call_sid}/analytics")
async def get_call_analytics(call_sid: str):
    """Get analytics for a specific call"""
    try:
        conversation_state = await get_conversation_state(call_sid)
        
        if not conversation_state:
            raise HTTPException(status_code=404, detail="Call analytics not found")
        
        analytics = {
            "call_sid": call_sid,
            "metrics": {
                "total_turns": conversation_state.get("turn_count", 0),
                "conversation_duration": "2:30",  # Mock duration
                "intent_detection_confidence": conversation_state.get("confidence", 0.0),
                "human_escalation": conversation_state.get("requires_human", False)
            },
            "intent_analysis": {
                "primary_intent": conversation_state.get("last_intent", "unknown"),
                "intent_confidence": conversation_state.get("confidence", 0.0),
                "intent_changes": 0
            },
            "quality_metrics": {
                "ai_response_quality": "high",
                "patient_satisfaction": "estimated_high",
                "resolution_rate": "estimated_80_percent"
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Failed to get call analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call analytics")

@router.get("/summary/daily")
async def get_daily_call_summary(
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """Get daily call summary"""
    try:
        # Mock daily summary data
        daily_summary = {
            "date": date,
            "total_calls": 45,
            "completed_calls": 42,
            "abandoned_calls": 3,
            "average_duration": "3:45",
            "scenarios": {
                "billing_inquiry": 25,
                "insurance_verification": 12,
                "appointment_scheduling": 8
            },
            "ai_performance": {
                "successful_resolutions": 38,
                "human_escalations": 4,
                "average_confidence": 0.87
            },
            "hipaa_compliance": {
                "consent_verified": 100,
                "phi_access_logged": 100,
                "audit_trails_complete": 100
            }
        }
        
        return daily_summary
        
    except Exception as e:
        logger.error(f"Failed to get daily call summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily call summary")

@router.get("/summary/weekly")
async def get_weekly_call_summary(
    week_start: str = Query(..., description="Week start date in YYYY-MM-DD format")
):
    """Get weekly call summary"""
    try:
        # Mock weekly summary data
        weekly_summary = {
            "week_start": week_start,
            "total_calls": 315,
            "average_daily_calls": 45,
            "peak_day": "Wednesday",
            "peak_hour": "10:00 AM",
            "scenario_distribution": {
                "billing_inquiry": 175,
                "insurance_verification": 84,
                "appointment_scheduling": 56
            },
            "performance_metrics": {
                "average_resolution_time": "2:15",
                "customer_satisfaction": "4.2/5.0",
                "cost_per_call": "$0.85"
            }
        }
        
        return weekly_summary
        
    except Exception as e:
        logger.error(f"Failed to get weekly call summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weekly call summary")

@router.post("/{call_sid}/escalate")
async def escalate_call(call_sid: str, reason: str = "manual_escalation"):
    """Manually escalate a call to human agent"""
    try:
        # Update conversation state
        conversation_state = await get_conversation_state(call_sid) or {}
        conversation_state.update({
            "requires_human": True,
            "escalation_reason": reason,
            "escalated_at": datetime.now().isoformat()
        })
        
        # In a real implementation, this would trigger TaskRouter
        escalation_result = {
            "call_sid": call_sid,
            "escalated": True,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "agent_queue": "healthcare_support"
        }
        
        return escalation_result
        
    except Exception as e:
        logger.error(f"Failed to escalate call: {e}")
        raise HTTPException(status_code=500, detail="Failed to escalate call")

@router.delete("/{call_sid}")
async def delete_call_data(call_sid: str):
    """Delete call data (for demo purposes)"""
    try:
        # In production, this would implement proper data retention policies
        # For demo, we'll just return success
        
        hipaa_logger.log_phi_access(
            "system",
            "call_data",
            "delete",
            {"call_sid": call_sid}
        )
        
        return {"message": "Call data deleted successfully", "call_sid": call_sid}
        
    except Exception as e:
        logger.error(f"Failed to delete call data: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete call data")
