"""
Twilio Service for Voice AI Demo
Telephony integration with call handling and routing
"""

from twilio.rest import Client
from twilio.twiml import VoiceResponse
from twilio.twiml.voice_response import Gather, Say, Dial, Enqueue
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.core.config import settings
from app.core.logging import get_hipaa_logger
from app.core.redis_client import set_call_session, get_call_session, publish_event

logger = logging.getLogger(__name__)
hipaa_logger = get_hipaa_logger('twilio')

class TwilioService:
    """Service for Twilio telephony operations"""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.phone_number = settings.TWILIO_PHONE_NUMBER
    
    async def initiate_call(self, to_number: str, workflow_url: str) -> Dict[str, Any]:
        """Initiate an outbound call"""
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=workflow_url,
                record=True,
                recording_status_callback=f"{settings.BASE_URL}/api/v1/twilio/recording-callback",
                status_callback=f"{settings.BASE_URL}/api/v1/twilio/status-callback",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            # Log call initiation
            hipaa_logger.log_phi_access(
                "system",
                "outbound_call",
                "initiate",
                {
                    "to_number": self._mask_phone_number(to_number),
                    "call_sid": call.sid,
                    "workflow_url": workflow_url
                }
            )
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "to": call.to,
                "from": call.from_
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate call: {e}")
            hipaa_logger.log_hipaa_violation(
                "call_initiation_failure",
                f"Twilio call creation failed: {str(e)}",
                "HIGH"
            )
            raise
    
    def create_voice_response(self, call_sid: str) -> VoiceResponse:
        """Create TwiML voice response for call handling"""
        response = VoiceResponse()
        
        # Add HIPAA compliance notice
        response.say(
            "This call may be recorded for quality assurance and HIPAA compliance purposes.",
            voice="alice"
        )
        
        # Add welcome message
        response.say(
            "Welcome to our healthcare billing assistance line. How can I help you today?",
            voice="alice"
        )
        
        # Add gather input for speech
        gather = Gather(
            input='speech',
            action=f'/api/v1/twilio/speech-callback/{call_sid}',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        
        gather.say(
            "Please state your question or concern.",
            voice="alice"
        )
        
        response.append(gather)
        
        # Fallback if no speech detected
        response.say(
            "I didn't hear anything. Please call back and try again.",
            voice="alice"
        )
        
        return response
    
    def create_speech_callback_response(self, call_sid: str, ai_response: str) -> VoiceResponse:
        """Create response for speech callback with AI-generated content"""
        response = VoiceResponse()
        
        # Play AI response
        response.say(ai_response, voice="alice")
        
        # Ask if they need more help
        response.say(
            "Is there anything else I can help you with?",
            voice="alice"
        )
        
        # Gather next input
        gather = Gather(
            input='speech',
            action=f'/api/v1/twilio/speech-callback/{call_sid}',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        
        gather.say(
            "Please let me know if you need further assistance or say goodbye to end the call.",
            voice="alice"
        )
        
        response.append(gather)
        
        # Handle goodbye or no input
        response.say(
            "Thank you for calling. Have a great day!",
            voice="alice"
        )
        
        return response
    
    def create_human_handoff_response(self, call_sid: str, queue_name: str = "healthcare_support") -> VoiceResponse:
        """Create response for human agent handoff"""
        response = VoiceResponse()
        
        response.say(
            "I'm connecting you to a human agent who can better assist you with your request.",
            voice="alice"
        )
        
        # Enqueue call to human agent
        enqueue = Enqueue(queue_name)
        enqueue.parameter(name="call_sid", value=call_sid)
        enqueue.parameter(name="escalation_reason", value="AI_ESCALATION")
        
        response.append(enqueue)
        
        return response
    
    def create_hold_music_response(self) -> VoiceResponse:
        """Create response for hold music"""
        response = VoiceResponse()
        
        response.say(
            "Please hold while we connect you to an agent. Your call is important to us.",
            voice="alice"
        )
        
        # Add hold music (in production, this would be a music file)
        response.play("https://example.com/hold-music.mp3")
        
        return response
    
    async def handle_call_status_update(self, call_sid: str, status: str, details: Dict[str, Any]):
        """Handle call status updates from Twilio"""
        try:
            # Update call session
            session_data = await get_call_session(call_sid) or {}
            session_data.update({
                "status": status,
                "last_updated": datetime.now().isoformat(),
                "twilio_details": details
            })
            
            await set_call_session(call_sid, session_data)
            
            # Publish event for real-time updates
            await publish_event("call_status_updates", {
                "call_sid": call_sid,
                "status": status,
                "timestamp": datetime.now().isoformat(),
                "details": details
            })
            
            # Log status change
            hipaa_logger.log_phi_access(
                "system",
                "call_status",
                "update",
                {
                    "call_sid": call_sid,
                    "status": status,
                    "details": details
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to handle call status update: {e}")
    
    async def handle_recording_callback(self, call_sid: str, recording_url: str, recording_sid: str):
        """Handle recording callback from Twilio"""
        try:
            # Store recording information
            session_data = await get_call_session(call_sid) or {}
            session_data.update({
                "recording_url": recording_url,
                "recording_sid": recording_sid,
                "recording_created": datetime.now().isoformat()
            })
            
            await set_call_session(call_sid, session_data)
            
            # Log recording creation
            hipaa_logger.log_data_encryption(
                "call_recording",
                "twilio_recording",
                True
            )
            
        except Exception as e:
            logger.error(f"Failed to handle recording callback: {e}")
    
    def _mask_phone_number(self, phone: str) -> str:
        """Mask phone number for logging"""
        if len(phone) < 10:
            return phone
        return f"{phone[:3]}***{phone[-4:]}"
    
    async def get_call_details(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get call details from Twilio"""
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "to": call.to,
                "from": call.from_,
                "duration": call.duration,
                "start_time": call.start_time.isoformat() if call.start_time else None,
                "end_time": call.end_time.isoformat() if call.end_time else None,
                "price": call.price,
                "price_unit": call.price_unit
            }
            
        except Exception as e:
            logger.error(f"Failed to get call details: {e}")
            return None
    
    async def end_call(self, call_sid: str) -> bool:
        """End an active call"""
        try:
            call = self.client.calls(call_sid).update(status="completed")
            
            # Log call termination
            hipaa_logger.log_phi_access(
                "system",
                "call_termination",
                "end_call",
                {
                    "call_sid": call_sid,
                    "final_status": call.status
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to end call: {e}")
            return False
    
    def create_workflow_webhook_url(self, endpoint: str) -> str:
        """Create webhook URL for Twilio workflow"""
        base_url = settings.BASE_URL.rstrip('/')
        return f"{base_url}{endpoint}"
    
    async def validate_webhook_signature(self, signature: str, url: str, params: Dict[str, Any]) -> bool:
        """Validate Twilio webhook signature for security"""
        try:
            # In production, implement proper signature validation
            # For demo purposes, we'll return True
            return True
        except Exception as e:
            logger.error(f"Webhook signature validation failed: {e}")
            return False

# Global service instance
twilio_service = TwilioService()
