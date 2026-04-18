"""Invariant checks for Phenomenology."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import PhenomenologyClaim, create_nominal_claim


def check_intentionality_directedness(data: PhenomenologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Intentionality exhibits directedness.

    Standard: Phenomenology domain invariant.
    Falsifies if: not intentionality_directed.
    falsifies_if: not intentionality_directed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.intentionality_directed
    proof = ProofObject(
        rule="check_intentionality_directedness",
        premises=[
            "domain=Phenomenology",
            f"intentionality_directed={{data.intentionality_directed}}",
        ],
        conclusion=(
            "PASS: Intentionality exhibits directedness"
            if success else "FAIL: Intentionality exhibits directedness"
        ),
    )
    return success, proof


def check_noema_nehma_distinction(data: PhenomenologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Noema and nema are distinct.

    Standard: Phenomenology domain invariant.
    Falsifies if: not noema_nema_distinct.
    falsifies_if: not noema_nema_distinct.

    Returns:
        Tuple of (success, proof).
    """
    success = data.noema_nema_distinct
    proof = ProofObject(
        rule="check_noema_nehma_distinction",
        premises=[
            "domain=Phenomenology",
            f"noema_nema_distinct={{data.noema_nema_distinct}}",
        ],
        conclusion=(
            "PASS: Noema and nema are distinct"
            if success else "FAIL: Noema and nema are distinct"
        ),
    )
    return success, proof


def check_lifeworld_presupposition(data: PhenomenologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Lifeworld is presupposed in experience.

    Standard: Phenomenology domain invariant.
    Falsifies if: not lifeworld_presupposed.
    falsifies_if: not lifeworld_presupposed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.lifeworld_presupposed
    proof = ProofObject(
        rule="check_lifeworld_presupposition",
        premises=[
            "domain=Phenomenology",
            f"lifeworld_presupposed={{data.lifeworld_presupposed}}",
        ],
        conclusion=(
            "PASS: Lifeworld is presupposed in experience"
            if success else "FAIL: Lifeworld is presupposed in experience"
        ),
    )
    return success, proof


def check_bracketing_reduction_valid(data: PhenomenologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Phenomenological bracketing is valid.

    Standard: Phenomenology domain invariant.
    Falsifies if: not bracketing_valid.
    falsifies_if: not bracketing_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.bracketing_valid
    proof = ProofObject(
        rule="check_bracketing_reduction_valid",
        premises=[
            "domain=Phenomenology",
            f"bracketing_valid={{data.bracketing_valid}}",
        ],
        conclusion=(
            "PASS: Phenomenological bracketing is valid"
            if success else "FAIL: Phenomenological bracketing is valid"
        ),
    )
    return success, proof


def check_epoche_completeness_fraction(data: PhenomenologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Epoche completeness is between 0 and 1.

    Standard: Phenomenology domain invariant.
    Falsifies if: not epoche_completeness.
    falsifies_if: not epoche_completeness.

    Returns:
        Tuple of (success, proof).
    """
    success = data.epoche_completeness >= Fraction(0)
    proof = ProofObject(
        rule="check_epoche_completeness_fraction",
        premises=[
            "domain=Phenomenology",
            f"epoche_completeness={{data.epoche_completeness}}",
        ],
        conclusion=(
            "PASS: Epoche completeness is between 0 and 1 is non-negative"
            if success else "FAIL: Epoche completeness is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Phenomenology nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_intentionality_directedness", check_intentionality_directedness),
        ("check_noema_nehma_distinction", check_noema_nehma_distinction),
        ("check_lifeworld_presupposition", check_lifeworld_presupposition),
        ("check_bracketing_reduction_valid", check_bracketing_reduction_valid),
        ("check_epoche_completeness_fraction", check_epoche_completeness_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
