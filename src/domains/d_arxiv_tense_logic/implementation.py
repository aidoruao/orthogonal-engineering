"""Implementation models for d_arxiv_tense_logic."""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class TenseLogicClaim:
    """Structured claim parameters derived from arXiv paper 2603.29424v1 (cs.LO)."""

    sequent_depth: Fraction
    is_intuitionistic: bool
    loop_check_terminates: bool
    counter_model_extracted: bool
    formula_provable: bool


def create_nominal_claim() -> TenseLogicClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return TenseLogicClaim(
        sequent_depth=Fraction(4),
        is_intuitionistic=True,
        loop_check_terminates=True,
        counter_model_extracted=True,
        formula_provable=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_TENSE_LOGIC",
    "paper_id": "2603.29424v1",
    "claim_model": "TenseLogicClaim",
    "check_functions": [
        "check_intuitionistic_base",
        "check_loop_termination",
        "check_counter_model_extraction",
        "check_sequent_depth_positive",
        "check_decidability_via_loop_check",
    ],
}
