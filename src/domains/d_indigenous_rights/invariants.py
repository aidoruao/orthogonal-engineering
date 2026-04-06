"""D_INDIGENOUS_RIGHTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ICWA (25 U.S.C. §1901), NHPA §106, Tribal Law and Order Act
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_indigenous_rights.implementation import (
    ICWAComplianceChecker,
    TribalSovereigntyAnalyzer,
    TrustResponsibilityChecker,
    ConsultationComplianceChecker,
    IndigenousRightsEnforcer,
    TribalNation,
    IndianChild,
    Placement,
    Treaty,
    TrustAsset,
    ConsultationRecord,
    TribalEntityType,
    TreatyRightType,
    ICWAPreference,
    ConsultationType,
    TrustAssetType,
)


def check_icwa_placement_preferences_followed() -> bool:
    """
    Invariant: ICWA placement preferences must be followed unless good cause.
    Falsification: If non-Indian placement preferred over tribal placement.
    """
    checker = ICWAComplianceChecker()
    
    # Placement with extended family (highest preference)
    family_placement = Placement(
        placement_id="P001",
        child_id="C001",
        placement_type="foster_family",
        is_extended_family=True,
        is_tribal_member=False,
        is_other_indian=False,
    )
    
    result = checker.check_placement_preference_compliance(family_placement)
    assert result["preference_followed"] is True, (
        "Extended family placement should meet ICWA preference"
    )
    assert result["highest_preference_met"] == "extended_family", (
        "Should recognize extended family preference"
    )
    
    # Placement with non-Indian, no good cause
    non_indian_placement = Placement(
        placement_id="P002",
        child_id="C001",
        placement_type="foster_family",
        is_extended_family=False,
        is_tribal_member=False,
        is_other_indian=False,
        good_cause_exception=None,
    )
    
    result2 = checker.check_placement_preference_compliance(non_indian_placement)
    assert result2["preference_followed"] is False, (
        "Non-Indian placement without good cause should fail"
    )
    assert result2["good_cause_required"] is True, (
        "Good cause required when preference not followed"
    )
    
    # Non-Indian placement with good cause
    non_indian_with_cause = Placement(
        placement_id="P003",
        child_id="C001",
        placement_type="foster_family",
        is_extended_family=False,
        is_tribal_member=False,
        is_other_indian=False,
        good_cause_exception="No Indian placements available after diligent search",
    )
    
    result3 = checker.check_placement_preference_compliance(non_indian_with_cause)
    assert result3["good_cause_documented"] is True, (
        "Should document good cause exception"
    )
    
    return True


def check_tribal_consultation_required() -> bool:
    """
    Invariant: Tribal consultation required for federal actions on tribal land.
    Falsification: If project affecting sacred sites proceeds without consultation.
    """
    checker = ConsultationComplianceChecker()
    
    # Project affecting sacred sites without consultation
    no_consultation = checker.check_nhpa_section_106(
        undertaking_affects_historic_properties=True,
        tribal_sacred_sites_affected=True,
        consultation_conducted=False,
    )
    
    assert no_consultation["compliant"] is False, (
        "Project affecting sacred sites without consultation should fail"
    )
    assert "violation" in no_consultation, (
        "Should identify NHPA violation"
    )
    
    # Same project with consultation
    with_consultation = checker.check_nhpa_section_106(
        undertaking_affects_historic_properties=True,
        tribal_sacred_sites_affected=True,
        consultation_conducted=True,
    )
    
    assert with_consultation["compliant"] is True, (
        "Project with consultation should be compliant"
    )
    
    # Project not affecting tribal interests
    no_tribal_impact = checker.check_nhpa_section_106(
        undertaking_affects_historic_properties=False,
        tribal_sacred_sites_affected=False,
        consultation_conducted=False,
    )
    
    assert no_tribal_impact["compliant"] is True, (
        "Project without tribal impact doesn't require consultation"
    )
    
    return True


def check_active_efforts_higher_standard() -> bool:
    """
    Invariant: ICWA requires "active efforts" (higher than reasonable efforts).
    Falsification: If ICWA case proceeds with only reasonable efforts.
    """
    checker = ICWAComplianceChecker()
    
    result = checker.check_active_efforts_requirement(datetime.now())
    
    assert result["active_efforts_required"] is True, (
        "ICWA requires active efforts"
    )
    assert result["standard"] == "active_efforts", (
        "ICWA standard should be active efforts"
    )
    # Active efforts more comprehensive than reasonable efforts
    assert "Tribal" in str(result["efforts_must_include"]), (
        "Active efforts must include tribal components"
    )
    
    return True


def check_tribal_criminal_jurisdiction_over_members() -> bool:
    """
    Invariant: Tribes have criminal jurisdiction over tribal members on reservation.
    Falsification: If state claims jurisdiction over tribal member on reservation.
    """
    analyzer = TribalSovereigntyAnalyzer()
    
    # Tribal member on reservation
    tribal_member = analyzer.analyze_criminal_jurisdiction(
        crime_location="reservation",
        victim_tribal_status="tribal_member",
        defendant_tribal_status="tribal_member",
        crime_type="misdemeanor",
    )
    
    assert tribal_member.get("tribal") is True, (
        "Tribe should have jurisdiction over member on reservation"
    )
    
    # Non-Indian on reservation (Oliphant rule)
    non_indian = analyzer.analyze_criminal_jurisdiction(
        crime_location="reservation",
        victim_tribal_status="tribal_member",
        defendant_tribal_status="non_indian",
        crime_type="misdemeanor",
    )
    
    assert non_indian.get("tribal") is not True, (
        "Tribe lacks criminal jurisdiction over non-Indians (Oliphant)"
    )
    
    return True


def check_trust_responsibility_for_recognized_tribes() -> bool:
    """
    Invariant: Federal trust responsibility applies to federally recognized tribes.
    Falsification: If unrecognized tribe claims trust responsibility.
    """
    checker = TrustResponsibilityChecker()
    
    # Federally recognized tribe
    recognized_tribe = TribalNation(
        tribe_id="T001",
        name="Recognized Tribe",
        federally_recognized=True,
        trust_land_acres=Fraction(10000),
    )
    
    result = checker.check_trust_responsibility(recognized_tribe)
    assert result["trust_responsibility_exists"] is True, (
        "Federal trust responsibility should exist for recognized tribes"
    )
    assert len(result["obligations"]) > 0, (
        "Trust responsibility creates obligations"
    )
    
    # Unrecognized tribe
    unrecognized_tribe = TribalNation(
        tribe_id="T002",
        name="Unrecognized Tribe",
        federally_recognized=False,
    )
    
    result2 = checker.check_trust_responsibility(unrecognized_tribe)
    assert result2["trust_responsibility_exists"] is False, (
        "No federal trust responsibility for unrecognized tribes"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("icwa_placement_preferences", check_icwa_placement_preferences_followed),
        ("tribal_consultation", check_tribal_consultation_required),
        ("active_efforts", check_active_efforts_higher_standard),
        ("tribal_criminal_jurisdiction", check_tribal_criminal_jurisdiction_over_members),
        ("trust_responsibility", check_trust_responsibility_for_recognized_tribes),
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
