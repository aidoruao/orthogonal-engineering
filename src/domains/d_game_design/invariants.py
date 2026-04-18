"""Invariant checks for Game Design."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import GameDesignClaim, create_nominal_claim


def check_core_loop_engagement(data: GameDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Core gameplay loop is engaging.

    Standard: Game Design domain invariant.
    Falsifies if: not core_loop_engaging.
    falsifies_if: not core_loop_engaging.

    Returns:
        Tuple of (success, proof).
    """
    success = data.core_loop_engaging
    proof = ProofObject(
        rule="check_core_loop_engagement",
        premises=[
            "domain=Game Design",
            f"core_loop_engaging={{data.core_loop_engaging}}",
        ],
        conclusion=(
            "PASS: Core gameplay loop is engaging"
            if success else "FAIL: Core gameplay loop is engaging"
        ),
    )
    return success, proof


def check_progression_curve_monotonic(data: GameDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Progression curve is monotonic.

    Standard: Game Design domain invariant.
    Falsifies if: not progression_monotonic.
    falsifies_if: not progression_monotonic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.progression_monotonic
    proof = ProofObject(
        rule="check_progression_curve_monotonic",
        premises=[
            "domain=Game Design",
            f"progression_monotonic={{data.progression_monotonic}}",
        ],
        conclusion=(
            "PASS: Progression curve is monotonic"
            if success else "FAIL: Progression curve is monotonic"
        ),
    )
    return success, proof


def check_balance_fairness_symmetric(data: GameDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Game balance is fair and symmetric.

    Standard: Game Design domain invariant.
    Falsifies if: not balance_fair_symmetric.
    falsifies_if: not balance_fair_symmetric.

    Returns:
        Tuple of (success, proof).
    """
    success = data.balance_fair_symmetric
    proof = ProofObject(
        rule="check_balance_fairness_symmetric",
        premises=[
            "domain=Game Design",
            f"balance_fair_symmetric={{data.balance_fair_symmetric}}",
        ],
        conclusion=(
            "PASS: Game balance is fair and symmetric"
            if success else "FAIL: Game balance is fair and symmetric"
        ),
    )
    return success, proof


def check_feedback_immediacy(data: GameDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Player feedback is immediate.

    Standard: Game Design domain invariant.
    Falsifies if: not feedback_immediate.
    falsifies_if: not feedback_immediate.

    Returns:
        Tuple of (success, proof).
    """
    success = data.feedback_immediate
    proof = ProofObject(
        rule="check_feedback_immediacy",
        premises=[
            "domain=Game Design",
            f"feedback_immediate={{data.feedback_immediate}}",
        ],
        conclusion=(
            "PASS: Player feedback is immediate"
            if success else "FAIL: Player feedback is immediate"
        ),
    )
    return success, proof


def check_difficulty_slope_fraction(data: GameDesignClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Difficulty slope is non-negative.

    Standard: Game Design domain invariant.
    Falsifies if: not difficulty_slope.
    falsifies_if: not difficulty_slope.

    Returns:
        Tuple of (success, proof).
    """
    success = data.difficulty_slope >= Fraction(0)
    proof = ProofObject(
        rule="check_difficulty_slope_fraction",
        premises=[
            "domain=Game Design",
            f"difficulty_slope={{data.difficulty_slope}}",
        ],
        conclusion=(
            "PASS: Difficulty slope is non-negative is non-negative"
            if success else "FAIL: Difficulty slope is non-negative is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Game Design nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_core_loop_engagement", check_core_loop_engagement),
        ("check_progression_curve_monotonic", check_progression_curve_monotonic),
        ("check_balance_fairness_symmetric", check_balance_fairness_symmetric),
        ("check_feedback_immediacy", check_feedback_immediacy),
        ("check_difficulty_slope_fraction", check_difficulty_slope_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
