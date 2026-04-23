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


def check_icu_bed_density_ratio(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: staffed ICU beds per 100k as fraction of floor >= 1.

    Standard: HHS ASPR Hospital Preparedness Program surge benchmark.
    Falsifies if: per_100k / MIN_ICU_BEDS_PER_100K < Fraction(1).
    falsifies_if: per_100k / MIN_ICU_BEDS_PER_100K < Fraction(1).
    """
    ratio = _per_100k(data.staffed_icu_beds, data.population)
    if MIN_ICU_BEDS_PER_100K > Fraction(0):
        coverage = ratio / MIN_ICU_BEDS_PER_100K
    else:
        coverage = Fraction(0)
    success = ratio >= MIN_ICU_BEDS_PER_100K
    proof = ProofObject(
        rule="check_icu_bed_density_ratio",
        premises=[
            f"staffed_icu_beds={data.staffed_icu_beds}",
            f"population={data.population}",
            f"per_100k={ratio}",
            f"floor={MIN_ICU_BEDS_PER_100K}",
            f"coverage={coverage}",
        ],
        conclusion=(
            f"PASS: ICU density {ratio} >= floor (coverage {coverage})"
            if success else f"FAIL: ICU density {ratio} < floor"
        ),
    )
    return success, proof


def check_ventilator_reserve_ratio(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: ventilator reserve per 100k as fraction of floor >= 1.

    Standard: CDC Strategic National Stockpile allocation guidance.
    Falsifies if: per_100k / MIN_VENTILATORS_PER_100K < Fraction(1).
    falsifies_if: per_100k / MIN_VENTILATORS_PER_100K < Fraction(1).
    """
    ratio = _per_100k(data.ventilator_reserve, data.population)
    if MIN_VENTILATORS_PER_100K > Fraction(0):
        coverage = ratio / MIN_VENTILATORS_PER_100K
    else:
        coverage = Fraction(0)
    success = ratio >= MIN_VENTILATORS_PER_100K
    proof = ProofObject(
        rule="check_ventilator_reserve_ratio",
        premises=[
            f"ventilator_reserve={data.ventilator_reserve}",
            f"population={data.population}",
            f"per_100k={ratio}",
            f"floor={MIN_VENTILATORS_PER_100K}",
            f"coverage={coverage}",
        ],
        conclusion=(
            f"PASS: ventilator density {ratio} >= floor (coverage {coverage})"
            if success else f"FAIL: ventilator density {ratio} < floor"
        ),
    )
    return success, proof


def check_ppe_supply_ratio(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: PPE days-of-supply as fraction of 90-day benchmark >= 1.

    Standard: ASPR pandemic stockpile 90-day benchmark.
    Falsifies if: ppe_days / MIN_PPE_DAYS < Fraction(1).
    falsifies_if: ppe_days / MIN_PPE_DAYS < Fraction(1).
    """
    if MIN_PPE_DAYS <= 0:
        ratio = Fraction(0)
        success = False
    else:
        ratio = Fraction(data.ppe_days_of_supply, MIN_PPE_DAYS)
        success = ratio >= Fraction(1)
    proof = ProofObject(
        rule="check_ppe_supply_ratio",
        premises=[
            f"ppe_days_of_supply={data.ppe_days_of_supply}",
            f"min={MIN_PPE_DAYS}",
            f"ratio={ratio}",
        ],
        conclusion=(
            f"PASS: PPE ratio {ratio} >= 1"
            if success else f"FAIL: PPE ratio {ratio} < 1"
        ),
    )
    return success, proof


def check_tracer_density_ratio(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: contact tracers per 100k as fraction of floor >= 1.

    Standard: Johns Hopkins Bloomberg School contact-tracing workforce model.
    Falsifies if: per_100k / MIN_TRACERS_PER_100K < Fraction(1).
    falsifies_if: per_100k / MIN_TRACERS_PER_100K < Fraction(1).
    """
    ratio = _per_100k(data.contact_tracer_headcount, data.population)
    if MIN_TRACERS_PER_100K > Fraction(0):
        coverage = ratio / MIN_TRACERS_PER_100K
    else:
        coverage = Fraction(0)
    success = ratio >= MIN_TRACERS_PER_100K
    proof = ProofObject(
        rule="check_tracer_density_ratio",
        premises=[
            f"contact_tracer_headcount={data.contact_tracer_headcount}",
            f"population={data.population}",
            f"per_100k={ratio}",
            f"floor={MIN_TRACERS_PER_100K}",
            f"coverage={coverage}",
        ],
        conclusion=(
            f"PASS: tracer density {ratio} >= floor (coverage {coverage})"
            if success else f"FAIL: tracer density {ratio} < floor"
        ),
    )
    return success, proof


def check_lab_turnaround_fraction(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: lab turnaround as fraction of max latency <= 1.

    Standard: CDC surveillance operational tempo threshold.
    Falsifies if: lab_turnaround_hours / MAX_LAB_LATENCY_HOURS > Fraction(1).
    falsifies_if: lab_turnaround_hours / MAX_LAB_LATENCY_HOURS > Fraction(1).
    """
    if MAX_LAB_LATENCY_HOURS <= 0:
        frac = Fraction(0)
        success = False
    else:
        frac = Fraction(data.lab_turnaround_hours, MAX_LAB_LATENCY_HOURS)
        success = frac <= Fraction(1)
    proof = ProofObject(
        rule="check_lab_turnaround_fraction",
        premises=[
            f"lab_turnaround_hours={data.lab_turnaround_hours}",
            f"max={MAX_LAB_LATENCY_HOURS}",
            f"fraction={frac}",
        ],
        conclusion=(
            f"PASS: lab turnaround fraction {frac} within limit"
            if success else f"FAIL: lab turnaround fraction {frac} exceeds limit"
        ),
    )
    return success, proof


def check_audit_staleness_fraction(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: audit staleness as fraction of max window <= 1.

    Standard: AF-008 quarterly scan + annual independent review.
    Falsifies if: days_ago / MAX_AUDIT_STALENESS_DAYS > Fraction(1).
    falsifies_if: days_ago / MAX_AUDIT_STALENESS_DAYS > Fraction(1).
    """
    if MAX_AUDIT_STALENESS_DAYS <= 0:
        frac = Fraction(0)
        success = False
    else:
        frac = Fraction(data.last_independent_audit_days_ago, MAX_AUDIT_STALENESS_DAYS)
        success = frac <= Fraction(1)
    proof = ProofObject(
        rule="check_audit_staleness_fraction",
        premises=[
            f"days_since_audit={data.last_independent_audit_days_ago}",
            f"max={MAX_AUDIT_STALENESS_DAYS}",
            f"staleness_fraction={frac}",
        ],
        conclusion=(
            f"PASS: audit staleness {frac} within window"
            if success else f"FAIL: audit staleness {frac} exceeds window"
        ),
    )
    return success, proof


def check_surveillance_coverage(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: sentinel surveillance coverage fraction meets threshold.

    Standard: WHO Integrated Disease Surveillance and Response (IDSR).
    Falsifies if: surveillance_coverage_fraction < Fraction(9, 10).
    falsifies_if: surveillance_coverage_fraction < Fraction(9, 10).
    """
    threshold = Fraction(9, 10)
    success = data.surveillance_coverage_fraction >= threshold
    proof = ProofObject(
        rule="check_surveillance_coverage",
        premises=[
            f"surveillance_coverage_fraction={data.surveillance_coverage_fraction}",
            f"threshold={threshold}",
        ],
        conclusion=(
            f"PASS: surveillance coverage {data.surveillance_coverage_fraction} >= {threshold}"
            if success
            else f"FAIL: surveillance coverage {data.surveillance_coverage_fraction} < {threshold}"
        ),
    )
    return success, proof


def check_staff_training_ratio(
    data: PublicHealthCapacityClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: staff training ratio meets minimum threshold.

    Standard: CDC Public Health Emergency Preparedness (PHEP) capability standards.
    Falsifies if: staff_training_ratio < Fraction(1, 2).
    falsifies_if: staff_training_ratio < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    success = data.staff_training_ratio >= threshold
    proof = ProofObject(
        rule="check_staff_training_ratio",
        premises=[
            f"staff_training_ratio={data.staff_training_ratio}",
            f"threshold={threshold}",
        ],
        conclusion=(
            f"PASS: training ratio {data.staff_training_ratio} >= {threshold}"
            if success
            else f"FAIL: training ratio {data.staff_training_ratio} < {threshold}"
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
        ("check_icu_bed_density_ratio", check_icu_bed_density_ratio),
        ("check_ventilator_reserve_ratio", check_ventilator_reserve_ratio),
        ("check_ppe_supply_ratio", check_ppe_supply_ratio),
        ("check_tracer_density_ratio", check_tracer_density_ratio),
        ("check_lab_turnaround_fraction", check_lab_turnaround_fraction),
        ("check_audit_staleness_fraction", check_audit_staleness_fraction),
        ("check_surveillance_coverage", check_surveillance_coverage),
        ("check_staff_training_ratio", check_staff_training_ratio),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
