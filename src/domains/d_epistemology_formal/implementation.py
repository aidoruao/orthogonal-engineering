"""Implementation models for Formal Epistemology."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class FormalEpistemologyClaim:
    """Structured claim parameters for Formal Epistemology domain invariants."""

    belief_set_consistent: bool
    knowledge_factiveness: bool
    justification_non_circular: bool
    credence_normal: bool
    prior_probability: Fraction
    credence: Fraction
    observed_frequency: Fraction


def create_nominal_claim() -> FormalEpistemologyClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return FormalEpistemologyClaim(
        belief_set_consistent=True,
        knowledge_factiveness=True,
        justification_non_circular=True,
        credence_normal=True,
        prior_probability=Fraction(1),
        credence=Fraction(7, 10),
        observed_frequency=Fraction(7, 10),
    )


DOMAIN_METADATA = {
    "id": "FORMAL_EPISTEMOLOGY",
    "claim_model": "FormalEpistemologyClaim",
    "check_functions": [
        "check_belief_set_consistent",
        "check_knowledge_factiveness",
        "check_justification_non_circular",
        "check_credence_normality",
        "check_prior_probability_fraction",
    ],
}
