"""Falsification tests for D_HOUSING_LAW"""
from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_housing_law import (
    FairHousingAnalyzer,
    EvictionProcess,
    TenantRights,
    HousingDiscriminationComplaint,
    LeaseAgreement,
    ProtectedClass,
    EvictionNoticeType,
    HabitabilityRequirement,
    check_protected_classes_enumerated,
    check_fair_housing_prohibits_discrimination,
)


def test_protected_classes_enumerated():
    """All seven FHA protected classes are recognized."""
    result = check_protected_classes_enumerated()
    assert result is True


def test_fair_housing_prohibits_discriminatory_ads():
    """Discriminatory advertising is flagged as non-compliant."""
    result = check_fair_housing_prohibits_discrimination()
    assert result is True


def test_discriminatory_advertising_detected():
    """Analyzer detects discriminatory language in ads."""
    analyzer = FairHousingAnalyzer()
    
    discriminatory_ad = "No children, Christian preferred, English speakers only"
    result = analyzer.check_advertising_compliance(discriminatory_ad)
    
    assert not result["compliant"]
    assert len(result["violations"]) >= 2


def test_compliant_advertising_passes():
    """Compliant advertising passes check."""
    analyzer = FairHousingAnalyzer()
    
    compliant_ad = "Beautiful 2BR apartment, near transit, pet-friendly"
    result = analyzer.check_advertising_compliance(compliant_ad)
    
    assert result["compliant"]
    assert len(result["violations"]) == 0


def test_eviction_requires_notice():
    """Cannot file eviction without serving notice first."""
    lease = LeaseAgreement(
        lease_id="L001",
        tenant_name="Tenant",
        landlord_name="Landlord",
        property_address="123 Main St",
        monthly_rent=Fraction(1000),
        security_deposit=Fraction(500),
        lease_term_months=12,
        start_date=datetime.now(),
    )
    
    tenant = TenantRights(tenant_id="T001", lease=lease)
    
    eviction = EvictionProcess(
        case_id="E001",
        lease=lease,
        tenant=tenant,
        reason="Nonpayment",
        rent_owed=Fraction(2000),
    )
    
    # Without notice, cannot file
    assert not eviction.can_file_forcible_entry()


def test_retaliation_defense_available():
    """Tenant with complaint history has retaliation defense."""
    lease = LeaseAgreement(
        lease_id="L002",
        tenant_name="Tenant",
        landlord_name="Landlord",
        property_address="456 Oak St",
        monthly_rent=Fraction(1200),
        security_deposit=Fraction(600),
        lease_term_months=12,
        start_date=datetime.now(),
    )
    
    tenant = TenantRights(
        tenant_id="T002",
        lease=lease,
        complaint_history=["Habitability complaint 2024-01-15"],
    )
    
    eviction = EvictionProcess(
        case_id="E002",
        lease=lease,
        tenant=tenant,
        reason="Nonpayment",
        rent_owed=Fraction(100),
    )
    
    defenses = eviction.tenant_has_defense()
    assert "RETALIATION" in defenses["defenses"]


def test_habitability_claim_requirements():
    """Tenant needs violations and repair requests for habitability claim."""
    lease = LeaseAgreement(
        lease_id="L003",
        tenant_name="Tenant",
        landlord_name="Landlord",
        property_address="789 Elm St",
        monthly_rent=Fraction(900),
        security_deposit=Fraction(450),
        lease_term_months=12,
        start_date=datetime.now(),
    )
    
    # No violations
    tenant1 = TenantRights(tenant_id="T003", lease=lease)
    assert not tenant1.has_habitability_claim()
    
    # Has violations but no repair requests
    tenant2 = TenantRights(
        tenant_id="T004",
        lease=lease,
        habitability_violations=[HabitabilityRequirement.HEATING],
    )
    assert not tenant2.has_habitability_claim()


if __name__ == "__main__":
    test_protected_classes_enumerated()
    test_fair_housing_prohibits_discriminatory_ads()
    test_discriminatory_advertising_detected()
    test_compliant_advertising_passes()
    test_eviction_requires_notice()
    test_retaliation_defense_available()
    test_habitability_claim_requirements()
    print("All D_HOUSING_LAW tests: PASS")
