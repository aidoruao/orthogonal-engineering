"""Invariant checks for d_arxiv_quantum_ergodic_process."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumErgodicProcessClaim, create_nominal_claim


def check_ergodicity(data: QuantumErgodicProcessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: is_ergodic must be True.

    Standard: arXiv 2604.09422v1 (quant-ph) claim operationalization.
    Falsifies if: Process is not ergodic.
    falsifies_if: not is_ergodic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_ergodic is True
    proof = ProofObject(
        rule="check_ergodicity",
        premises=[
            "paper_id=2604.09422v1",
            f"is_ergodic={data.is_ergodic}",
        ],
        conclusion=(
            "PASS: is_ergodic is True"
            if success else "FAIL: is_ergodic is not True"
        ),
    )
    return success, proof


def check_period_positive(data: QuantumErgodicProcessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: period must be at least 1.

    Standard: arXiv 2604.09422v1 (quant-ph) claim operationalization.
    Falsifies if: Period is less than 1.
    falsifies_if: period < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.period >= Fraction(1)
    proof = ProofObject(
        rule="check_period_positive",
        premises=[
            "paper_id=2604.09422v1",
            f"period={data.period}",
        ],
        conclusion=(
            "PASS: period >= 1"
            if success else "FAIL: period is less than 1"
        ),
    )
    return success, proof


def check_convergence_rate_valid(data: QuantumErgodicProcessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: convergence_rate must satisfy 0 < convergence_rate <= 1.

    Standard: arXiv 2604.09422v1 (quant-ph) claim operationalization.
    Falsifies if: Convergence rate is out of valid range.
    falsifies_if: convergence_rate <= 0 or convergence_rate > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.convergence_rate <= Fraction(1)
    proof = ProofObject(
        rule="check_convergence_rate_valid",
        premises=[
            "paper_id=2604.09422v1",
            f"convergence_rate={data.convergence_rate}",
        ],
        conclusion=(
            "PASS: convergence_rate in (0, 1]"
            if success else "FAIL: convergence_rate out of valid range"
        ),
    )
    return success, proof


def check_dimension_valid(data: QuantumErgodicProcessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: hilbert_space_dimension must be at least 2.

    Standard: arXiv 2604.09422v1 (quant-ph) claim operationalization.
    Falsifies if: Hilbert space dimension is less than 2.
    falsifies_if: hilbert_space_dimension < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.hilbert_space_dimension >= Fraction(2)
    proof = ProofObject(
        rule="check_dimension_valid",
        premises=[
            "paper_id=2604.09422v1",
            f"hilbert_space_dimension={data.hilbert_space_dimension}",
        ],
        conclusion=(
            "PASS: hilbert_space_dimension >= 2"
            if success else "FAIL: hilbert_space_dimension is less than 2"
        ),
    )
    return success, proof


def check_periodicity_flag(data: QuantumErgodicProcessClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: is_periodic must be True.

    Standard: arXiv 2604.09422v1 (quant-ph) claim operationalization.
    Falsifies if: Process is not periodic.
    falsifies_if: not is_periodic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_periodic is True
    proof = ProofObject(
        rule="check_periodicity_flag",
        premises=[
            "paper_id=2604.09422v1",
            f"is_periodic={data.is_periodic}",
        ],
        conclusion=(
            "PASS: is_periodic is True"
            if success else "FAIL: is_periodic is not True"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09422v1 (quant-ph) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_ergodicity", check_ergodicity),
        ("check_period_positive", check_period_positive),
        ("check_convergence_rate_valid", check_convergence_rate_valid),
        ("check_dimension_valid", check_dimension_valid),
        ("check_periodicity_flag", check_periodicity_flag),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
