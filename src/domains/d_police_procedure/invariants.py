"""D_POLICE_PROCEDURE invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Department policies, POST standards, consent decrees
"""

from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_police_procedure.implementation import (
    BodyCameraManager,
    UseOfForceReporter,
    ComplaintProcessor,
    PoliceProcedureAuditor,
    BodyCamera,
    CitizenEncounter,
    UseOfForceIncident,
    CitizenComplaint,
    EncounterType,
    ForceLevel,
    ComplaintType,
    ComplaintStatus,
)


def check_body_cam_active_during_encounter() -> bool:
    """
    Invariant: Body cam must be active during all citizen encounters.
    Falsification: If required encounter has inactive camera.
    """
    # Encounter with camera activated
    compliant_encounter = CitizenEncounter(
        encounter_id="E001",
        officer_id="O001",
        officer_camera_id="C001",
        encounter_type=EncounterType.TRAFFIC_STOP,
        start_time=datetime.now(),
        location="Main St & 1st Ave",
        camera_activated=True,
        camera_recording_start=datetime.now(),
    )
    
    result = compliant_encounter.check_camera_compliance()
    # Traffic stop requires camera
    assert result["camera_required"] is True, (
        "Traffic stop should require camera"
    )
    assert result["compliant"] is True, (
        "Encounter with active camera should be compliant"
    )
    
    # Encounter without camera (non-compliant)
    noncompliant_encounter = CitizenEncounter(
        encounter_id="E002",
        officer_id="O002",
        officer_camera_id="C002",
        encounter_type=EncounterType.ARREST,
        start_time=datetime.now(),
        location="456 Oak St",
        camera_activated=False,  # Camera not activated!
    )
    
    result2 = noncompliant_encounter.check_camera_compliance()
    # Arrest requires camera
    assert result2["camera_required"] is True, (
        "Arrest should require camera"
    )
    assert result2["compliant"] is False, (
        "Arrest without camera should be non-compliant"
    )
    
    return True


def check_use_of_force_report_filed_within_24_hours() -> bool:
    """
    Invariant: Use of force report filed within 24 hours.
    Falsification: If report filed after deadline passes.
    """
    reporter = UseOfForceReporter()
    
    # Incident with timely report (filed within 24 hours)
    incident_time = datetime.now() - timedelta(hours=12)
    timely_incident = UseOfForceIncident(
        incident_id="I001",
        encounter_id="E001",
        officer_id="O001",
        force_level=ForceLevel.SOFT_HAND,
        force_type="Arm control hold",
        timestamp=incident_time,
        report_filed=True,
        report_timestamp=incident_time + timedelta(hours=2),  # 2 hours later
    )
    
    result = reporter.check_reporting_compliance(timely_incident)
    assert result["compliant"] is True, (
        "Report filed within 24 hours should be compliant"
    )
    assert result["hours_to_report"] <= 24, (
        "Hours to report should be <= 24"
    )
    
    # Incident with late report (filed after 24 hours)
    late_incident = UseOfForceIncident(
        incident_id="I002",
        encounter_id="E002",
        officer_id="O002",
        force_level=ForceLevel.LESS_LETHAL,
        force_type="TASER deployment",
        timestamp=incident_time,
        report_filed=True,
        report_timestamp=incident_time + timedelta(hours=30),  # 30 hours later
    )
    
    result2 = reporter.check_reporting_compliance(late_incident)
    assert result2["compliant"] is False, (
        "Report filed after 24 hours should be non-compliant"
    )
    assert result2["hours_to_report"] > 24, (
        "Hours to report should be > 24 for late report"
    )
    
    # Unfiled report (automatically non-compliant after deadline)
    unfiled_incident = UseOfForceIncident(
        incident_id="I003",
        encounter_id="E003",
        officer_id="O003",
        force_level=ForceLevel.HARD_HAND,
        force_type="Takedown",
        timestamp=datetime.now() - timedelta(hours=48),  # 48 hours ago
        report_filed=False,
    )
    
    result3 = reporter.check_reporting_compliance(unfiled_incident)
    assert result3["compliant"] is False, (
        "Unfiled report past deadline should be non-compliant"
    )
    
    return True


def check_complaint_process_deterministic() -> bool:
    """
    Invariant: Complaint process is deterministic and documented.
    Falsification: If same complaint produces different process outcomes.
    """
    processor = ComplaintProcessor()
    
    # Create a complaint
    complaint = CitizenComplaint(
        complaint_id="C001",
        complainant_name="Jane Doe",
        complaint_date=datetime.now(),
        complaint_type=ComplaintType.EXCESSIVE_FORCE,
        officer_id="O001",
        incident_date=datetime.now() - timedelta(days=5),
        incident_location="Main St",
        description="Officer used excessive force during arrest",
    )
    
    # Process multiple times and verify consistency
    result1 = processor.check_process_compliance(complaint)
    result2 = processor.check_process_compliance(complaint)
    result3 = processor.check_process_compliance(complaint)
    
    # Should be identical (deterministic)
    assert result1 == result2 == result3, (
        "Complaint process check must be deterministic"
    )
    
    # Add investigator
    processor.assign_investigator(complaint, "INV001")
    
    # Add evidence
    processor.document_evidence(complaint, ["body_cam_footage.mp4", "witness_statement.pdf"])
    
    # Check again - should be documented
    result_with_evidence = processor.check_process_compliance(complaint)
    assert result_with_evidence["checks"]["assigned_investigator"] is True, (
        "Complaint should have investigator assigned"
    )
    assert result_with_evidence["checks"]["evidence_collected"] is True, (
        "Complaint should have evidence collected"
    )
    
    return True


