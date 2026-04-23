"""Implementation models for the public-health capacity domain.

A ``PublicHealthCapacityClaim`` records a jurisdiction's readiness to
absorb a surge event: staffed ICU beds per capita, ventilator reserve,
PPE days-of-supply, contact-tracer headcount, lab turnaround latency, and
independent-audit date. All ratios are :class:`fractions.Fraction` to keep
checks byte-exact across platforms.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

MIN_ICU_BEDS_PER_100K: Fraction = Fraction(20)
MIN_VENTILATORS_PER_100K: Fraction = Fraction(10)
MIN_PPE_DAYS: int = 90
MIN_TRACERS_PER_100K: Fraction = Fraction(30)
MAX_LAB_LATENCY_HOURS: int = 48
MAX_AUDIT_STALENESS_DAYS: int = 365


@dataclass(frozen=True)
class PublicHealthCapacityClaim:
    """Structured public-health capacity claim for one jurisdiction."""

    population: int
    staffed_icu_beds: int
    ventilator_reserve: int
    ppe_days_of_supply: int
    contact_tracer_headcount: int
    lab_turnaround_hours: int
    last_independent_audit_days_ago: int
    surveillance_coverage_fraction: Fraction = Fraction(95, 100)
    staff_training_ratio: Fraction = Fraction(9, 10)


def _per_100k(count: int, population: int) -> Fraction:
    """Return ``count`` per 100,000 population as a :class:`Fraction`."""
    if population <= 0:
        return Fraction(0)
    return Fraction(count, population) * Fraction(100_000)


def create_nominal_claim() -> PublicHealthCapacityClaim:
    """Create nominal claim data used by :func:`run_all_invariants`.

    Falsifies if: nominal jurisdiction fails any per-100k floor.
    falsifies_if: nominal jurisdiction fails any per-100k floor.
    """
    return PublicHealthCapacityClaim(
        population=1_000_000,
        staffed_icu_beds=250,
        ventilator_reserve=150,
        ppe_days_of_supply=120,
        contact_tracer_headcount=400,
        lab_turnaround_hours=24,
        last_independent_audit_days_ago=120,
        surveillance_coverage_fraction=Fraction(95, 100),
        staff_training_ratio=Fraction(9, 10),
    )


DOMAIN_METADATA = {
    "id": "D_PUBLIC_HEALTH_CAPACITY",
    "claim_model": "PublicHealthCapacityClaim",
    "check_functions": [
        "check_icu_bed_density",
        "check_ventilator_reserve_density",
        "check_ppe_days_of_supply",
        "check_contact_tracer_density",
        "check_lab_turnaround_within_limit",
        "check_audit_not_stale",
        "check_sentinel_surveillance_active",
    ],
}
