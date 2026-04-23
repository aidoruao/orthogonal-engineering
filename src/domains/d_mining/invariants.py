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
- Environmental permit validity fraction below threshold
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    MiningOperation, SafetyIncident, EnvironmentalPermit,
    ReclamationPlan, HealthMonitoring,
    MineStatus,
    MineType,
)


def check_ventilation_requirement(mine: MiningOperation) -> Tuple[bool, ProofObject]:
    """MSHA requires minimum 100 CFM per underground worker.

    Falsifies if: ventilation_cfms per underground worker falls below 100 CFM.
    falsifies_if: ventilation_cfms per underground_worker < 100 CFM.
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

    Falsifies if: respirable_dust_mg_m3 exceeds limit_mg_m3.
    falsifies_if: respirable_dust_mg_m3 > limit_mg_m3.
    """
    margin = limit_mg_m3 - health.respirable_dust_mg_m3
    if health.respirable_dust_mg_m3 > limit_mg_m3:
        return False, ProofObject(
            conclusion=f"VIOLATION: Dust exposure {health.respirable_dust_mg_m3} exceeds limit {limit_mg_m3}",
            premises=[
                f"Worker: {health.worker_id}",
                f"Exposure: {health.respirable_dust_mg_m3} mg/m3",
                f"Limit: {limit_mg_m3} mg/m3",
                f"Margin: {margin}"
            ],
            rule="msha_dust_exposure_limit"
        )

    return True, ProofObject(
        conclusion="Dust exposure within limits",
        premises=[
            f"Exposure: {health.respirable_dust_mg_m3} mg/m3",
            f"Margin: {margin}"
        ],
        rule="dust_exposure_compliant"
    )


def check_reclamation_bonding(plan: ReclamationPlan) -> Tuple[bool, ProofObject]:
    """SMCRA requires adequate reclamation bonding.

    Falsifies if: bonding_amount is less than estimated reclamation cost.
    falsifies_if: bonding_amount < total_acres_disturbed * 5000.
    """
    estimated = plan.total_acres_disturbed * 5000
    shortfall = estimated - plan.bonding_amount
    if not plan.bonding_adequate():
        return False, ProofObject(
            conclusion="VIOLATION: Reclamation bonding insufficient",
            premises=[
                f"Plan: {plan.plan_id}",
                f"Bond: ${plan.bonding_amount}",
                f"Estimated cost: ${estimated}",
                f"Acres: {plan.total_acres_disturbed}",
                f"Shortfall: ${shortfall}"
            ],
            rule="smcra_reclamation_bonding"
        )

    return True, ProofObject(
        conclusion="Reclamation bonding adequate",
        premises=[
            f"Bond: ${plan.bonding_amount}",
            f"Acres: {plan.total_acres_disturbed}",
            f"Shortfall: ${shortfall}"
        ],
        rule="bonding_adequate"
    )


