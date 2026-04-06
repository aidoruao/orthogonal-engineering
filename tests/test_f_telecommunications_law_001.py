"""Tests for d_telecommunications_law domain."""

from datetime import datetime, timedelta
from fractions import Fraction

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
    check_tcpa_consent_requirement,
    check_net_neutrality_violation,
    calculate_e_rate_discount,
)


def test_tcpa_no_consent_violation():
    """Test TCPA violation for autodialed call without consent."""
    checker = TCPAComplianceChecker()
    
    number = TelephoneNumber(
        number="555-1234",
        subscriber_id="S001",
        express_consent_given=False,
        is_wireless=True,
    )
    
    call = CallRecord(
        call_id="C001",
        caller_id="CALLER001",
        called_number="555-1234",
        call_date=datetime.now(),
        used_autodialer=True,
    )
    
    result = checker.check_call_compliance(call, number)
    assert result["compliant"] is False


def test_tcpa_with_consent():
    """Test TCPA compliance with prior consent."""
    checker = TCPAComplianceChecker()
    
    number = TelephoneNumber(
        number="555-5678",
        subscriber_id="S002",
        express_consent_given=True,
        express_consent_date=datetime.now() - timedelta(days=30),
        is_wireless=True,
    )
    
    call = CallRecord(
        call_id="C002",
        caller_id="CALLER001",
        called_number="555-5678",
        call_date=datetime.now(),
        used_autodialer=True,
    )
    
    result = checker.check_call_compliance(call, number)
    assert result["compliant"] is True


def test_net_neutrality_blocking():
    """Test net neutrality blocking violation."""
    checker = NetNeutralityComplianceChecker()
    
    service = BroadbandService(
        service_id="B001",
        carrier_id="C001",
        download_speed_mbps=100,
        upload_speed_mbps=20,
        blocking_allowed=True,
    )
    
    result = checker.check_blocking_compliance(service)
    assert result["compliant"] is False


def test_net_neutrality_compliance():
    """Test compliant net neutrality service."""
    checker = NetNeutralityComplianceChecker()
    
    service = BroadbandService(
        service_id="B002",
        carrier_id="C002",
        download_speed_mbps=100,
        upload_speed_mbps=20,
        blocking_allowed=False,
        throttling_allowed=False,
        paid_prioritization=False,
    )
    
    result = checker.conduct_comprehensive_audit(service)
    assert result["compliant"] is True


def test_net_neutrality_paid_prioritization():
    """Test net neutrality paid prioritization violation."""
    checker = NetNeutralityComplianceChecker()
    
    service = BroadbandService(
        service_id="B003",
        carrier_id="C003",
        download_speed_mbps=100,
        upload_speed_mbps=20,
        paid_prioritization=True,
    )
    
    result = checker.check_paid_prioritization(service)
    assert result["compliant"] is False


def test_e_rate_eligibility():
    """Test E-rate eligibility."""
    calculator = UniversalServiceFundCalculator()
    
    school = calculator.check_e_rate_eligibility("school")
    assert school["eligible"] is True
    
    library = calculator.check_e_rate_eligibility("library")
    assert library["eligible"] is True
    
    business = calculator.check_e_rate_eligibility("business")
    assert business["eligible"] is False


def test_spectrum_license_validity():
    """Test spectrum license validity."""
    valid = SpectrumLicense(
        license_id="L001",
        call_sign="WABC",
        frequency_block="700 MHz",
        bandwidth_mhz=10,
        licensee_id="C001",
        licensee_name="Carrier",
        issue_date=datetime.now() - timedelta(days=365),
        expiration_date=datetime.now() + timedelta(days=365),
        license_type=LicenseType.EXCLUSIVE_USE,
        geographic_scope="nationwide",
    )
    
    assert valid.is_valid is True
    assert valid.days_until_expiration > 0


def test_usf_contribution():
    """Test Universal Service Fund contribution calculation."""
    calculator = UniversalServiceFundCalculator()
    
    result = calculator.calculate_contribution(
        interstate_revenue=Fraction(10000),
        international_revenue=Fraction(5000),
    )
    
    assert result["assessable_revenue"] == Fraction(15000)
    assert result["contribution_due"] > 0


def test_tcpa_damages():
    """Test TCPA damages calculation."""
    checker = TCPAComplianceChecker()
    
    result = checker.calculate_damages(5, willful=False)
    assert result["amount"] == Fraction(2500)  # 5 * $500
    
    result2 = checker.calculate_damages(5, willful=True)
    assert result2["maximum"] == Fraction(7500)  # 5 * $1500


def test_convenience_function_tcpa():
    """Test convenience function for TCPA consent."""
    result = check_tcpa_consent_requirement(True, True)
    assert result["prior_express_consent_required"] is True
    
    result2 = check_tcpa_consent_requirement(False, True)
    assert result2["prior_express_consent_required"] is False


def test_convenience_function_net_neutrality():
    """Test convenience function for net neutrality."""
    result = check_net_neutrality_violation(True, False, False)
    assert result["violation"] is True
    assert "blocking" in result["violation_types"]
    
    result2 = check_net_neutrality_violation(False, False, False)
    assert result2["violation"] is False


def test_convenience_function_e_rate():
    """Test convenience function for E-rate discount."""
    result = calculate_e_rate_discount(urban=True, free_lunch_percent=80)
    assert result["discount_percent"] > 20
    assert result["urban"] is True
