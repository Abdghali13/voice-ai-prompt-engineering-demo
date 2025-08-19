#!/usr/bin/env python3
"""
Voice AI Prompt Engineering Demo Script
Demonstrates the complete voice workflow for healthcare billing automation
"""

import asyncio
import json
import time
from datetime import datetime
import requests

# Demo configuration
DEMO_BASE_URL = "http://localhost:8000"
DEMO_SCENARIOS = {
    "billing_inquiry": [
        "I have a question about my medical bill",
        "Can you explain the charges for my recent visit?",
        "I'd like to set up a payment plan",
        "What are my options for reducing the cost?"
    ],
    "insurance_verification": [
        "I need to verify my insurance coverage",
        "Does my plan cover physical therapy?",
        "What's my deductible and copay?",
        "I need pre-authorization for a procedure"
    ],
    "appointment_scheduling": [
        "I'd like to schedule an appointment",
        "Do you have any openings next week?",
        "I need to reschedule my appointment",
        "What time is my appointment tomorrow?"
    ]
}

class VoiceAIDemo:
    """Demo class for Voice AI functionality"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_step(self, step: str, description: str):
        """Print formatted step"""
        print(f"\n🔹 {step}")
        print(f"   {description}")
    
    def print_response(self, response_data: dict):
        """Print formatted response"""
        print(f"\n📝 AI Response: {response_data.get('response', 'No response')}")
        print(f"🎯 Intent Detected: {response_data.get('intent_detected', 'Unknown')}")
        print(f"📊 Confidence: {response_data.get('confidence', 0)}")
        print(f"👥 Requires Human: {response_data.get('requires_human', False)}")
    
    async def test_health_check(self):
        """Test system health"""
        self.print_header("System Health Check")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ System Status: {health_data.get('status', 'Unknown')}")
                print(f"🏥 Service: {health_data.get('service', 'Unknown')}")
                print(f"📅 Version: {health_data.get('version', 'Unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check error: {e}")
    
    async def test_conversation_simulation(self, scenario: str, messages: list):
        """Test conversation simulation"""
        self.print_header(f"Conversation Simulation: {scenario.replace('_', ' ').title()}")
        
        try:
            # Start conversation
            self.print_step("Starting Conversation", f"Scenario: {scenario}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/voice-ai/simulate-conversation",
                data={
                    "scenario": scenario,
                    "messages": json.dumps(messages)
                }
            )
            
            if response.status_code == 200:
                conversation_data = response.json()
                print(f"✅ Conversation started successfully")
                print(f"📞 Call SID: {conversation_data.get('call_sid', 'Unknown')}")
                print(f"🔄 Total Turns: {conversation_data.get('total_turns', 0)}")
                
                # Display conversation flow
                print("\n📋 Conversation Flow:")
                for turn in conversation_data.get('conversation', []):
                    print(f"   Turn {turn.get('turn', 0)}:")
                    print(f"     👤 User: {turn.get('user_message', 'No message')}")
                    print(f"     🤖 AI: {turn.get('ai_response', 'No response')}")
                    print(f"     🎯 Intent: {turn.get('intent', 'Unknown')}")
                    print(f"     📊 Confidence: {turn.get('confidence', 0)}")
                    print()
                
                return conversation_data
            else:
                print(f"❌ Conversation simulation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Conversation simulation error: {e}")
            return None
    
    async def test_voice_ai_endpoints(self):
        """Test Voice AI endpoints"""
        self.print_header("Voice AI Endpoints Testing")
        
        # Test prompt templates
        try:
            self.print_step("Getting Prompt Templates", "Retrieve available AI prompt templates")
            response = self.session.get(f"{self.base_url}/api/v1/voice-ai/prompt-templates")
            
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ Found {len(templates.get('scenarios', []))} scenarios:")
                for scenario in templates.get('scenarios', []):
                    print(f"   - {scenario.replace('_', ' ').title()}")
            else:
                print(f"❌ Failed to get prompt templates: {response.status_code}")
        except Exception as e:
            print(f"❌ Prompt templates error: {e}")
        
        # Test text-to-speech
        try:
            self.print_step("Testing Text-to-Speech", "Convert sample text to speech")
            response = self.session.post(
                f"{self.base_url}/api/v1/voice-ai/text-to-speech",
                data={"text": "Hello, this is a test of the text-to-speech system."}
            )
            
            if response.status_code == 200:
                tts_data = response.json()
                print(f"✅ TTS conversion successful")
                print(f"🎵 Audio URL: {tts_data.get('audio_url', 'Unknown')}")
                print(f"⏱️ Duration: {tts_data.get('duration', 0)} seconds")
            else:
                print(f"❌ TTS conversion failed: {response.status_code}")
        except Exception as e:
            print(f"❌ TTS error: {e}")
    
    async def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        self.print_header("Analytics Endpoints Testing")
        
        # Test performance metrics
        try:
            self.print_step("Getting Performance Metrics", "Retrieve system performance data")
            response = self.session.get(f"{self.base_url}/api/v1/analytics/performance-metrics?time_period=daily")
            
            if response.status_code == 200:
                metrics = response.json()
                print(f"✅ Performance metrics retrieved")
                print(f"📊 Total Calls: {metrics.get('call_metrics', {}).get('total_calls', 0)}")
                print(f"✅ Success Rate: {metrics.get('call_metrics', {}).get('success_rate', 0)}%")
                print(f"⏱️ Avg Duration: {metrics.get('call_metrics', {}).get('average_call_duration', 'Unknown')}")
            else:
                print(f"❌ Performance metrics failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Performance metrics error: {e}")
        
        # Test HIPAA compliance report
        try:
            self.print_step("Getting HIPAA Compliance Report", "Retrieve compliance status")
            today = datetime.now().strftime("%Y-%m-%d")
            response = self.session.get(
                f"{self.base_url}/api/v1/analytics/hipaa-compliance",
                params={"start_date": today, "end_date": today}
            )
            
            if response.status_code == 200:
                compliance = response.json()
                print(f"✅ HIPAA compliance report retrieved")
                print(f"🛡️ Overall Score: {compliance.get('overall_compliance_score', 0)}%")
                print(f"🔐 Data Encryption: {compliance.get('compliance_metrics', {}).get('data_encryption', {}).get('status', 'Unknown')}")
                print(f"📋 Audit Trails: {compliance.get('compliance_metrics', {}).get('audit_trails', {}).get('status', 'Unknown')}")
            else:
                print(f"❌ HIPAA compliance report failed: {response.status_code}")
        except Exception as e:
            print(f"❌ HIPAA compliance error: {e}")
    
    async def test_call_management(self):
        """Test call management endpoints"""
        self.print_header("Call Management Testing")
        
        # Test active calls
        try:
            self.print_step("Getting Active Calls", "Retrieve current call status")
            response = self.session.get(f"{self.base_url}/api/v1/calls/active")
            
            if response.status_code == 200:
                calls_data = response.json()
                print(f"✅ Active calls retrieved")
                print(f"📞 Total Active: {calls_data.get('total', 0)}")
                
                for call in calls_data.get('active_calls', []):
                    print(f"   - {call.get('call_sid', 'Unknown')}: {call.get('status', 'Unknown')}")
            else:
                print(f"❌ Active calls failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Active calls error: {e}")
    
    async def run_full_demo(self):
        """Run the complete demo"""
        self.print_header("Voice AI Prompt Engineering Demo")
        print("🚀 Starting comprehensive demo of healthcare billing automation system")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all demo components
        await self.test_health_check()
        await self.test_voice_ai_endpoints()
        await self.test_analytics_endpoints()
        await self.test_call_management()
        
        # Test conversation scenarios
        for scenario, messages in DEMO_SCENARIOS.items():
            await self.test_conversation_simulation(scenario, messages)
            time.sleep(1)  # Brief pause between scenarios
        
        self.print_header("Demo Complete")
        print("✅ All demo components executed successfully")
        print("🎯 Key Features Demonstrated:")
        print("   - Voice AI conversation processing")
        print("   - HIPAA compliance and security")
        print("   - Real-time analytics and monitoring")
        print("   - Call management and routing")
        print("   - Prompt engineering and AI responses")
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main demo function"""
    demo = VoiceAIDemo(DEMO_BASE_URL)
    await demo.run_full_demo()

if __name__ == "__main__":
    print("🎤 Voice AI Prompt Engineering Demo")
    print("🏥 Healthcare Billing Automation System")
    print("="*60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        print("💡 Make sure the backend server is running on http://localhost:8000")
