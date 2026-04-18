"""Invariant checks for Formal Epistemology."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import FormalEpistemologyClaim, create_nominal_claim


def check_belief_set_consistent(data: FormalEpistemologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Belief set is logically consistent.

    Standard: Formal Epistemology domain invariant.
    Falsifies if: not belief_set_consistent.
    falsifies_if: not belief_set_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.belief_set_consistent
    proof = ProofObject(
        rule="check_belief_set_consistent",
        premises=[
            "domain=Formal Epistemology",
            f"belief_set_consistent={{data.belief_set_consistent}}",
        ],
        conclusion=(
            "PASS: Belief set is logically consistent"
            if success else "FAIL: Belief set is logically consistent"
        ),
    )
    return success, proof


def check_knowledge_factiveness(data: FormalEpistemologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Knowledge satisfies factiveness condition.

    Standard: Formal Epistemology domain invariant.
    Falsifies if: not knowledge_factiveness.
    falsifies_if: not knowledge_factiveness.

    Returns:
        Tuple of (success, proof).
    """
    success = data.knowledge_factiveness
    proof = ProofObject(
        rule="check_knowledge_factiveness",
        premises=[
            "domain=Formal Epistemology",
            f"knowledge_factiveness={{data.knowledge_factiveness}}",
        ],
        conclusion=(
            "PASS: Knowledge satisfies factiveness condition"
            if success else "FAIL: Knowledge satisfies factiveness condition"
        ),
    )
    return success, proof


def check_justification_non_circular(data: FormalEpistemologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Justification is non-circular.

    Standard: Formal Epistemology domain invariant.
    Falsifies if: not justification_non_circular.
    falsifies_if: not justification_non_circular.

    Returns:
        Tuple of (success, proof).
    """
    success = data.justification_non_circular
    proof = ProofObject(
        rule="check_justification_non_circular",
        premises=[
            "domain=Formal Epistemology",
            f"justification_non_circular={{data.justification_non_circular}}",
        ],
        conclusion=(
            "PASS: Justification is non-circular"
            if success else "FAIL: Justification is non-circular"
        ),
    )
    return success, proof


def check_credence_normality(data: FormalEpistemologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Credence function is normalized.

    Standard: Formal Epistemology domain invariant.
    Falsifies if: not credence_normal.
    falsifies_if: not credence_normal.

    Returns:
        Tuple of (success, proof).
    """
    success = data.credence_normal
    proof = ProofObject(
        rule="check_credence_normality",
        premises=[
            "domain=Formal Epistemology",
            f"credence_normal={{data.credence_normal}}",
        ],
        conclusion=(
            "PASS: Credence function is normalized"
            if success else "FAIL: Credence function is normalized"
        ),
    )
    return success, proof


def check_prior_probability_fraction(data: FormalEpistemologyClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Prior probability is between 0 and 1.

    Standard: Formal Epistemology domain invariant.
    Falsifies if: not prior_probability.
    falsifies_if: not prior_probability.

    Returns:
        Tuple of (success, proof).
    """
    success = data.prior_probability >= Fraction(0)
    proof = ProofObject(
        rule="check_prior_probability_fraction",
        premises=[
            "domain=Formal Epistemology",
            f"prior_probability={{data.prior_probability}}",
        ],
        conclusion=(
            "PASS: Prior probability is between 0 and 1 is non-negative"
            if success else "FAIL: Prior probability is between 0 and 1 is negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Formal Epistemology nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_belief_set_consistent", check_belief_set_consistent),
        ("check_knowledge_factiveness", check_knowledge_factiveness),
        ("check_justification_non_circular", check_justification_non_circular),
        ("check_credence_normality", check_credence_normality),
        ("check_prior_probability_fraction", check_prior_probability_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
