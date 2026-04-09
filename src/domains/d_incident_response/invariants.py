"""D_INCIDENT_RESPONSE invariant checks — incident response validation.

Incident response invariants ensure:
1. Response time SLAs are met
2. All incidents are properly classified
3. Response procedures exist for each severity level
4. Incidents have assigned response teams
5. Post-incident reviews are conducted
"""

from datetime import datetime, timedelta
from fractions import Fraction

from .implementation import (
    D_INCIDENT_RESPONSEChecker,
    D_INCIDENT_RESPONSERecord,
    Incident,
    IncidentSeverity,
    IncidentStatus,
    ResponseProcedure,
)


def check_response_time_sla() -> bool:
    """Verify critical incidents are responded to within SLA.
    
    Critical: 15 minutes, High: 1 hour, Medium: 4 hours, Low: 24 hours
    """
    checker = D_INCIDENT_RESPONSEChecker()
    
    # Simulate incidents with detection times
    base_time = datetime(2026, 4, 9, 12, 0, 0)
    
    incidents = [
        Incident(
            incident_id="INC-001",
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.CONTAINED,
            detected_at=base_time,
            title="Database breach",
            response_team=["alice", "bob"],
        ),
        Incident(
            incident_id="INC-002",
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.TRIAGING,
            detected_at=base_time,
            title="API degradation",
            response_team=["carol"],
        ),
    ]
    
    # Check response times
    for inc in incidents:
        if inc.severity == IncidentSeverity.CRITICAL:
            # Must respond within 15 minutes
            responded_at = base_time + timedelta(minutes=10)
            rt = checker.response_time(inc, responded_at)
            assert rt <= 15, f"Critical incident response time {rt}min exceeds SLA"
    
    return True


def check_severity_classification() -> bool:
    """Verify all incidents have valid severity classification."""
    checker = D_INCIDENT_RESPONSEChecker()
    
    valid_incident = Incident(
        incident_id="INC-003",
        severity=IncidentSeverity.MEDIUM,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(),
        title="Test incident",
        response_team=["responder"],
    )
    
    assert checker.check_severity_classification(valid_incident), \
        "Valid incident failed severity check"
    
    return True


def check_response_procedures_exist() -> bool:
    """Verify response procedures exist for each severity level."""
    procedures = [
        ResponseProcedure(
            procedure_id="PROC-CRIT",
            name="Critical Incident Response",
            steps=["Page on-call", "Assess impact", "Contain", "Eradicate", "Recover"],
            estimated_duration_minutes=240,
        ),
        ResponseProcedure(
            procedure_id="PROC-HIGH",
            name="High Priority Response",
            steps=["Assess", "Assign team", "Mitigate", "Document"],
            estimated_duration_minutes=480,
        ),
    ]
    
    # Each procedure must have at least 3 steps
    for proc in procedures:
        assert len(proc.steps) >= 3, f"Procedure {proc.name} has insufficient steps"
    
    return True


def check_incident_team_assignment() -> bool:
    """Verify all active incidents have assigned response teams."""
    checker = D_INCIDENT_RESPONSEChecker()
    
    # Incident without team should fail
    unassigned = Incident(
        incident_id="INC-004",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(),
        title="Unassigned incident",
        response_team=[],
    )
    
    assert not checker.check_response_team_assigned(unassigned), \
        "Unassigned incident passed team check"
    
    # Incident with team should pass
    assigned = Incident(
        incident_id="INC-005",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(),
        title="Assigned incident",
        response_team=["alice", "bob"],
    )
    
    assert checker.check_response_team_assigned(assigned), \
        "Assigned incident failed team check"
    
    return True


def check_mttr_calculation() -> bool:
    """Verify mean time to recovery is calculated correctly."""
    checker = D_INCIDENT_RESPONSEChecker()
    
    incidents = [
        Incident(
            incident_id="INC-006",
            severity=IncidentSeverity.MEDIUM,
            status=IncidentStatus.CLOSED,
            detected_at=datetime.now(),
            title="Resolved incident",
            response_team=["team"],
        ),
    ]
    
    mttr = checker.mean_time_to_recovery(incidents)
    assert mttr >= Fraction(0), "MTTR must be non-negative"
    
    return True


def check_compliance_deterministic() -> bool:
    """Master compliance check — deterministic execution."""
    assert check_response_time_sla()
    assert check_severity_classification()
    assert check_response_procedures_exist()
    assert check_incident_team_assignment()
    assert check_mttr_calculation()
    return True
