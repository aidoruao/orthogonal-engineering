"""Falsification tests for D_PRIVACY_LAW"""
from src.domains.d_privacy_law import (
    PrivacyComplianceChecker, DataSubject, DataProcessing,
    DataType, ProcessingBasis
)

def test_consent_required_for_sensitive():
    checker = PrivacyComplianceChecker()
    
    subject = DataSubject(subject_id="S1", name="User")
    
    result = checker.check_consent_validity(
        subject, "marketing", DataType.SENSITIVE
    )
    assert result["valid"] is False  # No consent given

def test_breach_notification_timing():
    checker = PrivacyComplianceChecker()
    
    from datetime import datetime, timedelta
    breach_date = datetime.now() - timedelta(hours=24)
    
    result = checker.check_breach_notification(
        breach_date, 10000, True
    )
    assert result["notification_required"] is True
    assert result["gdpr_compliant"] is True  # Within 72 hours

if __name__ == "__main__":
    test_consent_required_for_sensitive()
    test_breach_notification_timing()
    print("All D_PRIVACY_LAW tests: PASS")
