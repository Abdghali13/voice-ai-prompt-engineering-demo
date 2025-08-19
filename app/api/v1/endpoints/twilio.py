"""
Twilio endpoints for telephony integration
"""

from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import Response
from typing import Dict, Any, Optional
import logging
import json

from app.services.twilio_service import twilio_service
from app.services.voice_ai import voice_ai_service
from app.core.logging import get_hipaa_logger
from app.core.redis_client import set_call_session, get_call_session

logger = logging.getLogger(__name__)
hipaa_logger = get_hipaa_logger('twilio_endpoints')

router = APIRouter()

@router.post("/webhook")
async def twilio_webhook(
    request: Request,
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    """Handle incoming Twilio webhook"""
    try:
        # Create call session
        session_data = {
            "call_sid": CallSid,
            "from_number": From,
            "to_number": To,
            "status": CallStatus,
            "created_at": "2024-01-01T00:00:00"
        }
        
        await set_call_session(CallSid, session_data)
        
        # Generate TwiML response
        response = twilio_service.create_voice_response(CallSid)
        
        return Response(
            content=str(response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Twilio webhook failed: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.post("/speech-callback/{call_sid}")
async def speech_callback(
    call_sid: str,
    SpeechResult: str = Form(...),
    Confidence: float = Form(...),
    scenario: str = Form("billing_inquiry")
):
    """Handle speech input from Twilio"""
    try:
        # Get conversation state
        conversation_state = await get_call_session(call_sid) or {}
        
        # Generate AI response
        ai_result = await voice_ai_service.generate_ai_response(
            message=SpeechResult,
            conversation_context=conversation_state,
            scenario=scenario
        )
        
        # Update conversation state
        conversation_state.update({
            "last_transcript": SpeechResult,
            "last_ai_response": ai_result["response"],
            "last_intent": ai_result["intent_detected"],
            "confidence": Confidence
        })
        
        await set_call_session(call_sid, conversation_state)
        
        # Check if human handoff is needed
        if ai_result["requires_human"]:
            response = twilio_service.create_human_handoff_response(call_sid)
        else:
            response = twilio_service.create_speech_callback_response(call_sid, ai_result["response"])
        
        return Response(
            content=str(response),
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Speech callback failed: {e}")
        # Return fallback response
        response = twilio_service.create_voice_response(call_sid)
        return Response(
            content=str(response),
            media_type="application/xml"
        )

@router.post("/status-callback")
async def status_callback(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    CallDuration: Optional[int] = Form(None),
    CallPrice: Optional[float] = Form(None)
):
    """Handle call status updates"""
    try:
        details = {
            "duration": CallDuration,
            "price": CallPrice,
            "timestamp": "2024-01-01T00:00:00"
        }
        
        await twilio_service.handle_call_status_update(CallSid, CallStatus, details)
        
        return {"message": "Status update processed"}
        
    except Exception as e:
        logger.error(f"Status callback failed: {e}")
        raise HTTPException(status_code=500, detail="Status update failed")

@router.post("/recording-callback")
async def recording_callback(
    CallSid: str = Form(...),
    RecordingUrl: str = Form(...),
    RecordingSid: str = Form(...)
):
    """Handle recording callbacks"""
    try:
        await twilio_service.handle_recording_callback(CallSid, RecordingUrl, RecordingSid)
        
        return {"message": "Recording callback processed"}
        
    except Exception as e:
        logger.error(f"Recording callback failed: {e}")
        raise HTTPException(status_code=500, detail="Recording callback failed")

@router.post("/initiate-call")
async def initiate_call(
    to_number: str = Form(...),
    workflow_url: str = Form(...)
):
    """Initiate an outbound call"""
    try:
        result = await twilio_service.initiate_call(to_number, workflow_url)
        
        return result
        
    except Exception as e:
        logger.error(f"Call initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Call initiation failed")

@router.get("/call-details/{call_sid}")
async def get_call_details(call_sid: str):
    """Get call details from Twilio"""
    try:
        details = await twilio_service.get_call_details(call_sid)
        
        if details:
            return details
        else:
            raise HTTPException(status_code=404, detail="Call not found")
            
    except Exception as e:
        logger.error(f"Failed to get call details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get call details")

@router.post("/end-call/{call_sid}")
async def end_call(call_sid: str):
    """End an active call"""
    try:
        success = await twilio_service.end_call(call_sid)
        
        if success:
            return {"message": "Call ended successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to end call")
            
    except Exception as e:
        logger.error(f"Failed to end call: {e}")
        raise HTTPException(status_code=500, detail="Failed to end call")

@router.get("/webhook-urls")
async def get_webhook_urls():
    """Get webhook URLs for Twilio configuration"""
    try:
        base_url = "http://localhost:8000"  # In production, use actual domain
        
        urls = {
            "webhook": f"{base_url}/api/v1/twilio/webhook",
            "speech_callback": f"{base_url}/api/v1/twilio/speech-callback/{{call_sid}}",
            "status_callback": f"{base_url}/api/v1/twilio/status-callback",
            "recording_callback": f"{base_url}/api/v1/twilio/recording-callback"
        }
        
        return urls
        
    except Exception as e:
        logger.error(f"Failed to get webhook URLs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get webhook URLs")
