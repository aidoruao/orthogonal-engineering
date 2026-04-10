"""D_HOUSING_LAW invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Fair Housing Act (42 U.S.C. §3601 et seq.)
- Americans with Disabilities Act, Title II/III
- HOPWA (Housing Opportunities for Persons With AIDS)
- State landlord-tenant laws, URLTA

Source: ontology/ontology.json#D_HOUSING_LAW
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple
from datetime import datetime, timedelta

from axioms.logic import ProofObject

from src.domains.d_housing_law.implementation import (
    FairHousingAnalyzer,
    EvictionProcess,
    TenantRights,
    HousingDiscriminationComplaint,
    LeaseAgreement,
    ProtectedClass,
    EvictionNoticeType,
    HabitabilityRequirement,
)


def check_fha_protected_classes() -> Tuple[bool, ProofObject]:
    """
    Invariant: All seven protected classes under FHA are recognized.
    
    Standard: 42 U.S.C. §3604
    Falsifies if: Any protected class is missing.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    expected_classes = {
        "RACE", "COLOR", "RELIGION", "NATIONAL_ORIGIN",
        "SEX", "FAMILIAL_STATUS", "DISABILITY",
    }
    
    actual_classes = {pc.name for pc in ProtectedClass}
    
    classes_match = actual_classes == expected_classes
    
    # Count verification
    seven_classes = len(actual_classes) == Fraction(7)
    
    success = classes_match and seven_classes
    
    proof = ProofObject(
        rule="FHAProtectedClasses",
        premises=[
            f"expected_classes = {expected_classes}",
            f"actual_classes = {actual_classes}",
            f"classes_match = {classes_match}",
            f"seven_classes = {seven_classes}",
        ],
        conclusion=(
            "42 U.S.C. §3604 protected classes enforced"
            if success
            else "FAIL: Protected classes mismatch"
        ),
    )
    return success, proof


def check_eviction_notice_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Eviction requires proper notice before filing.
    
    Standard: State landlord-tenant laws; URLTA §4-301
    Falsifies if: Eviction filed without notice or before notice period expires.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
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
        reason="Nonpayment of rent",
        rent_owed=Fraction(2000),
    )
    
    # Should not be able to file without serving notice
    cannot_file_without_notice = not eviction.can_file_forcible_entry()
    
    # Serve notice
    eviction.serve_notice(EvictionNoticeType.PAY_OR_QUIT, days_notice=3)
    
    notice_served = eviction.notice_served_date is not None
    notice_type_set = eviction.notice_type == EvictionNoticeType.PAY_OR_QUIT
    days_notice_set = eviction.days_notice_given == 3
    
    success = cannot_file_without_notice and notice_served and notice_type_set and days_notice_set
    
    proof = ProofObject(
        rule="EvictionNoticeRequirements",
        premises=[
            f"cannot_file_without_notice = {cannot_file_without_notice}",
            f"notice_served = {notice_served}",
            f"notice_type_set = {notice_type_set}",
            f"days_notice_set = {days_notice_set}",
        ],
        conclusion=(
            "Eviction notice requirements enforced"
            if success
            else "FAIL: Eviction notice requirements violated"
        ),
    )
    return success, proof


def check_habitability_requirements() -> Tuple[bool, ProofObject]:
    """
    Invariant: Implied warranty of habitability covers essential services.
    
    Standard: URLTA §2-104; state habitability laws
    Falsifies if: Essential habitability requirements are missing.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    essential_requirements = {
        HabitabilityRequirement.STRUCTURAL_INTEGRITY,
        HabitabilityRequirement.WEATHER_PROTECTION,
        HabitabilityRequirement.PLUMBING,
        HabitabilityRequirement.HEATING,
        HabitabilityRequirement.ELECTRICAL,
        HabitabilityRequirement.WATER,
    }
    
    all_requirements = set(HabitabilityRequirement)
    
    # Check all essential requirements exist
    essentials_present = all(req in all_requirements for req in essential_requirements)
    
    # Count requirements
    eight_requirements = len(all_requirements) >= Fraction(7)
    
    success = essentials_present and eight_requirements
    
    proof = ProofObject(
        rule="HabitabilityRequirements",
        premises=[
            f"essential_requirements_present = {essentials_present}",
            f"requirement_count_sufficient = {eight_requirements}",
            f"requirements = {[r.name for r in all_requirements]}",
        ],
        conclusion=(
            "Implied warranty of habitability requirements enforced"
            if success
            else "FAIL: Habitability requirements missing"
        ),
    )
    return success, proof


def check_fair_housing_discrimination_prohibition() -> Tuple[bool, ProofObject]:
    """
    Invariant: Fair Housing Act prohibits discrimination based on protected class.
    
    Standard: 42 U.S.C. §3604
    Falsifies if: Discriminatory advertising passes compliance check.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    analyzer = FairHousingAnalyzer()
    
    # Test discriminatory advertisement
    discriminatory_ad = "Quiet building, no children allowed, Christian preferred"
    result_discriminatory = analyzer.check_advertising_compliance(discriminatory_ad)
    discriminatory_flagged = result_discriminatory["compliant"] is False
    violations_found = len(result_discriminatory["violations"]) > 0
    
    # Test compliant advertisement
    compliant_ad = "Spacious 2-bedroom apartment, available now, close to parks"
    result_compliant = analyzer.check_advertising_compliance(compliant_ad)
    compliant_passes = result_compliant["compliant"] is True
    
    success = discriminatory_flagged and violations_found and compliant_passes
    
    proof = ProofObject(
        rule="FairHousingDiscriminationProhibition",
        premises=[
            f"discriminatory_flagged = {discriminatory_flagged}",
            f"violations_found = {violations_found}",
            f"violations = {result_discriminatory['violations']}",
            f"compliant_passes = {compliant_passes}",
        ],
        conclusion=(
            "42 U.S.C. §3604 discrimination prohibition enforced"
            if success
            else "FAIL: Discrimination not properly detected"
        ),
    )
    return success, proof


