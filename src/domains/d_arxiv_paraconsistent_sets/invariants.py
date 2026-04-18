"""Invariant checks for d_arxiv_paraconsistent_sets."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ParaconsistentSetClaim, create_nominal_claim


def check_paraconsistent_logic(data: ParaconsistentSetClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The underlying logic is paraconsistent (inconsistency-tolerant).

    Standard: arXiv 2604.07094v1 (math.LO) claim operationalization.
    Falsifies if: not is_paraconsistent.
    falsifies_if: not is_paraconsistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_paraconsistent
    proof = ProofObject(
        rule="check_paraconsistent_logic",
        premises=[
            "paper_id=2604.07094v1",
            f"is_paraconsistent={data.is_paraconsistent}",
        ],
        conclusion=(
            "PASS: underlying logic is paraconsistent"
            if success else "FAIL: logic is not paraconsistent"
        ),
    )
    return success, proof


def check_cardinality_definition(data: ParaconsistentSetClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Cardinality notion is well-defined in paraconsistent/paracomplete logic.

    Standard: arXiv 2604.07094v1 (math.LO) claim operationalization.
    Falsifies if: not cardinality_well_defined.
    falsifies_if: not cardinality_well_defined.

    Returns:
        Tuple of (success, proof).
    """
    success = data.cardinality_well_defined
    proof = ProofObject(
        rule="check_cardinality_definition",
        premises=[
            "paper_id=2604.07094v1",
            f"cardinality_well_defined={data.cardinality_well_defined}",
        ],
        conclusion=(
            "PASS: cardinality is well-defined in this logic"
            if success else "FAIL: cardinality notion is not well-defined"
        ),
    )
    return success, proof


def check_classical_extension(data: ParaconsistentSetClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The cardinality theory extends classical cardinality.

    Standard: arXiv 2604.07094v1 (math.LO) claim operationalization.
    Falsifies if: not classical_cardinality_extends.
    falsifies_if: not classical_cardinality_extends.

    Returns:
        Tuple of (success, proof).
    """
    success = data.classical_cardinality_extends
    proof = ProofObject(
        rule="check_classical_extension",
        premises=[
            "paper_id=2604.07094v1",
            f"classical_cardinality_extends={data.classical_cardinality_extends}",
        ],
        conclusion=(
            "PASS: cardinality theory extends classical cardinality"
            if success else "FAIL: cardinality theory does not extend classical cardinality"
        ),
    )
    return success, proof


def check_set_size_nonnegative(data: ParaconsistentSetClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The set cardinality is non-negative.

    Standard: arXiv 2604.07094v1 (math.LO) claim operationalization.
    Falsifies if: set_size < 0.
    falsifies_if: set_size < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.set_size >= Fraction(0)
    proof = ProofObject(
        rule="check_set_size_nonnegative",
        premises=[
            "paper_id=2604.07094v1",
            f"set_size={data.set_size}",
        ],
        conclusion=(
            "PASS: set size is non-negative"
            if success else "FAIL: set size must be non-negative"
        ),
    )
    return success, proof


def check_paracomplete_consistency(data: ParaconsistentSetClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The logic is paracomplete (allows truth-value gaps).

    Standard: arXiv 2604.07094v1 (math.LO) claim operationalization.
    Falsifies if: not is_paracomplete.
    falsifies_if: not is_paracomplete.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_paracomplete
    proof = ProofObject(
        rule="check_paracomplete_consistency",
        premises=[
            "paper_id=2604.07094v1",
            f"is_paracomplete={data.is_paracomplete}",
        ],
        conclusion=(
            "PASS: logic is paracomplete allowing truth-value gaps"
            if success else "FAIL: logic is not paracomplete"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.07094v1 (math.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_paraconsistent_logic", check_paraconsistent_logic),
        ("check_cardinality_definition", check_cardinality_definition),
        ("check_classical_extension", check_classical_extension),
        ("check_set_size_nonnegative", check_set_size_nonnegative),
        ("check_paracomplete_consistency", check_paracomplete_consistency),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
