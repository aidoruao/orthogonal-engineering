"""Invariant checks for d_arxiv_quantum_randomized_subspace."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumRandomizedSubspaceClaim, create_nominal_claim


def check_subspace_dimension_valid(data: QuantumRandomizedSubspaceClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: subspace_dimension must satisfy 1 <= subspace_dimension <= ambient_dimension.

    Standard: arXiv 2604.09483v1 (quant-ph) claim operationalization.
    Falsifies if: Subspace dimension is out of valid range.
    falsifies_if: subspace_dimension < 1 or subspace_dimension > ambient_dimension.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(1) <= data.subspace_dimension <= data.ambient_dimension
    proof = ProofObject(
        rule="check_subspace_dimension_valid",
        premises=[
            "paper_id=2604.09483v1",
            f"subspace_dimension={data.subspace_dimension}",
            f"ambient_dimension={data.ambient_dimension}",
        ],
        conclusion=(
            "PASS: subspace_dimension in [1, ambient_dimension]"
            if success else "FAIL: subspace_dimension out of valid range"
        ),
    )
    return success, proof


def check_spectral_gap_positive(data: QuantumRandomizedSubspaceClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: spectral_gap must be positive.

    Standard: arXiv 2604.09483v1 (quant-ph) claim operationalization.
    Falsifies if: Spectral gap is not positive.
    falsifies_if: spectral_gap <= 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.spectral_gap > Fraction(0)
    proof = ProofObject(
        rule="check_spectral_gap_positive",
        premises=[
            "paper_id=2604.09483v1",
            f"spectral_gap={data.spectral_gap}",
        ],
        conclusion=(
            "PASS: spectral_gap > 0"
            if success else "FAIL: spectral_gap is not positive"
        ),
    )
    return success, proof


def check_iteration_count_positive(data: QuantumRandomizedSubspaceClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: iteration_count must be at least 1.

    Standard: arXiv 2604.09483v1 (quant-ph) claim operationalization.
    Falsifies if: Iteration count is less than 1.
    falsifies_if: iteration_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.iteration_count >= Fraction(1)
    proof = ProofObject(
        rule="check_iteration_count_positive",
        premises=[
            "paper_id=2604.09483v1",
            f"iteration_count={data.iteration_count}",
        ],
        conclusion=(
            "PASS: iteration_count >= 1"
            if success else "FAIL: iteration_count is less than 1"
        ),
    )
    return success, proof


def check_approximation_error_nonnegative(data: QuantumRandomizedSubspaceClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: approximation_error must be nonnegative.

    Standard: arXiv 2604.09483v1 (quant-ph) claim operationalization.
    Falsifies if: Approximation error is negative.
    falsifies_if: approximation_error < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.approximation_error >= Fraction(0)
    proof = ProofObject(
        rule="check_approximation_error_nonnegative",
        premises=[
            "paper_id=2604.09483v1",
            f"approximation_error={data.approximation_error}",
        ],
        conclusion=(
            "PASS: approximation_error >= 0"
            if success else "FAIL: approximation_error is negative"
        ),
    )
    return success, proof


def check_ambient_dimension_positive(data: QuantumRandomizedSubspaceClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: ambient_dimension must be at least 1.

    Standard: arXiv 2604.09483v1 (quant-ph) claim operationalization.
    Falsifies if: Ambient dimension is less than 1.
    falsifies_if: ambient_dimension < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.ambient_dimension >= Fraction(1)
    proof = ProofObject(
        rule="check_ambient_dimension_positive",
        premises=[
            "paper_id=2604.09483v1",
            f"ambient_dimension={data.ambient_dimension}",
        ],
        conclusion=(
            "PASS: ambient_dimension >= 1"
            if success else "FAIL: ambient_dimension is less than 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09483v1 (quant-ph) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_subspace_dimension_valid", check_subspace_dimension_valid),
        ("check_spectral_gap_positive", check_spectral_gap_positive),
        ("check_iteration_count_positive", check_iteration_count_positive),
        ("check_approximation_error_nonnegative", check_approximation_error_nonnegative),
        ("check_ambient_dimension_positive", check_ambient_dimension_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
