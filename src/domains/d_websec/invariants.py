"""D_WEBSEC invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: OWASP Top 10, NIST Cybersecurity Framework
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Dict, Optional
import re


@dataclass
class WebApplication:
    """Web application security configuration."""
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
    """Authentication mechanism."""
    auth_id: str
    mfa_enabled: bool
    password_min_length: int
    password_requires_complexity: bool
    brute_force_protection: bool
    session_timeout_minutes: int


@dataclass
class SensitiveData:
    """Sensitive data handling."""
    data_id: str
    encrypted_at_rest: bool
    encrypted_in_transit: bool
    access_logging_enabled: bool
    pii_detected: bool


def check_https_enforced() -> bool:
    """
    Invariant: All traffic uses HTTPS (TLS 1.2+).
    Falsification: If HTTP traffic allowed without redirect.
    """
    app = WebApplication(
        app_id="APP001",
        name="Banking Portal",
        https_enforced=False,  # Not enforced!
        hsts_enabled=False,
        csrf_protection=True,
        xss_protection=True,
        input_validated=True,
        sql_injection_protected=True,
    )
    
    assert app.https_enforced is True, (
        f"Application {app.name} must enforce HTTPS"
    )
    
    return True


def check_hsts_header() -> bool:
    """
    Invariant: HSTS header prevents downgrade attacks.
    Falsification: If HTTPS site lacks HSTS header.
    """
    app = WebApplication(
        app_id="APP002",
        name="Secure Portal",
        https_enforced=True,
        hsts_enabled=False,  # Missing HSTS!
        csrf_protection=True,
        xss_protection=True,
        input_validated=True,
        sql_injection_protected=True,
    )
    
    if app.https_enforced:
        assert app.hsts_enabled is True, (
            f"HTTPS application {app.name} must have HSTS enabled"
        )
    
    return True


def check_csrf_protection() -> bool:
    """
    Invariant: State-changing actions require CSRF tokens.
    Falsification: If POST requests accepted without CSRF protection.
    """
    app = WebApplication(
        app_id="APP003",
        name="Social Network",
        https_enforced=True,
        hsts_enabled=True,
        csrf_protection=False,  # No CSRF protection!
        xss_protection=True,
        input_validated=True,
        sql_injection_protected=True,
    )
    
    assert app.csrf_protection is True, (
        f"Application {app.name} must have CSRF protection"
    )
    
    return True


def check_input_validation() -> bool:
    """
    Invariant: All user input validated before processing.
    Falsification: If raw user input used in queries/responses.
    """
    app = WebApplication(
        app_id="APP004",
        name="Search Engine",
        https_enforced=True,
        hsts_enabled=True,
        csrf_protection=True,
        xss_protection=True,
        input_validated=False,  # No validation!
        sql_injection_protected=False,
    )
    
    assert app.input_validated is True, (
        f"Application {app.name} must validate all user input"
    )
    
    return True


def check_sql_injection_protection() -> bool:
    """
    Invariant: Database queries use parameterized statements.
    Falsification: If string concatenation used for SQL queries.
    """
    app = WebApplication(
        app_id="APP005",
        name="E-commerce Site",
        https_enforced=True,
        hsts_enabled=True,
        csrf_protection=True,
        xss_protection=True,
        input_validated=True,
        sql_injection_protected=False,  # Vulnerable!
    )
    
    assert app.sql_injection_protected is True, (
        f"Application {app.name} must use SQL injection protection (parameterized queries)"
    )
    
    return True


def check_mfa_for_sensitive_operations() -> bool:
    """
    Invariant: Multi-factor authentication required for sensitive operations.
    Falsification: If password-only auth allows sensitive actions.
    """
    auth = AuthenticationSystem(
        auth_id="AUTH001",
        mfa_enabled=False,  # No MFA!
        password_min_length=8,
        password_requires_complexity=True,
        brute_force_protection=True,
        session_timeout_minutes=30,
    )
    
    assert auth.mfa_enabled is True, (
        f"Authentication {auth.auth_id} must have MFA for sensitive operations"
    )
    
    return True


def check_password_policy() -> bool:
    """
    Invariant: Passwords meet minimum complexity requirements.
    Falsification: If weak passwords (short/no complexity) accepted.
    """
    auth = AuthenticationSystem(
        auth_id="AUTH002",
        mfa_enabled=True,
        password_min_length=6,  # Too short!
        password_requires_complexity=False,  # No complexity!
        brute_force_protection=True,
        session_timeout_minutes=30,
    )
    
    assert auth.password_min_length >= 12, (
        f"Password min length {auth.password_min_length} below recommended 12"
    )
    assert auth.password_requires_complexity is True, (
        f"Passwords must require complexity (upper, lower, digit, special)"
    )
    
    return True


def check_session_timeout() -> bool:
    """
    Invariant: Sessions timeout after period of inactivity.
    Falsification: If sessions remain valid indefinitely.
    """
    auth = AuthenticationSystem(
        auth_id="AUTH003",
        mfa_enabled=True,
        password_min_length=12,
        password_requires_complexity=True,
        brute_force_protection=True,
        session_timeout_minutes=0,  # No timeout!
    )
    
    assert auth.session_timeout_minutes > 0, (
        f"Session timeout must be configured, got {auth.session_timeout_minutes}"
    )
    assert auth.session_timeout_minutes <= 60, (
        f"Session timeout {auth.session_timeout_minutes} too long (max 60 min)"
    )
    
    return True


def check_data_encryption() -> bool:
    """
    Invariant: Sensitive data encrypted at rest and in transit.
    Falsification: If PII stored or transmitted unencrypted.
    """
    data = SensitiveData(
        data_id="DATA001",
        encrypted_at_rest=False,  # Not encrypted!
        encrypted_in_transit=True,
        access_logging_enabled=True,
        pii_detected=True,
    )
    
    if data.pii_detected:
        assert data.encrypted_at_rest is True, (
            f"Data {data.data_id} with PII must be encrypted at rest"
        )
        assert data.encrypted_in_transit is True, (
            f"Data {data.data_id} with PII must be encrypted in transit"
        )
    
    return True


def check_access_logging() -> bool:
    """
    Invariant: Access to sensitive data is logged.
    Falsification: If sensitive data access not audited.
    """
    data = SensitiveData(
        data_id="DATA002",
        encrypted_at_rest=True,
        encrypted_in_transit=True,
        access_logging_enabled=False,  # No logging!
        pii_detected=True,
    )
    
    if data.pii_detected:
        assert data.access_logging_enabled is True, (
            f"Access to data {data.data_id} with PII must be logged"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("https_enforced", check_https_enforced),
        ("hsts_header", check_hsts_header),
        ("csrf_protection", check_csrf_protection),
        ("input_validation", check_input_validation),
        ("sql_injection", check_sql_injection_protection),
        ("mfa_required", check_mfa_for_sensitive_operations),
        ("password_policy", check_password_policy),
        ("session_timeout", check_session_timeout),
        ("data_encryption", check_data_encryption),
        ("access_logging", check_access_logging),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_WEBSEC invariants: PASS")
