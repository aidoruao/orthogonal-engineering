"""Implementation models for d_arxiv_quantum_fock_lattice."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumFockLatticeClaim:
    """Structured claim parameters derived from arXiv paper 2604.09341v1 (quant-ph)."""

    mode_count: Fraction
    max_photon_number: Fraction
    lattice_element_count: Fraction
    has_lattice_structure: bool
    is_distributive: bool


def create_nominal_claim() -> QuantumFockLatticeClaim:
    """Create nominal claim data used by run_all_invariants().

    Falsifies if: nominal claim data cannot be constructed.
    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumFockLatticeClaim(
        mode_count=Fraction(2),
        max_photon_number=Fraction(5),
        lattice_element_count=Fraction(36),
        has_lattice_structure=True,
        is_distributive=True,
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_FOCK_LATTICE",
    "paper_id": "2604.09341v1",
    "claim_model": "QuantumFockLatticeClaim",
    "check_functions": [
        "check_lattice_structure",
        "check_distributivity",
        "check_mode_count_positive",
        "check_photon_number_nonnegative",
        "check_lattice_size_valid",
    ],
}
