"""Invariant checks for Philosophy of Science."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import PhilosophyOfScienceClaim, create_nominal_claim


def check_falsifiability_criterion(data: PhilosophyOfScienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Theory meets falsifiability criterion.

    Standard: Philosophy of Science domain invariant.
    Falsifies if: not falsifiability_criterion_met.
    falsifies_if: not falsifiability_criterion_met.

    Returns:
        Tuple of (success, proof).
    """
    success = data.falsifiability_criterion_met
    proof = ProofObject(
        rule="check_falsifiability_criterion",
        premises=[
            "domain=Philosophy of Science",
            f"falsifiability_criterion_met={{data.falsifiability_criterion_met}}",
        ],
        conclusion=(
            "PASS: Theory meets falsifiability criterion"
            if success else "FAIL: Theory meets falsifiability criterion"
        ),
    )
    return success, proof


def check_reproducibility_mandate(data: PhilosophyOfScienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Reproducibility mandate is met.

    Standard: Philosophy of Science domain invariant.
    Falsifies if: not reproducibility_mandate_met.
    falsifies_if: not reproducibility_mandate_met.

    Returns:
        Tuple of (success, proof).
    """
    success = data.reproducibility_mandate_met
    proof = ProofObject(
        rule="check_reproducibility_mandate",
        premises=[
            "domain=Philosophy of Science",
            f"reproducibility_mandate_met={{data.reproducibility_mandate_met}}",
        ],
        conclusion=(
            "PASS: Reproducibility mandate is met"
            if success else "FAIL: Reproducibility mandate is met"
        ),
    )
    return success, proof


def check_paradigm_incommensurability(data: PhilosophyOfScienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Paradigms are commensurable under translation.

    Standard: Philosophy of Science domain invariant.
    Falsifies if: not paradigm_commensurable.
    falsifies_if: not paradigm_commensurable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.paradigm_commensurable
    proof = ProofObject(
        rule="check_paradigm_incommensurability",
        premises=[
            "domain=Philosophy of Science",
            f"paradigm_commensurable={{data.paradigm_commensurable}}",
        ],
        conclusion=(
            "PASS: Paradigms are commensurable under translation"
            if success else "FAIL: Paradigms are commensurable under translation"
        ),
    )
    return success, proof


def check_underdetermination_bounded(data: PhilosophyOfScienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Underdetermination is bounded.

    Standard: Philosophy of Science domain invariant.
    Falsifies if: not underdetermination_bounded.
    falsifies_if: not underdetermination_bounded.

    Returns:
        Tuple of (success, proof).
    """
    success = data.underdetermination_bounded
    proof = ProofObject(
        rule="check_underdetermination_bounded",
        premises=[
            "domain=Philosophy of Science",
            f"underdetermination_bounded={{data.underdetermination_bounded}}",
        ],
        conclusion=(
            "PASS: Underdetermination is bounded"
            if success else "FAIL: Underdetermination is bounded"
        ),
    )
    return success, proof


def check_bayesian_confirmation_fraction(data: PhilosophyOfScienceClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Bayes factor is non-negative.

    Standard: Philosophy of Science domain invariant.
    Falsifies if: not bayes_factor.
    falsifies_if: not bayes_factor.

    Returns:
        Tuple of (success, proof).
    """
    success = data.bayes_factor >= Fraction(0)
    proof = ProofObject(
        rule="check_bayesian_confirmation_fraction",
        premises=[
            "domain=Philosophy of Science",
            f"bayes_factor={{data.bayes_factor}}",
        ],
        conclusion=(
            "PASS: Bayes factor is non-negative is non-negative"
            if success else "FAIL: Bayes factor is non-negative is negative"
        ),
    )
    return success, proof




def check_effect_size_fraction(data: PhilosophyOfScienceClaim) -> Tuple[bool, ProofObject]:
    """Minimum detectable effect size must be >= Fraction(1, 20) for scientific relevance.

    Standard: PHILSCI-006 effect size threshold.
    Falsifies if: effect_size < Fraction(1, 20).
    falsifies_if: effect_size < Fraction(1, 20).
    """
    success = data.effect_size >= Fraction(1, 20)
    proof = ProofObject(
        rule="philsci_effect_size_fraction",
        premises=[f"effect_size={data.effect_size}"],
        conclusion=(
            "PASS: Effect size above scientific relevance threshold"
            if success else f"FAIL: Effect size {data.effect_size} < 1/20"
        ),
    )
    return success, proof

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Philosophy of Science nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_falsifiability_criterion", check_falsifiability_criterion),
        ("check_reproducibility_mandate", check_reproducibility_mandate),
        ("check_paradigm_incommensurability", check_paradigm_incommensurability),
        ("check_underdetermination_bounded", check_underdetermination_bounded),
        ("check_bayesian_confirmation_fraction", check_bayesian_confirmation_fraction),
        ("check_effect_size_fraction", check_effect_size_fraction),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
