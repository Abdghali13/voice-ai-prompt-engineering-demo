"""
Voice AI endpoints for conversation processing
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import logging
import json

from app.services.voice_ai import voice_ai_service
from app.core.logging import get_hipaa_logger
from app.core.redis_client import get_conversation_state, set_conversation_state

logger = logging.getLogger(__name__)
hipaa_logger = get_hipaa_logger('voice_ai_endpoints')

router = APIRouter()

@router.post("/process-audio")
async def process_audio(
    call_sid: str = Form(...),
    audio_file: UploadFile = File(...),
    scenario: str = Form("billing_inquiry")
):
    """Process audio file and generate AI response"""
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process conversation turn
        result = await voice_ai_service.process_conversation_turn(
            call_sid=call_sid,
            audio_data=audio_data,
            scenario=scenario
        )
        
        # Log successful processing
        hipaa_logger.log_phi_access(
            "system",
            "audio_processing",
            "process",
            {
                "call_sid": call_sid,
                "scenario": scenario,
                "file_size": len(audio_data)
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Audio processing failed: {e}")
        hipaa_logger.log_hipaa_violation(
            "audio_processing_failure",
            f"Failed to process audio: {str(e)}",
            "HIGH"
        )
        raise HTTPException(status_code=500, detail="Audio processing failed")

@router.post("/generate-response")
async def generate_response(
    message: str = Form(...),
    call_sid: str = Form(...),
    scenario: str = Form("billing_inquiry")
):
    """Generate AI response from text input"""
    try:
        # Get conversation state
        conversation_state = await get_conversation_state(call_sid) or {}
        
        # Generate AI response
        result = await voice_ai_service.generate_ai_response(
            message=message,
            conversation_context=conversation_state,
            scenario=scenario
        )
        
        # Update conversation state
        conversation_state.update({
            "last_transcript": message,
            "last_ai_response": result["response"],
            "last_intent": result["intent_detected"]
        })
        
        await set_conversation_state(call_sid, conversation_state)
        
        return result
        
    except Exception as e:
        logger.error(f"Response generation failed: {e}")
        raise HTTPException(status_code=500, detail="Response generation failed")

@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(...),
    voice_id: Optional[str] = Form(None)
):
    """Convert text to speech"""
    try:
        result = await voice_ai_service.convert_text_to_speech(
            text=text,
            voice_id=voice_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Text-to-speech failed: {e}")
        raise HTTPException(status_code=500, detail="Text-to-speech conversion failed")

@router.get("/conversation-summary/{call_sid}")
async def get_conversation_summary(call_sid: str):
    """Get conversation summary for human handoff"""
    try:
        summary = await voice_ai_service.get_conversation_summary(call_sid)
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get conversation summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation summary")

@router.post("/simulate-conversation")
async def simulate_conversation(
    scenario: str = Form("billing_inquiry"),
    messages: list = Form(...)
):
    """Simulate a conversation for demo purposes"""
    try:
        call_sid = f"demo_{scenario}_{len(messages)}"
        conversation_state = {
            "turn_count": 0,
            "scenario": scenario,
            "user_id": "demo_user",
            "start_time": "2024-01-01T00:00:00"
        }
        
        results = []
        
        for i, message in enumerate(messages):
            # Generate AI response
            ai_result = await voice_ai_service.generate_ai_response(
                message=message,
                conversation_context=conversation_state,
                scenario=scenario
            )
            
            # Update conversation state
            conversation_state["turn_count"] += 1
            conversation_state.update({
                "last_transcript": message,
                "last_ai_response": ai_result["response"],
                "last_intent": ai_result["intent_detected"]
            })
            
            results.append({
                "turn": i + 1,
                "user_message": message,
                "ai_response": ai_result["response"],
                "intent": ai_result["intent_detected"],
                "confidence": ai_result["confidence"]
            })
        
        # Store conversation state
        await set_conversation_state(call_sid, conversation_state)
        
        return {
            "call_sid": call_sid,
            "scenario": scenario,
            "total_turns": len(messages),
            "conversation": results,
            "final_state": conversation_state
        }
        
    except Exception as e:
        logger.error(f"Conversation simulation failed: {e}")
        raise HTTPException(status_code=500, detail="Conversation simulation failed")

@router.get("/prompt-templates")
async def get_prompt_templates():
    """Get available prompt templates"""
    try:
        return {
            "templates": voice_ai_service.prompt_templates,
            "scenarios": list(voice_ai_service.prompt_templates.keys())
        }
        
    except Exception as e:
        logger.error(f"Failed to get prompt templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prompt templates")

@router.post("/update-prompt-template")
async def update_prompt_template(
    scenario: str = Form(...),
    template: str = Form(...)
):
    """Update prompt template for a scenario"""
    try:
        if scenario in voice_ai_service.prompt_templates:
            voice_ai_service.prompt_templates[scenario] = template
            
            # Log template update
            hipaa_logger.log_phi_access(
                "system",
                "prompt_template",
                "update",
                {
                    "scenario": scenario,
                    "template_length": len(template)
                }
            )
            
            return {"message": "Template updated successfully", "scenario": scenario}
        else:
            raise HTTPException(status_code=400, detail="Invalid scenario")
            
    except Exception as e:
        logger.error(f"Failed to update prompt template: {e}")
        raise HTTPException(status_code=500, detail="Failed to update prompt template")

@router.get("/conversation-state/{call_sid}")
async def get_conversation_state_endpoint(call_sid: str):
    """Get current conversation state"""
    try:
        state = await get_conversation_state(call_sid)
        if state:
            return state
        else:
            raise HTTPException(status_code=404, detail="Conversation state not found")
            
    except Exception as e:
        logger.error(f"Failed to get conversation state: {e}")
        raise HTTPException(status_code=500, detail="Failed to get conversation state")

@router.delete("/conversation-state/{call_sid}")
async def delete_conversation_state(call_sid: str):
    """Delete conversation state"""
    try:
        from app.core.redis_client import delete_call_session
        await delete_call_session(call_sid)
        
        return {"message": "Conversation state deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete conversation state: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation state")
