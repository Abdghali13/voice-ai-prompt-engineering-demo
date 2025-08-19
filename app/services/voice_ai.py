"""
Voice AI Service for Healthcare Billing Automation
Integrates OpenAI GPT-4, AWS Transcribe, and AWS Polly
"""

import openai
import boto3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from io import BytesIO

from app.core.config import settings
from app.core.logging import get_hipaa_logger
from app.core.redis_client import set_conversation_state, get_conversation_state

logger = logging.getLogger(__name__)
hipaa_logger = get_hipaa_logger('voice_ai')

# Initialize OpenAI client
openai.api_key = settings.OPENAI_API_KEY

# Initialize AWS clients
transcribe_client = boto3.client(
    'transcribe',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

polly_client = boto3.client(
    'polly',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

class VoiceAIService:
    """Main service for voice AI operations"""
    
    def __init__(self):
        self.conversation_contexts = {}
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different healthcare scenarios"""
        return {
            "billing_inquiry": """You are a helpful healthcare billing assistant. Your role is to:
1. Help patients understand their medical bills
2. Verify insurance information
3. Explain charges and payment options
4. Schedule payment arrangements
5. Escalate complex issues to human agents

Current conversation context: {context}

Patient's message: {message}

Respond naturally and helpfully. If you need more information, ask specific questions. If the issue is complex, offer to connect them with a human agent.

Remember: Always maintain HIPAA compliance and only access necessary information.""",
            
            "insurance_verification": """You are a healthcare insurance verification specialist. Your role is to:
1. Verify insurance eligibility
2. Check coverage for specific procedures
3. Explain benefits and limitations
4. Handle pre-authorization requests
5. Provide claims status updates

Current conversation context: {context}

Patient's message: {message}

Respond professionally and clearly. If you need specific information, ask for it. For complex insurance issues, offer human assistance.""",
            
            "appointment_scheduling": """You are a healthcare appointment scheduler. Your role is to:
1. Find available appointment slots
2. Verify insurance coverage
3. Confirm appointment details
4. Send confirmation information
5. Handle rescheduling requests

Current conversation context: {context}

Patient's message: {message}

Be helpful and efficient. Confirm all details before finalizing appointments. Offer alternatives if requested times aren't available."""
        }
    
    async def process_speech_to_text(self, audio_data: bytes, language: str = "en-US") -> Dict[str, Any]:
        """Process audio to text using AWS Transcribe Medical"""
        try:
            # For demo purposes, we'll simulate transcription
            # In production, this would use AWS Transcribe Medical
            
            # Simulate transcription delay
            await asyncio.sleep(0.5)
            
            # Mock transcription result
            transcription_result = {
                "transcript": "I have a question about my medical bill",
                "confidence": 0.95,
                "language_code": language,
                "segments": [
                    {
                        "start_time": 0.0,
                        "end_time": 3.5,
                        "text": "I have a question about my medical bill",
                        "confidence": 0.95
                    }
                ]
            }
            
            hipaa_logger.log_data_encryption(
                "audio_transcription",
                "aws_transcribe_medical",
                True
            )
            
            return transcription_result
            
        except Exception as e:
            logger.error(f"Speech-to-text processing failed: {e}")
            hipaa_logger.log_hipaa_violation(
                "transcription_failure",
                f"STT processing failed: {str(e)}",
                "MEDIUM"
            )
            raise
    
    async def generate_ai_response(
        self, 
        message: str, 
        conversation_context: Dict[str, Any],
        scenario: str = "billing_inquiry"
    ) -> Dict[str, Any]:
        """Generate AI response using OpenAI GPT-4"""
        try:
            # Get appropriate prompt template
            template = self.prompt_templates.get(scenario, self.prompt_templates["billing_inquiry"])
            
            # Prepare conversation context
            context_str = json.dumps(conversation_context, indent=2)
            
            # Format prompt
            formatted_prompt = template.format(
                context=context_str,
                message=message
            )
            
            # Add system message for HIPAA compliance
            system_message = {
                "role": "system",
                "content": "You are a HIPAA-compliant healthcare assistant. Never share PHI, always verify consent, and maintain patient privacy."
            }
            
            user_message = {
                "role": "user",
                "content": formatted_prompt
            }
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=settings.OPENAI_MODEL,
                messages=[system_message, user_message],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE
            )
            
            ai_response = response.choices[0].message.content
            
            # Log the interaction for audit
            hipaa_logger.log_phi_access(
                conversation_context.get("user_id", "unknown"),
                "ai_conversation",
                "generate_response",
                {
                    "scenario": scenario,
                    "message_length": len(message),
                    "response_length": len(ai_response)
                }
            )
            
            return {
                "response": ai_response,
                "confidence": 0.9,
                "intent_detected": self._detect_intent(message),
                "requires_human": self._should_escalate_to_human(ai_response, conversation_context)
            }
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            hipaa_logger.log_hipaa_violation(
                "ai_response_failure",
                f"OpenAI API call failed: {str(e)}",
                "HIGH"
            )
            raise
    
    async def convert_text_to_speech(self, text: str, voice_id: str = None) -> Dict[str, Any]:
        """Convert text to speech using AWS Polly"""
        try:
            voice_id = voice_id or settings.AWS_POLLY_VOICE_ID
            
            # For demo purposes, we'll simulate TTS
            # In production, this would use AWS Polly
            
            # Simulate TTS processing delay
            await asyncio.sleep(0.3)
            
            # Mock TTS result
            tts_result = {
                "audio_url": f"/audio/generated_{datetime.now().timestamp()}.mp3",
                "duration": len(text.split()) * 0.5,  # Rough estimate
                "voice_id": voice_id,
                "text_length": len(text)
            }
            
            hipaa_logger.log_data_encryption(
                "text_to_speech",
                "aws_polly",
                True
            )
            
            return tts_result
            
        except Exception as e:
            logger.error(f"Text-to-speech conversion failed: {e}")
            hipaa_logger.log_hipaa_violation(
                "tts_failure",
                f"Polly API call failed: {str(e)}",
                "MEDIUM"
            )
            raise
    
    def _detect_intent(self, message: str) -> str:
        """Detect intent from user message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["bill", "charge", "payment", "cost"]):
            return "billing_inquiry"
        elif any(word in message_lower for word in ["insurance", "coverage", "benefit"]):
            return "insurance_verification"
        elif any(word in message_lower for word in ["appointment", "schedule", "booking"]):
            return "appointment_scheduling"
        elif any(word in message_lower for word in ["complaint", "issue", "problem"]):
            return "complaint_handling"
        else:
            return "general_inquiry"
    
    def _should_escalate_to_human(self, ai_response: str, context: Dict[str, Any]) -> bool:
        """Determine if conversation should be escalated to human"""
        # Check for complex scenarios
        complex_keywords = [
            "escalate", "human", "agent", "supervisor", "manager",
            "complex", "complicated", "detailed", "specific"
        ]
        
        if any(keyword in ai_response.lower() for keyword in complex_keywords):
            return True
        
        # Check conversation length
        if context.get("turn_count", 0) > 5:
            return True
        
        # Check for sensitive topics
        sensitive_topics = ["legal", "complaint", "dispute", "appeal"]
        if any(topic in ai_response.lower() for topic in sensitive_topics):
            return True
        
        return False
    
    async def process_conversation_turn(
        self, 
        call_sid: str, 
        audio_data: bytes, 
        scenario: str = "billing_inquiry"
    ) -> Dict[str, Any]:
        """Process a complete conversation turn"""
        try:
            # Get conversation state
            conversation_state = await get_conversation_state(call_sid) or {
                "turn_count": 0,
                "scenario": scenario,
                "user_id": None,
                "start_time": datetime.now().isoformat()
            }
            
            # Increment turn count
            conversation_state["turn_count"] += 1
            
            # Process speech to text
            stt_result = await self.process_speech_to_text(audio_data)
            
            # Generate AI response
            ai_result = await self.generate_ai_response(
                stt_result["transcript"],
                conversation_state,
                scenario
            )
            
            # Convert response to speech
            tts_result = await self.convert_text_to_speech(ai_result["response"])
            
            # Update conversation state
            conversation_state.update({
                "last_transcript": stt_result["transcript"],
                "last_ai_response": ai_result["response"],
                "last_intent": ai_result["intent_detected"],
                "requires_human": ai_result["requires_human"]
            })
            
            await set_conversation_state(call_sid, conversation_state)
            
            return {
                "transcript": stt_result["transcript"],
                "ai_response": ai_result["response"],
                "audio_url": tts_result["audio_url"],
                "intent": ai_result["intent_detected"],
                "confidence": ai_result["confidence"],
                "requires_human": ai_result["requires_human"],
                "turn_count": conversation_state["turn_count"]
            }
            
        except Exception as e:
            logger.error(f"Conversation turn processing failed: {e}")
            raise
    
    async def get_conversation_summary(self, call_sid: str) -> Dict[str, Any]:
        """Get summary of conversation for human agent handoff"""
        try:
            conversation_state = await get_conversation_state(call_sid)
            if not conversation_state:
                return {"error": "No conversation state found"}
            
            return {
                "summary": {
                    "total_turns": conversation_state.get("turn_count", 0),
                    "scenario": conversation_state.get("scenario", "unknown"),
                    "intent": conversation_state.get("last_intent", "unknown"),
                    "key_topics": self._extract_key_topics(conversation_state),
                    "escalation_reason": conversation_state.get("escalation_reason", "None")
                },
                "transcript_highlights": [
                    conversation_state.get("last_transcript", "No transcript available")
                ],
                "recommended_actions": self._get_recommended_actions(conversation_state)
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation summary: {e}")
            raise
    
    def _extract_key_topics(self, conversation_state: Dict[str, Any]) -> List[str]:
        """Extract key topics from conversation"""
        topics = []
        
        if conversation_state.get("last_intent"):
            topics.append(conversation_state["last_intent"])
        
        if conversation_state.get("scenario"):
            topics.append(conversation_state["scenario"])
        
        return topics
    
    def _get_recommended_actions(self, conversation_state: Dict[str, Any]) -> List[str]:
        """Get recommended actions for human agent"""
        actions = []
        
        if conversation_state.get("requires_human"):
            actions.append("Review conversation history")
            actions.append("Verify patient identity")
            actions.append("Address specific concerns")
            actions.append("Provide detailed explanation")
        
        return actions

# Global service instance
voice_ai_service = VoiceAIService()