def check_permit_validity_fraction(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """Environmental permit validity fraction must meet regulatory floor.

    Standard: Operating without adequate permit validity violates environmental law.
    falsifies_if: permit_validity_fraction < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    if permit.permit_validity_fraction < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Environmental permit validity fraction {permit.permit_validity_fraction} below threshold {threshold}",
            premises=[
                f"Permit: {permit.permit_id}",
                f"Type: {permit.permit_type}",
                f"Validity fraction: {permit.permit_validity_fraction}",
                f"Threshold: {threshold}"
            ],
            rule="environmental_permit_validity"
        )

    return True, ProofObject(
        conclusion="Environmental permit validity fraction adequate",
        premises=[
            f"Permit: {permit.permit_id}",
            f"Validity fraction: {permit.permit_validity_fraction}",
            f"Threshold: {threshold}"
        ],
        rule="permit_validity_compliant"
    )


def check_investigation_completeness(incident: SafetyIncident) -> Tuple[bool, ProofObject]:
    """MSHA requires investigation completeness score above threshold for serious incidents.

    Standard: MSHA incident investigation requirements (30 CFR 50).
    falsifies_if: investigation_completeness_score < Fraction(3, 4).
    """
    threshold = Fraction(3, 4)
    if incident.investigation_completeness_score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Investigation completeness score {incident.investigation_completeness_score} below threshold {threshold}",
            premises=[
                f"Incident: {incident.incident_id}",
                f"Mine: {incident.mine_id}",
                f"Completeness score: {incident.investigation_completeness_score}",
                f"Threshold: {threshold}"
            ],
            rule="msha_investigation_completeness"
        )

    return True, ProofObject(
        conclusion="Incident investigation completeness adequate",
        premises=[
            f"Incident: {incident.incident_id}",
            f"Completeness score: {incident.investigation_completeness_score}",
            f"Threshold: {threshold}"
        ],
        rule="investigation_completeness_compliant"
    )


def check_screening_compliance_score(health: HealthMonitoring) -> Tuple[bool, ProofObject]:
    """Black Lung screening compliance score must meet periodic screening floor.

    Standard: Black Lung Benefits Act periodic screening requirements.
    falsifies_if: screening_compliance_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    if health.screening_compliance_score < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Screening compliance score {health.screening_compliance_score} below threshold {threshold}",
            premises=[
                f"Worker: {health.worker_id}",
                f"Screening compliance score: {health.screening_compliance_score}",
                f"Threshold: {threshold}"
            ],
            rule="black_lung_screening_compliance"
        )

    return True, ProofObject(
        conclusion="Black lung screening compliance adequate",
        premises=[
            f"Worker: {health.worker_id}",
            f"Screening compliance score: {health.screening_compliance_score}",
            f"Threshold: {threshold}"
        ],
        rule="black_lung_screening_compliant"
    )


def run_all_invariants() -> dict:
    """Run all D_MINING invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    health_monitoring = HealthMonitoring(
        worker_id="WORKER-001",
        mine_id="MINE-001",
        chest_xray_date=None,
        xray_classification=None,
        respirable_dust_mg_m3=Fraction(1),
        silica_exceedance=False,
        noise_exposure_dba=Fraction(1),
        hearing_conservation_required=False,
        screening_compliance_score=Fraction(1, 1),
    )
    environmental_permit = EnvironmentalPermit(
        permit_id="PERMIT-001",
        mine_id="MINE-001",
        permit_type="NPDES",
        issued_date=None,
        expiration_date=None,
        discharge_limits={},
        monitoring_required=True,
        permit_validity_fraction=Fraction(1, 1),
    )
    safety_incident = SafetyIncident(
        incident_id="INC-001",
        mine_id="MINE-001",
        incident_date=None,
        incident_type="near-miss",
        classification="A",
        injured_count=0,
        fatality=False,
        msha_investigation=True,
        root_cause_identified=True,
        investigation_completeness_score=Fraction(1, 1),
    )
    reclamation_plan = ReclamationPlan(
        plan_id="PLAN-001",
        mine_id="MINE-001",
        total_acres_disturbed=Fraction(1),
        acres_reclaimed=Fraction(1),
        bonding_amount=Fraction(10000),
        bonding_type="surety",
    )
    mining_operation = MiningOperation(
        mine_id="MINE-001",
        mine_name="Test Mine",
        mine_type=MineType.UNDERGROUND_COAL,
        status=MineStatus.ACTIVE,
        state="WV",
        msha_id="MSHA-001",
        total_employees=100,
        underground_workers=50,
        annual_tonnage=10000,
        primary_commodity="coal",
        ventilation_cfms=10000,
        escapeways=2,
        msha_inspections_annual=4,
        violations_pending=0,
    )

    checks = [
        ("check_screening_compliance_score", lambda: check_screening_compliance_score(health_monitoring)),
        ("check_dust_exposure_limit", lambda: check_dust_exposure_limit(health_monitoring, Fraction(1000))),
        ("check_permit_validity_fraction", lambda: check_permit_validity_fraction(environmental_permit)),
        ("check_investigation_completeness", lambda: check_investigation_completeness(safety_incident)),
        ("check_reclamation_bonding", lambda: check_reclamation_bonding(reclamation_plan)),
        ("check_ventilation_requirement", lambda: check_ventilation_requirement(mining_operation)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_MINING invariants: PASS")
