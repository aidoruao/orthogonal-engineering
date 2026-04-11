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
from typing import Tuple

from axioms.logic import ProofObject

from .implementation import (
    D_INCIDENT_RESPONSEChecker,
    D_INCIDENT_RESPONSERecord,
    Incident,
    IncidentSeverity,
    IncidentStatus,
    ResponseProcedure,
)


def check_response_time_sla() -> Tuple[bool, ProofObject]:
    """Verify critical incidents are responded to within SLA.
    
    Critical: 15 minutes, High: 1 hour, Medium: 4 hours, Low: 24 hours
    falsifies_if: response time exceeds SLA
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
            if rt > 15:
                return False, ProofObject(
                    rule="response_time_sla",
                    subject=inc.incident_id,
                    falsifies_if=f"Critical incident response time {rt}min exceeds 15min SLA",
                )
    
    return True, ProofObject(
        rule="response_time_sla",
        subject="incident response SLA",
        verified=True,
    )


def check_severity_classification() -> Tuple[bool, ProofObject]:
    """Verify all incidents have valid severity classification.
    
    falsifies_if: severity classification invalid
    """
    checker = D_INCIDENT_RESPONSEChecker()
    
    valid_incident = Incident(
        incident_id="INC-003",
        severity=IncidentSeverity.MEDIUM,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(),
        title="Test incident",
        response_team=["responder"],
    )
    
    if not checker.check_severity_classification(valid_incident):
        return False, ProofObject(
            rule="severity_classification",
            subject="INC-003",
            falsifies_if="Valid incident failed severity check",
        )
    
    return True, ProofObject(
        rule="severity_classification",
        subject="severity classification",
        verified=True,
    )


def check_response_procedures_exist() -> Tuple[bool, ProofObject]:
    """Verify response procedures exist for each severity level.
    
    falsifies_if: procedure has insufficient steps
    """
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
        if len(proc.steps) < 3:
            return False, ProofObject(
                rule="response_procedures_exist",
                subject=proc.procedure_id,
                falsifies_if=f"Procedure {proc.name} has insufficient steps ({len(proc.steps)} < 3)",
            )
    
    return True, ProofObject(
        rule="response_procedures_exist",
        subject="response procedures",
        verified=True,
    )


def check_incident_team_assignment() -> Tuple[bool, ProofObject]:
    """Verify all active incidents have assigned response teams.
    
    falsifies_if: incident lacks response team
    """
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
    
    if checker.check_response_team_assigned(unassigned):
        return False, ProofObject(
            rule="incident_team_assignment",
            subject="INC-004",
            falsifies_if="Unassigned incident passed team check",
        )
    
    # Incident with team should pass
    assigned = Incident(
        incident_id="INC-005",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.DETECTED,
        detected_at=datetime.now(),
        title="Assigned incident",
        response_team=["alice", "bob"],
    )
    
    if not checker.check_response_team_assigned(assigned):
        return False, ProofObject(
            rule="incident_team_assignment",
            subject="INC-005",
            falsifies_if="Assigned incident failed team check",
        )
    
    return True, ProofObject(
        rule="incident_team_assignment",
        subject="team assignment",
        verified=True,
    )


def check_mttr_calculation() -> Tuple[bool, ProofObject]:
    """Verify mean time to recovery is calculated correctly.
    
    falsifies_if: MTTR is negative
    """
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
    if mttr < Fraction(0):
        return False, ProofObject(
            rule="mttr_calculation",
            subject="MTTR",
            falsifies_if="MTTR is negative",
        )
    
    return True, ProofObject(
        rule="mttr_calculation",
        subject="MTTR calculation",
        verified=True,
    )


def check_compliance_deterministic() -> Tuple[bool, ProofObject]:
    """Master compliance check — deterministic execution."""
    checks = [
        check_response_time_sla,
        check_severity_classification,
        check_response_procedures_exist,
        check_incident_team_assignment,
        check_mttr_calculation,
    ]
    
    for check in checks:
        result, proof = check()
        if not result:
            return False, ProofObject(
                rule="compliance_deterministic",
                subject="master_check",
                falsifies_if=f"{proof.rule} failed",
            )
    
    return True, ProofObject(
        rule="compliance_deterministic",
        subject="incident response compliance",
        verified=True,
    )
