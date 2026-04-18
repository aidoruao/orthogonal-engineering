"""Invariant checks for d_arxiv_quantum_error_correction_gkp."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumGKPErrorCorrectionClaim, create_nominal_claim


def check_error_rate_suppression(data: QuantumGKPErrorCorrectionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: if preprocessing_applied then logical_error_rate < physical_error_rate.

    Standard: arXiv 2604.08247v1 (quant-ph) claim operationalization.
    Falsifies if: Preprocessing applied but logical error rate not below physical.
    falsifies_if: preprocessing_applied and logical_error_rate >= physical_error_rate.

    Returns:
        Tuple of (success, proof).
    """
    if data.preprocessing_applied:
        success = data.logical_error_rate < data.physical_error_rate
    else:
        success = True
    proof = ProofObject(
        rule="check_error_rate_suppression",
        premises=[
            "paper_id=2604.08247v1",
            f"preprocessing_applied={data.preprocessing_applied}",
            f"logical_error_rate={data.logical_error_rate}",
            f"physical_error_rate={data.physical_error_rate}",
        ],
        conclusion=(
            "PASS: error rate suppression condition satisfied"
            if success else "FAIL: logical_error_rate >= physical_error_rate with preprocessing"
        ),
    )
    return success, proof


def check_squeezing_nonnegative(data: QuantumGKPErrorCorrectionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: squeezing_db must be nonnegative.

    Standard: arXiv 2604.08247v1 (quant-ph) claim operationalization.
    Falsifies if: Squeezing value is negative.
    falsifies_if: squeezing_db < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.squeezing_db >= Fraction(0)
    proof = ProofObject(
        rule="check_squeezing_nonnegative",
        premises=[
            "paper_id=2604.08247v1",
            f"squeezing_db={data.squeezing_db}",
        ],
        conclusion=(
            "PASS: squeezing_db >= 0"
            if success else "FAIL: squeezing_db is negative"
        ),
    )
    return success, proof


def check_physical_error_rate_valid(data: QuantumGKPErrorCorrectionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: physical_error_rate must satisfy 0 <= value <= 1.

    Standard: arXiv 2604.08247v1 (quant-ph) claim operationalization.
    Falsifies if: Physical error rate is outside [0, 1].
    falsifies_if: physical_error_rate < 0 or physical_error_rate > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.physical_error_rate <= Fraction(1)
    proof = ProofObject(
        rule="check_physical_error_rate_valid",
        premises=[
            "paper_id=2604.08247v1",
            f"physical_error_rate={data.physical_error_rate}",
        ],
        conclusion=(
            "PASS: physical_error_rate in [0, 1]"
            if success else "FAIL: physical_error_rate outside [0, 1]"
        ),
    )
    return success, proof


def check_logical_error_rate_valid(data: QuantumGKPErrorCorrectionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: logical_error_rate must satisfy 0 <= value <= 1.

    Standard: arXiv 2604.08247v1 (quant-ph) claim operationalization.
    Falsifies if: Logical error rate is outside [0, 1].
    falsifies_if: logical_error_rate < 0 or logical_error_rate > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.logical_error_rate <= Fraction(1)
    proof = ProofObject(
        rule="check_logical_error_rate_valid",
        premises=[
            "paper_id=2604.08247v1",
            f"logical_error_rate={data.logical_error_rate}",
        ],
        conclusion=(
            "PASS: logical_error_rate in [0, 1]"
            if success else "FAIL: logical_error_rate outside [0, 1]"
        ),
    )
    return success, proof


def check_code_distance_positive(data: QuantumGKPErrorCorrectionClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: code_distance must be at least 1.

    Standard: arXiv 2604.08247v1 (quant-ph) claim operationalization.
    Falsifies if: Code distance is less than 1.
    falsifies_if: code_distance < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.code_distance >= Fraction(1)
    proof = ProofObject(
        rule="check_code_distance_positive",
        premises=[
            "paper_id=2604.08247v1",
            f"code_distance={data.code_distance}",
        ],
        conclusion=(
            "PASS: code_distance >= 1"
            if success else "FAIL: code_distance is less than 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.08247v1 (quant-ph) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_error_rate_suppression", check_error_rate_suppression),
        ("check_squeezing_nonnegative", check_squeezing_nonnegative),
        ("check_physical_error_rate_valid", check_physical_error_rate_valid),
        ("check_logical_error_rate_valid", check_logical_error_rate_valid),
        ("check_code_distance_positive", check_code_distance_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
