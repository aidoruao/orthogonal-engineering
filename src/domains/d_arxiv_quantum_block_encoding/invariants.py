"""Invariant checks for d_arxiv_quantum_block_encoding."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumBlockEncodingClaim, create_nominal_claim


def check_subnormalization_valid(data: QuantumBlockEncodingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: operator_norm must not exceed subnormalization_factor.

    Standard: arXiv 2604.09538v1 (quant-ph) claim operationalization.
    Falsifies if: Operator norm exceeds subnormalization factor.
    falsifies_if: operator_norm > subnormalization_factor.

    Returns:
        Tuple of (success, proof).
    """
    success = data.operator_norm <= data.subnormalization_factor
    proof = ProofObject(
        rule="check_subnormalization_valid",
        premises=[
            "paper_id=2604.09538v1",
            f"operator_norm={data.operator_norm}",
            f"subnormalization_factor={data.subnormalization_factor}",
        ],
        conclusion=(
            "PASS: operator_norm <= subnormalization_factor"
            if success else "FAIL: operator_norm exceeds subnormalization_factor"
        ),
    )
    return success, proof


def check_ancilla_count_positive(data: QuantumBlockEncodingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: ancilla_qubit_count must be at least 1.

    Standard: arXiv 2604.09538v1 (quant-ph) claim operationalization.
    Falsifies if: Ancilla qubit count is less than 1.
    falsifies_if: ancilla_qubit_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ancilla_qubit_count >= Fraction(1)
    proof = ProofObject(
        rule="check_ancilla_count_positive",
        premises=[
            "paper_id=2604.09538v1",
            f"ancilla_qubit_count={data.ancilla_qubit_count}",
        ],
        conclusion=(
            "PASS: ancilla_qubit_count >= 1"
            if success else "FAIL: ancilla_qubit_count is less than 1"
        ),
    )
    return success, proof


def check_circuit_depth_positive(data: QuantumBlockEncodingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: circuit_depth must be at least 1.

    Standard: arXiv 2604.09538v1 (quant-ph) claim operationalization.
    Falsifies if: Circuit depth is less than 1.
    falsifies_if: circuit_depth < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.circuit_depth >= Fraction(1)
    proof = ProofObject(
        rule="check_circuit_depth_positive",
        premises=[
            "paper_id=2604.09538v1",
            f"circuit_depth={data.circuit_depth}",
        ],
        conclusion=(
            "PASS: circuit_depth >= 1"
            if success else "FAIL: circuit_depth is less than 1"
        ),
    )
    return success, proof


def check_efficiency(data: QuantumBlockEncodingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: is_efficient must be True.

    Standard: arXiv 2604.09538v1 (quant-ph) claim operationalization.
    Falsifies if: Encoding is not efficient.
    falsifies_if: not is_efficient.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_efficient is True
    proof = ProofObject(
        rule="check_efficiency",
        premises=[
            "paper_id=2604.09538v1",
            f"is_efficient={data.is_efficient}",
        ],
        conclusion=(
            "PASS: is_efficient is True"
            if success else "FAIL: is_efficient is not True"
        ),
    )
    return success, proof


def check_subnormalization_factor_positive(data: QuantumBlockEncodingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: subnormalization_factor must be positive.

    Standard: arXiv 2604.09538v1 (quant-ph) claim operationalization.
    Falsifies if: Subnormalization factor is not positive.
    falsifies_if: subnormalization_factor <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.subnormalization_factor > Fraction(0)
    proof = ProofObject(
        rule="check_subnormalization_factor_positive",
        premises=[
            "paper_id=2604.09538v1",
            f"subnormalization_factor={data.subnormalization_factor}",
        ],
        conclusion=(
            "PASS: subnormalization_factor > 0"
            if success else "FAIL: subnormalization_factor is not positive"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09538v1 (quant-ph) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_subnormalization_valid", check_subnormalization_valid),
        ("check_ancilla_count_positive", check_ancilla_count_positive),
        ("check_circuit_depth_positive", check_circuit_depth_positive),
        ("check_efficiency", check_efficiency),
        ("check_subnormalization_factor_positive", check_subnormalization_factor_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
