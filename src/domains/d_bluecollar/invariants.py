#!/usr/bin/env python3
"""D_BLUECOLLAR Invariants — OSHA safety, field service, manufacturing QC

Blue-collar trades per OSHA 1910/1926, field service audit trails, and Six Sigma QC.
All invariants use Fraction arithmetic for exact time and quality measurements.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    SafetyAlert, FieldServiceRecord, ManufacturingQC, OSHAIncident,
    HazardLevel, OperationalMode,
    safety_alert_critical_max_seconds, safety_alert_high_max_seconds,
    osha_incident_reporting_hours, manufacturing_defect_rate_max
)


def check_safety_alert_response_time(alert: SafetyAlert) -> Tuple[bool, ProofObject]:
    """
    Worker safety alerts must be delivered within required response time by hazard level.

    Falsifies if: CRITICAL AND response_time > 30s, or HIGH AND response_time > 120s
    
    
    if alert.hazard_level == HazardLevel.CRITICAL:
        max_seconds = safety_alert_critical_max_seconds()
        if alert.response_time_seconds > max_seconds:
            return False, ProofObject(
                conclusion=f"VIOLATION: CRITICAL safety alert {alert.alert_id} delivered in {alert.response_time_seconds}s (max {max_seconds}s)",
                premises=[
                    f"Hazard level: CRITICAL",
                    f"Response time: {alert.response_time_seconds} seconds",
                    f"Max: {max_seconds} seconds"
                ],
                rule="osha_safety_alert_critical"
            )

    if alert.hazard_level == HazardLevel.HIGH:
        max_seconds = safety_alert_high_max_seconds()
        if alert.response_time_seconds > max_seconds:
            return False, ProofObject(
                conclusion=f"VIOLATION: HIGH safety alert {alert.alert_id} delivered in {alert.response_time_seconds}s (max {max_seconds}s)",
                premises=[
                    f"Hazard level: HIGH",
                    f"Response time: {alert.response_time_seconds} seconds",
                    f"Max: {max_seconds} seconds"
                ],
                rule="osha_safety_alert_high"
            )

    return True, ProofObject(
        conclusion=f"Safety alert {alert.alert_id} delivered within required timeframe",
        premises=[
            f"Hazard level: {alert.hazard_level.name}",
            f"Response time: {alert.response_time_seconds} seconds"
        ],
        rule="osha_safety_alert_response"
    )


def check_field_service_tamper_evident(record: FieldServiceRecord) -> Tuple[bool, ProofObject]:
    """
    Field service records must be immutably logged with tamper-evident hashing.

    Falsifies if: tamper_evident_hash is empty or None
    
    
    if not record.tamper_evident_hash:
        return False, ProofObject(
            conclusion=f"VIOLATION: Field service record {record.record_id} lacks tamper-evident hash",
            premises=[
                f"Tamper-evident hash: {record.tamper_evident_hash or 'MISSING'}"
            ],
            rule="field_service_tamper_evident"
        )

    return True, ProofObject(
        conclusion=f"Field service record {record.record_id} is tamper-evident",
        premises=[f"Hash: {record.tamper_evident_hash[:16]}..."],
        rule="field_service_tamper_evident"
    )


def check_offline_capability(record: FieldServiceRecord) -> Tuple[bool, ProofObject]:
    """
    Critical field service functions must work offline (network-independent).

    Falsifies if: NOT offline_capable
    
    
    if not record.offline_capable:
        return False, ProofObject(
            conclusion=f"VIOLATION: Field service record {record.record_id} not offline-capable",
            premises=[
                f"Offline capable: {record.offline_capable}",
                "Critical field operations require offline mode"
            ],
            rule="offline_capability_requirement"
        )

    return True, ProofObject(
        conclusion=f"Field service record {record.record_id} is offline-capable",
        premises=[f"Offline capable: {record.offline_capable}"],
        rule="offline_capability_requirement"
    )


def check_manufacturing_defect_rate(qc: ManufacturingQC) -> Tuple[bool, ProofObject]:
    """
    Manufacturing defect rate must be <= 2% (Six Sigma standard).

    Falsifies if: defect_rate_percent > 0.02
    
    
    max_defect_rate = manufacturing_defect_rate_max()

    if qc.defect_rate_percent > max_defect_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Batch {qc.batch_id} defect rate {qc.defect_rate_percent * 100}% > {max_defect_rate * 100}%",
            premises=[
                f"Defect rate: {qc.defect_rate_percent * 100}%",
                f"Max: {max_defect_rate * 100}% (Six Sigma)"
            ],
            rule="manufacturing_six_sigma_defect_rate"
        )

    return True, ProofObject(
        conclusion=f"Batch {qc.batch_id} meets Six Sigma defect rate standard",
        premises=[f"Defect rate: {qc.defect_rate_percent * 100}% <= {max_defect_rate * 100}%"],
        rule="manufacturing_six_sigma_defect_rate"
    )


def check_osha_incident_reporting(incident: OSHAIncident) -> Tuple[bool, ProofObject]:
    """
    OSHA serious incidents (days away from work) must be reported within 8 hours.

    Falsifies if: days_away_from_work > 0 AND reported_within_hours > 8
    
    
    max_hours = osha_incident_reporting_hours()

    if incident.days_away_from_work > 0 and incident.reported_within_hours > max_hours:
        return False, ProofObject(
            conclusion=f"VIOLATION: OSHA incident {incident.incident_id} with {incident.days_away_from_work} days away reported after {incident.reported_within_hours} hours (max {max_hours})",
            premises=[
                f"Days away from work: {incident.days_away_from_work}",
                f"Reported within: {incident.reported_within_hours} hours",
                f"OSHA deadline: {max_hours} hours"
            ],
            rule="osha_1904_incident_reporting"
        )

    return True, ProofObject(
        conclusion=f"OSHA incident {incident.incident_id} reported within required timeframe",
        premises=[
            f"Days away: {incident.days_away_from_work}",
            f"Reported within: {incident.reported_within_hours} hours"
        ],
        rule="osha_1904_incident_reporting"
    )


def check_osha_300_logging(incident: OSHAIncident) -> Tuple[bool, ProofObject]:
    """
    OSHA recordable incidents must be logged in OSHA 300 log.

    Falsifies if: days_away_from_work > 0 AND NOT osha_300_logged
    
    
    if incident.days_away_from_work > 0 and not incident.osha_300_logged:
        return False, ProofObject(
            conclusion=f"VIOLATION: OSHA incident {incident.incident_id} with days away not logged in OSHA 300",
            premises=[
                f"Days away from work: {incident.days_away_from_work}",
                f"OSHA 300 logged: {incident.osha_300_logged}"
            ],
            rule="osha_1904_300_log"
        )

    return True, ProofObject(
        conclusion=f"OSHA incident {incident.incident_id} properly logged",
        premises=[
            f"Days away: {incident.days_away_from_work}",
            f"OSHA 300 logged: {incident.osha_300_logged}"
        ],
        rule="osha_1904_300_log"
    )
