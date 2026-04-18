"""Invariant checks for d_arxiv_banking_api_quotient."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import BankingAPIQuotientClaim, create_nominal_claim


def check_quotient_existence(data: BankingAPIQuotientClaim) -> Tuple[bool, ProofObject]:
    """Invariant: A universal quotient of the banking API category exists.

    Standard: arXiv 2604.08833v1 (math.CT) claim operationalization.
    Falsifies if: not quotient_exists.
    falsifies_if: not quotient_exists.

    Returns:
        Tuple of (success, proof).
    """
    success = data.quotient_exists
    proof = ProofObject(
        rule="check_quotient_existence",
        premises=[
            "paper_id=2604.08833v1",
            f"quotient_exists={data.quotient_exists}",
        ],
        conclusion=(
            "PASS: universal quotient of banking APIs exists"
            if success else "FAIL: universal quotient does not exist"
        ),
    )
    return success, proof


def check_universality(data: BankingAPIQuotientClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The quotient is universal (initial among compatible morphisms).

    Standard: arXiv 2604.08833v1 (math.CT) claim operationalization.
    Falsifies if: not is_universal.
    falsifies_if: not is_universal.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_universal
    proof = ProofObject(
        rule="check_universality",
        premises=[
            "paper_id=2604.08833v1",
            f"is_universal={data.is_universal}",
        ],
        conclusion=(
            "PASS: quotient is universal"
            if success else "FAIL: quotient is not universal"
        ),
    )
    return success, proof


def check_financial_invariants_preserved(data: BankingAPIQuotientClaim) -> Tuple[bool, ProofObject]:
    """Invariant: The quotient preserves financial operations and invariants.

    Standard: arXiv 2604.08833v1 (math.CT) claim operationalization.
    Falsifies if: not preserves_financial_invariants.
    falsifies_if: not preserves_financial_invariants.

    Returns:
        Tuple of (success, proof).
    """
    success = data.preserves_financial_invariants
    proof = ProofObject(
        rule="check_financial_invariants_preserved",
        premises=[
            "paper_id=2604.08833v1",
            f"preserves_financial_invariants={data.preserves_financial_invariants}",
        ],
        conclusion=(
            "PASS: quotient preserves financial invariants"
            if success else "FAIL: quotient does not preserve financial invariants"
        ),
    )
    return success, proof


def check_api_count_positive(data: BankingAPIQuotientClaim) -> Tuple[bool, ProofObject]:
    """Invariant: At least one banking API is present in the category.

    Standard: arXiv 2604.08833v1 (math.CT) claim operationalization.
    Falsifies if: api_count < 1.
    falsifies_if: api_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.api_count >= Fraction(1)
    proof = ProofObject(
        rule="check_api_count_positive",
        premises=[
            "paper_id=2604.08833v1",
            f"api_count={data.api_count}",
        ],
        conclusion=(
            "PASS: API count is positive"
            if success else "FAIL: API count must be at least 1"
        ),
    )
    return success, proof


def check_morphism_count_positive(data: BankingAPIQuotientClaim) -> Tuple[bool, ProofObject]:
    """Invariant: At least one morphism between APIs exists.

    Standard: arXiv 2604.08833v1 (math.CT) claim operationalization.
    Falsifies if: morphism_count < 1.
    falsifies_if: morphism_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.morphism_count >= Fraction(1)
    proof = ProofObject(
        rule="check_morphism_count_positive",
        premises=[
            "paper_id=2604.08833v1",
            f"morphism_count={data.morphism_count}",
        ],
        conclusion=(
            "PASS: morphism count is positive"
            if success else "FAIL: morphism count must be at least 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.08833v1 (math.CT) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_quotient_existence", check_quotient_existence),
        ("check_universality", check_universality),
        ("check_financial_invariants_preserved", check_financial_invariants_preserved),
        ("check_api_count_positive", check_api_count_positive),
        ("check_morphism_count_positive", check_morphism_count_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
