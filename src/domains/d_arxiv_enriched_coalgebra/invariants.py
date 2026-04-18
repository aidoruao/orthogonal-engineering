"""Invariant checks for d_arxiv_enriched_coalgebra."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import EnrichedCoalgebraClaim, create_nominal_claim


def check_comonadicity(data: EnrichedCoalgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The enriched coalgebras are comonadic.

    Standard: arXiv 2604.09354v1 (math.CT) claim operationalization.
    Falsifies if: not is_comonadic.
    falsifies_if: not is_comonadic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_comonadic
    proof = ProofObject(
        rule="check_comonadicity",
        premises=[
            "paper_id=2604.09354v1",
            f"is_comonadic={data.is_comonadic}",
        ],
        conclusion=(
            "PASS: enriched coalgebras are comonadic"
            if success else "FAIL: enriched coalgebras are not comonadic"
        ),
    )
    return success, proof


def check_comonad_existence(data: EnrichedCoalgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The comonad structure exists on the category.

    Standard: arXiv 2604.09354v1 (math.CT) claim operationalization.
    Falsifies if: not comonad_exists.
    falsifies_if: not comonad_exists.

    Returns:
        Tuple of (success, proof).
    """
    success = data.comonad_exists
    proof = ProofObject(
        rule="check_comonad_existence",
        premises=[
            "paper_id=2604.09354v1",
            f"comonad_exists={data.comonad_exists}",
        ],
        conclusion=(
            "PASS: comonad structure exists"
            if success else "FAIL: comonad structure does not exist"
        ),
    )
    return success, proof


def check_comparison_equivalence(data: EnrichedCoalgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The comparison functor is an equivalence of categories.

    Standard: arXiv 2604.09354v1 (math.CT) claim operationalization.
    Falsifies if: not comparison_functor_is_equivalence.
    falsifies_if: not comparison_functor_is_equivalence.

    Returns:
        Tuple of (success, proof).
    """
    success = data.comparison_functor_is_equivalence
    proof = ProofObject(
        rule="check_comparison_equivalence",
        premises=[
            "paper_id=2604.09354v1",
            f"comparison_functor_is_equivalence={data.comparison_functor_is_equivalence}",
        ],
        conclusion=(
            "PASS: comparison functor is an equivalence"
            if success else "FAIL: comparison functor is not an equivalence"
        ),
    )
    return success, proof


def check_base_category_nonempty(data: EnrichedCoalgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The base category has at least one object.

    Standard: arXiv 2604.09354v1 (math.CT) claim operationalization.
    Falsifies if: base_category_size < 1.
    falsifies_if: base_category_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.base_category_size >= Fraction(1)
    proof = ProofObject(
        rule="check_base_category_nonempty",
        premises=[
            "paper_id=2604.09354v1",
            f"base_category_size={data.base_category_size}",
        ],
        conclusion=(
            "PASS: base category is non-empty"
            if success else "FAIL: base category must have at least one object"
        ),
    )
    return success, proof


def check_enrichment_nonempty(data: EnrichedCoalgebraClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The enriching category has at least one object.

    Standard: arXiv 2604.09354v1 (math.CT) claim operationalization.
    Falsifies if: enrichment_category_size < 1.
    falsifies_if: enrichment_category_size < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.enrichment_category_size >= Fraction(1)
    proof = ProofObject(
        rule="check_enrichment_nonempty",
        premises=[
            "paper_id=2604.09354v1",
            f"enrichment_category_size={data.enrichment_category_size}",
        ],
        conclusion=(
            "PASS: enriching category is non-empty"
            if success else "FAIL: enriching category must have at least one object"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.09354v1 (math.CT) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_comonadicity", check_comonadicity),
        ("check_comonad_existence", check_comonad_existence),
        ("check_comparison_equivalence", check_comparison_equivalence),
        ("check_base_category_nonempty", check_base_category_nonempty),
        ("check_enrichment_nonempty", check_enrichment_nonempty),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
