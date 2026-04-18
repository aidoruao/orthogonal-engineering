"""Implementation models for Probability Theory."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ProbabilityTheoryClaim:
    """Structured claim parameters for Probability Theory domain invariants."""

    probability_non_negative: bool
    total_probability_unity: bool
    conditional_probability_bounded: bool
    independence_symmetric: bool
    expectation_linearity: Fraction


def create_nominal_claim() -> ProbabilityTheoryClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ProbabilityTheoryClaim(
        probability_non_negative=True,
        total_probability_unity=True,
        conditional_probability_bounded=True,
        independence_symmetric=True,
        expectation_linearity=Fraction(1),
    )


DOMAIN_METADATA = {
    "id": "PROBABILITY_THEORY",
    "claim_model": "ProbabilityTheoryClaim",
    "check_functions": [
        "check_probability_measure_non_negative",
        "check_total_probability_unity",
        "check_conditional_probability_bounded",
        "check_independence_symmetric",
        "check_expectation_linear_fraction",
    ],
}
