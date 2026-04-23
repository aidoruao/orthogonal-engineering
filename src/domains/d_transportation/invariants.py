"""D_TRANSPORTATION invariants — Yeshua Standard. 0 floats.

Standards:
- 49 U.S.C. 40101 — Aviation safety (FAA)
- 49 U.S.C. 20101 — Rail safety (FRA)
- 49 U.S.C. 30101 — Motor vehicle safety (NHTSA)
- FMCSA Hours of Service (49 CFR Part 395) — driver fatigue prevention
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import TransportationRecord, TransportationStatus


def check_safety_incident_rate(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Safety incident rate must remain below regulatory threshold.

    Standard: DOT safety management systems — incident rate benchmarking
    Falsifies if: safety_incident_rate > Fraction(1, 100).
    falsifies_if: safety_incident_rate > Fraction(1, 100).
    """
    threshold = Fraction(1, 100)
    ok = record.safety_incident_rate <= threshold
    premises = [
        f"record_id={record.record_id}",
        f"safety_incident_rate={record.safety_incident_rate}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="SafetyIncidentRate",
        premises=premises,
        conclusion=f"PASS: incident rate {record.safety_incident_rate} <= {threshold}" if ok else f"VIOLATION: incident rate {record.safety_incident_rate} > {threshold}",
    )


def check_on_time_performance(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """On-time performance must meet service reliability floor.

    Standard: DOT on-time performance requirements (14 CFR 234 for aviation)
    Falsifies if: on_time_performance < Fraction(9, 10).
    falsifies_if: on_time_performance < Fraction(9, 10).
    """
    threshold = Fraction(9, 10)
    ok = record.on_time_performance >= threshold
    premises = [
        f"record_id={record.record_id}",
        f"on_time_performance={record.on_time_performance}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="OnTimePerformance",
        premises=premises,
        conclusion=f"PASS: on-time {record.on_time_performance} >= {threshold}" if ok else f"VIOLATION: on-time {record.on_time_performance} < {threshold}",
    )


def check_driver_rest_compliance(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Driver rest compliance must satisfy hours-of-service requirements.

    Standard: FMCSA Hours of Service (49 CFR Part 395)
    Falsifies if: driver_rest_compliance < Fraction(7, 8).
    falsifies_if: driver_rest_compliance < Fraction(7, 8).
    """
    threshold = Fraction(7, 8)
    ok = record.driver_rest_compliance >= threshold
    premises = [
        f"record_id={record.record_id}",
        f"driver_rest_compliance={record.driver_rest_compliance}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="DriverRestCompliance",
        premises=premises,
        conclusion=f"PASS: rest compliance {record.driver_rest_compliance} >= {threshold}" if ok else f"VIOLATION: rest compliance {record.driver_rest_compliance} < {threshold}",
    )


def check_maintenance_score(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Vehicle maintenance score must meet safety inspection floor.

    Standard: FMCSA vehicle maintenance requirements (49 CFR 396)
    Falsifies if: maintenance_score < Fraction(3, 4).
    falsifies_if: maintenance_score < Fraction(3, 4).
    """
    threshold = Fraction(3, 4)
    ok = record.maintenance_score >= threshold
    premises = [
        f"record_id={record.record_id}",
        f"maintenance_score={record.maintenance_score}",
        f"threshold={threshold}",
    ]
    return ok, ProofObject(
        rule="MaintenanceScore",
        premises=premises,
        conclusion=f"PASS: maintenance {record.maintenance_score} >= {threshold}" if ok else f"VIOLATION: maintenance {record.maintenance_score} < {threshold}",
    )


def check_fleet_size_adequate(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Fleet size must be adequate for operational requirements.

    Standard: DOT operational capacity assessment
    Falsifies if: fleet_size < 10.
    falsifies_if: fleet_size < 10.
    """
    ok = record.fleet_size >= 10
    premises = [
        f"record_id={record.record_id}",
        f"fleet_size={record.fleet_size}",
    ]
    return ok, ProofObject(
        rule="FleetSizeAdequate",
        premises=premises,
        conclusion=f"PASS: fleet size {record.fleet_size} >= 10" if ok else f"VIOLATION: fleet size {record.fleet_size} < 10",
    )


def check_record_status_valid(record: TransportationRecord) -> Tuple[bool, ProofObject]:
    """Record status must be a valid TransportationStatus.

    Standard: DOT audit trail requirements
    Falsifies if: status is not a TransportationStatus instance.
    falsifies_if: status is not a TransportationStatus instance.
    """
    ok = isinstance(record.status, TransportationStatus)
    premises = [
        f"record_id={record.record_id}",
        f"status={record.status}",
    ]
    return ok, ProofObject(
        rule="RecordStatusValid",
        premises=premises,
        conclusion=f"PASS: status {record.status.name} valid" if ok else "VIOLATION: invalid status",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    record = TransportationRecord(
        record_id="TRANS-2024-001",
        status=TransportationStatus.COMPLIANT,
        fleet_size=100,
        safety_incident_rate=Fraction(1, 10000),
        on_time_performance=Fraction(95, 100),
        driver_rest_compliance=Fraction(1, 1),
        maintenance_score=Fraction(1, 1),
    )
    results = {}
    for fn, args in [
        (check_safety_incident_rate, (record,)),
        (check_on_time_performance, (record,)),
        (check_driver_rest_compliance, (record,)),
        (check_maintenance_score, (record,)),
        (check_fleet_size_adequate, (record,)),
        (check_record_status_valid, (record,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
