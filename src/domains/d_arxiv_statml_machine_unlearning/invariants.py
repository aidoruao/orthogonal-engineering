"""Invariant checks for d_arxiv_statml_machine_unlearning."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import MachineUnlearningClaim, create_nominal_claim


def check_minimax_optimality(data: MachineUnlearningClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Unlearning achieves minimax optimal rate.

    Standard: arXiv 2604.05669v1 (stat.ML) claim operationalization.
    Falsifies if: not is_minimax_optimal.
    falsifies_if: not is_minimax_optimal.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_minimax_optimal is True
    proof = ProofObject(
        rule="check_minimax_optimality",
        premises=[
            f"paper_id=2604.05669v1",
            f'is_minimax_optimal={data.is_minimax_optimal}',
        ],
        conclusion=(
            "PASS: unlearning achieves minimax optimal rate"
            if success else "FAIL: not is_minimax_optimal"
        ),
    )
    return success, proof



def check_unlearning_error_valid(data: MachineUnlearningClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Unlearning error is in [0, 1].

    Standard: arXiv 2604.05669v1 (stat.ML) claim operationalization.
    Falsifies if: unlearning_error < 0 or unlearning_error > 1.
    falsifies_if: unlearning_error < 0 or unlearning_error > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.unlearning_error <= Fraction(1)
    proof = ProofObject(
        rule="check_unlearning_error_valid",
        premises=[
            f"paper_id=2604.05669v1",
            f'unlearning_error={data.unlearning_error}',
        ],
        conclusion=(
            "PASS: unlearning error is in [0, 1]"
            if success else "FAIL: unlearning_error < 0 or unlearning_error > 1"
        ),
    )
    return success, proof



def check_forget_set_valid(data: MachineUnlearningClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Forget set size is in [1, total_dataset_size].

    Standard: arXiv 2604.05669v1 (stat.ML) claim operationalization.
    Falsifies if: forget_set_size < 1 or forget_set_size > total_dataset_size.
    falsifies_if: forget_set_size < 1 or forget_set_size > total_dataset_size.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(1) <= data.forget_set_size <= data.total_dataset_size
    proof = ProofObject(
        rule="check_forget_set_valid",
        premises=[
            f"paper_id=2604.05669v1",
            f'forget_set_size={data.forget_set_size}',
            f'total_dataset_size={data.total_dataset_size}',
        ],
        conclusion=(
            "PASS: forget set size is in [1, total_dataset_size]"
            if success else "FAIL: forget_set_size < 1 or forget_set_size > total_dataset_size"
        ),
    )
    return success, proof



def check_computational_efficiency(data: MachineUnlearningClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Computational overhead is < 1 (efficient vs full retraining).

    Standard: arXiv 2604.05669v1 (stat.ML) claim operationalization.
    Falsifies if: computational_overhead >= 1.
    falsifies_if: computational_overhead >= 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.computational_overhead < Fraction(1)
    proof = ProofObject(
        rule="check_computational_efficiency",
        premises=[
            f"paper_id=2604.05669v1",
            f'computational_overhead={data.computational_overhead}',
        ],
        conclusion=(
            "PASS: computational overhead is < 1 (efficient vs full retraining)"
            if success else "FAIL: computational_overhead >= 1"
        ),
    )
    return success, proof



def check_dataset_size_positive(data: MachineUnlearningClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Total dataset size is >= 1.

    Standard: arXiv 2604.05669v1 (stat.ML) claim operationalization.
    Falsifies if: total_dataset_size < 1.
    falsifies_if: total_dataset_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.total_dataset_size >= Fraction(1)
    proof = ProofObject(
        rule="check_dataset_size_positive",
        premises=[
            f"paper_id=2604.05669v1",
            f'total_dataset_size={data.total_dataset_size}',
        ],
        conclusion=(
            "PASS: total dataset size is >= 1"
            if success else "FAIL: total_dataset_size < 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.05669v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_minimax_optimality", check_minimax_optimality),
        ("check_unlearning_error_valid", check_unlearning_error_valid),
        ("check_forget_set_valid", check_forget_set_valid),
        ("check_computational_efficiency", check_computational_efficiency),
        ("check_dataset_size_positive", check_dataset_size_positive),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
