"""
Database configuration and models for Voice AI Demo
SQLAlchemy with HIPAA compliance
"""

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Database URL for async operations
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=False
)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    echo=False
)

# Session factories
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Base class for models
Base = declarative_base()

async def init_db():
    """Initialize database connection"""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def get_db() -> AsyncSession:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Database Models

class User(Base):
    """User model with HIPAA compliance"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # HIPAA fields
    consent_given = Column(Boolean, default=False)
    purpose_of_use = Column(String(255))
    minimum_necessary = Column(Boolean, default=True)
    
    # Relationships
    calls = relationship("Call", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Call(Base):
    """Call model for voice interactions"""
    __tablename__ = "calls"
    
    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    phone_number = Column(String(20), nullable=False)
    call_type = Column(String(50), default="billing_inquiry")
    status = Column(String(50), default="initiated")
    duration = Column(Integer, default=0)  # seconds
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    
    # Voice AI fields
    transcription = Column(Text)
    ai_response = Column(Text)
    intent_detected = Column(String(100))
    confidence_score = Column(Integer)
    human_handoff = Column(Boolean, default=False)
    
    # HIPAA fields
    phi_data_accessed = Column(Boolean, default=False)
    consent_verified = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="calls")
    transcript_segments = relationship("TranscriptSegment", back_populates="call")
    audio_files = relationship("AudioFile", back_populates="call")

class TranscriptSegment(Base):
    """Individual transcript segments for detailed analysis"""
    __tablename__ = "transcript_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    segment_number = Column(Integer, nullable=False)
    speaker = Column(String(20), default="patient")  # patient, ai, agent
    text = Column(Text, nullable=False)
    confidence = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="transcript_segments")

class AudioFile(Base):
    """Audio file storage with encryption"""
    __tablename__ = "audio_files"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(20), default="wav")
    file_size = Column(Integer)
    duration = Column(Integer)  # seconds
    encryption_key = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    call = relationship("Call", back_populates="audio_files")

class AuditLog(Base):
    """HIPAA-compliant audit logging"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=False)
    details = Column(JSON)
    session_id = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    hash_value = Column(String(64))  # SHA-256 hash for integrity
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class PromptTemplate(Base):
    """AI prompt templates for different scenarios"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    template = Column(Text, nullable=False)
    variables = Column(JSON)  # Template variables
    category = Column(String(50), default="billing")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkflowDefinition(Base):
    """Voice workflow definitions"""
    __tablename__ = "workflow_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    steps = Column(JSON, nullable=False)  # Workflow steps
    decision_points = Column(JSON)  # Decision tree
    fallback_actions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
