"""Implementation models for the civilizational polymath capability domain.

A "civilizational polymath" claim certifies that a system is accountable in
each of the five domain registers the Orthogonal Engineering framework treats
as load-bearing for a civilization: formal mathematics, empirical science,
engineering, governance, and theology / ethics. Every register is represented
by a capability flag plus a measured coverage fraction, so the domain can be
checked symbolically (every capability HAS evidence) and quantitatively (every
register clears its Fraction-based coverage floor).
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


MIN_REGISTER_COVERAGE: Fraction = Fraction(4, 5)
"""Minimum per-register coverage floor (80%).

Standard: BC-004 capability comparison (HAS / DOES_NOT_HAVE / UNKNOWN) plus
AF-008 quarterly scan requirement.
"""


@dataclass(frozen=True)
class PolymathClaim:
    """Capability + coverage record for a civilizational polymath claim.

    Every capability flag is the HAS/DOES_NOT_HAVE/UNKNOWN assertion from
    BC-004 — here represented as a boolean after the UNKNOWN state has been
    resolved. Coverage fractions are measured as Fraction(passing, total) so
    determinism is preserved end-to-end.
    """

    has_formal_mathematics: bool
    has_empirical_science: bool
    has_engineering: bool
    has_governance: bool
    has_theology_ethics: bool
    mathematics_coverage: Fraction
    science_coverage: Fraction
    engineering_coverage: Fraction
    governance_coverage: Fraction
    theology_coverage: Fraction
    cross_register_entailments_proved: int
    cross_register_entailments_total: int


def create_nominal_claim() -> PolymathClaim:
    """Create nominal claim data used by :func:`run_all_invariants`.

    Falsifies if: the nominal claim cannot be constructed with all five
    registers at HAS status and coverage >= :data:`MIN_REGISTER_COVERAGE`.
    falsifies_if: the nominal claim cannot be constructed with all five
    registers at HAS status and coverage >= MIN_REGISTER_COVERAGE.
    """
    return PolymathClaim(
        has_formal_mathematics=True,
        has_empirical_science=True,
        has_engineering=True,
        has_governance=True,
        has_theology_ethics=True,
        mathematics_coverage=Fraction(9, 10),
        science_coverage=Fraction(17, 20),
        engineering_coverage=Fraction(19, 20),
        governance_coverage=Fraction(4, 5),
        theology_coverage=Fraction(21, 25),
        cross_register_entailments_proved=10,
        cross_register_entailments_total=10,
    )


DOMAIN_METADATA = {
    "id": "D_CIVILIZATIONAL_POLYMATH",
    "claim_model": "PolymathClaim",
    "check_functions": [
        "check_all_registers_has_capability",
        "check_register_coverage_floor",
        "check_cross_register_entailments_complete",
        "check_coverage_monotone_across_registers",
        "check_polymath_capability_invariant",
    ],
}
