"""Invariant checks for d_arxiv_quantum_uncertainty_entropy."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumUncertaintyEntropyClaim, create_nominal_claim


def check_von_neumann_nonnegative(data: QuantumUncertaintyEntropyClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: von_neumann_entropy must be nonnegative.

    Standard: arXiv 2604.09384v1 (quant-ph) claim operationalization.
    Falsifies if: Von Neumann entropy is negative.
    falsifies_if: von_neumann_entropy < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.von_neumann_entropy >= Fraction(0)
    proof = ProofObject(
        rule="check_von_neumann_nonnegative",
        premises=[
            "paper_id=2604.09384v1",
            f"von_neumann_entropy={data.von_neumann_entropy}",
        ],
        conclusion=(
            "PASS: von_neumann_entropy is nonnegative"
            if success else "FAIL: von_neumann_entropy is negative"
        ),
    )
    return success, proof


def check_purity_valid(data: QuantumUncertaintyEntropyClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: purity must satisfy 0 < purity <= 1.

    Standard: arXiv 2604.09384v1 (quant-ph) claim operationalization.
    Falsifies if: Purity is out of valid range.
    falsifies_if: purity <= 0 or purity > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.purity <= Fraction(1)
    proof = ProofObject(
        rule="check_purity_valid",
        premises=[
            "paper_id=2604.09384v1",
            f"purity={data.purity}",
        ],
        conclusion=(
            "PASS: purity is in valid range (0, 1]"
            if success else "FAIL: purity is out of valid range"
        ),
    )
    return success, proof


def check_entropy_purity_tradeoff(data: QuantumUncertaintyEntropyClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: von_neumann_entropy must not exceed dimension.

    Standard: arXiv 2604.09384v1 (quant-ph) claim operationalization.
    Falsifies if: Von Neumann entropy exceeds system dimension.
    falsifies_if: von_neumann_entropy > dimension.

    Returns:
        Tuple of (success, proof).
    """
    success = data.von_neumann_entropy <= data.dimension
    proof = ProofObject(
        rule="check_entropy_purity_tradeoff",
        premises=[
            "paper_id=2604.09384v1",
            f"von_neumann_entropy={data.von_neumann_entropy}",
            f"dimension={data.dimension}",
        ],
        conclusion=(
            "PASS: von_neumann_entropy <= dimension"
            if success else "FAIL: von_neumann_entropy exceeds dimension"
        ),
    )
    return success, proof


def check_min_entropy_nonnegative(data: QuantumUncertaintyEntropyClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: min_entropy must be nonnegative.

    Standard: arXiv 2604.09384v1 (quant-ph) claim operationalization.
    Falsifies if: Min entropy is negative.
    falsifies_if: min_entropy < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.min_entropy >= Fraction(0)
    proof = ProofObject(
        rule="check_min_entropy_nonnegative",
        premises=[
            "paper_id=2604.09384v1",
            f"min_entropy={data.min_entropy}",
        ],
        conclusion=(
            "PASS: min_entropy is nonnegative"
            if success else "FAIL: min_entropy is negative"
        ),
    )
    return success, proof


def check_uncertainty_lower_bound(data: QuantumUncertaintyEntropyClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: uncertainty_lower_bound must be nonnegative.

    Standard: arXiv 2604.09384v1 (quant-ph) claim operationalization.
    Falsifies if: Uncertainty lower bound is negative.
    falsifies_if: uncertainty_lower_bound < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.uncertainty_lower_bound >= Fraction(0)
    proof = ProofObject(
        rule="check_uncertainty_lower_bound",
        premises=[
            "paper_id=2604.09384v1",
            f"uncertainty_lower_bound={data.uncertainty_lower_bound}",
        ],
        conclusion=(
            "PASS: uncertainty_lower_bound is nonnegative"
            if success else "FAIL: uncertainty_lower_bound is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09384v1 (quant-ph) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_von_neumann_nonnegative", check_von_neumann_nonnegative),
        ("check_purity_valid", check_purity_valid),
        ("check_entropy_purity_tradeoff", check_entropy_purity_tradeoff),
        ("check_min_entropy_nonnegative", check_min_entropy_nonnegative),
        ("check_uncertainty_lower_bound", check_uncertainty_lower_bound),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
