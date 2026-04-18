"""Implementation models for d_arxiv_disjunction_failure."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class DisjunctionFailureClaim:
    """Structured claim parameters derived from arXiv paper 2604.04830v1 (math.LO)."""

    theory_has_disjunction_property: bool
    counterexample_exists: bool
    theory_is_consistent: bool
    disjunct_count: Fraction
    provability_witness_exists: bool


def create_nominal_claim() -> DisjunctionFailureClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return DisjunctionFailureClaim(
        theory_has_disjunction_property=False,
        counterexample_exists=True,
        theory_is_consistent=True,
        disjunct_count=Fraction(2),
        provability_witness_exists=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_DISJUNCTION_FAILURE",
    "paper_id": "2604.04830v1",
    "claim_model": "DisjunctionFailureClaim",
    "check_functions": [
        "check_theory_consistency",
        "check_counterexample_witness",
        "check_disjunction_property_failure",
        "check_disjunct_count_positive",
        "check_provability_witness",
    ],
}
