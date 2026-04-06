"""Tests for d_indigenous_rights domain."""

from datetime import datetime, timedelta
from fractions import Fraction

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
    check_icwa_applicability,
    check_tribal_criminal_jurisdiction,
    check_trust_land_status,
)


def test_icwa_applicability_enrolled():
    """Test ICWA applicability for enrolled child."""
    checker = ICWAComplianceChecker()
    
    child = IndianChild(
        child_id="C001",
        name="Enrolled Child",
        date_of_birth=datetime.now() - timedelta(days=365*5),
        enrolled_tribe_id="T001",
        icwa_eligible=True,
    )
    
    result = checker.check_icwa_applicability(child)
    assert result["icwa_applies"] is True
    assert result["basis"] == "enrolled_member"


def test_icwa_applicability_eligible():
    """Test ICWA applicability for eligible child."""
    checker = ICWAComplianceChecker()
    
    child = IndianChild(
        child_id="C002",
        name="Eligible Child",
        date_of_birth=datetime.now() - timedelta(days=365*5),
        eligible_for_enrollment=True,
        biological_parent_enrolled=True,
        icwa_eligible=True,
    )
    
    result = checker.check_icwa_applicability(child)
    assert result["icwa_applies"] is True


def test_icwa_placement_preference_extended_family():
    """Test ICWA extended family placement preference."""
    checker = ICWAComplianceChecker()
    
    placement = Placement(
        placement_id="P001",
        child_id="C001",
        placement_type="foster_family",
        is_extended_family=True,
    )
    
    result = checker.check_placement_preference_compliance(placement)
    assert result["preference_followed"] is True
    assert result["highest_preference_met"] == "extended_family"


def test_icwa_placement_no_good_cause():
    """Test ICWA placement without good cause fails."""
    checker = ICWAComplianceChecker()
    
    placement = Placement(
        placement_id="P002",
        child_id="C001",
        placement_type="foster_family",
        is_extended_family=False,
        is_tribal_member=False,
        is_other_indian=False,
        good_cause_exception=None,
    )
    
    result = checker.check_placement_preference_compliance(placement)
    assert result["preference_followed"] is False
    assert result["good_cause_required"] is True


def test_nhpa_consultation_required():
    """Test NHPA consultation required for sacred sites."""
    checker = ConsultationComplianceChecker()
    
    result = checker.check_nhpa_section_106(
        undertaking_affects_historic_properties=True,
        tribal_sacred_sites_affected=True,
        consultation_conducted=False,
    )
    
    assert result["compliant"] is False
    assert "violation" in result


def test_nhpa_consultation_compliant():
    """Test NHPA consultation compliance."""
    checker = ConsultationComplianceChecker()
    
    result = checker.check_nhpa_section_106(
        undertaking_affects_historic_properties=True,
        tribal_sacred_sites_affected=True,
        consultation_conducted=True,
    )
    
    assert result["compliant"] is True


def test_tribal_jurisdiction_member():
    """Test tribal jurisdiction over member on reservation."""
    analyzer = TribalSovereigntyAnalyzer()
    
    result = analyzer.analyze_criminal_jurisdiction(
        crime_location="reservation",
        victim_tribal_status="tribal_member",
        defendant_tribal_status="tribal_member",
        crime_type="misdemeanor",
    )
    
    assert result.get("tribal") is True


def test_tribal_jurisdiction_non_indian():
    """Test lack of tribal jurisdiction over non-Indian (Oliphant)."""
    analyzer = TribalSovereigntyAnalyzer()
    
    result = analyzer.analyze_criminal_jurisdiction(
        crime_location="reservation",
        victim_tribal_status="tribal_member",
        defendant_tribal_status="non_indian",
        crime_type="misdemeanor",
    )
    
    assert result.get("tribal") is not True


def test_trust_responsibility_recognized():
    """Test trust responsibility for recognized tribe."""
    checker = TrustResponsibilityChecker()
    
    tribe = TribalNation(
        tribe_id="T001",
        name="Recognized Tribe",
        federally_recognized=True,
        trust_land_acres=Fraction(10000),
    )
    
    result = checker.check_trust_responsibility(tribe)
    assert result["trust_responsibility_exists"] is True
    assert len(result["obligations"]) > 0


def test_trust_responsibility_unrecognized():
    """Test no trust responsibility for unrecognized tribe."""
    checker = TrustResponsibilityChecker()
    
    tribe = TribalNation(
        tribe_id="T002",
        name="Unrecognized Tribe",
        federally_recognized=False,
        trust_land_acres=Fraction(0),
    )
    
    result = checker.check_trust_responsibility(tribe)
    assert result["trust_responsibility_exists"] is False


def test_active_efforts_requirement():
    """Test ICWA active efforts requirement."""
    checker = ICWAComplianceChecker()
    
    result = checker.check_active_efforts_requirement(datetime.now())
    assert result["active_efforts_required"] is True
    assert result["standard"] == "active_efforts"
    assert "Tribal" in str(result["efforts_must_include"])


def test_qualified_expert_witness():
    """Test qualified expert witness requirement."""
    checker = ICWAComplianceChecker()
    
    result = checker.check_qualified_expert_witness_requirement()
    assert result["qew_required"] is True
    assert len(result["qew_qualifications"]) > 0


def test_convenience_function_icwa():
    """Test convenience function for ICWA applicability."""
    result = check_icwa_applicability(True, False, False)
    assert result["icwa_applies"] is True
    
    result2 = check_icwa_applicability(False, True, True)
    assert result2["icwa_applies"] is True
    
    result3 = check_icwa_applicability(False, True, False)
    assert result3["icwa_applies"] is False


def test_convenience_function_jurisdiction():
    """Test convenience function for tribal jurisdiction."""
    result = check_tribal_criminal_jurisdiction(True, "reservation")
    assert result["tribal_jurisdiction"] is True
    
    result2 = check_tribal_criminal_jurisdiction(False, "reservation")
    assert result2["tribal_jurisdiction"] is False


def test_convenience_function_trust_land():
    """Test convenience function for trust land status."""
    result = check_trust_land_status("trust")
    assert result["trust_land"] is True
    assert result["tax_exempt"] is True
    
    result2 = check_trust_land_status("fee")
    assert result2["trust_land"] is False