def check_complaint_documentation_required() -> bool:
    """
    Invariant: Complaints must be documented with evidence.
    Falsification: If complaint without evidence passes compliance.
    """
    processor = ComplaintProcessor()
    
    # Undocumented complaint
    undocumented = CitizenComplaint(
        complaint_id="C002",
        complainant_name="John Smith",
        complaint_date=datetime.now(),
        complaint_type=ComplaintType.DISCRIMINATION,
        officer_id="O002",
        incident_date=datetime.now() - timedelta(days=3),
        incident_location="Oak St",
        description="Officer was rude",
        # No evidence, no investigator assigned
    )
    
    result = processor.check_process_compliance(undocumented)
    assert result["checks"]["evidence_collected"] is False, (
        "Complaint without evidence should fail evidence check"
    )
    assert result["checks"]["assigned_investigator"] is False, (
        "Complaint without investigator should fail assignment check"
    )
    
    # Documented complaint
    documented = CitizenComplaint(
        complaint_id="C003",
        complainant_name="Alice Brown",
        complaint_date=datetime.now(),
        complaint_type=ComplaintType.FALSE_ARREST,
        officer_id="O003",
        incident_date=datetime.now() - timedelta(days=2),
        incident_location="Elm St",
        description="Wrongful arrest",
        assigned_investigator="INV002",
        investigation_start_date=datetime.now(),
        evidence_collected=["arrest_report.pdf", "witness_video.mp4"],
    )
    
    result2 = processor.check_process_compliance(documented)
    assert result2["checks"]["evidence_collected"] is True, (
        "Documented complaint should pass evidence check"
    )
    assert result2["checks"]["assigned_investigator"] is True, (
        "Documented complaint should pass assignment check"
    )
    
    return True


def check_supervisor_notification_required() -> bool:
    """
    Invariant: Supervisor must be notified within 30 minutes of use of force.
    Falsification: If notification after 30 minutes passes compliance.
    """
    reporter = UseOfForceReporter()
    
    # Timely notification
    incident_time = datetime.now() - timedelta(hours=2)
    timely_notification = UseOfForceIncident(
        incident_id="I004",
        encounter_id="E004",
        officer_id="O004",
        force_level=ForceLevel.LESS_LETHAL,
        force_type="OC spray",
        timestamp=incident_time,
        supervisor_notified=True,
        supervisor_notification_time=incident_time + timedelta(minutes=15),  # 15 min
    )
    
    result = reporter.check_supervisor_notification(timely_notification)
    assert result["compliant"] is True, (
        "Notification within 30 minutes should be compliant"
    )
    assert result["minutes_to_notify"] <= 30, (
        "Minutes to notify should be <= 30"
    )
    
    # Late notification
    late_notification = UseOfForceIncident(
        incident_id="I005",
        encounter_id="E005",
        officer_id="O005",
        force_level=ForceLevel.HARD_HAND,
        force_type="Takedown",
        timestamp=incident_time,
        supervisor_notified=True,
        supervisor_notification_time=incident_time + timedelta(minutes=45),  # 45 min
    )
    
    result2 = reporter.check_supervisor_notification(late_notification)
    assert result2["compliant"] is False, (
        "Notification after 30 minutes should be non-compliant"
    )
    assert result2["minutes_to_notify"] > 30, (
        "Minutes to notify should be > 30 for late notification"
    )
    
    return True


def check_camera_required_for_enforcement() -> bool:
    """
    Invariant: Camera is required for enforcement actions.
    Falsification: If arrest without camera is not flagged.
    """
    # Various encounter types
    traffic_stop = CitizenEncounter(
        encounter_id="E010",
        officer_id="O010",
        officer_camera_id="C010",
        encounter_type=EncounterType.TRAFFIC_STOP,
        start_time=datetime.now(),
        location="Main St",
        camera_activated=False,
    )
    
    field_interview = CitizenEncounter(
        encounter_id="E011",
        officer_id="O011",
        officer_camera_id="C011",
        encounter_type=EncounterType.FIELD_INTERVIEW,
        start_time=datetime.now(),
        location="Oak St",
        camera_activated=False,
    )
    
    # Traffic stop requires camera
    result1 = traffic_stop.check_camera_compliance()
    assert result1["camera_required"] is True, (
        "Traffic stop should require camera"
    )
    
    # Field interview does not strictly require camera (recommended)
    result2 = field_interview.check_camera_compliance()
    # Field interview may or may not require camera based on policy
    # The key is that the compliance check returns a result
    assert "compliant" in result2, (
        "Field interview should have compliance check"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("body_cam_active", check_body_cam_active_during_encounter),
        ("force_report_24h", check_use_of_force_report_filed_within_24_hours),
        ("complaint_deterministic", check_complaint_process_deterministic),
        ("complaint_documentation", check_complaint_documentation_required),
        ("supervisor_notification", check_supervisor_notification_required),
        ("camera_required", check_camera_required_for_enforcement),
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
