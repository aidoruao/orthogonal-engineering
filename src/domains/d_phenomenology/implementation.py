"""Implementation models for Phenomenology."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class PhenomenologyClaim:
    """Structured claim parameters for Phenomenology domain invariants."""

    intentionality_directed: bool
    noema_nema_distinct: bool
    lifeworld_presupposed: bool
    bracketing_valid: bool
    epoche_completeness: Fraction


def create_nominal_claim() -> PhenomenologyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return PhenomenologyClaim(
        intentionality_directed=True,
        noema_nema_distinct=True,
        lifeworld_presupposed=True,
        bracketing_valid=True,
        epoche_completeness=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "PHENOMENOLOGY",
    "claim_model": "PhenomenologyClaim",
    "check_functions": [
        "check_intentionality_directedness",
        "check_noema_nehma_distinction",
        "check_lifeworld_presupposition",
        "check_bracketing_reduction_valid",
        "check_epoche_completeness_fraction",
    ],
}
