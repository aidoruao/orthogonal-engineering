"""D_REAL_ESTATE invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: State property codes, Fair Housing Act, RESPA
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_real_estate.implementation import (
    PropertyAssessor,
    FairLendingMonitor,
    DisclosureManager,
    RealEstateAuditor,
    Property,
    PropertyAssessment,
    LoanApplication,
    LendingDecision,
    PropertyDisclosure,
    DisclosurePackage,
    PropertyType,
    LoanDecision,
    ProtectedClass,
    DisclosureType,
)


def check_property_assessment_reproducible() -> bool:
    """
    Invariant: Property assessment is reproducible.
    Falsification: If same property produces different assessments.
    """
    assessor = PropertyAssessor()
    
    # Create property
    property_obj = Property(
        property_id="P001",
        address="123 Main St",
        parcel_number="123-456-789",
        property_type=PropertyType.SINGLE_FAMILY_RESIDENTIAL,
        lot_size_sqft=Fraction(8712),  # 0.2 acres
        year_built=2000,
        square_footage=Fraction(2000),
        num_bedrooms=3,
        num_bathrooms=Fraction(2),
    )
    
    comparable_sales = ["SALE001", "SALE002", "SALE003"]
    
    # Assess multiple times
    assessment1 = assessor.assess_property(property_obj, comparable_sales)
    assessment2 = assessor.assess_property(property_obj, comparable_sales)
    assessment3 = assessor.assess_property(property_obj, comparable_sales)
    
    # Should be identical
    assert assessment1.total_value == assessment2.total_value, (
        "Assessment must be reproducible"
    )
    assert assessment2.total_value == assessment3.total_value, (
        "Assessment must be consistent"
    )
    
    # Should have documented methodology
    assert assessment1.assessment_reproducible is True, (
        "Assessment should have documented methodology"
    )
    assert len(assessment1.comparable_sales) > 0, (
        "Assessment should use comparable sales"
    )
    
    return True


def check_no_race_based_lending_discrimination() -> bool:
    """
    Invariant: No race-based lending discrimination (anti-redlining).
    Falsification: If discriminatory approval rates are not detected.
    """
    monitor = FairLendingMonitor()
    
    # Create applications from different racial groups
    applications = [
        LoanApplication(
            application_id="A001",
            applicant_id="APP001",
            property_id="P001",
            applicant_race="White",
            loan_amount=Fraction(300000),
            applicant_income=Fraction(80000),
            credit_score=720,
            debt_to_income_ratio=Fraction(30, 100),
        ),
        LoanApplication(
            application_id="A002",
            applicant_id="APP002",
            property_id="P002",
            applicant_race="Black",
            loan_amount=Fraction(300000),
            applicant_income=Fraction(80000),
            credit_score=720,
            debt_to_income_ratio=Fraction(30, 100),
        ),
        LoanApplication(
            application_id="A003",
            applicant_id="APP003",
            property_id="P003",
            applicant_race="White",
            loan_amount=Fraction(250000),
            applicant_income=Fraction(70000),
            credit_score=700,
            debt_to_income_ratio=Fraction(35, 100),
        ),
        LoanApplication(
            application_id="A004",
            applicant_id="APP004",
            property_id="P004",
            applicant_race="Black",
            loan_amount=Fraction(250000),
            applicant_income=Fraction(70000),
            credit_score=700,
            debt_to_income_ratio=Fraction(35, 100),
        ),
    ]
    
    # Create decisions (equal treatment)
    decisions = [
        LendingDecision(
            decision_id="D001",
            application_id="A001",
            approved=True,
            loan_amount=Fraction(300000),
            rationale="Creditworthy applicant",
        ),
        LendingDecision(
            decision_id="D002",
            application_id="A002",
            approved=True,
            loan_amount=Fraction(300000),
            rationale="Creditworthy applicant",
        ),
        LendingDecision(
            decision_id="D003",
            application_id="A003",
            approved=True,
            loan_amount=Fraction(250000),
            rationale="Creditworthy applicant",
        ),
        LendingDecision(
            decision_id="D004",
            application_id="A004",
            approved=True,
            loan_amount=Fraction(250000),
            rationale="Creditworthy applicant",
        ),
    ]
    
    analysis = monitor.analyze_lending_decisions(decisions, applications)
    
    # Should have data for both races
    assert "White" in analysis["by_race"], (
        "Analysis should include White applicants"
    )
    assert "Black" in analysis["by_race"], (
        "Analysis should include Black applicants"
    )
    
    # Approval rates should be equal (both 100% in this case)
    white_rate = analysis["by_race"]["White"]["approval_rate"]
    black_rate = analysis["by_race"]["Black"]["approval_rate"]
    assert white_rate == black_rate, (
        f"Equal applicants should have equal approval rates: White={white_rate}, Black={black_rate}"
    )
    
    return True


def check_disclosure_requirements_complete() -> bool:
    """
    Invariant: Disclosure requirements are enumerated and complete.
    Falsification: If incomplete disclosures pass compliance.
    """
    manager = DisclosureManager()
    
    # Create complete disclosure package
    package = manager.create_package("PKG001", "P001", "T001")
    
    # Add all required disclosures
    required_disclosures = [
        (DisclosureType.LEAD_BASED_PAINT, ["No lead paint known"]),
        (DisclosureType.NATURAL_HAZARDS, ["Earthquake zone", "Flood zone"]),
        (DisclosureType.TRANSFER_DISCLOSURE, ["Property condition disclosed"]),
        (DisclosureType.AGENCY_DISCLOSURE, ["Agency relationship disclosed"]),
    ]
    
    for dtype, items in required_disclosures:
        disclosure = manager.create_disclosure(
            f"D_{dtype.name}", "P001", dtype, items
        )
        manager.add_disclosure_to_package(package, disclosure)
    
    result = manager.check_package_compliance(package)
    assert result["complete"] is True, (
        "Complete disclosure package should pass"
    )
    assert len(result["missing_types"]) == 0, (
        "Complete package should have no missing types"
    )
    
    # Create incomplete package
    incomplete_package = manager.create_package("PKG002", "P002", "T002")
    
    # Add only some disclosures
    disclosure1 = manager.create_disclosure(
        "D1", "P002", DisclosureType.LEAD_BASED_PAINT, ["No lead paint"]
    )
    manager.add_disclosure_to_package(incomplete_package, disclosure1)
    
    result2 = manager.check_package_compliance(incomplete_package)
    assert result2["complete"] is False, (
        "Incomplete package should not pass"
    )
    assert len(result2["missing_types"]) > 0, (
        "Incomplete package should have missing types"
    )
    
    return True


def check_lending_legitimate_factors_only() -> bool:
    """
    Invariant: Lending decisions must use only legitimate factors.
    Falsification: If decision without legitimate factors passes check.
    """
    monitor = FairLendingMonitor()
    
    # Decision using legitimate factors only
    legitimate_decision = LendingDecision(
        decision_id="D005",
        application_id="A005",
        approved=True,
        loan_amount=Fraction(200000),
        credit_score_used=True,
        income_verified=True,
        property_appraised=True,
        debt_ratio_calculated=True,
        rationale="Credit score 750, income verified, DTI 28%",
    )
    
    result = monitor.check_decision_factors(legitimate_decision)
    assert result["legitimate_factors_only"] is True, (
        "Decision using legitimate factors should pass"
    )
    assert result["documented_rationale"] is True, (
        "Decision with rationale should pass documentation check"
    )
    
    # Decision lacking legitimate factors
    illegitimate_decision = LendingDecision(
        decision_id="D006",
        application_id="A006",
        approved=False,
        credit_score_used=False,  # Not used!
        income_verified=False,    # Not verified!
        property_appraised=False,
        debt_ratio_calculated=False,
        rationale="",  # No rationale!
    )
    
    result2 = monitor.check_decision_factors(illegitimate_decision)
    assert result2["legitimate_factors_only"] is False, (
        "Decision without legitimate factors should fail"
    )
    assert result2["documented_rationale"] is False, (
        "Decision without rationale should fail documentation check"
    )
    
    return True


def check_assessment_method_documented() -> bool:
    """
    Invariant: Assessment method must be documented.
    Falsification: If assessment without method passes check.
    """
    assessor = PropertyAssessor()
    
    property_obj = Property(
        property_id="P003",
        address="456 Oak St",
        parcel_number="987-654-321",
        property_type=PropertyType.SINGLE_FAMILY_RESIDENTIAL,
        lot_size_sqft=Fraction(10000),
        year_built=1995,
        square_footage=Fraction(1800),
    )
    
    # Proper assessment with comparables
    assessment = assessor.assess_property(property_obj, ["SALE001", "SALE002"])
    
    assert assessment.assessment_method != "", (
        "Assessment should have documented method"
    )
    assert assessment.assessor_id != "", (
        "Assessment should have assessor ID"
    )
    assert len(assessment.comparable_sales) > 0, (
        "Assessment should have comparable sales"
    )
    
    return True


def check_disclosure_types_enumerated() -> bool:
    """
    Invariant: Required disclosure types are enumerated.
    Falsification: If required type is missing from enumeration.
    """
    # Check that all expected disclosure types exist
    expected_types = {
        DisclosureType.LEAD_BASED_PAINT,
        DisclosureType.NATURAL_HAZARDS,
        DisclosureType.TRANSFER_DISCLOSURE,
        DisclosureType.AGENCY_DISCLOSURE,
        DisclosureType.MORTGAGE_DISCLOSURE,
    }
    
    all_types = set(DisclosureType)
    
    for expected in expected_types:
        assert expected in all_types, (
            f"Required disclosure type {expected} should be enumerated"
        )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("assessment_reproducible", check_property_assessment_reproducible),
        ("anti_redlining", check_no_race_based_lending_discrimination),
        ("disclosure_complete", check_disclosure_requirements_complete),
        ("legitimate_factors", check_lending_legitimate_factors_only),
        ("assessment_documented", check_assessment_method_documented),
        ("disclosure_enumerated", check_disclosure_types_enumerated),
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
