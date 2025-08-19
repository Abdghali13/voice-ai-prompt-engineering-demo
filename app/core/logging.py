"""
Logging configuration for Voice AI Demo
HIPAA-compliant logging with audit trails
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Dict, Any

from app.core.config import settings

def setup_logging():
    """Setup application logging with HIPAA compliance"""
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for general logs
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    root_logger.addHandler(error_handler)
    
    # HIPAA audit log handler
    if settings.AUDIT_LOG_ENABLED:
        audit_handler = logging.handlers.RotatingFileHandler(
            'logs/audit.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10  # Keep more audit logs
        )
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        
        # Create audit logger
        audit_logger = logging.getLogger('audit')
        audit_logger.setLevel(logging.INFO)
        audit_logger.addHandler(audit_handler)
        audit_logger.propagate = False
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('redis').setLevel(logging.WARNING)
    
    # Log startup
    logging.info("Logging system initialized")
    if settings.AUDIT_LOG_ENABLED:
        logging.info("HIPAA audit logging enabled")

class HIPAACompliantLogger:
    """HIPAA-compliant logger for sensitive operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.audit_logger = logging.getLogger('audit')
    
    def log_phi_access(self, user_id: str, resource: str, action: str, details: Dict[str, Any]):
        """Log PHI data access for audit purposes"""
        if settings.AUDIT_LOG_ENABLED:
            # Sanitize details for logging
            sanitized_details = self._sanitize_phi_data(details)
            
            audit_message = f"PHI_ACCESS - User: {user_id}, Resource: {resource}, Action: {action}"
            self.audit_logger.info(audit_message)
            
            # Log sanitized details
            if sanitized_details:
                self.audit_logger.info(f"Details: {sanitized_details}")
    
    def log_consent_verification(self, user_id: str, consent_type: str, verified: bool):
        """Log consent verification"""
        if settings.AUDIT_LOG_ENABLED:
            message = f"CONSENT_VERIFICATION - User: {user_id}, Type: {consent_type}, Verified: {verified}"
            self.audit_logger.info(message)
    
    def log_data_encryption(self, data_type: str, encryption_method: str, success: bool):
        """Log data encryption operations"""
        if settings.AUDIT_LOG_ENABLED:
            message = f"DATA_ENCRYPTION - Type: {data_type}, Method: {encryption_method}, Success: {success}"
            self.audit_logger.info(message)
    
    def log_hipaa_violation(self, violation_type: str, details: str, severity: str = "HIGH"):
        """Log HIPAA violations"""
        if settings.AUDIT_LOG_ENABLED:
            message = f"HIPAA_VIOLATION - Type: {violation_type}, Severity: {severity}, Details: {details}"
            self.audit_logger.error(message)
            
            # Also log to main error log
            self.logger.error(f"HIPAA VIOLATION: {message}")
    
    def _sanitize_phi_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize PHI data for logging"""
        phi_fields = [
            "ssn", "date_of_birth", "medical_record_number", 
            "insurance_id", "phone_number", "email", "address"
        ]
        
        sanitized = data.copy()
        for field in phi_fields:
            if field in sanitized and sanitized[field]:
                value = str(sanitized[field])
                if len(value) > 4:
                    sanitized[field] = f"***{value[-4:]}"
                else:
                    sanitized[field] = "***"
        
        return sanitized

def get_hipaa_logger(name: str) -> HIPAACompliantLogger:
    """Get HIPAA-compliant logger instance"""
    return HIPAACompliantLogger(name)

# Global audit logger
audit_logger = get_hipaa_logger('global')
