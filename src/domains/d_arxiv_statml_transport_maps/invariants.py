"""Invariant checks for d_arxiv_statml_transport_maps."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import TransportMapClaim, create_nominal_claim


def check_unique_recovery(data: TransportMapClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Transport map is uniquely recoverable from finite data.

    Standard: arXiv 2604.07671v1 (stat.ML) claim operationalization.
    Falsifies if: not is_uniquely_recoverable.
    falsifies_if: not is_uniquely_recoverable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_uniquely_recoverable is True
    proof = ProofObject(
        rule="check_unique_recovery",
        premises=[
            f"paper_id=2604.07671v1",
            f'is_uniquely_recoverable={data.is_uniquely_recoverable}',
        ],
        conclusion=(
            "PASS: transport map is uniquely recoverable from finite data"
            if success else "FAIL: not is_uniquely_recoverable"
        ),
    )
    return success, proof



def check_transport_cost_nonnegative(data: TransportMapClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Transport cost (wasserstein distance) is non-negative.

    Standard: arXiv 2604.07671v1 (stat.ML) claim operationalization.
    Falsifies if: transport_cost < 0.
    falsifies_if: transport_cost < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.transport_cost >= Fraction(0)
    proof = ProofObject(
        rule="check_transport_cost_nonnegative",
        premises=[
            f"paper_id=2604.07671v1",
            f'transport_cost={data.transport_cost}',
        ],
        conclusion=(
            "PASS: transport cost (Wasserstein distance) is non-negative"
            if success else "FAIL: transport_cost < 0"
        ),
    )
    return success, proof



def check_support_sizes_positive(data: TransportMapClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Source and target measure support sizes are each >= 1.

    Standard: arXiv 2604.07671v1 (stat.ML) claim operationalization.
    Falsifies if: source_measure_support_size < 1 or target_measure_support_size < 1.
    falsifies_if: source_measure_support_size < 1 or target_measure_support_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.source_measure_support_size >= Fraction(1) and data.target_measure_support_size >= Fraction(1)
    proof = ProofObject(
        rule="check_support_sizes_positive",
        premises=[
            f"paper_id=2604.07671v1",
            f'source_measure_support_size={data.source_measure_support_size}',
            f'target_measure_support_size={data.target_measure_support_size}',
        ],
        conclusion=(
            "PASS: source and target measure support sizes are each >= 1"
            if success else "FAIL: source_measure_support_size < 1 or target_measure_support_size < 1"
        ),
    )
    return success, proof



def check_data_sufficient(data: TransportMapClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Data point count is sufficient relative to source support size.

    Standard: arXiv 2604.07671v1 (stat.ML) claim operationalization.
    Falsifies if: data_point_count < source_measure_support_size.
    falsifies_if: data_point_count < source_measure_support_size.

    Returns:
        Tuple of (success, proof).
    """
    success = data.data_point_count >= data.source_measure_support_size
    proof = ProofObject(
        rule="check_data_sufficient",
        premises=[
            f"paper_id=2604.07671v1",
            f'data_point_count={data.data_point_count}',
            f'source_measure_support_size={data.source_measure_support_size}',
        ],
        conclusion=(
            "PASS: data point count is sufficient relative to source support size"
            if success else "FAIL: data_point_count < source_measure_support_size"
        ),
    )
    return success, proof



def check_finite_data(data: TransportMapClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: At least one data point is available.

    Standard: arXiv 2604.07671v1 (stat.ML) claim operationalization.
    Falsifies if: data_point_count < 1.
    falsifies_if: data_point_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.data_point_count >= Fraction(1)
    proof = ProofObject(
        rule="check_finite_data",
        premises=[
            f"paper_id=2604.07671v1",
            f'data_point_count={data.data_point_count}',
        ],
        conclusion=(
            "PASS: at least one data point is available"
            if success else "FAIL: data_point_count < 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07671v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_unique_recovery", check_unique_recovery),
        ("check_transport_cost_nonnegative", check_transport_cost_nonnegative),
        ("check_support_sizes_positive", check_support_sizes_positive),
        ("check_data_sufficient", check_data_sufficient),
        ("check_finite_data", check_finite_data),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
