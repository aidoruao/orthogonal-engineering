"""D_PRIVACY_LAW implementation — Privacy Law (GDPR, CCPA, HIPAA, FERPA)

Implements privacy protections including data subject rights,
consent requirements, and breach notification.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: GDPR (EU), CCPA (California), HIPAA (health), FERPA (education)

Biblical: Psalm 139:1 — "You have searched me, LORD, and you know me."
Implies reverence for personal knowledge and boundaries.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from datetime import datetime, timedelta
from fractions import Fraction

class DataType(Enum):
    PERSONAL = auto()
    SENSITIVE = auto()  # Race, religion, health, etc.
    FINANCIAL = auto()
    BIOMETRIC = auto()
    CHILD = auto()  # COPPA

class ProcessingBasis(Enum):
    CONSENT = auto()
    CONTRACT = auto()
    LEGAL_OBLIGATION = auto()
    VITAL_INTERESTS = auto()
    PUBLIC_TASK = auto()
    LEGITIMATE_INTEREST = auto()

@dataclass
class DataSubject:
    subject_id: str
    name: str
    is_child: bool = False
    data: Dict[str, str] = field(default_factory=dict)
    consent_given: Dict[str, datetime] = field(default_factory=dict)
    consent_withdrawn: List[str] = field(default_factory=list)

@dataclass
class DataProcessing:
    processing_id: str
    data_types: Set[DataType]
    basis: ProcessingBasis
    purpose: str
    retention_days: int
    started_date: datetime = field(default_factory=datetime.now)
    
    def requires_consent(self) -> bool:
        """Check if processing requires explicit consent."""
        return (
            DataType.SENSITIVE in self.data_types or
            DataType.BIOMETRIC in self.data_types or
            (DataType.CHILD in self.data_types and self.basis != ProcessingBasis.CONSENT)
        )
    
    def is_retention_expired(self) -> bool:
        """Check if data retention period expired."""
        expiry = self.started_date + timedelta(days=self.retention_days)
        return datetime.now() > expiry

class PrivacyComplianceChecker:
    """Checker for privacy law compliance."""
    
    GDPR_BREACH_THRESHOLD = 72  # Hours to report
    CCPA_SALE_OPT_OUT = True  # Must allow opt-out
    
    def check_consent_validity(
        self,
        subject: DataSubject,
        purpose: str,
        data_type: DataType,
    ) -> Dict:
        """Check if consent is valid for processing."""
        if data_type == DataType.CHILD and subject.is_child:
            # Requires parental consent (COPPA/GDPR)
            return {"valid": False, "requires_parental_consent": True}
        
        if purpose in subject.consent_withdrawn:
            return {"valid": False, "reason": "Consent withdrawn"}
        
        consent_date = subject.consent_given.get(purpose)
        if not consent_date:
            return {"valid": False, "reason": "No consent given"}
        
        # Check consent age (older than 2 years may need refresh)
        consent_age = (datetime.now() - consent_date).days
        
        return {
            "valid": True,
            "consent_age_days": consent_age,
            "stale": consent_age > 730,
        }
    
    def check_breach_notification(
        self,
        breach_date: datetime,
        data_subjects_affected: int,
        sensitive_data_involved: bool,
    ) -> Dict:
        """Check breach notification requirements."""
        hours_elapsed = (datetime.now() - breach_date).total_seconds() / 3600
        
        # GDPR requires notification within 72 hours
        gdpr_compliant = hours_elapsed <= self.GDPR_BREACH_THRESHOLD
        
        # Notification required if sensitive data or > 5000 subjects
        notification_required = sensitive_data_involved or data_subjects_affected > 5000
        
        return {
            "notification_required": notification_required,
            "gdpr_compliant": gdpr_compliant,
            "hours_elapsed": hours_elapsed,
            "regulators_to_notify": ["supervisory_authority"] if gdpr_compliant else ["supervisory_authority", "delay_explanation_required"],
        }
    
    def check_data_subject_rights(
        self,
        subject: DataSubject,
        right_exercised: str,  # "access", "deletion", "portability", "correction"
    ) -> Dict:
        """Check data subject rights request."""
        response_deadline = datetime.now() + timedelta(days=30)
        
        fees_allowed = False
        if right_exercised == "access":
            fees_allowed = len(subject.data) > 1000  # Excessive requests
        
        return {
            "request_valid": True,
            "response_deadline": response_deadline,
            "fees_may_apply": fees_allowed,
            "format_required": "machine_readable" if right_exercised == "portability" else "any",
        }

def check_gdpr_compliance(data_types: List[str], has_consent: bool) -> Dict:
    """Quick GDPR compliance check."""
    sensitive = any(t in data_types for t in ["health", "biometric", "religion", "political"])
    
    return {
        "lawful_basis_required": True,
        "consent_sufficient": has_consent or not sensitive,
        "dpo_required": sensitive and len(data_types) > 10,
        "impact_assessment_required": sensitive,
    }