def check_retaliation_protection() -> Tuple[bool, ProofObject]:
    """
    Invariant: Retaliation against tenants for protected activity is prohibited.
    
    Standard: 42 U.S.C. §3617; URLTA §5-501
    Falsifies if: Tenant with complaint history not protected from eviction.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
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
        complaint_history=["Habitability complaint filed 2024-01-15"],
    )
    
    # Tenant has engaged in protected activity
    protected_from_retaliation = tenant.is_protected_from_retaliation()
    
    eviction = EvictionProcess(
        case_id="E002",
        lease=lease,
        tenant=tenant,
        reason="Nonpayment",
        rent_owed=Fraction(100),
    )
    
    defenses = eviction.tenant_has_defense()
    retaliation_defense_available = "RETALIATION" in defenses["defenses"]
    has_defense = defenses["has_defense"] is True
    
    success = protected_from_retaliation and retaliation_defense_available and has_defense
    
    proof = ProofObject(
        rule="RetaliationProtection",
        premises=[
            f"protected_from_retaliation = {protected_from_retaliation}",
            f"retaliation_defense_available = {retaliation_defense_available}",
            f"has_defense = {has_defense}",
        ],
        conclusion=(
            "42 U.S.C. §3617 retaliation protection enforced"
            if success
            else "FAIL: Retaliation protection not enforced"
        ),
    )
    return success, proof


def check_reasonable_accommodation_requirement() -> Tuple[bool, ProofObject]:
    """
    Invariant: Reasonable accommodations required for disabilities.
    
    Standard: 42 U.S.C. §3604(f)(3); ADA Title III
    Falsifies if: Disability accommodations not provided when requested.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    analyzer = FairHousingAnalyzer()
    
    # Mobility accommodations
    mobility_accommodations = analyzer.get_reasonable_accommodations_required("mobility")
    mobility_has_parking = "Accessible parking space" in mobility_accommodations
    mobility_has_ramp = "Ramp or lift installation" in mobility_accommodations
    
    # Visual accommodations
    visual_accommodations = analyzer.get_reasonable_accommodations_required("visual")
    visual_has_braille = "Braille signage" in visual_accommodations
    visual_has_service_animal = "Service animal allowance" in visual_accommodations
    
    # Hearing accommodations
    hearing_accommodations = analyzer.get_reasonable_accommodations_required("hearing")
    hearing_has_visual_alarm = "Visual doorbell/alarm" in hearing_accommodations
    
    success = (
        mobility_has_parking and mobility_has_ramp and
        visual_has_braille and visual_has_service_animal and
        hearing_has_visual_alarm
    )
    
    proof = ProofObject(
        rule="ReasonableAccommodationRequirement",
        premises=[
            f"mobility_accommodations = {mobility_accommodations}",
            f"visual_accommodations = {visual_accommodations}",
            f"hearing_accommodations = {hearing_accommodations}",
        ],
        conclusion=(
            "42 U.S.C. §3604(f)(3) reasonable accommodation requirements enforced"
            if success
            else "FAIL: Reasonable accommodation requirements not met"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_HOUSING_LAW invariants."""
    checks = [
        ("check_fha_protected_classes", check_fha_protected_classes),
        ("check_eviction_notice_requirements", check_eviction_notice_requirements),
        ("check_habitability_requirements", check_habitability_requirements),
        ("check_fair_housing_discrimination_prohibition", check_fair_housing_discrimination_prohibition),
        ("check_retaliation_protection", check_retaliation_protection),
        ("check_reasonable_accommodation_requirement", check_reasonable_accommodation_requirement),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
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
    print("All D_HOUSING_LAW invariants: PASS")
