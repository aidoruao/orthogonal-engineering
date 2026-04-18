"""Implementation models for d_arxiv_quantum_block_encoding."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumBlockEncodingClaim:
    """Structured claim parameters derived from arXiv paper 2604.09538v1 (quant-ph)."""

    subnormalization_factor: Fraction
    ancilla_qubit_count: Fraction
    circuit_depth: Fraction
    operator_norm: Fraction
    is_efficient: bool


def create_nominal_claim() -> QuantumBlockEncodingClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumBlockEncodingClaim(
        subnormalization_factor=Fraction(4),
        ancilla_qubit_count=Fraction(6),
        circuit_depth=Fraction(100),
        operator_norm=Fraction(3),
        is_efficient=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_BLOCK_ENCODING",
    "paper_id": "2604.09538v1",
    "claim_model": "QuantumBlockEncodingClaim",
    "check_functions": [
        "check_subnormalization_valid",
        "check_ancilla_count_positive",
        "check_circuit_depth_positive",
        "check_efficiency",
        "check_subnormalization_factor_positive",
    ],
}
