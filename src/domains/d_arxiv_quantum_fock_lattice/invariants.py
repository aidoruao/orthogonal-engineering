"""Invariant checks for d_arxiv_quantum_fock_lattice."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumFockLatticeClaim, create_nominal_claim


def check_lattice_structure(data: QuantumFockLatticeClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: has_lattice_structure must be True.

    Standard: arXiv 2604.09341v1 (quant-ph) claim operationalization.
    Falsifies if: Fock space does not have lattice structure.
    falsifies_if: not has_lattice_structure.

    Returns:
        Tuple of (success, proof).
    """
    success = data.has_lattice_structure is True
    proof = ProofObject(
        rule="check_lattice_structure",
        premises=[
            "paper_id=2604.09341v1",
            f"has_lattice_structure={data.has_lattice_structure}",
        ],
        conclusion=(
            "PASS: has_lattice_structure is True"
            if success else "FAIL: has_lattice_structure is not True"
        ),
    )
    return success, proof


def check_distributivity(data: QuantumFockLatticeClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: is_distributive must be True.

    Standard: arXiv 2604.09341v1 (quant-ph) claim operationalization.
    Falsifies if: Lattice is not distributive.
    falsifies_if: not is_distributive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_distributive is True
    proof = ProofObject(
        rule="check_distributivity",
        premises=[
            "paper_id=2604.09341v1",
            f"is_distributive={data.is_distributive}",
        ],
        conclusion=(
            "PASS: is_distributive is True"
            if success else "FAIL: is_distributive is not True"
        ),
    )
    return success, proof


def check_mode_count_positive(data: QuantumFockLatticeClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: mode_count must be at least 1.

    Standard: arXiv 2604.09341v1 (quant-ph) claim operationalization.
    Falsifies if: Mode count is less than 1.
    falsifies_if: mode_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.mode_count >= Fraction(1)
    proof = ProofObject(
        rule="check_mode_count_positive",
        premises=[
            "paper_id=2604.09341v1",
            f"mode_count={data.mode_count}",
        ],
        conclusion=(
            "PASS: mode_count >= 1"
            if success else "FAIL: mode_count is less than 1"
        ),
    )
    return success, proof


def check_photon_number_nonnegative(data: QuantumFockLatticeClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: max_photon_number must be nonnegative.

    Standard: arXiv 2604.09341v1 (quant-ph) claim operationalization.
    Falsifies if: Max photon number is negative.
    falsifies_if: max_photon_number < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.max_photon_number >= Fraction(0)
    proof = ProofObject(
        rule="check_photon_number_nonnegative",
        premises=[
            "paper_id=2604.09341v1",
            f"max_photon_number={data.max_photon_number}",
        ],
        conclusion=(
            "PASS: max_photon_number >= 0"
            if success else "FAIL: max_photon_number is negative"
        ),
    )
    return success, proof


def check_lattice_size_valid(data: QuantumFockLatticeClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: lattice_element_count must be at least 1.

    Standard: arXiv 2604.09341v1 (quant-ph) claim operationalization.
    Falsifies if: Lattice element count is less than 1.
    falsifies_if: lattice_element_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.lattice_element_count >= Fraction(1)
    proof = ProofObject(
        rule="check_lattice_size_valid",
        premises=[
            "paper_id=2604.09341v1",
            f"lattice_element_count={data.lattice_element_count}",
        ],
        conclusion=(
            "PASS: lattice_element_count >= 1"
            if success else "FAIL: lattice_element_count is less than 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09341v1 (quant-ph) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_lattice_structure", check_lattice_structure),
        ("check_distributivity", check_distributivity),
        ("check_mode_count_positive", check_mode_count_positive),
        ("check_photon_number_nonnegative", check_photon_number_nonnegative),
        ("check_lattice_size_valid", check_lattice_size_valid),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
