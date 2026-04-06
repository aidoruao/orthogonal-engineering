"""Tests for d_child_welfare domain."""

from datetime import datetime, timedelta
from fractions import Fraction

from src.domains.d_child_welfare.implementation import (
    MandatoryReportingSystem,
    FosterCarePlacementSystem,
    TPREvaluator,
    ChildWelfareCaseManager,
    Child,
    Parent,
    Placement,
    AbuseReport,
    AbuseType,
    ReporterType,
    PlacementType,
    TPRGround,
    check_mandatory_reporting_deadline,
    check_icwa_placement_preference,
    check_asfa_timeline,
)


def test_mandatory_reporting_compliance():
    """Test that reports within 48 hours are compliant."""
    system = MandatoryReportingSystem()
    
    report = AbuseReport(
        report_id="R001",
        child_id="C001",
        reporter_type=ReporterType.TEACHER,
        reporter_id="T001",
        report_date=datetime.now(),
        discovery_date=datetime.now() - timedelta(hours=12),
        abuse_types={AbuseType.PHYSICAL_ABUSE},
        description="Bruising observed",
    )
    
    result = system.check_reporting_compliance(report)
    assert result["compliant"] is True
    assert result["hours_elapsed"] == 12


def test_mandatory_reporting_non_compliance():
    """Test that reports after 48 hours are non-compliant."""
    system = MandatoryReportingSystem()
    
    report = AbuseReport(
        report_id="R002",
        child_id="C002",
        reporter_type=ReporterType.DOCTOR,
        reporter_id="D001",
        report_date=datetime.now(),
        discovery_date=datetime.now() - timedelta(hours=96),
        abuse_types={AbuseType.NEGLECT},
        description="Malnutrition",
    )
    
    result = system.check_reporting_compliance(report)
    assert result["compliant"] is False


def test_abuse_report_screening():
    """Test that physical abuse reports are screened in."""
    system = MandatoryReportingSystem()
    
    report = AbuseReport(
        report_id="R003",
        child_id="C003",
        reporter_type=ReporterType.DOCTOR,
        reporter_id="D002",
        report_date=datetime.now(),
        abuse_types={AbuseType.PHYSICAL_ABUSE, AbuseType.NEGLECT},
        description="Multiple injuries",
    )
    
    result = system.screen_report(report)
    assert result["screened_in"] is True
    assert result["requires_immediate_response"] is True


def test_icwa_applies_to_indian_child():
    """Test that ICWA requirements are identified for Indian children."""
    evaluator = TPREvaluator()
    
    child = Child(
        child_id="C004",
        name="Native Child",
        date_of_birth=datetime.now() - timedelta(days=365*2),
        tribal_affiliation="Cherokee Nation",
    )
    
    result = evaluator.check_icwa_requirements(child)
    assert result["applicable"] is True
    assert result["active_efforts_required"] is True
    assert result["expert_witness_required"] is True


def test_icwa_does_not_apply_to_non_indian():
    """Test that ICWA does not apply to non-Indian children."""
    evaluator = TPREvaluator()
    
    child = Child(
        child_id="C005",
        name="Non-Native Child",
        date_of_birth=datetime.now() - timedelta(days=365*2),
        tribal_affiliation=None,
    )
    
    result = evaluator.check_icwa_requirements(child)
    assert result["applicable"] is False


def test_permanency_timeline_overdue():
    """Test that 500 days in care triggers overdue status."""
    system = FosterCarePlacementSystem()
    
    placement = Placement(
        placement_id="PL001",
        placement_type=PlacementType.FOSTER_FAMILY,
        provider_id="F001",
        provider_name="Foster Family",
        start_date=datetime.now() - timedelta(days=500),
    )
    
    child = Child(
        child_id="C006",
        name="Long-term Child",
        date_of_birth=datetime.now() - timedelta(days=365*8),
        placement_history=[placement],
    )
    
    result = system.check_permanency_timeline(child)
    assert result["overdue"] is True
    assert result["requires_tpr_consideration"] is True


def test_tpr_evidence_standard():
    """Test that TPR requires clear and convincing evidence."""
    evaluator = TPREvaluator()
    
    child = Child(
        child_id="C007",
        name="Test Child",
        date_of_birth=datetime.now() - timedelta(days=365*3),
    )
    
    parent = Parent(
        parent_id="P001",
        name="Test Parent",
    )
    
    result = evaluator.evaluate_tpr_grounds(parent, child, [])
    assert result["burden"] == "clear_and_convincing"
    assert result["clear_and_convincing_evidence_required"] is True


def test_parent_case_plan_compliance():
    """Test calculation of parent case plan compliance rate."""
    parent = Parent(
        parent_id="P002",
        name="Compliant Parent",
        services_completed=["Parenting class"],
        services_required=["Parenting class", "Counseling"],
    )
    
    assert parent.case_plan_compliance_rate == Fraction(1, 2)


def test_child_age_calculation():
    """Test child age calculation."""
    child = Child(
        child_id="C008",
        name="Test Child",
        date_of_birth=datetime.now() - timedelta(days=365*10 + 100),  # ~10 years
    )
    
    assert child.age == 10


def test_convenience_function_reporting_deadline():
    """Test convenience function for reporting deadline."""
    discovery = datetime.now() - timedelta(hours=36)
    report = datetime.now()
    
    result = check_mandatory_reporting_deadline(discovery, report)
    assert result["compliant"] is True  # 36 hours is within 48
    assert 35 < result["hours_elapsed"] < 37  # Allow floating point variance


def test_convenience_function_asfa_timeline():
    """Test convenience function for ASFA timeline."""
    result = check_asfa_timeline(500)
    assert result["permanency_hearing_required"] is True
    assert result["tpr_filing_required"] is True
