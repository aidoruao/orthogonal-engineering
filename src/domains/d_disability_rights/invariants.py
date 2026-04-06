"""D_DISABILITY_RIGHTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ADA (42 U.S.C. §12101), Section 504, WCAG 2.1
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_disability_rights.implementation import (
    ReasonableAccommodationAnalyzer,
    AccessibilityComplianceChecker,
    DisabilityRightsEnforcer,
    Individual,
    Employer,
    AccommodationRequest,
    PhysicalFacility,
    DigitalContent,
    AccessibilityBarrier,
    DisabilityType,
    AccommodationType,
    EntityType,
)


def check_interactive_process_required() -> bool:
    """
    Invariant: Interactive process required before denying accommodation.
    Falsification: If accommodation denied without interactive process.
    """
    analyzer = ReasonableAccommodationAnalyzer()
    
    # Request without interactive process
    request_no_process = AccommodationRequest(
        request_id="R001",
        individual_id="I001",
        employer_id="E001",
        accommodation_type=AccommodationType.SCHEDULE_MODIFICATION,
        description="Flexible schedule for medical appointments",
        request_date=datetime.now(),
        interactive_process_started=None,
        granted=False,
    )
    
    result = analyzer.check_interactive_process(request_no_process)
    assert result["compliant"] is False, (
        "Denial without interactive process should be non-compliant"
    )
    
    # Request with interactive process
    request_with_process = AccommodationRequest(
        request_id="R002",
        individual_id="I002",
        employer_id="E001",
        accommodation_type=AccommodationType.EQUIPMENT_PROVISION,
        description="Screen reader software",
        request_date=datetime.now(),
        interactive_process_started=datetime.now() - timedelta(days=5),
        interactive_process_completed=datetime.now() - timedelta(days=1),
        granted=True,
    )
    
    result2 = analyzer.check_interactive_process(request_with_process)
    assert result2["compliant"] is True, (
        "Request with completed interactive process should be compliant"
    )
    
    return True


def check_employer_ada_coverage_threshold() -> bool:
    """
    Invariant: ADA Title I covers employers with 15+ employees.
    Falsification: If 10-employee employer is covered or 100-employee employer is not.
    """
    # Small employer - not covered
    small_employer = Employer(
        employer_id="E001",
        name="Small Business",
        employee_count=10,
    )
    assert small_employer.ada_covered is False, (
        "Employer with 10 employees should not be covered by ADA Title I"
    )
    
    # Medium employer - covered
    medium_employer = Employer(
        employer_id="E002",
        name="Medium Business",
        employee_count=50,
    )
    assert medium_employer.ada_covered is True, (
        "Employer with 50 employees should be covered by ADA Title I"
    )
    
    # Large employer - covered
    large_employer = Employer(
        employer_id="E003",
        name="Large Corporation",
        employee_count=5000,
    )
    assert large_employer.ada_covered is True, (
        "Employer with 5000 employees should be covered by ADA Title I"
    )
    
    return True


def check_accommodation_effective_unless_undue_hardship() -> bool:
    """
    Invariant: Accommodation must be effective unless undue hardship.
    Falsification: If low-cost accommodation denied without reason.
    """
    analyzer = ReasonableAccommodationAnalyzer()
    
    employer = Employer(
        employer_id="E004",
        name="Test Employer",
        employee_count=100,
    )
    
    individual = Individual(
        individual_id="I003",
        name="Employee with Disability",
        disabilities={DisabilityType.SENSORY},
    )
    
    request = AccommodationRequest(
        request_id="R003",
        individual_id="I003",
        employer_id="E004",
        accommodation_type=AccommodationType.EQUIPMENT_PROVISION,
        description="Magnification software",
        request_date=datetime.now(),
        interactive_process_started=datetime.now() - timedelta(days=7),
        interactive_process_completed=datetime.now() - timedelta(days=1),
    )
    
    # Low cost accommodation ($500) for large employer ($10M revenue)
    result = analyzer.evaluate_accommodation(
        request=request,
        employer=employer,
        individual=individual,
        estimated_cost=Fraction(500),
        employer_revenue=Fraction(10_000_000),
    )
    
    assert result["accommodation_granted"] is True, (
        "Low-cost accommodation should be granted"
    )
    assert result["undue_hardship"] is False, (
        "0.005% cost ratio should not be undue hardship"
    )
    
    # Very high cost accommodation for small employer
    result2 = analyzer.evaluate_accommodation(
        request=request,
        employer=Employer(employer_id="E005", name="Small", employee_count=15),
        individual=individual,
        estimated_cost=Fraction(100_000),
        employer_revenue=Fraction(500_000),
    )
    
    assert result2["accommodation_granted"] is False, (
        "20% cost accommodation may be undue hardship"
    )
    
    return True


def check_public_accommodations_accessible() -> bool:
    """
    Invariant: Public accommodations must be accessible (Title III).
    Falsification: If facility without accessible entrance passes compliance.
    """
    checker = AccessibilityComplianceChecker()
    
    # Non-compliant facility
    bad_facility = PhysicalFacility(
        facility_id="F001",
        name="Inaccessible Store",
        address="123 Main St",
        entity_type=EntityType.PUBLIC_ACCOMMODATION,
        has_accessible_entrance=False,
        has_accessible_restroom=False,
        has_accessible_parking=False,
    )
    
    result = checker.check_physical_accessibility(bad_facility)
    assert result["compliant"] is False, (
        "Facility without accessible features should fail"
    )
    assert len(result["issues"]) > 0, (
        "Should identify accessibility issues"
    )
    
    # Compliant facility
    good_facility = PhysicalFacility(
        facility_id="F002",
        name="Accessible Store",
        address="456 Oak St",
        entity_type=EntityType.PUBLIC_ACCOMMODATION,
        has_accessible_entrance=True,
        has_accessible_restroom=True,
        has_accessible_parking=True,
    )
    
    result2 = checker.check_physical_accessibility(good_facility)
    assert result2["compliant"] is True, (
        "Facility with accessible features should pass"
    )
    
    return True


def check_wcag_aa_compliance() -> bool:
    """
    Invariant: Digital content should meet WCAG 2.1 AA standards.
    Falsification: If content missing alt text, captions, keyboard nav passes AA.
    """
    checker = AccessibilityComplianceChecker()
    
    # Non-compliant digital content
    bad_content = DigitalContent(
        content_id="D001",
        content_type="website",
        owner_id="E001",
        has_alt_text=False,
        has_captions=False,
        has_keyboard_navigation=False,
        has_screen_reader_support=False,
        has_sufficient_contrast=False,
    )
    
    result = checker.check_digital_accessibility(bad_content)
    assert result["wcag_aa_compliant"] is False, (
        "Content missing accessibility features should not pass WCAG AA"
    )
    assert len(result["missing"]) > 0, (
        "Should identify missing accessibility features"
    )
    
    # Compliant digital content
    good_content = DigitalContent(
        content_id="D002",
        content_type="website",
        owner_id="E002",
        has_alt_text=True,
        has_captions=True,
        has_keyboard_navigation=True,
        has_screen_reader_support=True,
        has_sufficient_contrast=True,
        wcag_level="AA",
    )
    
    result2 = checker.check_digital_accessibility(good_content)
    assert result2["wcag_aa_compliant"] is True, (
        "Content with all accessibility features should pass WCAG AA"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("interactive_process", check_interactive_process_required),
        ("ada_coverage_threshold", check_employer_ada_coverage_threshold),
        ("accommodation_effective", check_accommodation_effective_unless_undue_hardship),
        ("public_accommodations", check_public_accommodations_accessible),
        ("wcag_aa", check_wcag_aa_compliance),
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
