"""Implementation models for d_arxiv_tarskian_truth."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class TarskianTruthClaim:
    """Structured claim parameters derived from arXiv paper 2604.03825v2 (math.LO)."""

    object_theory_consistent: bool
    truth_predicate_consistent: bool
    satisfies_tarski_biconditional: bool
    compositional: bool
    disquotational_axiom_count: Fraction


def create_nominal_claim() -> TarskianTruthClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return TarskianTruthClaim(
        object_theory_consistent=True,
        truth_predicate_consistent=True,
        satisfies_tarski_biconditional=True,
        compositional=True,
        disquotational_axiom_count=Fraction(10),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_TARSKIAN_TRUTH",
    "paper_id": "2604.03825v2",
    "claim_model": "TarskianTruthClaim",
    "check_functions": [
        "check_object_theory_consistency",
        "check_truth_predicate_consistency",
        "check_tarski_biconditional",
        "check_compositionality",
        "check_axiom_count_positive",
    ],
}
