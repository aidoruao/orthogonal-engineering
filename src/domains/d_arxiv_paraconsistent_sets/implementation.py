"""Implementation models for d_arxiv_paraconsistent_sets."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class ParaconsistentSetClaim:
    """Structured claim parameters derived from arXiv paper 2604.07094v1 (math.LO)."""

    set_size: Fraction
    is_paraconsistent: bool
    is_paracomplete: bool
    cardinality_well_defined: bool
    classical_cardinality_extends: bool


def create_nominal_claim() -> ParaconsistentSetClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return ParaconsistentSetClaim(
        set_size=Fraction(10),
        is_paraconsistent=True,
        is_paracomplete=True,
        cardinality_well_defined=True,
        classical_cardinality_extends=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_PARACONSISTENT_SETS",
    "paper_id": "2604.07094v1",
    "claim_model": "ParaconsistentSetClaim",
    "check_functions": [
        "check_paraconsistent_logic",
        "check_cardinality_definition",
        "check_classical_extension",
        "check_set_size_nonnegative",
        "check_paracomplete_consistency",
    ],
}
