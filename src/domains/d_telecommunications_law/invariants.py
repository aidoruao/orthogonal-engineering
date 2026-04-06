"""D_TELECOMMUNICATIONS_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Communications Act (47 U.S.C.), TCPA (47 U.S.C. §227)
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_telecommunications_law.implementation import (
    TCPAComplianceChecker,
    NetNeutralityComplianceChecker,
    SpectrumAuctionSystem,
    UniversalServiceFundCalculator,
    TelecommunicationsRegulator,
    TelecommunicationsCarrier,
    SpectrumLicense,
    TelephoneNumber,
    CallRecord,
    BroadbandService,
    ServiceType,
    LicenseType,
    RobocallType,
)


def check_tcpa_requires_prior_consent() -> bool:
    """
    Invariant: TCPA requires prior express consent for autodialed wireless calls.
    Falsification: If autodialed call to wireless without consent passes check.
    """
    checker = TCPAComplianceChecker()
    
    # Number without consent
    no_consent = TelephoneNumber(
        number="555-1234",
        subscriber_id="S001",
        express_consent_given=False,
        is_wireless=True,
    )
    
    # Autodialed call to wireless without consent
    robocall = CallRecord(
        call_id="C001",
        caller_id="CALLER001",
        called_number="555-1234",
        call_date=datetime.now(),
        used_autodialer=True,
        used_prerecorded_voice=True,
    )
    
    result = checker.check_call_compliance(robocall, no_consent)
    assert result["compliant"] is False, (
        "Autodialed call to wireless without consent should violate TCPA"
    )
    assert len(result["violations"]) > 0, (
        "Should identify TCPA violations"
    )
    
    # Number with consent
    with_consent = TelephoneNumber(
        number="555-5678",
        subscriber_id="S002",
        express_consent_given=True,
        express_consent_date=datetime.now() - timedelta(days=30),
        is_wireless=True,
    )
    
    # Same call to number with consent
    result2 = checker.check_call_compliance(robocall, with_consent)
    assert result2["compliant"] is True, (
        "Autodialed call with prior consent should be compliant"
    )
    
    return True


def check_net_neutrality_no_blocking() -> bool:
    """
    Invariant: Broadband providers cannot block lawful content.
    Falsification: If blocking service passes net neutrality check.
    """
    checker = NetNeutralityComplianceChecker()
    
    # Service that blocks content
    blocking_service = BroadbandService(
        service_id="B001",
        carrier_id="C001",
        download_speed_mbps=100,
        upload_speed_mbps=20,
        blocking_allowed=True,  # Violation
        throttling_allowed=False,
        paid_prioritization=False,
    )
    
    result = checker.check_blocking_compliance(blocking_service)
    assert result["compliant"] is False, (
        "Service with blocking should violate net neutrality"
    )
    
    # Service that doesn't block
    neutral_service = BroadbandService(
        service_id="B002",
        carrier_id="C002",
        download_speed_mbps=100,
        upload_speed_mbps=20,
        blocking_allowed=False,
        throttling_allowed=False,
        paid_prioritization=False,
    )
    
    result2 = checker.check_blocking_compliance(neutral_service)
    assert result2["compliant"] is True, (
        "Service without blocking should be compliant"
    )
    
    return True


def check_net_neutrality_no_paid_prioritization() -> bool:
    """
    Invariant: Paid prioritization violates net neutrality.
    Falsification: If service with paid prioritization passes check.
    """
    checker = NetNeutralityComplianceChecker()
    
    # Service with paid prioritization
    prioritized_service = BroadbandService(
        service_id="B003",
        carrier_id="C003",
        download_speed_mbps=100,
        upload_speed_mbps=20,
        blocking_allowed=False,
        throttling_allowed=False,
        paid_prioritization=True,  # Violation
    )
    
    result = checker.check_paid_prioritization(prioritized_service)
    assert result["compliant"] is False, (
        "Service with paid prioritization should violate net neutrality"
    )
    
    return True


def check_e_rate_discount_calculation() -> bool:
    """
    Invariant: E-rate discounts range from 20-90% based on need.
    Falsification: If discount calculated outside valid range.
    """
    calculator = UniversalServiceFundCalculator()
    
    # High-need rural school
    high_need = calculator.check_e_rate_eligibility("school")
    assert high_need["eligible"] is True, (
        "Schools should be eligible for E-rate"
    )
    assert high_need["discount_range_percent"] == (20, 90), (
        "Discount range should be 20-90%"
    )
    
    # Library also eligible
    library = calculator.check_e_rate_eligibility("library")
    assert library["eligible"] is True, (
        "Libraries should be eligible for E-rate"
    )
    
    # Non-eligible entity
    business = calculator.check_e_rate_eligibility("business")
    assert business["eligible"] is False, (
        "Businesses should not be eligible for E-rate"
    )
    
    return True


def check_spectrum_license_validity() -> bool:
    """
    Invariant: Spectrum license required for broadcast/transmission.
    Falsification: If expired license shows as valid.
    """
    # Valid license
    valid_license = SpectrumLicense(
        license_id="L001",
        call_sign="WABC",
        frequency_block="700 MHz Block A",
        bandwidth_mhz=10,
        licensee_id="C001",
        licensee_name="Carrier A",
        issue_date=datetime.now() - timedelta(days=365),
        expiration_date=datetime.now() + timedelta(days=365*10),
        license_type=LicenseType.EXCLUSIVE_USE,
        geographic_scope="nationwide",
    )
    
    assert valid_license.is_valid is True, (
        "Future expiration should be valid"
    )
    assert valid_license.days_until_expiration > 0, (
        "Days until expiration should be positive"
    )
    
    # Expired license
    expired_license = SpectrumLicense(
        license_id="L002",
        call_sign="WXYZ",
        frequency_block="800 MHz Block B",
        bandwidth_mhz=10,
        licensee_id="C002",
        licensee_name="Carrier B",
        issue_date=datetime.now() - timedelta(days=365*11),
        expiration_date=datetime.now() - timedelta(days=365),
        license_type=LicenseType.EXCLUSIVE_USE,
        geographic_scope="regional",
    )
    
    assert expired_license.is_valid is False, (
        "Past expiration should be invalid"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("tcpa_consent", check_tcpa_requires_prior_consent),
        ("net_neutrality_blocking", check_net_neutrality_no_blocking),
        ("net_neutrality_prioritization", check_net_neutrality_no_paid_prioritization),
        ("e_rate_discount", check_e_rate_discount_calculation),
        ("spectrum_license", check_spectrum_license_validity),
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
