"""Invariant checks for the public-health capacity domain."""
from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject

from .implementation import (
    MAX_AUDIT_STALENESS_DAYS,
    MAX_LAB_LATENCY_HOURS,
    MIN_ICU_BEDS_PER_100K,
    MIN_PPE_DAYS,
    MIN_TRACERS_PER_100K,
    MIN_VENTILATORS_PER_100K,
    PublicHealthCapacityClaim,
    _per_100k,
    create_nominal_claim,
)


def check_icu_bed_density(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: staffed ICU beds per 100k >= MIN_ICU_BEDS_PER_100K.

    Standard: HHS ASPR Hospital Preparedness Program surge benchmark.
    Falsifies if: per-100k density below the floor.
    falsifies_if: per-100k density below the floor.
    """
    ratio = _per_100k(data.staffed_icu_beds, data.population)
    success = ratio >= MIN_ICU_BEDS_PER_100K
    proof = ProofObject(
        rule="check_icu_bed_density",
        premises=[
            f"staffed_icu_beds={data.staffed_icu_beds}",
            f"population={data.population}",
            f"per_100k={ratio}",
            f"floor={MIN_ICU_BEDS_PER_100K}",
        ],
        conclusion=(
            "PASS: ICU bed density >= floor"
            if success else f"FAIL: {ratio} < {MIN_ICU_BEDS_PER_100K}"
        ),
    )
    return success, proof


def check_ventilator_reserve_density(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: ventilator reserve per 100k >= MIN_VENTILATORS_PER_100K.

    Standard: CDC Strategic National Stockpile allocation guidance.
    Falsifies if: per-100k density below the floor.
    falsifies_if: per-100k density below the floor.
    """
    ratio = _per_100k(data.ventilator_reserve, data.population)
    success = ratio >= MIN_VENTILATORS_PER_100K
    proof = ProofObject(
        rule="check_ventilator_reserve_density",
        premises=[
            f"ventilator_reserve={data.ventilator_reserve}",
            f"population={data.population}",
            f"per_100k={ratio}",
            f"floor={MIN_VENTILATORS_PER_100K}",
        ],
        conclusion=(
            "PASS: ventilator reserve density >= floor"
            if success else f"FAIL: {ratio} < {MIN_VENTILATORS_PER_100K}"
        ),
    )
    return success, proof


def check_ppe_days_of_supply(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: PPE days-of-supply >= MIN_PPE_DAYS.

    Standard: ASPR pandemic stockpile 90-day benchmark.
    Falsifies if: ppe_days_of_supply < MIN_PPE_DAYS.
    falsifies_if: ppe_days_of_supply < MIN_PPE_DAYS.
    """
    success = data.ppe_days_of_supply >= MIN_PPE_DAYS
    proof = ProofObject(
        rule="check_ppe_days_of_supply",
        premises=[
            f"ppe_days_of_supply={data.ppe_days_of_supply}",
            f"floor={MIN_PPE_DAYS}",
        ],
        conclusion=(
            "PASS: PPE supply >= floor"
            if success else f"FAIL: {data.ppe_days_of_supply} < {MIN_PPE_DAYS}"
        ),
    )
    return success, proof


def check_contact_tracer_density(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: contact tracers per 100k >= MIN_TRACERS_PER_100K.

    Standard: Johns Hopkins Bloomberg School contact-tracing workforce model.
    Falsifies if: per-100k density below the floor.
    falsifies_if: per-100k density below the floor.
    """
    ratio = _per_100k(data.contact_tracer_headcount, data.population)
    success = ratio >= MIN_TRACERS_PER_100K
    proof = ProofObject(
        rule="check_contact_tracer_density",
        premises=[
            f"contact_tracer_headcount={data.contact_tracer_headcount}",
            f"population={data.population}",
            f"per_100k={ratio}",
            f"floor={MIN_TRACERS_PER_100K}",
        ],
        conclusion=(
            "PASS: tracer density >= floor"
            if success else f"FAIL: {ratio} < {MIN_TRACERS_PER_100K}"
        ),
    )
    return success, proof


def check_lab_turnaround_within_limit(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: lab turnaround hours <= MAX_LAB_LATENCY_HOURS.

    Standard: CDC surveillance operational tempo threshold.
    Falsifies if: lab_turnaround_hours > MAX_LAB_LATENCY_HOURS.
    falsifies_if: lab_turnaround_hours > MAX_LAB_LATENCY_HOURS.
    """
    success = data.lab_turnaround_hours <= MAX_LAB_LATENCY_HOURS
    proof = ProofObject(
        rule="check_lab_turnaround_within_limit",
        premises=[
            f"lab_turnaround_hours={data.lab_turnaround_hours}",
            f"limit={MAX_LAB_LATENCY_HOURS}",
        ],
        conclusion=(
            "PASS: lab turnaround <= limit"
            if success
            else f"FAIL: {data.lab_turnaround_hours} > {MAX_LAB_LATENCY_HOURS}"
        ),
    )
    return success, proof


def check_audit_not_stale(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: last independent audit was within the staleness window.

    Standard: AF-008 quarterly scan + annual independent review.
    Falsifies if: last_independent_audit_days_ago > MAX_AUDIT_STALENESS_DAYS.
    falsifies_if: last_independent_audit_days_ago > MAX_AUDIT_STALENESS_DAYS.
    """
    success = data.last_independent_audit_days_ago <= MAX_AUDIT_STALENESS_DAYS
    proof = ProofObject(
        rule="check_audit_not_stale",
        premises=[
            f"days_since_audit={data.last_independent_audit_days_ago}",
            f"max_staleness={MAX_AUDIT_STALENESS_DAYS}",
        ],
        conclusion=(
            "PASS: audit within staleness window"
            if success
            else (
                f"FAIL: {data.last_independent_audit_days_ago} > "
                f"{MAX_AUDIT_STALENESS_DAYS}"
            )
        ),
    )
    return success, proof


def check_sentinel_surveillance_active(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: sentinel surveillance pipeline is active.

    Standard: WHO Integrated Disease Surveillance & Response (IDSR).
    Falsifies if: sentinel_surveillance_active False.
    falsifies_if: sentinel_surveillance_active False.
    """
    success = data.sentinel_surveillance_active
    proof = ProofObject(
        rule="check_sentinel_surveillance_active",
        premises=[
            f"sentinel_surveillance_active={data.sentinel_surveillance_active}",
        ],
        conclusion=(
            "PASS: sentinel surveillance active"
            if success else "FAIL: sentinel surveillance inactive"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain on the nominal claim.

    Standard: Public-health capacity nominal executable check set.
    Falsifies if: any invariant check returns False on the nominal claim.
    falsifies_if: any invariant check returns False on the nominal claim.
    """
    data = create_nominal_claim()
    checks = [
        ("check_icu_bed_density", check_icu_bed_density),
        ("check_ventilator_reserve_density", check_ventilator_reserve_density),
        ("check_ppe_days_of_supply", check_ppe_days_of_supply),
        ("check_contact_tracer_density", check_contact_tracer_density),
        ("check_lab_turnaround_within_limit", check_lab_turnaround_within_limit),
        ("check_audit_not_stale", check_audit_not_stale),
        ("check_sentinel_surveillance_active", check_sentinel_surveillance_active),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
