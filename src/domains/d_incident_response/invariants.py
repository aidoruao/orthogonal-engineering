"""D_INCIDENT_RESPONSE invariants — Yeshua Standard. 0 floats.

Standards:
- NIST SP 800-61r2 — Computer Security Incident Handling Guide
- ISO/IEC 27035 — Information security incident management
- CISA Cybersecurity Incident Response Guidelines
- GDPR Article 33 — 72-hour breach notification
"""

from __future__ import annotations
from datetime import datetime
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import Incident, ResponseProcedure, IncidentSeverity, IncidentStatus


def check_incident_has_title(incident: Incident) -> Tuple[bool, ProofObject]:
    """Incident must have a non-empty title.

    Standard: NIST SP 800-61r2 §3.2.2 — incident documentation
    falsifies_if: incident.title is empty.
    """
    ok = bool(incident.title.strip())
    premises = [
        f"incident_id={incident.incident_id}",
        f"title_present={ok}",
    ]
    return ok, ProofObject(
        rule="IncidentHasTitle",
        premises=premises,
        conclusion="PASS: incident titled" if ok else "VIOLATION: incident title empty",
    )


def check_incident_id_nonempty(incident: Incident) -> Tuple[bool, ProofObject]:
    """Incident must have a non-empty identifier.

    Standard: NIST SP 800-61r2 — incident tracking
    falsifies_if: incident.incident_id is empty.
    """
    ok = bool(incident.incident_id.strip())
    premises = [f"incident_id={incident.incident_id!r}"]
    return ok, ProofObject(
        rule="IncidentIdNonEmpty",
        premises=premises,
        conclusion="PASS: incident_id set" if ok else "VIOLATION: incident_id empty",
    )


def check_severity_is_valid(incident: Incident) -> Tuple[bool, ProofObject]:
    """Incident severity must be a valid IncidentSeverity enum value.

    Standard: NIST SP 800-61r2 §3.2.6 — severity categorization
    falsifies_if: incident.severity is not a valid IncidentSeverity.
    """
    ok = isinstance(incident.severity, IncidentSeverity)
    premises = [
        f"incident_id={incident.incident_id}",
        f"severity={incident.severity!r}",
    ]
    return ok, ProofObject(
        rule="SeverityIsValid",
        premises=premises,
        conclusion=f"PASS: severity {incident.severity.name}" if ok else "VIOLATION: invalid severity",
    )


def check_procedure_has_name(procedure: ResponseProcedure) -> Tuple[bool, ProofObject]:
    """Response procedure must have a non-empty name.

    Standard: ISO/IEC 27035 §7.3 — procedure naming
    falsifies_if: procedure.name is empty.
    """
    ok = bool(procedure.name.strip())
    premises = [
        f"procedure_id={procedure.procedure_id}",
        f"name={procedure.name!r}",
    ]
    return ok, ProofObject(
        rule="ProcedureHasName",
        premises=premises,
        conclusion="PASS: procedure named" if ok else "VIOLATION: procedure name empty",
    )


def check_procedure_duration_nonneg(procedure: ResponseProcedure) -> Tuple[bool, ProofObject]:
    """Estimated duration must be >= 0 minutes.

    Standard: NIST IR timeline requirements
    falsifies_if: procedure.estimated_duration_minutes < 0.
    """
    ok = procedure.estimated_duration_minutes >= 0
    premises = [
        f"procedure_id={procedure.procedure_id}",
        f"estimated_duration_minutes={procedure.estimated_duration_minutes}",
    ]
    return ok, ProofObject(
        rule="ProcedureDurationNonNeg",
        premises=premises,
        conclusion=f"PASS: duration {procedure.estimated_duration_minutes}min" if ok else "VIOLATION: negative duration",
    )


def check_critical_incident_immediate(incident: Incident) -> Tuple[bool, ProofObject]:
    """CRITICAL severity incident must not be in OPEN status more than 1 hour (structural check).

    Standard: NIST SP 800-61r2 §3.3 — containment strategy
    falsifies_if: severity is CRITICAL and status is OPEN (structural — must be actioned).
    """
    if incident.severity == IncidentSeverity.CRITICAL:
        ok = incident.status != IncidentStatus.OPEN
    else:
        ok = True
    premises = [
        f"incident_id={incident.incident_id}",
        f"severity={incident.severity.name}",
        f"status={incident.status.name}",
    ]
    return ok, ProofObject(
        rule="CriticalIncidentImmediate",
        premises=premises,
        conclusion="PASS: critical incident properly actioned" if ok else "VIOLATION: CRITICAL incident still OPEN",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    incident = Incident(
        incident_id="INC-2024-001",
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.TRIAGING,
        detected_at=datetime(2024, 1, 1, 12, 0),
        title="Unauthorized access detected",
    )
    procedure = ResponseProcedure(
        procedure_id="PROC-001",
        name="Containment and Eradication",
        steps=["isolate", "eradicate", "recover"],
        estimated_duration_minutes=120,
    )
    results = {}
    for fn, args in [
        (check_incident_has_title, (incident,)),
        (check_incident_id_nonempty, (incident,)),
        (check_severity_is_valid, (incident,)),
        (check_procedure_has_name, (procedure,)),
        (check_procedure_duration_nonneg, (procedure,)),
        (check_critical_incident_immediate, (incident,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
