#!/usr/bin/env python3
"""D_WEBSEC Invariants — Web Security

Verifies OWASP Top 10 protections, NIST authentication standards,
transport security, input validation, data encryption.
OWASP Top 10, NIST SP 800-63B, PCI DSS.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    WebApplication, AuthenticationSystem, SensitiveData,
    AuthMethod,
    owasp_https_required, owasp_password_min_length,
    nist_session_timeout_max_minutes, pci_dss_encryption_required
)


def check_https_enforced(app: WebApplication) -> Tuple[bool, ProofObject]:
    """
    All web traffic must use HTTPS (TLS 1.2+) with no plaintext HTTP.

    OWASP Top 10 A02:2021 Cryptographic Failures: Sensitive data must
    be protected in transit using strong encryption.

    Falsifies if: https_enforced=False
    falsifies_if: https_enforced=False
    """
    if not app.https_enforced:
        return False, ProofObject(
            conclusion=f"VIOLATION: Application {app.name} does not enforce HTTPS",
            premises=[
                f"App: {app.app_id} ({app.name})",
                f"HTTPS enforced: {app.https_enforced}",
                "OWASP A02:2021 requires HTTPS for all traffic"
            ],
            rule="owasp_a02_2021_https"
        )

    return True, ProofObject(
        conclusion=f"Application {app.name} enforces HTTPS",
        premises=["HTTPS enforced: True"],
        rule="owasp_a02_2021_https"
    )


def check_hsts_header(app: WebApplication) -> Tuple[bool, ProofObject]:
    """
    HTTPS sites must send HSTS header to prevent downgrade attacks.

    OWASP: HTTP Strict Transport Security (HSTS) header forces browsers
    to use HTTPS, preventing man-in-the-middle downgrade attacks.

    Falsifies if: https_enforced=True and hsts_enabled=False
    falsifies_if: https_enforced=True and hsts_enabled=False
    """
    if app.https_enforced and not app.hsts_enabled:
        return False, ProofObject(
            conclusion=f"VIOLATION: HTTPS application {app.name} lacks HSTS header",
            premises=[
                f"HTTPS enforced: {app.https_enforced}",
                f"HSTS enabled: {app.hsts_enabled}",
                "HSTS required for HTTPS sites to prevent downgrade attacks"
            ],
            rule="owasp_hsts_header"
        )

    return True, ProofObject(
        conclusion=f"Application {app.name} has proper HSTS configuration",
        premises=[f"HSTS: {app.hsts_enabled}"],
        rule="owasp_hsts_header"
    )


def check_csrf_protection(app: WebApplication) -> Tuple[bool, ProofObject]:
    """
    State-changing requests must have CSRF token validation.

    OWASP Top 10 A01:2021 Broken Access Control: CSRF tokens prevent
    unauthorized commands from being transmitted from a user's browser.

    Falsifies if: csrf_protection=False
    falsifies_if: csrf_protection=False
    """
    if not app.csrf_protection:
        return False, ProofObject(
            conclusion=f"VIOLATION: Application {app.name} lacks CSRF protection",
            premises=[
                f"App: {app.app_id}",
                f"CSRF protection: {app.csrf_protection}",
                "OWASP A01:2021 requires CSRF protection for state-changing operations"
            ],
            rule="owasp_a01_2021_csrf"
        )

    return True, ProofObject(
        conclusion=f"Application {app.name} has CSRF protection",
        premises=["CSRF protection: True"],
        rule="owasp_a01_2021_csrf"
    )


def check_input_validation(app: WebApplication) -> Tuple[bool, ProofObject]:
    """
    All user input must be validated before processing.

    OWASP Top 10 A03:2021 Injection: Input validation prevents injection
    attacks (SQL, XSS, command injection, etc.).

    Falsifies if: input_validated=False or sql_injection_protected=False
    falsifies_if: input_validated=False or sql_injection_protected=False
    """
    if not app.input_validated:
        return False, ProofObject(
            conclusion=f"VIOLATION: Application {app.name} does not validate user input",
            premises=[
                f"Input validated: {app.input_validated}",
                "OWASP A03:2021 requires input validation"
            ],
            rule="owasp_a03_2021_input_validation"
        )

    if not app.sql_injection_protected:
        return False, ProofObject(
            conclusion=f"VIOLATION: Application {app.name} vulnerable to SQL injection",
            premises=[
                f"SQL injection protected: {app.sql_injection_protected}",
                "OWASP A03:2021 requires parameterized queries"
            ],
            rule="owasp_a03_2021_sql_injection"
        )

    return True, ProofObject(
        conclusion=f"Application {app.name} validates input and prevents SQL injection",
        premises=["Input validated: True", "SQL injection protected: True"],
        rule="owasp_a03_2021_input_validation"
    )


def check_password_policy(auth: AuthenticationSystem) -> Tuple[bool, ProofObject]:
    """
    Passwords must meet minimum length and complexity requirements.

    NIST SP 800-63B: Minimum 12 characters for user-chosen passwords.
    Complexity (upper, lower, digit, special) recommended.

    Falsifies if: password_min_length < 12 or no complexity requirement
    falsifies_if: password_min_length < 12 or no complexity requirement
    """
    min_length = owasp_password_min_length()

    if auth.password_min_length < min_length:
        return False, ProofObject(
            conclusion=f"VIOLATION: Auth system {auth.auth_id} password min length {auth.password_min_length} below NIST requirement {min_length}",
            premises=[
                f"Auth: {auth.auth_id}",
                f"Password min length: {auth.password_min_length}",
                f"Required: {min_length}",
                "NIST SP 800-63B requires 12+ character passwords"
            ],
            rule="nist_800_63b_password_length"
        )

    if not auth.password_requires_complexity:
        return False, ProofObject(
            conclusion=f"VIOLATION: Auth system {auth.auth_id} does not require password complexity",
            premises=[
                f"Complexity required: {auth.password_requires_complexity}",
                "OWASP recommends password complexity"
            ],
            rule="owasp_password_complexity"
        )

    return True, ProofObject(
        conclusion=f"Auth system {auth.auth_id} meets password policy requirements",
        premises=[
            f"Min length: {auth.password_min_length} >= {min_length}",
            f"Complexity: {auth.password_requires_complexity}"
        ],
        rule="nist_800_63b_password_policy"
    )


def check_session_timeout(auth: AuthenticationSystem) -> Tuple[bool, ProofObject]:
    """
    Sessions must timeout after period of inactivity (max 60 minutes).

    NIST SP 800-63B: Sessions for sensitive operations should timeout
    after reasonable inactivity period to limit exposure.

    Falsifies if: session_timeout_minutes <= 0 or > 60
    falsifies_if: session_timeout_minutes <= 0 or > 60
    """
    max_timeout = nist_session_timeout_max_minutes()

    if auth.session_timeout_minutes <= Fraction(0):
        return False, ProofObject(
            conclusion=f"VIOLATION: Auth system {auth.auth_id} has no session timeout",
            premises=[
                f"Session timeout: {auth.session_timeout_minutes} minutes",
                "NIST requires session timeout configuration"
            ],
            rule="nist_session_timeout"
        )

    if auth.session_timeout_minutes > max_timeout:
        return False, ProofObject(
            conclusion=f"VIOLATION: Session timeout {auth.session_timeout_minutes} minutes exceeds max {max_timeout}",
            premises=[
                f"Timeout: {auth.session_timeout_minutes} minutes",
                f"Max: {max_timeout} minutes",
                "NIST recommends <= 60 minute timeout for sensitive operations"
            ],
            rule="nist_session_timeout"
        )

    return True, ProofObject(
        conclusion=f"Auth system {auth.auth_id} has appropriate session timeout",
        premises=[f"Timeout: {auth.session_timeout_minutes} minutes <= {max_timeout}"],
        rule="nist_session_timeout"
    )


def check_data_encryption(data: SensitiveData) -> Tuple[bool, ProofObject]:
    """
    Sensitive data (PII) must be encrypted at rest and in transit.

    PCI DSS Requirement 3: Protect stored cardholder data with encryption.
    PCI DSS Requirement 4: Encrypt transmission of cardholder data.

    Falsifies if: pii_detected and (not encrypted_at_rest or not encrypted_in_transit)
    falsifies_if: pii_detected and (not encrypted_at_rest or not encrypted_in_transit)
    """
    if not data.pii_detected:
        return True, ProofObject(
            conclusion=f"Data {data.data_id} does not contain PII, encryption N/A",
            premises=["PII detected: False"],
            rule="pci_dss_encryption"
        )

    if not data.encrypted_at_rest:
        return False, ProofObject(
            conclusion=f"VIOLATION: PII data {data.data_id} not encrypted at rest",
            premises=[
                f"Data: {data.data_id}",
                f"PII detected: {data.pii_detected}",
                f"Encrypted at rest: {data.encrypted_at_rest}",
                "PCI DSS Requirement 3: Encrypt stored sensitive data"
            ],
            rule="pci_dss_req_3_encryption_at_rest"
        )

    if not data.encrypted_in_transit:
        return False, ProofObject(
            conclusion=f"VIOLATION: PII data {data.data_id} not encrypted in transit",
            premises=[
                f"Encrypted in transit: {data.encrypted_in_transit}",
                "PCI DSS Requirement 4: Encrypt data transmission"
            ],
            rule="pci_dss_req_4_encryption_in_transit"
        )

    return True, ProofObject(
        conclusion=f"PII data {data.data_id} properly encrypted (at rest + in transit)",
        premises=["Encrypted at rest: True", "Encrypted in transit: True"],
        rule="pci_dss_encryption"
    )


def run_all_invariants() -> dict:
    """Run all D_WEBSEC invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    web_application = WebApplication(
        app_id=None,
        name=None,
        https_enforced=None,
        hsts_enabled=None,
        csrf_protection=None,
        xss_protection=None,
        input_validated=None,
        sql_injection_protected=None,
    )
    sensitive_data = SensitiveData(
        data_id=None,
        encrypted_at_rest=None,
        encrypted_in_transit=None,
        access_logging_enabled=None,
        pii_detected=None,
    )
    authentication_system = AuthenticationSystem(
        auth_id=None,
        auth_method=AuthMethod.PASSWORD_ONLY,
        password_min_length=Fraction(1),
        password_requires_complexity=None,
        brute_force_protection=None,
        session_timeout_minutes=Fraction(1),
    )

    checks = [
        ("check_csrf_protection", lambda: check_csrf_protection(web_application)),
        ("check_data_encryption", lambda: check_data_encryption(sensitive_data)),
        ("check_hsts_header", lambda: check_hsts_header(web_application)),
        ("check_https_enforced", lambda: check_https_enforced(web_application)),
        ("check_input_validation", lambda: check_input_validation(web_application)),
        ("check_password_policy", lambda: check_password_policy(authentication_system)),
        ("check_session_timeout", lambda: check_session_timeout(authentication_system)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_WEBSEC invariants: PASS")
