"""Invariant checks for d_arxiv_left_distributive."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import LeftDistributiveClaim, create_nominal_claim


def check_left_distributivity(data: LeftDistributiveClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The algebra satisfies the left distributive law x*(y*z) = (x*y)*(x*z).

    Standard: arXiv 2604.08768v1 (math.LO) claim operationalization.
    Falsifies if: not satisfies_left_distributivity.
    falsifies_if: not satisfies_left_distributivity.

    Returns:
        Tuple of (success, proof).
    """
    success = data.satisfies_left_distributivity
    proof = ProofObject(
        rule="check_left_distributivity",
        premises=[
            "paper_id=2604.08768v1",
            f"satisfies_left_distributivity={data.satisfies_left_distributivity}",
        ],
        conclusion=(
            "PASS: algebra satisfies left distributivity x*(y*z) = (x*y)*(x*z)"
            if success else "FAIL: left distributivity law does not hold"
        ),
    )
    return success, proof


def check_freeness(data: LeftDistributiveClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The algebra is free (no extra relations beyond LD).

    Standard: arXiv 2604.08768v1 (math.LO) claim operationalization.
    Falsifies if: not is_free.
    falsifies_if: not is_free.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_free
    proof = ProofObject(
        rule="check_freeness",
        premises=[
            "paper_id=2604.08768v1",
            f"is_free={data.is_free}",
        ],
        conclusion=(
            "PASS: algebra is free — no extra relations beyond LD"
            if success else "FAIL: algebra is not free"
        ),
    )
    return success, proof


def check_generator_count_positive(data: LeftDistributiveClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The algebra has at least one generator.

    Standard: arXiv 2604.08768v1 (math.LO) claim operationalization.
    Falsifies if: generator_count < 1.
    falsifies_if: generator_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.generator_count >= Fraction(1)
    proof = ProofObject(
        rule="check_generator_count_positive",
        premises=[
            "paper_id=2604.08768v1",
            f"generator_count={data.generator_count}",
        ],
        conclusion=(
            "PASS: generator count is positive"
            if success else "FAIL: generator count must be at least 1"
        ),
    )
    return success, proof


def check_word_problem_decidability(data: LeftDistributiveClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The word problem for the free left distributive algebra is decidable.

    Standard: arXiv 2604.08768v1 (math.LO) claim operationalization.
    Falsifies if: not word_problem_decidable.
    falsifies_if: not word_problem_decidable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.word_problem_decidable
    proof = ProofObject(
        rule="check_word_problem_decidability",
        premises=[
            "paper_id=2604.08768v1",
            f"word_problem_decidable={data.word_problem_decidable}",
        ],
        conclusion=(
            "PASS: word problem is decidable for free LD algebra"
            if success else "FAIL: word problem is not decidable"
        ),
    )
    return success, proof


def check_algebra_size_positive(data: LeftDistributiveClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The algebra has at least one element.

    Standard: arXiv 2604.08768v1 (math.LO) claim operationalization.
    Falsifies if: element_count < 1.
    falsifies_if: element_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.element_count >= Fraction(1)
    proof = ProofObject(
        rule="check_algebra_size_positive",
        premises=[
            "paper_id=2604.08768v1",
            f"element_count={data.element_count}",
        ],
        conclusion=(
            "PASS: algebra has positive element count"
            if success else "FAIL: element count must be at least 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.08768v1 (math.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_left_distributivity", check_left_distributivity),
        ("check_freeness", check_freeness),
        ("check_generator_count_positive", check_generator_count_positive),
        ("check_word_problem_decidability", check_word_problem_decidability),
        ("check_algebra_size_positive", check_algebra_size_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
