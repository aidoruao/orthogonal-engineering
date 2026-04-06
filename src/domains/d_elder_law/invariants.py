"""D_ELDER_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: SSA (42 U.S.C. §1395), Medicaid (42 U.S.C. §1396), Elder Justice Act
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_elder_law.implementation import (
    MedicareEligibilityChecker,
    MedicaidEligibilityCalculator,
    ElderAbuseDetector,
    GuardianshipEvaluator,
    ElderLawCaseManager,
    Senior,
    LongTermCareFacility,
    ElderAbuseReport,
    Guardianship,
    MedicarePart,
    MedicaidCategory,
    AbuseType,
    GuardianType,
)


def check_medicare_part_a_automatic_at_65() -> bool:
    """
    Invariant: Medicare Part A is automatic at age 65 (if work credits).
    Falsification: If 70-year-old is denied Part A without cause.
    """
    checker = MedicareEligibilityChecker()
    
    # Senior age 70 - should be eligible for Part A
    senior_70 = Senior(
        senior_id="S001",
        name="Seventy Year Old",
        date_of_birth=datetime.now() - timedelta(days=365*70),
        medicare_enrolled=False,
    )
    
    result = checker.check_medicare_eligibility(senior_70)
    assert result["part_a_eligible"] is True, (
        "70-year-old should be eligible for Part A"
    )
    assert result["automatic_enrollment"] is True, (
        "Automatic enrollment should apply at 70"
    )
    
    # Senior age 60 - not yet eligible
    senior_60 = Senior(
        senior_id="S002",
        name="Sixty Year Old",
        date_of_birth=datetime.now() - timedelta(days=365*60),
        medicare_enrolled=False,
    )
    
    result2 = checker.check_medicare_eligibility(senior_60)
    assert result2["part_a_eligible"] is False, (
        "60-year-old should not be eligible for Part A"
    )
    
    return True


def check_medicaid_asset_limit() -> bool:
    """
    Invariant: Medicaid has asset limits ($2,000 individual, $3,000 couple).
    Falsification: If senior with $50,000 countable assets is eligible.
    """
    calculator = MedicaidEligibilityCalculator()
    
    # Low-asset senior - should be eligible
    low_asset_senior = Senior(
        senior_id="S003",
        name="Low Asset Senior",
        date_of_birth=datetime.now() - timedelta(days=365*75),
        monthly_income=Fraction(1000),
        countable_assets=Fraction(1500),  # Below $2,000 limit
    )
    
    result = calculator.check_medicaid_eligibility(low_asset_senior)
    assert result["asset_eligible"] is True, (
        "Senior with $1,500 assets should pass asset test"
    )
    
    # High-asset senior - should not be eligible
    high_asset_senior = Senior(
        senior_id="S004",
        name="High Asset Senior",
        date_of_birth=datetime.now() - timedelta(days=365*75),
        monthly_income=Fraction(1000),
        countable_assets=Fraction(50000),  # Above $2,000 limit
    )
    
    result2 = calculator.check_medicaid_eligibility(high_asset_senior)
    assert result2["asset_eligible"] is False, (
        "Senior with $50,000 assets should fail asset test"
    )
    
    return True


def check_guardianship_requires_incapacity() -> bool:
    """
    Invariant: Guardianship requires finding of incapacity.
    Falsification: If guardianship granted without incapacity finding.
    """
    evaluator = GuardianshipEvaluator()
    
    # No capacity assessment - no guardianship
    no_guardianship = evaluator.evaluate_guardianship_need(
        senior=Senior("S005", "Test", datetime.now() - timedelta(days=365*80)),
        medical_capacity_assessment="capable",
        less_restrictive_options_exhausted=True,
    )
    
    assert no_guardianship["guardianship_appropriate"] is False, (
        "Capable senior should not have guardianship"
    )
    assert no_guardianship["incapacity_found"] is False, (
        "Should not find incapacity for capable senior"
    )
    
    # Incapacity found - guardianship may be appropriate
    with_guardianship = evaluator.evaluate_guardianship_need(
        senior=Senior("S006", "Test", datetime.now() - timedelta(days=365*80)),
        medical_capacity_assessment="incapable",
        less_restrictive_options_exhausted=True,
    )
    
    assert with_guardianship["incapacity_found"] is True, (
        "Should find incapacity for incapable senior"
    )
    assert with_guardianship["guardianship_appropriate"] is True, (
        "Guardianship should be appropriate with incapacity and exhausted alternatives"
    )
    
    return True


def check_clear_and_convincing_evidence_guardianship() -> bool:
    """
    Invariant: Guardianship requires clear and convincing evidence.
    Falsification: If preponderance standard accepted for guardianship.
    """
    evaluator = GuardianshipEvaluator()
    
    result = evaluator.evaluate_guardianship_need(
        senior=Senior("S007", "Test", datetime.now() - timedelta(days=365*80)),
        medical_capacity_assessment="incapable",
        less_restrictive_options_exhausted=True,
    )
    
    assert result["clear_and_convincing_required"] is True, (
        "Guardianship must require clear and convincing evidence"
    )
    
    return True


def check_abuse_reporting_mandatory() -> bool:
    """
    Invariant: Certain professionals must report suspected elder abuse.
    Falsification: If physician with clear abuse indicators doesn't report.
    """
    detector = ElderAbuseDetector()
    
    # Physician must report
    physician_report = detector.check_mandatory_reporting("physician", True)
    assert physician_report["reporting_mandatory"] is True, (
        "Physician must report suspected abuse"
    )
    assert physician_report["timeframe"] == "immediately", (
        "Mandatory reporting must be immediate"
    )
    
    # Facility staff must report
    staff_report = detector.check_mandatory_reporting("facility_staff", True)
    assert staff_report["reporting_mandatory"] is True, (
        "Facility staff must report suspected abuse"
    )
    
    # Bystander not mandatory (but encouraged)
    bystander_report = detector.check_mandatory_reporting("bystander", True)
    assert bystander_report["reporting_mandatory"] is False, (
        "Bystander reporting is not mandatory"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("medicare_part_a_65", check_medicare_part_a_automatic_at_65),
        ("medicaid_asset_limit", check_medicaid_asset_limit),
        ("guardianship_incapacity", check_guardianship_requires_incapacity),
        ("clear_convincing_guardianship", check_clear_and_convincing_evidence_guardianship),
        ("abuse_reporting", check_abuse_reporting_mandatory),
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
