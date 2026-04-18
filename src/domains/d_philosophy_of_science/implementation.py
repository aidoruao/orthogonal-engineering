"""Implementation models for Philosophy of Science."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class PhilosophyOfScienceClaim:
    """Structured claim parameters for Philosophy of Science domain invariants."""

    falsifiability_criterion_met: bool
    reproducibility_mandate_met: bool
    paradigm_commensurable: bool
    underdetermination_bounded: bool
    bayes_factor: Fraction


def create_nominal_claim() -> PhilosophyOfScienceClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return PhilosophyOfScienceClaim(
        falsifiability_criterion_met=True,
        reproducibility_mandate_met=True,
        paradigm_commensurable=True,
        underdetermination_bounded=True,
        bayes_factor=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "PHILOSOPHY_OF_SCIENCE",
    "claim_model": "PhilosophyOfScienceClaim",
    "check_functions": [
        "check_falsifiability_criterion",
        "check_reproducibility_mandate",
        "check_paradigm_incommensurability",
        "check_underdetermination_bounded",
        "check_bayesian_confirmation_fraction",
    ],
}
