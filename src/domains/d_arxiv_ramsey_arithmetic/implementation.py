"""Implementation models for d_arxiv_ramsey_arithmetic."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class RamseyArithmeticClaim:
    """Structured claim parameters derived from arXiv paper 2603.23704v2 (math.LO)."""

    coloring_count: Fraction
    vertex_count: Fraction
    ramsey_number: Fraction
    bounding_principle_holds: bool
    provable_in_base_theory: bool


def create_nominal_claim() -> RamseyArithmeticClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return RamseyArithmeticClaim(
        coloring_count=Fraction(2),
        vertex_count=Fraction(6),
        ramsey_number=Fraction(6),
        bounding_principle_holds=True,
        provable_in_base_theory=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_RAMSEY_ARITHMETIC",
    "paper_id": "2603.23704v2",
    "claim_model": "RamseyArithmeticClaim",
    "check_functions": [
        "check_vertex_count_positive",
        "check_coloring_count_positive",
        "check_ramsey_number_valid",
        "check_bounding_principle",
        "check_provability",
    ],
}
