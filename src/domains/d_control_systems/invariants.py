"""Invariant checks for Control Systems."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ControlSystemsClaim, create_nominal_claim


def check_stability_lyapunov(data: ControlSystemsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: System is Lyapunov stable.

    Standard: Control Systems domain invariant.
    Falsifies if: not lyapunov_stable.
    falsifies_if: not lyapunov_stable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.lyapunov_stable
    proof = ProofObject(
        rule="check_stability_lyapunov",
        premises=[
            "domain=Control Systems",
            f"lyapunov_stable={{data.lyapunov_stable}}",
        ],
        conclusion=(
            "PASS: System is Lyapunov stable"
            if success else "FAIL: System is Lyapunov stable"
        ),
    )
    return success, proof


def check_controllability_rank(data: ControlSystemsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Controllability matrix has full rank.

    Standard: Control Systems domain invariant.
    Falsifies if: not controllable_full_rank.
    falsifies_if: not controllable_full_rank.

    Returns:
        Tuple of (success, proof).
    """
    success = data.controllable_full_rank
    proof = ProofObject(
        rule="check_controllability_rank",
        premises=[
            "domain=Control Systems",
            f"controllable_full_rank={{data.controllable_full_rank}}",
        ],
        conclusion=(
            "PASS: Controllability matrix has full rank"
            if success else "FAIL: Controllability matrix has full rank"
        ),
    )
    return success, proof


def check_observability_rank(data: ControlSystemsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Observability matrix has full rank.

    Standard: Control Systems domain invariant.
    Falsifies if: not observable_full_rank.
    falsifies_if: not observable_full_rank.

    Returns:
        Tuple of (success, proof).
    """
    success = data.observable_full_rank
    proof = ProofObject(
        rule="check_observability_rank",
        premises=[
            "domain=Control Systems",
            f"observable_full_rank={{data.observable_full_rank}}",
        ],
        conclusion=(
            "PASS: Observability matrix has full rank"
            if success else "FAIL: Observability matrix has full rank"
        ),
    )
    return success, proof


def check_settling_time_bounded(data: ControlSystemsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Settling time is bounded.

    Standard: Control Systems domain invariant.
    Falsifies if: not settling_time_bounded.
    falsifies_if: not settling_time_bounded.

    Returns:
        Tuple of (success, proof).
    """
    success = data.settling_time_bounded
    proof = ProofObject(
        rule="check_settling_time_bounded",
        premises=[
            "domain=Control Systems",
            f"settling_time_bounded={{data.settling_time_bounded}}",
        ],
        conclusion=(
            "PASS: Settling time is bounded"
            if success else "FAIL: Settling time is bounded"
        ),
    )
    return success, proof


def check_overshoot_fraction(data: ControlSystemsClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Overshoot percentage is non-negative.

    Standard: Control Systems domain invariant.
    Falsifies if: not overshoot_percent.
    falsifies_if: not overshoot_percent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.overshoot_percent >= Fraction(0)
    proof = ProofObject(
        rule="check_overshoot_fraction",
        premises=[
            "domain=Control Systems",
            f"overshoot_percent={{data.overshoot_percent}}",
        ],
        conclusion=(
            "PASS: Overshoot percentage is non-negative is non-negative"
            if success else "FAIL: Overshoot percentage is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Control Systems nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_stability_lyapunov", check_stability_lyapunov),
        ("check_controllability_rank", check_controllability_rank),
        ("check_observability_rank", check_observability_rank),
        ("check_settling_time_bounded", check_settling_time_bounded),
        ("check_overshoot_fraction", check_overshoot_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
