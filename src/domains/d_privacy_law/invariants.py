"""D_PRIVACY_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: GDPR (EU), CCPA (California), HIPAA (health), FERPA (education)
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_privacy_law.implementation import (
    PrivacyComplianceChecker,
    DataSubject,
    DataProcessing,
    DataType,
    ProcessingBasis,
)


def check_consent_required_before_processing() -> bool:
    """
    Invariant: Consent required before processing sensitive data.
    Falsification: If sensitive data processing without consent passes check.
    """
    checker = PrivacyComplianceChecker()
    
    # Subject with consent for sensitive data
    subject_with_consent = DataSubject(
        subject_id="S001",
        name="Consenting User",
        is_child=False,
        consent_given={"marketing": datetime.now() - timedelta(days=30)},
    )
    
    result = checker.check_consent_validity(
        subject_with_consent, "marketing", DataType.PERSONAL
    )
    assert result["valid"] is True, (
        "Subject with consent should pass"
    )
    
    # Subject without consent
    subject_no_consent = DataSubject(
        subject_id="S002",
        name="Non-consenting User",
        is_child=False,
        consent_given={},
    )
    
    result2 = checker.check_consent_validity(
        subject_no_consent, "marketing", DataType.PERSONAL
    )
    assert result2["valid"] is False, (
        "Subject without consent should fail"
    )
    
    # Child subject requires parental consent
    child_subject = DataSubject(
        subject_id="S003",
        name="Child User",
        is_child=True,
        consent_given={"marketing": datetime.now()},
    )
    
    result3 = checker.check_consent_validity(
        child_subject, "marketing", DataType.CHILD
    )
    assert result3["valid"] is False, (
        "Child should require parental consent"
    )
    assert result3.get("requires_parental_consent") is True, (
        "Should flag parental consent requirement"
    )
    
    return True


def check_right_to_deletion() -> bool:
    """
    Invariant: Data subjects have right to deletion (GDPR Art. 17).
    Falsification: If deletion request denied for valid subject data.
    """
    checker = PrivacyComplianceChecker()
    
    subject = DataSubject(
        subject_id="S004",
        name="Deletion Requester",
        data={"email": "test@example.com", "preferences": "dark_mode"},
    )
    
    result = checker.check_data_subject_rights(subject, "deletion")
    assert result["request_valid"] is True, (
        "Deletion request should be valid"
    )
    assert result["response_deadline"] <= datetime.now() + timedelta(days=30), (
        "GDPR requires response within 30 days"
    )
    
    return True


def check_breach_notification_within_72_hours() -> bool:
    """
    Invariant: GDPR breach notification must be within 72 hours.
    Falsification: If breach reported after 72 hours is marked compliant.
    """
    checker = PrivacyComplianceChecker()
    
    # Breach reported within 24 hours - compliant
    recent_breach = datetime.now() - timedelta(hours=24)
    result = checker.check_breach_notification(
        breach_date=recent_breach,
        data_subjects_affected=10000,
        sensitive_data_involved=True,
    )
    assert result["gdpr_compliant"] is True, (
        "24-hour breach notification should be compliant"
    )
    
    # Breach reported after 72 hours - non-compliant
    old_breach = datetime.now() - timedelta(hours=96)
    result2 = checker.check_breach_notification(
        breach_date=old_breach,
        data_subjects_affected=10000,
        sensitive_data_involved=True,
    )
    assert result2["gdpr_compliant"] is False, (
        "96-hour breach notification should be non-compliant"
    )
    
    # Large breach requires notification
    assert result["notification_required"] is True, (
        "Large breach with sensitive data requires notification"
    )
    
    return True


def check_consent_withdrawal() -> bool:
    """
    Invariant: Withdrawing consent must stop processing.
    Falsification: If processing continues after consent withdrawal.
    """
    checker = PrivacyComplianceChecker()
    
    # Subject who withdrew consent for marketing
    subject_withdrawn = DataSubject(
        subject_id="S005",
        name="Opted Out User",
        consent_given={"analytics": datetime.now()},
        consent_withdrawn=["marketing"],
    )
    
    result = checker.check_consent_validity(
        subject_withdrawn, "marketing", DataType.PERSONAL
    )
    assert result["valid"] is False, (
        "Processing after consent withdrawal should fail"
    )
    assert "withdrawn" in result.get("reason", "").lower(), (
        "Should indicate consent was withdrawn"
    )
    
    # Analytics consent still valid
    result2 = checker.check_consent_validity(
        subject_withdrawn, "analytics", DataType.PERSONAL
    )
    assert result2["valid"] is True, (
        "Non-withdrawn consent should remain valid"
    )
    
    return True


def check_data_portability_rights() -> bool:
    """
    Invariant: Data subjects have right to data portability (GDPR Art. 20).
    Falsification: If portability request doesn't require machine-readable format.
    """
    checker = PrivacyComplianceChecker()
    
    subject = DataSubject(
        subject_id="S006",
        name="Portability Requester",
        data={"purchase_history": "item1,item2,item3"},
    )
    
    result = checker.check_data_subject_rights(subject, "portability")
    assert result["request_valid"] is True, (
        "Portability request should be valid"
    )
    assert result["format_required"] == "machine_readable", (
        "GDPR requires machine-readable format for portability"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("consent_required", check_consent_required_before_processing),
        ("right_to_deletion", check_right_to_deletion),
        ("breach_notification_72h", check_breach_notification_within_72_hours),
        ("consent_withdrawal", check_consent_withdrawal),
        ("data_portability", check_data_portability_rights),
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
