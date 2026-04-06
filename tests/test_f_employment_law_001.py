"""Falsification tests for D_EMPLOYMENT_LAW"""
from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_employment_law import (
    TitleVIIAnalyzer,
    ADAAccommodationAnalyzer,
    FMLAEligibilityChecker,
    WageHourCompliance,
    Employee,
    EmploymentAction,
    DiscriminationClaim,
    AccommodationRequest,
    ProtectedClass,
    FMLAQualifyingReason,
    EmploymentActionType,
    check_title_vii_prohibits_discrimination,
    check_ada_accommodation_required,
    check_fmla_eligibility,
)


def test_title_vii_discrimination():
    """Title VII prohibits discrimination based on protected classes."""
    analyzer = TitleVIIAnalyzer()
    
    employee = Employee(
        employee_id="E001",
        name="Protected Employee",
        hire_date=datetime(2020, 1, 1),
        protected_classes={ProtectedClass.RACE},
    )
    
    action = EmploymentAction(
        action_id="A001",
        employee=employee,
        action_type=EmploymentActionType.TERMINATION,
        action_date=datetime(2024, 6, 1),
        decision_reason="Performance",
    )
    
    claim = DiscriminationClaim(
        claim_id="C001",
        employee=employee,
        adverse_action=action,
        protected_class=ProtectedClass.RACE,
        comparator_treatment=[
            {"name": "Similar", "similarly_situated": True, "adverse_action": False},
        ],
    )
    
    result = analyzer.analyze_discrimination_claim(claim)
    assert result["prima_facie"] is True


def test_disparate_impact():
    """Disparate impact detected when selection rate < 80%."""
    analyzer = TitleVIIAnalyzer()
    
    result = analyzer.analyze_disparate_impact(
        selection_rate_protected=Fraction(40, 100),
        selection_rate_non_protected=Fraction(80, 100),
    )
    
    assert result["disparate_impact"] is True


def test_ada_accommodation():
    """ADA requires interactive process for accommodations."""
    analyzer = ADAAccommodationAnalyzer()
    
    employee = Employee(
        employee_id="E002",
        name="Disabled Employee",
        hire_date=datetime(2020, 1, 1),
        has_disability=True,
    )
    
    # Employer failed to engage
    request = AccommodationRequest(
        request_id="R001",
        employee=employee,
        accommodation_type="ADA",
        requested_accommodation="Flexible schedule",
        disability_or_religion="Back condition",
        employer_response=None,
    )
    
    result = analyzer.analyze_accommodation_request(request)
    assert result.get("violation") == "FAILURE_TO_ENGAGE"


def test_fmla_eligibility():
    """FMLA requires 12 months + 1250 hours."""
    checker = FMLAEligibilityChecker()
    
    # Eligible employee
    employee = Employee(
        employee_id="E003",
        name="Eligible",
        hire_date=datetime(2019, 1, 1),
        hours_worked_last_12_months=2000,
    )
    
    result = checker.check_eligibility(employee)
    assert result["eligible"] is True
    assert result["leave_remaining"] == 60  # 12 weeks


def test_fmla_leave_limit():
    """FMLA limits leave to 12 weeks (60 days)."""
    checker = FMLAEligibilityChecker()
    
    employee = Employee(
        employee_id="E004",
        name="Partial Leave",
        hire_date=datetime(2019, 1, 1),
        hours_worked_last_12_months=2000,
        fmla_leave_taken=50,  # 50 days used
    )
    
    result = checker.validate_leave_request(
        employee=employee,
        reason=FMLAQualifyingReason.BIRTH_OF_CHILD,
        requested_days=20,  # Would exceed 60
    )
    
    assert result["approved"] is False


def test_minimum_wage_compliance():
    """Minimum wage is $7.25 federal."""
    checker = WageHourCompliance()
    
    # Compliant wage
    result = checker.check_minimum_wage(Fraction(10))
    assert result["compliant"] is True
    
    # Non-compliant wage
    result2 = checker.check_minimum_wage(Fraction(6))
    assert result2["compliant"] is False


def test_overtime_calculation():
    """Overtime is 1.5x after 40 hours."""
    checker = WageHourCompliance()
    
    result = checker.calculate_overtime_pay(
        regular_rate=Fraction(10),
        hours_worked=50,
    )
    
    assert result["overtime_hours"] == 10
    assert result["overtime_pay"] > result["regular_pay"] * Fraction(1, 4)


def test_wage_theft_detection():
    """Unpaid hours detected as wage theft."""
    checker = WageHourCompliance()
    
    result = checker.detect_wage_theft(
        hours_worked=50,
        hours_paid=40,
        regular_rate=Fraction(15),
    )
    
    assert result["wage_theft_detected"] is True
    assert result["unpaid_hours"] == 10


def test_retaliation_timing():
    """Adverse action shortly after protected activity suggests retaliation."""
    employee = Employee(
        employee_id="E005",
        name="Whistleblower",
        hire_date=datetime(2020, 1, 1),
        complaints_filed=["Complaint 2024-05-01"],
    )
    
    action = EmploymentAction(
        action_id="A002",
        employee=employee,
        action_type=EmploymentActionType.TERMINATION,
        action_date=datetime(2024, 5, 15),
        protected_activity_date=datetime(2024, 5, 1),
    )
    
    assert action.days_since_protected_activity == 14
    assert action.days_since_protected_activity <= 90


if __name__ == "__main__":
    test_title_vii_discrimination()
    test_disparate_impact()
    test_ada_accommodation()
    test_fmla_eligibility()
    test_fmla_leave_limit()
    test_minimum_wage_compliance()
    test_overtime_calculation()
    test_wage_theft_detection()
    test_retaliation_timing()
    print("All D_EMPLOYMENT_LAW tests: PASS")
