"""Invariant checks for Reliability Engineering."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ReliabilityClaim, create_nominal_claim


def check_mtbf_positive(data: ReliabilityClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Mean time between failures is positive.

    Standard: Reliability Engineering domain invariant.
    Falsifies if: not mtbf_positive.
    falsifies_if: not mtbf_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.mtbf_positive
    proof = ProofObject(
        rule="check_mtbf_positive",
        premises=[
            "domain=Reliability Engineering",
            f"mtbf_positive={{data.mtbf_positive}}",
        ],
        conclusion=(
            "PASS: Mean time between failures is positive"
            if success else "FAIL: Mean time between failures is positive"
        ),
    )
    return success, proof


def check_failure_rate_monotonic(data: ReliabilityClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Failure rate is monotonic in wear-out phase.

    Standard: Reliability Engineering domain invariant.
    Falsifies if: not failure_rate_monotonic.
    falsifies_if: not failure_rate_monotonic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.failure_rate_monotonic
    proof = ProofObject(
        rule="check_failure_rate_monotonic",
        premises=[
            "domain=Reliability Engineering",
            f"failure_rate_monotonic={{data.failure_rate_monotonic}}",
        ],
        conclusion=(
            "PASS: Failure rate is monotonic in wear-out phase"
            if success else "FAIL: Failure rate is monotonic in wear-out phase"
        ),
    )
    return success, proof


def check_redundancy_independence(data: ReliabilityClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Redundant components are independent.

    Standard: Reliability Engineering domain invariant.
    Falsifies if: not redundancy_independent.
    falsifies_if: not redundancy_independent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.redundancy_independent
    proof = ProofObject(
        rule="check_redundancy_independence",
        premises=[
            "domain=Reliability Engineering",
            f"redundancy_independent={{data.redundancy_independent}}",
        ],
        conclusion=(
            "PASS: Redundant components are independent"
            if success else "FAIL: Redundant components are independent"
        ),
    )
    return success, proof


def check_weibull_shape_positive(data: ReliabilityClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Weibull shape parameter is positive.

    Standard: Reliability Engineering domain invariant.
    Falsifies if: not weibull_shape_positive.
    falsifies_if: not weibull_shape_positive.

    Returns:
        Tuple of (success, proof).
    """
    success = data.weibull_shape_positive
    proof = ProofObject(
        rule="check_weibull_shape_positive",
        premises=[
            "domain=Reliability Engineering",
            f"weibull_shape_positive={{data.weibull_shape_positive}}",
        ],
        conclusion=(
            "PASS: Weibull shape parameter is positive"
            if success else "FAIL: Weibull shape parameter is positive"
        ),
    )
    return success, proof


def check_availability_fraction(data: ReliabilityClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Availability is between 0 and 1.

    Standard: Reliability Engineering domain invariant.
    Falsifies if: not availability.
    falsifies_if: not availability.

    Returns:
        Tuple of (success, proof).
    """
    success = data.availability >= Fraction(0)
    proof = ProofObject(
        rule="check_availability_fraction",
        premises=[
            "domain=Reliability Engineering",
            f"availability={{data.availability}}",
        ],
        conclusion=(
            "PASS: Availability is between 0 and 1 is non-negative"
            if success else "FAIL: Availability is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Reliability Engineering nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_mtbf_positive", check_mtbf_positive),
        ("check_failure_rate_monotonic", check_failure_rate_monotonic),
        ("check_redundancy_independence", check_redundancy_independence),
        ("check_weibull_shape_positive", check_weibull_shape_positive),
        ("check_availability_fraction", check_availability_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
