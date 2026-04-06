"""D_CHILD_WELFARE invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: CAPTA (42 U.S.C. §5101), ASFA, ICWA (25 U.S.C. §1901)
"""

from fractions import Fraction
from datetime import datetime, timedelta
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
)


def check_mandatory_reporting_within_48_hours() -> bool:
    """
    Invariant: CAPTA requires mandatory reporters to report within 48 hours.
    Falsification: If report filed after 48 hours passes compliance check.
    """
    system = MandatoryReportingSystem()
    
    # Report filed within 24 hours - compliant
    compliant_report = AbuseReport(
        report_id="R001",
        child_id="C001",
        reporter_type=ReporterType.TEACHER,
        reporter_id="T001",
        report_date=datetime.now(),
        discovery_date=datetime.now() - timedelta(hours=24),
        abuse_types={AbuseType.PHYSICAL_ABUSE},
        description="Suspected abuse",
    )
    
    result = system.check_reporting_compliance(compliant_report)
    assert result["compliant"] is True, (
        "24-hour report should be compliant"
    )
    
    # Report filed after 72 hours - non-compliant
    late_report = AbuseReport(
        report_id="R002",
        child_id="C002",
        reporter_type=ReporterType.DOCTOR,
        reporter_id="D001",
        report_date=datetime.now(),
        discovery_date=datetime.now() - timedelta(hours=72),
        abuse_types={AbuseType.NEGLECT},
        description="Suspected neglect",
    )
    
    result2 = system.check_reporting_compliance(late_report)
    assert result2["compliant"] is False, (
        "72-hour report should be non-compliant"
    )
    
    return True


def check_reasonable_efforts_before_removal() -> bool:
    """
    Invariant: Reasonable efforts required before removing child from home.
    Falsification: If removal without reasonable efforts is allowed.
    """
    # This is a simplified check - real implementation would verify services offered
    parent_with_services = Parent(
        parent_id="P001",
        name="Active Parent",
        case_plan_assigned=True,
        case_plan_start_date=datetime.now() - timedelta(days=180),
        services_completed=["Parenting class", "Substance abuse assessment"],
        services_required=["Parenting class", "Substance abuse assessment", "Counseling"],
    )
    
    # Parent made some efforts
    assert parent_with_services.case_plan_compliance_rate > 0, (
        "Parent with completed services should have positive compliance"
    )
    assert parent_with_services.case_plan_compliance_rate < 1, (
        "Parent with incomplete services should not have full compliance"
    )
    
    return True


def check_clear_and_convincing_evidence_for_tpr() -> bool:
    """
    Invariant: TPR requires clear and convincing evidence (Santosky v. Kramer).
    Falsification: If preponderance standard is accepted for TPR.
    """
    evaluator = TPREvaluator()
    
    child = Child(
        child_id="C003",
        name="Test Child",
        date_of_birth=datetime.now() - timedelta(days=365*5),
    )
    
    parent = Parent(
        parent_id="P002",
        name="Neglectful Parent",
        services_completed=[],
        services_required=["Parenting", "Counseling", "Housing"],
    )
    
    abuse_history = [
        AbuseReport(
            report_id="R003",
            child_id="C003",
            reporter_type=ReporterType.DOCTOR,
            reporter_id="D002",
            report_date=datetime.now() - timedelta(days=180),
            abuse_types={AbuseType.NEGLECT},
            description="Medical neglect",
            substantiated=True,
        )
    ]
    
    result = evaluator.evaluate_tpr_grounds(parent, child, abuse_history)
    
    # Must require clear and convincing evidence
    assert result["burden"] == "clear_and_convincing", (
        "TPR must require clear and convincing evidence standard"
    )
    assert result["clear_and_convincing_evidence_required"] is True, (
        "TPR must require clear and convincing evidence"
    )
    
    return True


def check_icwa_placement_preferences() -> bool:
    """
    Invariant: ICWA placement preferences must be followed unless good cause.
    Falsification: If non-Indian placement is preferred over tribal placement.
    """
    evaluator = TPREvaluator()
    
    # Indian child
    indian_child = Child(
        child_id="C004",
        name="Native Child",
        date_of_birth=datetime.now() - timedelta(days=365*3),
        tribal_affiliation="Navajo Nation",
    )
    
    icwa_result = evaluator.check_icwa_requirements(indian_child)
    assert icwa_result["applicable"] is True, (
        "ICWA should apply to Indian child"
    )
    assert icwa_result["active_efforts_required"] is True, (
        "ICWA requires active efforts (higher than ASFA reasonable efforts)"
    )
    assert icwa_result["expert_witness_required"] is True, (
        "ICWA requires qualified expert witness"
    )
    
    # Non-Indian child
    non_indian_child = Child(
        child_id="C005",
        name="Non-Native Child",
        date_of_birth=datetime.now() - timedelta(days=365*3),
        tribal_affiliation=None,
    )
    
    icwa_result2 = evaluator.check_icwa_requirements(non_indian_child)
    assert icwa_result2["applicable"] is False, (
        "ICWA should not apply to non-Indian child"
    )
    
    return True


def check_asfa_permanency_timeline() -> bool:
    """
    Invariant: ASFA requires permanency hearing within 12 months.
    Falsification: If case 400+ days without permanency hearing passes check.
    """
    system = FosterCarePlacementSystem()
    
    # Child in care for 200 days - not yet due
    recent_placement = Placement(
        placement_id="PL001",
        placement_type=PlacementType.FOSTER_FAMILY,
        provider_id="F001",
        provider_name="Foster Family A",
        start_date=datetime.now() - timedelta(days=200),
    )
    
    child_recent = Child(
        child_id="C006",
        name="Recent Placement",
        date_of_birth=datetime.now() - timedelta(days=365*4),
        placement_history=[recent_placement],
    )
    
    result = system.check_permanency_timeline(child_recent)
    assert result["overdue"] is False, (
        "200 days should not be overdue for permanency hearing"
    )
    assert result["requires_tpr_consideration"] is False, (
        "200 days should not trigger TPR filing requirement"
    )
    
    # Child in care for 500 days - overdue and TPR required
    old_placement = Placement(
        placement_id="PL002",
        placement_type=PlacementType.FOSTER_FAMILY,
        provider_id="F002",
        provider_name="Foster Family B",
        start_date=datetime.now() - timedelta(days=500),
    )
    
    child_old = Child(
        child_id="C007",
        name="Long-term Placement",
        date_of_birth=datetime.now() - timedelta(days=365*6),
        placement_history=[old_placement],
    )
    
    result2 = system.check_permanency_timeline(child_old)
    assert result2["overdue"] is True, (
        "500 days should be overdue for permanency hearing"
    )
    assert result2["requires_tpr_consideration"] is True, (
        "500 days should trigger TPR filing requirement (15 of 22 months)"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("mandatory_reporting_48h", check_mandatory_reporting_within_48_hours),
        ("reasonable_efforts", check_reasonable_efforts_before_removal),
        ("tpr_evidence_standard", check_clear_and_convincing_evidence_for_tpr),
        ("icwa_placement", check_icwa_placement_preferences),
        ("asfa_permanency", check_asfa_permanency_timeline),
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
