"""D_NUCLEAR invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes NRC/IAEA nuclear safety
requirements for reactor safety, radiation protection, waste containment,
emergency planning, and criticality control.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    ReactorUnit,
    RadiationExposure,
    WasteContainer,
    EmergencyPlan,
    CriticalityAssessment,
)


def check_scram_response_time(reactor: ReactorUnit) -> Tuple[bool, ProofObject]:
    """
    Rule: Reactor scram response time must not exceed the design scram limit (NUREG-0800).

    falsifies_if: scram_time_ms > design_scram_limit_ms
    """
    within_limit = reactor.scram_time_ms <= reactor.design_scram_limit_ms

    if not within_limit:
        return False, ProofObject(
            rule="scram_response_time",
            premises=[
                f"unit_id={reactor.unit_id}",
                f"scram_time_ms={reactor.scram_time_ms}",
                f"design_scram_limit_ms={reactor.design_scram_limit_ms}",
            ],
            conclusion="VIOLATION: Scram response time exceeds design limit per NUREG-0800",
        )

    return True, ProofObject(
        rule="scram_response_time",
        premises=[
            f"unit_id={reactor.unit_id}",
            f"scram_time_ms={reactor.scram_time_ms}",
            f"design_scram_limit_ms={reactor.design_scram_limit_ms}",
        ],
        conclusion="Scram response time within design limit per NUREG-0800",
    )


def check_radiation_dose_alara(exposure: RadiationExposure) -> Tuple[bool, ProofObject]:
    """
    Rule: Worker radiation dose must remain at or below the ALARA target (10 CFR 20).

    falsifies_if: dose_msv > alara_target_msv
    """
    within_alara = exposure.dose_msv <= exposure.alara_target_msv

    if not within_alara:
        return False, ProofObject(
            rule="radiation_dose_alara",
            premises=[
                f"worker_id={exposure.worker_id}",
                f"dose_msv={exposure.dose_msv}",
                f"alara_target_msv={exposure.alara_target_msv}",
                f"annual_limit_msv={exposure.annual_limit_msv}",
            ],
            conclusion="VIOLATION: Worker dose exceeds ALARA target per 10 CFR 20",
        )

    return True, ProofObject(
        rule="radiation_dose_alara",
        premises=[
            f"worker_id={exposure.worker_id}",
            f"dose_msv={exposure.dose_msv}",
            f"alara_target_msv={exposure.alara_target_msv}",
        ],
        conclusion="Worker dose within ALARA target per 10 CFR 20",
    )


def check_containment_integrity(reactor: ReactorUnit) -> Tuple[bool, ProofObject]:
    """
    Rule: Reactor containment integrity must be maintained at all times (10 CFR 50, defense-in-depth).

    falsifies_if: containment_integrity is False
    """
    intact = reactor.containment_integrity

    if not intact:
        return False, ProofObject(
            rule="containment_integrity",
            premises=[
                f"unit_id={reactor.unit_id}",
                "containment_integrity=False",
            ],
            conclusion="VIOLATION: Containment integrity lost per 10 CFR 50 defense-in-depth",
        )

    return True, ProofObject(
        rule="containment_integrity",
        premises=[
            f"unit_id={reactor.unit_id}",
            "containment_integrity=True",
        ],
        conclusion="Containment integrity maintained per 10 CFR 50 defense-in-depth",
    )


def check_waste_containment(container: WasteContainer) -> Tuple[bool, ProofObject]:
    """
    Rule: Waste container leak rate and storage duration must remain within design bounds (10 CFR 61).

    falsifies_if: leak_rate_bq_per_s > max_leak_rate_bq_per_s OR storage_years > design_life_years
    """
    leak_ok = container.leak_rate_bq_per_s <= container.max_leak_rate_bq_per_s
    storage_ok = container.storage_years <= container.design_life_years

    if not (leak_ok and storage_ok):
        return False, ProofObject(
            rule="waste_containment",
            premises=[
                f"container_id={container.container_id}",
                f"leak_rate_bq_per_s={container.leak_rate_bq_per_s}",
                f"max_leak_rate_bq_per_s={container.max_leak_rate_bq_per_s}",
                f"storage_years={container.storage_years}",
                f"design_life_years={container.design_life_years}",
                f"leak_ok={leak_ok}",
                f"storage_ok={storage_ok}",
            ],
            conclusion="VIOLATION: Waste container leak rate or storage duration exceeds bounds per 10 CFR 61",
        )

    return True, ProofObject(
        rule="waste_containment",
        premises=[
            f"container_id={container.container_id}",
            f"leak_rate_bq_per_s={container.leak_rate_bq_per_s}",
            f"max_leak_rate_bq_per_s={container.max_leak_rate_bq_per_s}",
            f"storage_years={container.storage_years}",
            f"design_life_years={container.design_life_years}",
        ],
        conclusion="Waste container within leak and storage design bounds per 10 CFR 61",
    )


def check_emergency_notification(plan: EmergencyPlan) -> Tuple[bool, ProofObject]:
    """
    Rule: Emergency notification must be completed within maximum allowed time (10 CFR 50.72).

    falsifies_if: notification_time_min > max_notification_time_min
    """
    on_time = plan.notification_time_min <= plan.max_notification_time_min

    if not on_time:
        return False, ProofObject(
            rule="emergency_notification",
            premises=[
                f"plan_id={plan.plan_id}",
                f"notification_time_min={plan.notification_time_min}",
                f"max_notification_time_min={plan.max_notification_time_min}",
            ],
            conclusion="VIOLATION: Emergency notification time exceeds limit per 10 CFR 50.72",
        )

    return True, ProofObject(
        rule="emergency_notification",
        premises=[
            f"plan_id={plan.plan_id}",
            f"notification_time_min={plan.notification_time_min}",
            f"max_notification_time_min={plan.max_notification_time_min}",
        ],
        conclusion="Emergency notification time within limit per 10 CFR 50.72",
    )


def check_criticality_safety(assessment: CriticalityAssessment) -> Tuple[bool, ProofObject]:
    """
    Rule: k-effective must be strictly less than 1 and subcritical margin must meet minimum (IAEA Safety Standards GSR Part 4).

    falsifies_if: k_effective >= Fraction(1) OR subcritical_margin < min_subcritical_margin
    """
    subcritical = assessment.k_effective < Fraction(1)
    sufficient_margin = assessment.subcritical_margin >= assessment.min_subcritical_margin

    if not (subcritical and sufficient_margin):
        return False, ProofObject(
            rule="criticality_safety",
            premises=[
                f"assessment_id={assessment.assessment_id}",
                f"k_effective={assessment.k_effective}",
                f"subcritical_margin={assessment.subcritical_margin}",
                f"min_subcritical_margin={assessment.min_subcritical_margin}",
                f"subcritical={subcritical}",
                f"sufficient_margin={sufficient_margin}",
            ],
            conclusion="VIOLATION: Criticality safety margin violated per IAEA GSR Part 4",
        )

    return True, ProofObject(
        rule="criticality_safety",
        premises=[
            f"assessment_id={assessment.assessment_id}",
            f"k_effective={assessment.k_effective}",
            f"subcritical_margin={assessment.subcritical_margin}",
            f"min_subcritical_margin={assessment.min_subcritical_margin}",
        ],
        conclusion="Criticality maintained subcritical with adequate margin per IAEA GSR Part 4",
    )


def check_defense_in_depth(reactor: ReactorUnit) -> Tuple[bool, ProofObject]:
    """
    Rule: At least three independent barriers must be maintained (10 CFR 50 Appendix A, defense-in-depth principle).

    falsifies_if: active_barriers < 3
    """
    adequate_barriers = reactor.active_barriers >= 3

    if not adequate_barriers:
        return False, ProofObject(
            rule="defense_in_depth",
            premises=[
                f"unit_id={reactor.unit_id}",
                f"active_barriers={reactor.active_barriers}",
            ],
            conclusion="VIOLATION: Fewer than 3 active barriers per 10 CFR 50 Appendix A defense-in-depth",
        )

    return True, ProofObject(
        rule="defense_in_depth",
        premises=[
            f"unit_id={reactor.unit_id}",
            f"active_barriers={reactor.active_barriers}",
        ],
        conclusion="Three or more active barriers maintained per 10 CFR 50 Appendix A defense-in-depth",
    )


def run_all_invariants() -> dict:
    """Run all D_NUCLEAR invariants with nominal sample data.

    falsifies_if: any nuclear safety invariant fails or raises an exception.
    """
    reactor = ReactorUnit(
        unit_id="REACTOR-001",
        thermal_power_mw=Fraction(3000),
        coolant_temp_c=Fraction(290),
        coolant_pressure_bar=Fraction(155),
        scram_time_ms=Fraction(200),
        design_scram_limit_ms=Fraction(500),
        containment_integrity=True,
        fuel_burnup_mwd_per_t=Fraction(35000),
        control_rod_insertion_fraction=Fraction(1, 2),
        active_barriers=4,
    )
    exposure = RadiationExposure(
        worker_id="WORKER-001",
        dose_msv=Fraction(1),
        annual_limit_msv=Fraction(50),
        alara_target_msv=Fraction(5),
        monitoring_period_days=Fraction(365),
    )
    container = WasteContainer(
        container_id="CONTAINER-001",
        waste_class="Class-B",
        shielding_factor=Fraction(1000),
        leak_rate_bq_per_s=Fraction(1, 1000),
        max_leak_rate_bq_per_s=Fraction(1, 100),
        storage_years=Fraction(10),
        design_life_years=Fraction(100),
    )
    plan = EmergencyPlan(
        plan_id="PLAN-001",
        evacuation_zone_km=Fraction(16),
        notification_time_min=Fraction(12),
        max_notification_time_min=Fraction(15),
        drill_frequency_per_year=Fraction(2),
        min_drill_frequency=Fraction(2),
    )
    assessment = CriticalityAssessment(
        assessment_id="CRIT-001",
        k_effective=Fraction(95, 100),
        subcritical_margin=Fraction(5, 100),
        min_subcritical_margin=Fraction(5, 100),
    )

    checks = [
        ("check_scram_response_time", lambda: check_scram_response_time(reactor)),
        ("check_radiation_dose_alara", lambda: check_radiation_dose_alara(exposure)),
        ("check_containment_integrity", lambda: check_containment_integrity(reactor)),
        ("check_waste_containment", lambda: check_waste_containment(container)),
        ("check_emergency_notification", lambda: check_emergency_notification(plan)),
        ("check_criticality_safety", lambda: check_criticality_safety(assessment)),
        ("check_defense_in_depth", lambda: check_defense_in_depth(reactor)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json

    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_NUCLEAR invariants: PASS")
