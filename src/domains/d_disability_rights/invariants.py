"""D_DISABILITYRIGHTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ADA (42 U.S.C. §12101), Section 504 (29 U.S.C. §794), IDEA (20 U.S.C. §1400)
"""

from fractions import Fraction
from src.domains.d_disability_rights.implementation import (
    Employee,
    Employer,
    PublicFacility,
    Student,
    IEP,
    DisabilityType,
    ADAComplianceChecker,
    IDEAComplianceChecker,
)


def check_reasonable_accommodation() -> bool:
    """
    Invariant: Employer must provide reasonable accommodation unless undue hardship.
    Falsification: If employer with 15+ employees denies accommodation without hardship.
    """
    checker = ADAComplianceChecker()
    
    # Employee with disability requests accommodation
    employee = Employee(
        employee_id="E001",
        name="Disabled Worker",
        disability_type=DisabilityType.PHYSICAL,
        essential_job_functions=["data_entry", "phone_calls", "meetings"],
        requested_accommodation="wheelchair accessible desk",
        qualified_for_position=True,
    )
    
    # Large employer (covered by ADA)
    large_employer = Employer(
        employer_id="EMP001",
        name="Big Corp",
        num_employees=500,  # Well over 15 threshold
        provided_accommodation=False,
        undue_hardship_claimed=False,
        hardship_justification="",
    )
    
    result = checker.check_reasonable_accommodation(employee, large_employer)
    assert result["compliant"] is False, (
        "Large employer denying accommodation without hardship should fail"
    )
    assert result["accommodation_required"] is True, (
        "Accommodation should be required"
    )
    
    # Employer with valid undue hardship claim
    hardship_employer = Employer(
        employer_id="EMP002",
        name="Small Business",
        num_employees=500,
        provided_accommodation=False,
        undue_hardship_claimed=True,
        hardship_justification="Accommodation would cost $100,000 for small department",
    )
    
    result2 = checker.check_reasonable_accommodation(employee, hardship_employer)
    assert result2["compliant"] is True, (
        "Undue hardship claim should be valid exception"
    )
    
    # Small employer (under 15, not covered by ADA Title I)
    small_employer = Employer(
        employer_id="EMP003",
        name="Tiny Shop",
        num_employees=5,
        provided_accommodation=False,
        undue_hardship_claimed=False,
        hardship_justification="",
    )
    
    result3 = checker.check_reasonable_accommodation(employee, small_employer)
    assert result3["acpliant"] is not False, (
        "Small employer under 15 not covered by ADA"
    )
    
    return True


def check_employment_discrimination() -> bool:
    """
    Invariant: Qualified individual cannot be rejected on disability alone.
    Falsification: If qualified applicant rejected due to disability.
    """
    checker = ADAComplianceChecker()
    
    # Qualified employee with disability
    qualified = Employee(
        employee_id="E002",
        name="Qualified Applicant",
        disability_type=DisabilityType.SENSORY,
        essential_job_functions=["programming", "code_review", "documentation"],
        requested_accommodation="screen reader software",
        qualified_for_position=True,
    )
    
    # Employer who discriminates
    discriminating = Employer(
        employer_id="EMP004",
        name="Discriminatory Corp",
        num_employees=100,
        provided_accommodation=False,
        undue_hardship_claimed=False,
        hardship_justification="",
    )
    
    result = checker.check_employment_discrimination(qualified, discriminating)
    assert result["compliant"] is False, (
        "Discriminating against qualified individual should fail"
    )
    assert result["violation"] == "discrimination", (
        "Should be classified as discrimination"
    )
    
    # Non-qualified individual can be rejected
    unqualified = Employee(
        employee_id="E003",
        name="Unqualified Applicant",
        disability_type=DisabilityType.PHYSICAL,
        essential_job_functions=["heavy_lifting", "construction"],
        requested_accommodation="wheelchair access",
        qualified_for_position=False,  # Cannot perform essential functions
    )
    
    result2 = checker.check_employment_discrimination(unqualified, discriminating)
    assert result2["compliant"] is True, (
        "Rejecting unqualified individual is not discrimination"
    )
    
    return True


