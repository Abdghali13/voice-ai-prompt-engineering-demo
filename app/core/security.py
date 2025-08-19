"""
Security module for Voice AI Demo
JWT authentication, encryption, and HIPAA compliance
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import hashlib
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise ValueError("Invalid token")

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data for HIPAA compliance"""
    if not settings.HIPAA_ENABLED:
        return data
    
    try:
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise ValueError("Encryption failed")

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not settings.HIPAA_ENABLED:
        return encrypted_data
    
    try:
        decrypted_data = fernet.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError("Decryption failed")

def hash_phi_data(data: str) -> str:
    """Hash PHI data for secure storage"""
    return hashlib.sha256(data.encode()).hexdigest()

def sanitize_phi_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize PHI data for logging and external systems"""
    phi_fields = [
        "ssn", "date_of_birth", "medical_record_number", 
        "insurance_id", "phone_number", "email", "address"
    ]
    
    sanitized = data.copy()
    for field in phi_fields:
        if field in sanitized and sanitized[field]:
            sanitized[field] = f"***{str(sanitized[field])[-4:]}" if len(str(sanitized[field])) > 4 else "***"
    
    return sanitized

def create_audit_log(action: str, user_id: str, resource: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Create HIPAA-compliant audit log entry"""
    if not settings.AUDIT_LOG_ENABLED:
        return {}
    
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "details": sanitize_phi_data(details),
        "session_id": details.get("session_id"),
        "ip_address": details.get("ip_address"),
        "user_agent": details.get("user_agent")
    }
    
    # Hash sensitive information
    audit_entry["hash"] = hash_phi_data(json.dumps(audit_entry, sort_keys=True))
    
    return audit_entry

def validate_hipaa_compliance(data: Dict[str, Any]) -> bool:
    """Validate data for HIPAA compliance"""
    required_fields = ["consent_given", "purpose_of_use", "minimum_necessary"]
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    return True

def generate_secure_session_id() -> str:
    """Generate secure session ID"""
    import secrets
    return secrets.token_urlsafe(32)

def mask_phone_number(phone: str) -> str:
    """Mask phone number for display"""
    if len(phone) < 10:
        return phone
    
    return f"{phone[:3]}***{phone[-4:]}"

def mask_ssn(ssn: str) -> str:
    """Mask SSN for display"""
    if len(ssn) < 9:
        return ssn
    
    return f"***-**-{ssn[-4:]}"
