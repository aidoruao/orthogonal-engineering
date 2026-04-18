"""Implementation models for d_arxiv_goodstein."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class GoodsteinClaim:
    """Structured claim parameters derived from arXiv paper 2603.19981v1 (math.LO)."""

    sequence_length: Fraction
    base_reached: Fraction
    terminates: bool
    requires_transfinite_induction: bool
    peano_cannot_prove: bool


def create_nominal_claim() -> GoodsteinClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return GoodsteinClaim(
        sequence_length=Fraction(100),
        base_reached=Fraction(3),
        terminates=True,
        requires_transfinite_induction=True,
        peano_cannot_prove=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_GOODSTEIN",
    "paper_id": "2603.19981v1",
    "claim_model": "GoodsteinClaim",
    "check_functions": [
        "check_termination",
        "check_transfinite_required",
        "check_sequence_length_positive",
        "check_base_positive",
        "check_unprovable_in_peano",
    ],
}
