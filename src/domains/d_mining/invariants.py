#!/usr/bin/env python3
"""Mining Domain Invariants — MSHA safety, environmental, reclamation.

Standards:
- MSHA 30 CFR
- NEPA environmental review
- SMCRA (Surface Mining Control and Reclamation Act)
- Black Lung Benefits Act

Falsifies if:
- Ventilation inadequate
- Dust exposure exceeds limits
- Reclamation bonding insufficient
- Environmental permit expired
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    MiningOperation, SafetyIncident, EnvironmentalPermit,
    ReclamationPlan, HealthMonitoring
)


def check_ventilation_requirement(mine: MiningOperation) -> Tuple[bool, ProofObject]:
    """MSHA requires minimum 100 CFM per underground worker.
    
    falsifies_if:
        - ventilation_cfms / underground_workers < 100
    """
    if mine.underground_workers == 0:
        return True, ProofObject(
            conclusion="No underground workers, ventilation check not applicable",
            premises=["Underground workers: 0"],
            rule="ventilation_not_applicable"
        )
    
    cfm_per_worker = Fraction(mine.ventilation_cfms, mine.underground_workers)
    MIN_CFM = Fraction(100)
    
    if cfm_per_worker < MIN_CFM:
        return False, ProofObject(
            conclusion=f"VIOLATION: Ventilation {cfm_per_worker} CFM/worker below minimum {MIN_CFM}",
            premises=[
                f"Mine: {mine.mine_name}",
                f"Total CFM: {mine.ventilation_cfms}",
                f"Workers: {mine.underground_workers}",
                f"CFM/worker: {cfm_per_worker}"
            ],
            rule="msha_30_cfr_75_325_ventilation"
        )
    
    return True, ProofObject(
        conclusion="Ventilation meets MSHA requirements",
        premises=[f"CFM/worker: {cfm_per_worker}"],
        rule="ventilation_compliant"
    )


def check_dust_exposure_limit(health: HealthMonitoring, limit_mg_m3: Fraction) -> Tuple[bool, ProofObject]:
    """MSHA respirable dust standard is 1.0 mg/m3 (coal) or 0.05 mg/m3 (silica).
    
    falsifies_if:
        - respirable_dust_mg_m3 > limit
    """
    if health.respirable_dust_mg_m3 > limit_mg_m3:
        return False, ProofObject(
            conclusion=f"VIOLATION: Dust exposure {health.respirable_dust_mg_m3} exceeds limit {limit_mg_m3}",
            premises=[
                f"Worker: {health.worker_id}",
                f"Exposure: {health.respirable_dust_mg_m3} mg/m3",
                f"Limit: {limit_mg_m3} mg/m3"
            ],
            rule="msha_dust_exposure_limit"
        )
    
    return True, ProofObject(
        conclusion="Dust exposure within limits",
        premises=[f"Exposure: {health.respirable_dust_mg_m3} mg/m3"],
        rule="dust_exposure_compliant"
    )


def check_reclamation_bonding(plan: ReclamationPlan) -> Tuple[bool, ProofObject]:
    """SMCRA requires adequate reclamation bonding.
    
    falsifies_if:
        - bonding_amount < estimated reclamation cost
    """
    if not plan.bonding_adequate():
        estimated = plan.total_acres_disturbed * 5000
        return False, ProofObject(
            conclusion="VIOLATION: Reclamation bonding insufficient",
            premises=[
                f"Plan: {plan.plan_id}",
                f"Bond: ${plan.bonding_amount}",
                f"Estimated cost: ${estimated}",
                f"Acres: {plan.total_acres_disturbed}"
            ],
            rule="smcra_reclamation_bonding"
        )
    
    return True, ProofObject(
        conclusion="Reclamation bonding adequate",
        premises=[
            f"Bond: ${plan.bonding_amount}",
            f"Acres: {plan.total_acres_disturbed}"
        ],
        rule="bonding_adequate"
    )


def check_environmental_permit_current(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """Operating without current environmental permit violates law.
    
    falsifies_if:
        - expiration_date passed
    """
    if not permit.is_current():
        days_expired = (datetime.now() - permit.expiration_date).days
        return False, ProofObject(
            conclusion=f"VIOLATION: Environmental permit expired {days_expired} days ago",
            premises=[
                f"Permit: {permit.permit_id}",
                f"Type: {permit.permit_type}",
                f"Expired: {permit.expiration_date}"
            ],
            rule="environmental_permit_current"
        )
    
    return True, ProofObject(
        conclusion="Environmental permit current",
        premises=[
            f"Permit: {permit.permit_id}",
            f"Expires: {permit.expiration_date}"
        ],
        rule="permit_current"
    )


def check_incident_investigation(incident: SafetyIncident) -> Tuple[bool, ProofObject]:
    """MSHA requires investigation of serious incidents.
    
    falsifies_if:
        - Fatality without MSHA investigation
        - Root cause not identified
    """
    if incident.fatality and not incident.msha_investigation:
        return False, ProofObject(
            conclusion="VIOLATION: Fatality without MSHA investigation",
            premises=[
                f"Incident: {incident.incident_id}",
                f"Mine: {incident.mine_id}",
                f"Date: {incident.incident_date}",
                "MSHA investigation: False"
            ],
            rule="msha_fatality_investigation"
        )
    
    if incident.fatality and not incident.root_cause_identified:
        return False, ProofObject(
            conclusion="VIOLATION: Fatal incident root cause not identified",
            premises=[
                f"Incident: {incident.incident_id}",
                "Root cause: Not identified"
            ],
            rule="msha_root_cause_analysis"
        )
    
    return True, ProofObject(
        conclusion="Incident properly investigated",
        premises=[
            f"MSHA investigation: {incident.msha_investigation}",
            f"Root cause: {incident.root_cause_identified}"
        ],
        rule="incident_investigation_compliant"
    )


def check_black_lung_screening(health: HealthMonitoring) -> Tuple[bool, ProofObject]:
    """Black Lung Benefits Act requires periodic screening.
    
    falsifies_if:
        - chest_xray_date > 5 years old
        - Pneumoconiosis detected but not reported
    """
    if health.chest_xray_date is None:
        return False, ProofObject(
            conclusion="VIOLATION: Worker has no chest x-ray on file",
            premises=[
                f"Worker: {health.worker_id}",
                "X-ray: None"
            ],
            rule="black_lung_screening_required"
        )
    
    days_since_xray = (datetime.now() - health.chest_xray_date).days
    MAX_DAYS = 5 * 365  # 5 years
    
    if days_since_xray > MAX_DAYS:
        return False, ProofObject(
            conclusion="VIOLATION: Chest x-ray overdue",
            premises=[
                f"Worker: {health.worker_id}",
                f"Last x-ray: {health.chest_xray_date}",
                f"Days since: {days_since_xray}"
            ],
            rule="black_lung_periodic_screening"
        )
    
    return True, ProofObject(
        conclusion="Black lung screening current",
        premises=[
            f"X-ray: {health.chest_xray_date}",
            f"ILO: {health.xray_classification}"
        ],
        rule="black_lung_screening_compliant"
    )
