"""D_WEBSEC implementation — Web Security

Layer: 3 (Regulatory)
CardinalStrength: PREDICATIVE

OWASP Top 10, NIST Cybersecurity Framework, secure authentication,
transport security, input validation, data protection.
"""

from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from enum import Enum
from typing import List


class AuthMethod(Enum):
    """Authentication methods"""
    PASSWORD_ONLY = 1
    MFA = 2
    BIOMETRIC = 3


@dataclass
class WebApplication:
    """Web application security configuration"""
    app_id: str
    name: str
    https_enforced: bool
    hsts_enabled: bool
    csrf_protection: bool
    xss_protection: bool
    input_validated: bool
    sql_injection_protected: bool


@dataclass
class AuthenticationSystem:
    """Authentication mechanism"""
    auth_id: str
    auth_method: AuthMethod
    password_min_length: Fraction
    password_requires_complexity: bool
    brute_force_protection: bool
    session_timeout_minutes: Fraction


@dataclass
class SensitiveData:
    """Sensitive data handling"""
    data_id: str
    encrypted_at_rest: bool
    encrypted_in_transit: bool
    access_logging_enabled: bool
    pii_detected: bool


def owasp_https_required() -> bool:
    """OWASP: All traffic must use HTTPS (TLS 1.2+)"""
    return True


def owasp_password_min_length() -> Fraction:
    """OWASP: Minimum password length 12 characters"""
    return Fraction(12, 1)


def nist_session_timeout_max_minutes() -> Fraction:
    """NIST: Maximum session timeout 60 minutes for sensitive operations"""
    return Fraction(60, 1)


def pci_dss_encryption_required() -> bool:
    """PCI DSS: Sensitive data must be encrypted at rest and in transit"""
    return True
