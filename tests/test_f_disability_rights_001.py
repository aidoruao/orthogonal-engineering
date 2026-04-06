"""Tests for d_disability_rights domain."""

from datetime import datetime, timedelta
from fractions import Fraction

from src.domains.d_disability_rights.implementation import (
    ReasonableAccommodationAnalyzer,
    AccessibilityComplianceChecker,
    DisabilityRightsEnforcer,
    Individual,
    Employer,
    AccommodationRequest,
    PhysicalFacility,
    DigitalContent,
    DisabilityType,
    AccommodationType,
    EntityType,
    check_reasonable_accommodation_requirement,
    check_wcag_compliance,
    check_undue_hardship_threshold,
)


def test_employer_ada_coverage():
    """Test ADA coverage threshold for employers."""
    small = Employer("E001", "Small Co", 10)
    assert small.ada_covered is False
    
    medium = Employer("E002", "Medium Co", 50)
    assert medium.ada_covered is True
    
    large = Employer("E003", "Large Co", 500)
    assert large.ada_covered is True


def test_interactive_process_compliance():
    """Test interactive process requirement."""
    analyzer = ReasonableAccommodationAnalyzer()
    
    # No interactive process
    request_bad = AccommodationRequest(
        request_id="R001",
        individual_id="I001",
        employer_id="E001",
        accommodation_type=AccommodationType.SCHEDULE_MODIFICATION,
        description="Flexible hours",
        request_date=datetime.now(),
        granted=False,
    )
    
    result = analyzer.check_interactive_process(request_bad)
    assert result["compliant"] is False
    
    # With interactive process
    request_good = AccommodationRequest(
        request_id="R002",
        individual_id="I002",
        employer_id="E001",
        accommodation_type=AccommodationType.EQUIPMENT_PROVISION,
        description="Screen reader",
        request_date=datetime.now(),
        interactive_process_started=datetime.now() - timedelta(days=5),
        interactive_process_completed=datetime.now() - timedelta(days=1),
        granted=True,
    )
    
    result2 = analyzer.check_interactive_process(request_good)
    assert result2["compliant"] is True


def test_accommodation_evaluation():
    """Test accommodation evaluation logic."""
    analyzer = ReasonableAccommodationAnalyzer()
    
    employer = Employer("E004", "Test Employer", 100)
    individual = Individual("I003", "Test Employee", {DisabilityType.MOBILITY})
    request = AccommodationRequest(
        request_id="R003",
        individual_id="I003",
        employer_id="E004",
        accommodation_type=AccommodationType.ACCESSIBLE_FACILITY,
        description="Ramp",
        request_date=datetime.now(),
    )
    
    result = analyzer.evaluate_accommodation(
        request, employer, individual,
        estimated_cost=Fraction(5000),
        employer_revenue=Fraction(1_000_000),
    )
    
    assert result["accommodation_granted"] is True


def test_physical_accessibility_compliance():
    """Test physical facility accessibility compliance."""
    checker = AccessibilityComplianceChecker()
    
    bad_facility = PhysicalFacility(
        facility_id="F001",
        name="Bad Store",
        address="123 Main",
        entity_type=EntityType.PUBLIC_ACCOMMODATION,
        has_accessible_entrance=False,
        has_accessible_restroom=False,
    )
    
    result = checker.check_physical_accessibility(bad_facility)
    assert result["compliant"] is False


def test_digital_accessibility_compliance():
    """Test digital content WCAG compliance."""
    checker = AccessibilityComplianceChecker()
    
    bad_content = DigitalContent(
        content_id="D001",
        content_type="website",
        owner_id="E001",
        has_alt_text=False,
        has_captions=False,
    )
    
    result = checker.check_digital_accessibility(bad_content)
    assert result["wcag_aa_compliant"] is False


def test_convenience_function_ada_requirement():
    """Test convenience function for ADA requirement."""
    result = check_reasonable_accommodation_requirement(10)
    assert result["covered_by_ada"] is False
    
    result2 = check_reasonable_accommodation_requirement(20)
    assert result2["covered_by_ada"] is True


def test_convenience_function_wcag():
    """Test convenience function for WCAG compliance."""
    result = check_wcag_compliance(True, True, True)
    assert result["wcag_aa_compliant"] is True
    
    result2 = check_wcag_compliance(True, False, True)
    assert result2["wcag_aa_compliant"] is False


def test_convenience_function_undue_hardship():
    """Test convenience function for undue hardship."""
    result = check_undue_hardship_threshold(1000, 100000)
    assert result["undue_hardship"] is False  # 1% < 5%
    
    result2 = check_undue_hardship_threshold(10000, 100000)
    assert result2["undue_hardship"] is True  # 10% > 5%


def test_title_i_audit():
    """Test Title I audit functionality."""
    enforcer = DisabilityRightsEnforcer()
    
    covered_employer = Employer("E005", "Covered", 50)
    result = enforcer.conduct_title_i_audit(covered_employer)
    assert result["covered"] is True
    
    uncovered_employer = Employer("E006", "Uncovered", 5)
    result2 = enforcer.conduct_title_i_audit(uncovered_employer)
    assert result2["covered"] is False