def check_public_access_compliance() -> bool:
    """
    Invariant: Public facilities must meet ADA accessibility standards.
    Falsification: If facility lacks wheelchair access, accessible restrooms, or parking.
    """
    checker = ADAComplianceChecker()
    
    # Compliant facility
    compliant = PublicFacility(
        facility_id="F001",
        name="Accessible Library",
        facility_type="library",
        has_wheelchair_access=True,
        has_accessible_restrooms=True,
        has_accessible_parking=True,
        has_sign_language_interpreters=True,
        has_braille_signage=True,
    )
    
    result = checker.check_public_access_compliance(compliant)
    assert result["compliant"] is True, (
        "Fully accessible facility should pass"
    )
    assert len(result["issues"]) == 0, (
        "Should have no accessibility issues"
    )
    
    # Non-compliant facility
    noncompliant = PublicFacility(
        facility_id="F002",
        name="Inaccessible Building",
        facility_type="office",
        has_wheelchair_access=False,  # Violation
        has_accessible_restrooms=False,  # Violation
        has_accessible_parking=False,  # Violation
        has_sign_language_interpreters=False,
        has_braille_signage=False,
    )
    
    result2 = checker.check_public_access_compliance(noncompliant)
    assert result2["compliant"] is False, (
        "Inaccessible facility should fail"
    )
    assert len(result2["issues"]) >= 3, (
        "Should have multiple accessibility issues"
    )
    
    return True


def check_iep_components() -> bool:
    """
    Invariant: IEP must contain all required components under IDEA.
    Falsification: If IEP missing present levels, goals, services, or placement.
    """
    checker = IDEAComplianceChecker()
    
    # Complete IEP
    complete_iep = IEP(
        iep_id="IEP001",
        student_id="S001",
        present_levels="Student reads at 3rd grade level, needs assistive technology",
        annual_goals=["Read at grade level", "Use text-to-speech software independently"],
        special_education_services=["Reading instruction", "Speech therapy"],
        related_services=["Occupational therapy", "Counseling"],
        accommodations=["Extended time", "Text-to-speech", "Preferential seating"],
        placement="General education with pull-out services",
    )
    
    result = checker.check_iep_components(complete_iep)
    assert result["compliant"] is True, (
        "Complete IEP should pass"
    )
    assert result["has_all_required"] is True, (
        "Should have all required components"
    )
    
    # Incomplete IEP (missing required components)
    incomplete_iep = IEP(
        iep_id="IEP002",
        student_id="S002",
        present_levels="",  # Missing!
        annual_goals=[],  # Missing!
        special_education_services=["Reading instruction"],
        related_services=[],
        accommodations=["Extended time"],
        placement="",  # Missing!
    )
    
    result2 = checker.check_iep_components(incomplete_iep)
    assert result2["compliant"] is False, (
        "Incomplete IEP should fail"
    )
    assert "present_levels" in result2["missing_components"], (
        "Should flag missing present levels"
    )
    assert "annual_goals" in result2["missing_components"], (
        "Should flag missing goals"
    )
    
    return True


def check_least_restrictive_environment() -> bool:
    """
    Invariant: Students must be placed in least restrictive environment.
    Falsification: If student placed in restrictive setting without justification.
    """
    checker = IDEAComplianceChecker()
    
    # Student in LRE
    lre_student = Student(
        student_id="S003",
        name="Inclusive Student",
        disability_type=DisabilityType.COGNITIVE,
        age=10,
        has_iep=True,
        iep_components=["accommodations", "modifications"],
        in_least_restrictive_environment=True,
        receiving_related_services=True,
    )
    
    result = checker.check_least_restrictive_environment(lre_student)
    assert result["compliant"] is True, (
        "Student in LRE should pass"
    )
    assert result["placement"] == "LRE", (
        "Should indicate LRE placement"
    )
    
    # Student in overly restrictive environment
    restrictive_student = Student(
        student_id="S004",
        name="Segregated Student",
        disability_type=DisabilityType.COGNITIVE,
        age=10,
        has_iep=True,
        iep_components=["accommodations"],
        in_least_restrictive_environment=False,  # Violation
        receiving_related_services=True,
    )
    
    result2 = checker.check_least_restrictive_environment(restrictive_student)
    assert result2["compliant"] is False, (
        "Student not in LRE should fail"
    )
    assert result2["placement"] == "restrictive", (
        "Should indicate restrictive placement"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("reasonable_accommodation", check_reasonable_accommodation),
        ("employment_discrimination", check_employment_discrimination),
        ("public_access", check_public_access_compliance),
        ("iep_components", check_iep_components),
        ("least_restrictive_environment", check_least_restrictive_environment),
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


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_DISABILITYRIGHTS invariants: PASS")
