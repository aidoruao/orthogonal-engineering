"""Tests for d_elder_law domain."""

from datetime import datetime, timedelta
from fractions import Fraction

from src.domains.d_elder_law.implementation import (
    MedicareEligibilityChecker,
    MedicaidEligibilityCalculator,
    ElderAbuseDetector,
    GuardianshipEvaluator,
    ElderLawCaseManager,
    Senior,
    LongTermCareFacility,
    Guardianship,
    GuardianType,
    MedicarePart,
    MedicaidCategory,
    AbuseType,
    check_medicare_part_a_eligibility,
    check_medicaid_asset_limit,
    check_guardianship_incapacity_standard,
)


def test_medicare_eligibility_age_70():
    """Test Medicare eligibility at age 70."""
    checker = MedicareEligibilityChecker()
    
    senior = Senior(
        senior_id="S001",
        name="Test Senior",
        date_of_birth=datetime.now() - timedelta(days=365*70),
    )
    
    result = checker.check_medicare_eligibility(senior)
    assert result["part_a_eligible"] is True
    assert result["automatic_enrollment"] is True


def test_medicare_eligibility_age_60():
    """Test Medicare ineligibility at age 60."""
    checker = MedicareEligibilityChecker()
    
    senior = Senior(
        senior_id="S002",
        name="Younger Senior",
        date_of_birth=datetime.now() - timedelta(days=365*60),
    )
    
    result = checker.check_medicare_eligibility(senior)
    assert result["part_a_eligible"] is False


def test_medicaid_asset_eligibility():
    """Test Medicaid asset eligibility."""
    calculator = MedicaidEligibilityCalculator()
    
    low_asset = Senior(
        senior_id="S003",
        name="Low Asset",
        date_of_birth=datetime.now() - timedelta(days=365*75),
        monthly_income=Fraction(1000),
        countable_assets=Fraction(1500),
    )
    
    result = calculator.check_medicaid_eligibility(low_asset)
    assert result["asset_eligible"] is True


def test_medicaid_asset_ineligibility():
    """Test Medicaid asset ineligibility."""
    calculator = MedicaidEligibilityCalculator()
    
    high_asset = Senior(
        senior_id="S004",
        name="High Asset",
        date_of_birth=datetime.now() - timedelta(days=365*75),
        monthly_income=Fraction(1000),
        countable_assets=Fraction(50000),
    )
    
    result = calculator.check_medicaid_eligibility(high_asset)
    assert result["asset_eligible"] is False


def test_guardianship_not_appropriate():
    """Test guardianship not appropriate for capable senior."""
    evaluator = GuardianshipEvaluator()
    
    senior = Senior("S005", "Capable", datetime.now() - timedelta(days=365*80))
    
    result = evaluator.evaluate_guardianship_need(
        senior, "capable", True
    )
    assert result["guardianship_appropriate"] is False


def test_guardianship_appropriate():
    """Test guardianship appropriate for incapable senior."""
    evaluator = GuardianshipEvaluator()
    
    senior = Senior("S006", "Incapable", datetime.now() - timedelta(days=365*80))
    
    result = evaluator.evaluate_guardianship_need(
        senior, "incapable", True
    )
    assert result["incapacity_found"] is True
    assert result["guardianship_appropriate"] is True


def test_mandatory_abuse_reporting():
    """Test mandatory abuse reporting for professionals."""
    detector = ElderAbuseDetector()
    
    result = detector.check_mandatory_reporting("physician", True)
    assert result["reporting_mandatory"] is True
    
    result2 = detector.check_mandatory_reporting("bystander", True)
    assert result2["reporting_mandatory"] is False


def test_guardianship_compliance():
    """Test guardianship reporting compliance."""
    evaluator = GuardianshipEvaluator()
    
    guardianship = Guardianship(
        case_id="G001",
        ward_id="S007",
        guardian_id="G001",
        guardian_type=GuardianType.PLENARY,
        petition_filed=datetime.now() - timedelta(days=365),
        hearing_date=datetime.now() - timedelta(days=300),
        incapacity_finding=True,
        last_report_date=datetime.now() - timedelta(days=400),  # Overdue
    )
    
    result = evaluator.check_guardianship_compliance(guardianship)
    assert result["compliant"] is False  # Report is overdue
    assert result["report_due"] is True


def test_part_b_premium_calculation():
    """Test Part B premium calculation with IRMAA."""
    checker = MedicareEligibilityChecker()
    
    # Low income - no IRMAA
    result_low = checker.calculate_part_b_premium(Fraction(50000))
    assert result_low["irmaa_applies"] is False
    assert result_low["total_premium"] == result_low["base_premium"]
    
    # High income - IRMAA applies
    result_high = checker.calculate_part_b_premium(Fraction(150000))
    assert result_high["irmaa_applies"] is True
    assert result_high["total_premium"] > result_high["base_premium"]


def test_medicaid_spend_down():
    """Test Medicaid spend-down calculation."""
    calculator = MedicaidEligibilityCalculator()
    
    result = calculator.calculate_medicaid_spend_down(
        monthly_income=Fraction(2000),
        medical_expenses=Fraction(1500),
        income_limit=Fraction(1215),
    )
    assert result["countable_income"] == Fraction(500)
    assert result["spend_down_met"] is True


def test_abuse_indicators():
    """Test abuse indicator detection."""
    detector = ElderAbuseDetector()
    
    senior = Senior(
        senior_id="S008",
        name="At Risk",
        date_of_birth=datetime.now() - timedelta(days=365*80),
        monthly_income=Fraction(3000),
        countable_assets=Fraction(200),  # Low assets despite income
    )
    
    result = detector.check_abuse_indicators(senior)
    assert "Income_assets_mismatch" in result["indicators"]


def test_convenience_function_medicare():
    """Test convenience function for Medicare eligibility."""
    result = check_medicare_part_a_eligibility(70)
    assert result["eligible"] is True
    
    result2 = check_medicare_part_a_eligibility(60)
    assert result2["eligible"] is False


def test_convenience_function_medicaid():
    """Test convenience function for Medicaid asset limit."""
    result = check_medicaid_asset_limit(1500)
    assert result["eligible"] is True
    
    result2 = check_medicaid_asset_limit(5000)
    assert result2["eligible"] is False


def test_convenience_function_guardianship():
    """Test convenience function for guardianship standard."""
    result = check_guardianship_incapacity_standard(True)
    assert result["standard_met"] is True
    
    result2 = check_guardianship_incapacity_standard(False)
    assert result2["standard_met"] is False
