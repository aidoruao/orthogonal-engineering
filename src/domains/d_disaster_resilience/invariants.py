"""Invariant checks for the disaster-resilience domain."""
from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject

from .implementation import (
    MAX_AFTER_ACTION_STALENESS_DAYS,
    MAX_WARNING_LATENCY_SECONDS,
    MIN_BACKUP_POWER_HOURS,
    MIN_EMERGENCY_FUEL_DAYS,
    MIN_EVAC_CAPACITY_FRACTION,
    MIN_MUTUAL_AID_PARTNERS,
    DisasterResilienceClaim,
    create_nominal_claim,
    evacuation_capacity_fraction,
)


def check_warning_latency_fraction(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: warning latency as fraction of SLA budget must not exceed 1.

    Standard: FEMA IPAWS / NOAA EAS 2-minute public-alert SLA.
    Falsifies if: warning_latency_seconds / MAX_WARNING_LATENCY_SECONDS > Fraction(1).
    falsifies_if: warning_latency_seconds / MAX_WARNING_LATENCY_SECONDS > Fraction(1).
    """
    if MAX_WARNING_LATENCY_SECONDS <= 0:
        latency_frac = Fraction(0)
        success = False
        conclusion = f"FAIL: invalid SLA budget (MAX_WARNING_LATENCY_SECONDS={MAX_WARNING_LATENCY_SECONDS})"
    else:
        latency_frac = Fraction(data.warning_latency_seconds, MAX_WARNING_LATENCY_SECONDS)
        success = latency_frac <= Fraction(1)
        conclusion = (
            f"PASS: latency fraction {latency_frac} within SLA"
            if success
            else f"FAIL: latency fraction {latency_frac} exceeds SLA"
        )
    proof = ProofObject(
        rule="check_warning_latency_fraction",
        premises=[
            f"warning_latency_seconds={data.warning_latency_seconds}",
            f"max={MAX_WARNING_LATENCY_SECONDS}",
            f"latency_fraction={latency_frac}",
        ],
        conclusion=conclusion,
    )
    return success, proof


def check_evacuation_capacity_ratio(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: evacuation lift as fraction of population >= 25%.

    Standard: FEMA CPG 101 mass-care planning threshold.
    Falsifies if: evacuation_capacity / population < MIN_EVAC_CAPACITY_FRACTION.
    falsifies_if: evacuation_capacity / population < MIN_EVAC_CAPACITY_FRACTION.
    """
    ratio = evacuation_capacity_fraction(data)
    success = ratio >= MIN_EVAC_CAPACITY_FRACTION
    proof = ProofObject(
        rule="check_evacuation_capacity_ratio",
        premises=[
            f"evacuation_capacity={data.evacuation_capacity}",
            f"population={data.population}",
            f"ratio={ratio}",
            f"floor={MIN_EVAC_CAPACITY_FRACTION}",
        ],
        conclusion=(
            f"PASS: evacuation ratio {ratio} >= {MIN_EVAC_CAPACITY_FRACTION}"
            if success else f"FAIL: evacuation ratio {ratio} < {MIN_EVAC_CAPACITY_FRACTION}"
        ),
    )
    return success, proof


def check_fuel_reserve_ratio(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: emergency fuel reserve as fraction of minimum requirement >= 1.

    Standard: DHS/CISA Lifeline Sector fuel-continuity guidance.
    Falsifies if: emergency_fuel_days / MIN_EMERGENCY_FUEL_DAYS < Fraction(1).
    falsifies_if: emergency_fuel_days / MIN_EMERGENCY_FUEL_DAYS < Fraction(1).
    """
    if MIN_EMERGENCY_FUEL_DAYS <= 0:
        ratio = Fraction(0)
        success = False
    else:
        ratio = Fraction(data.emergency_fuel_days, MIN_EMERGENCY_FUEL_DAYS)
        success = ratio >= Fraction(1)
    proof = ProofObject(
        rule="check_fuel_reserve_ratio",
        premises=[
            f"emergency_fuel_days={data.emergency_fuel_days}",
            f"min={MIN_EMERGENCY_FUEL_DAYS}",
            f"ratio={ratio}",
        ],
        conclusion=(
            f"PASS: fuel ratio {ratio} >= 1"
            if success else f"FAIL: fuel ratio {ratio} < 1"
        ),
    )
    return success, proof


def check_mutual_aid_coverage_ratio(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: mutual-aid partners as fraction of minimum requirement >= 1.

    Standard: EMAC interstate mutual-aid framework.
    Falsifies if: mutual_aid_partner_count / MIN_MUTUAL_AID_PARTNERS < Fraction(1).
    falsifies_if: mutual_aid_partner_count / MIN_MUTUAL_AID_PARTNERS < Fraction(1).
    """
    if MIN_MUTUAL_AID_PARTNERS <= 0:
        ratio = Fraction(0)
        success = False
    else:
        ratio = Fraction(data.mutual_aid_partner_count, MIN_MUTUAL_AID_PARTNERS)
        success = ratio >= Fraction(1)
    proof = ProofObject(
        rule="check_mutual_aid_coverage_ratio",
        premises=[
            f"mutual_aid_partner_count={data.mutual_aid_partner_count}",
            f"min={MIN_MUTUAL_AID_PARTNERS}",
            f"ratio={ratio}",
        ],
        conclusion=(
            f"PASS: mutual-aid ratio {ratio} >= 1"
            if success else f"FAIL: mutual-aid ratio {ratio} < 1"
        ),
    )
    return success, proof


def check_backup_power_fraction(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: backup power hours as fraction of minimum requirement >= 1.

    Standard: NFPA 110 Level 1 emergency power system.
    Falsifies if: backup_power_autonomy_hours / MIN_BACKUP_POWER_HOURS < Fraction(1).
    falsifies_if: backup_power_autonomy_hours / MIN_BACKUP_POWER_HOURS < Fraction(1).
    """
    if MIN_BACKUP_POWER_HOURS <= 0:
        ratio = Fraction(0)
        success = False
    else:
        ratio = Fraction(data.backup_power_autonomy_hours, MIN_BACKUP_POWER_HOURS)
        success = ratio >= Fraction(1)
    proof = ProofObject(
        rule="check_backup_power_fraction",
        premises=[
            f"backup_power_autonomy_hours={data.backup_power_autonomy_hours}",
            f"min={MIN_BACKUP_POWER_HOURS}",
            f"ratio={ratio}",
        ],
        conclusion=(
            f"PASS: backup power ratio {ratio} >= 1"
            if success else f"FAIL: backup power ratio {ratio} < 1"
        ),
    )
    return success, proof


def check_after_action_staleness_fraction(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: after-action report staleness as fraction of max window <= 1.

    Standard: FEMA HSEEP after-action report cadence.
    Falsifies if: days_ago / MAX_AFTER_ACTION_STALENESS_DAYS > Fraction(1).
    falsifies_if: days_ago / MAX_AFTER_ACTION_STALENESS_DAYS > Fraction(1).
    """
    if MAX_AFTER_ACTION_STALENESS_DAYS <= 0:
        staleness = Fraction(0)
        success = False
        conclusion = f"FAIL: invalid staleness window (MAX_AFTER_ACTION_STALENESS_DAYS={MAX_AFTER_ACTION_STALENESS_DAYS})"
    else:
        staleness = Fraction(data.last_after_action_report_days_ago, MAX_AFTER_ACTION_STALENESS_DAYS)
        success = staleness <= Fraction(1)
        conclusion = (
            f"PASS: staleness fraction {staleness} within window"
            if success else f"FAIL: staleness fraction {staleness} exceeds window"
        )
    proof = ProofObject(
        rule="check_after_action_staleness_fraction",
        premises=[
            f"days_since_report={data.last_after_action_report_days_ago}",
            f"max={MAX_AFTER_ACTION_STALENESS_DAYS}",
            f"staleness_fraction={staleness}",
        ],
        conclusion=conclusion,
    )
    return success, proof


def check_cyber_readiness_score(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: cyber incident-response readiness score meets floor.

    Standard: CISA Cyber Incident Response Playbook (2021) + NIST SP 800-61r2.
    Falsifies if: cyber_readiness_score < Fraction(1, 2).
    falsifies_if: cyber_readiness_score < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    success = data.cyber_readiness_score >= threshold
    proof = ProofObject(
        rule="check_cyber_readiness_score",
        premises=[
            f"cyber_readiness_score={data.cyber_readiness_score}",
            f"threshold={threshold}",
        ],
        conclusion=(
            f"PASS: cyber readiness {data.cyber_readiness_score} >= {threshold}"
            if success else f"FAIL: cyber readiness {data.cyber_readiness_score} < {threshold}"
        ),
    )
    return success, proof


def check_infrastructure_redundancy(
    data: DisasterResilienceClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: critical infrastructure redundancy meets minimum fraction.

    Standard: DHS National Infrastructure Protection Plan redundancy requirements.
    Falsifies if: infrastructure_redundancy < Fraction(1, 2).
    falsifies_if: infrastructure_redundancy < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    success = data.infrastructure_redundancy >= threshold
    proof = ProofObject(
        rule="check_infrastructure_redundancy",
        premises=[
            f"infrastructure_redundancy={data.infrastructure_redundancy}",
            f"threshold={threshold}",
        ],
        conclusion=(
            f"PASS: redundancy {data.infrastructure_redundancy} >= {threshold}"
            if success else f"FAIL: redundancy {data.infrastructure_redundancy} < {threshold}"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain on the nominal claim.

    Standard: Disaster-resilience nominal executable check set.
    Falsifies if: any invariant check returns False on the nominal claim.
    falsifies_if: any invariant check returns False on the nominal claim.
    """
    data = create_nominal_claim()
    checks = [
        ("check_warning_latency_fraction", check_warning_latency_fraction),
        ("check_evacuation_capacity_ratio", check_evacuation_capacity_ratio),
        ("check_fuel_reserve_ratio", check_fuel_reserve_ratio),
        ("check_mutual_aid_coverage_ratio", check_mutual_aid_coverage_ratio),
        ("check_backup_power_fraction", check_backup_power_fraction),
        ("check_after_action_staleness_fraction", check_after_action_staleness_fraction),
        ("check_cyber_readiness_score", check_cyber_readiness_score),
        ("check_infrastructure_redundancy", check_infrastructure_redundancy),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
