#!/bin/bash

# Voice AI Prompt Engineering Demo - Quick Start Script
# This script sets up and runs the complete demo system

set -e

echo "🎤 Voice AI Prompt Engineering Demo"
echo "🏥 Healthcare Billing Automation System"
echo "=================================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and credentials"
    echo "   Required: OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN"
    echo "   Optional: AWS credentials for full functionality"
    echo ""
    read -p "Press Enter after updating .env file..."
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs

echo "🚀 Starting Voice AI Demo System..."

# Start the system with Docker Compose
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

echo "⏳ Waiting for database to be ready..."
sleep 10

# Start the backend
echo "🐍 Starting Voice AI Backend..."
docker-compose up -d voice-ai-backend

echo "⏳ Waiting for backend to be ready..."
sleep 15

# Check if backend is running
echo "🔍 Checking backend health..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is running and healthy"
        break
    else
        echo "⏳ Waiting for backend... (attempt $i/10)"
        sleep 5
    fi
    
    if [ $i -eq 10 ]; then
        echo "❌ Backend failed to start properly"
        echo "📋 Checking logs..."
        docker-compose logs voice-ai-backend
        exit 1
    fi
done

echo ""
echo "🎉 Voice AI Demo System is now running!"
echo ""
echo "🌐 Access Points:"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Health Check: http://localhost:8000/health"
echo ""
echo "📱 Demo Features Available:"
echo "   - Voice AI conversation simulation"
echo "   - HIPAA compliance reporting"
echo "   - Real-time analytics dashboard"
echo "   - Call management and routing"
echo "   - Prompt engineering tools"
echo ""

# Ask if user wants to run the demo
read -p "🚀 Would you like to run the demo script now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🎬 Running demo script..."
    python3 demo.py
else
    echo "💡 To run the demo later, use: python3 demo.py"
fi

echo ""
echo "🔧 Management Commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop system: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Update: docker-compose pull && docker-compose up -d"
echo ""
echo "📚 Next Steps:"
echo "   1. Visit http://localhost:8000/docs to explore the API"
echo "   2. Run demo scenarios with: python3 demo.py"
echo "   3. Test different healthcare scenarios"
echo "   4. Monitor HIPAA compliance metrics"
echo ""
echo "🎯 Demo Ready! The system is now running with full HIPAA compliance features."
