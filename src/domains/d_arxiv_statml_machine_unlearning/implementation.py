"""Implementation models for d_arxiv_statml_machine_unlearning."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class MachineUnlearningClaim:
    """Structured claim parameters derived from arXiv paper 2604.05669v1 (stat.ML)."""

    forget_set_size: Fraction
    total_dataset_size: Fraction
    unlearning_error: Fraction
    computational_overhead: Fraction
    is_minimax_optimal: bool


def create_nominal_claim() -> MachineUnlearningClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return MachineUnlearningClaim(
        forget_set_size=Fraction(10),
        total_dataset_size=Fraction(1000),
        unlearning_error=Fraction(1, 100),
        computational_overhead=Fraction(1, 10),
        is_minimax_optimal=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_STATML_MACHINE_UNLEARNING",
    "paper_id": "2604.05669v1",
    "claim_model": "MachineUnlearningClaim",
    "check_functions": [
        "check_minimax_optimality",
        "check_unlearning_error_valid",
        "check_forget_set_valid",
        "check_computational_efficiency",
        "check_dataset_size_positive",
    ],
}
