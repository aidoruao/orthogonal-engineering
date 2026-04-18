"""Implementation models for d_arxiv_left_distributive."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class LeftDistributiveClaim:
    """Structured claim parameters derived from arXiv paper 2604.08768v1 (math.LO)."""

    element_count: Fraction
    satisfies_left_distributivity: bool
    is_free: bool
    generator_count: Fraction
    word_problem_decidable: bool


def create_nominal_claim() -> LeftDistributiveClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return LeftDistributiveClaim(
        element_count=Fraction(100),
        satisfies_left_distributivity=True,
        is_free=True,
        generator_count=Fraction(2),
        word_problem_decidable=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_LEFT_DISTRIBUTIVE",
    "paper_id": "2604.08768v1",
    "claim_model": "LeftDistributiveClaim",
    "check_functions": [
        "check_left_distributivity",
        "check_freeness",
        "check_generator_count_positive",
        "check_word_problem_decidability",
        "check_algebra_size_positive",
    ],
}
