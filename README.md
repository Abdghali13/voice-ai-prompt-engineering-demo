# Voice AI Prompt Engineering Demo

A comprehensive MVP demonstrating automated administrative calls in healthcare billing using voice AI technology. This demo showcases end-to-end voice workflows with HIPAA-compliant infrastructure.

## 🚀 Features

- **Telephony Integration**: Twilio-based call handling with routing and hold detection
- **Speech-to-Text**: Real-time transcription using AWS Transcribe Medical
- **AI-Powered Conversations**: GPT-4 with prompt engineering for healthcare billing workflows
- **Text-to-Speech**: Natural voice responses using AWS Polly
- **Human Handoff**: Intelligent routing to human agents via TaskRouter
- **HIPAA Compliance**: Encryption, access control, and audit trails
- **Real-time Dashboard**: Monitor calls, view transcripts, and manage workflows
- **Healthcare Integration**: FHIR-compliant data handling and EHR integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Twilio        │    │   FastAPI       │    │   OpenAI        │
│   Telephony     │◄──►│   Backend       │◄──►│   GPT-4         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AWS Transcribe│    │   Redis Cache   │    │   AWS Polly     │
│   STT Pipeline  │    │   & Database    │    │   TTS Engine    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for real-time data
- **AI**: OpenAI GPT-4 for conversation logic
- **Voice**: AWS Transcribe Medical + AWS Polly
- **Telephony**: Twilio for call handling
- **Frontend**: React with TypeScript
- **Infrastructure**: AWS with Terraform
- **Security**: HIPAA/SOC2 compliance features

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- AWS CLI configured
- Twilio account

### 1. Clone and Setup

```bash
git clone <repository-url>
cd voice_aI_prompt_engineering
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 5. Start with Docker (Alternative)

```bash
docker-compose up -d
```

## 📱 Demo Scenarios

### 1. Patient Billing Inquiry
- Patient calls about medical bill
- AI identifies account and explains charges
- Handles payment arrangements
- Schedules follow-up calls

### 2. Insurance Verification
- Automated insurance eligibility checks
- Coverage explanation
- Pre-authorization status
- Claims status updates

### 3. Appointment Scheduling
- Available slot identification
- Insurance verification
- Confirmation and reminders
- Rescheduling requests

## 🔒 HIPAA Compliance Features

- **Encryption**: AES-256 encryption at rest and in transit
- **Access Control**: Role-based permissions with MFA
- **Audit Trails**: Comprehensive logging of all data access
- **Data Retention**: Configurable retention policies
- **Secure APIs**: JWT authentication with refresh tokens
- **Environment Isolation**: Separate dev/staging/prod environments

## 📊 Monitoring & Analytics

- Real-time call metrics
- AI response quality scoring
- Human handoff analytics
- HIPAA compliance reporting
- Performance monitoring
- Error tracking and alerting

## 🧪 Testing

```bash
# Run backend tests
pytest

# Run frontend tests
cd frontend && npm test

# Run integration tests
pytest tests/integration/
```

## 🚀 Deployment

### AWS Deployment

```bash
# Deploy infrastructure
terraform init
terraform plan
terraform apply

# Deploy application
./deploy.sh
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Optional
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379
HIPAA_ENABLED=true
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary and confidential. All rights reserved.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Note**: This is a demo application. For production use, ensure all security measures are properly configured and tested.
# voice-ai-prompt-engineering-demo
