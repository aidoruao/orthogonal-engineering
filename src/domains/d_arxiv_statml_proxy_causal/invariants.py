"""Invariant checks for d_arxiv_statml_proxy_causal."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import ProxyCausalClaim, create_nominal_claim


def check_identifiability(data: ProxyCausalClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Causal effect is identifiable via proxy.

    Standard: arXiv 2604.09135v1 (stat.ML) claim operationalization.
    Falsifies if: not identifiable.
    falsifies_if: not identifiable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.identifiable
    proof = ProofObject(
        rule="check_identifiability",
        premises=[
            f"paper_id=2604.09135v1",
            f'identifiable={data.identifiable}',
        ],
        conclusion=(
            "PASS: causal effect is identifiable via proxy"
            if success else "FAIL: not identifiable"
        ),
    )
    return success, proof



def check_consistency(data: ProxyCausalClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Consistency condition for identification is met.

    Standard: arXiv 2604.09135v1 (stat.ML) claim operationalization.
    Falsifies if: not consistency_condition_met.
    falsifies_if: not consistency_condition_met.

    Returns:
        Tuple of (success, proof).
    """
    success = data.consistency_condition_met
    proof = ProofObject(
        rule="check_consistency",
        premises=[
            f"paper_id=2604.09135v1",
            f'consistency_condition_met={data.consistency_condition_met}',
        ],
        conclusion=(
            "PASS: consistency condition for identification is met"
            if success else "FAIL: not consistency_condition_met"
        ),
    )
    return success, proof



def check_proxy_relevance_valid(data: ProxyCausalClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Proxy relevance is in (0, 1].

    Standard: arXiv 2604.09135v1 (stat.ML) claim operationalization.
    Falsifies if: proxy_relevance <= 0 or proxy_relevance > 1.
    falsifies_if: proxy_relevance <= 0 or proxy_relevance > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.proxy_relevance <= Fraction(1)
    proof = ProofObject(
        rule="check_proxy_relevance_valid",
        premises=[
            f"paper_id=2604.09135v1",
            f'proxy_relevance={data.proxy_relevance}',
        ],
        conclusion=(
            "PASS: proxy relevance is in (0, 1]"
            if success else "FAIL: proxy_relevance <= 0 or proxy_relevance > 1"
        ),
    )
    return success, proof



def check_proxy_count_positive(data: ProxyCausalClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Proxy variable count is >= 1.

    Standard: arXiv 2604.09135v1 (stat.ML) claim operationalization.
    Falsifies if: proxy_variable_count < 1.
    falsifies_if: proxy_variable_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.proxy_variable_count >= Fraction(1)
    proof = ProofObject(
        rule="check_proxy_count_positive",
        premises=[
            f"paper_id=2604.09135v1",
            f'proxy_variable_count={data.proxy_variable_count}',
        ],
        conclusion=(
            "PASS: proxy variable count is >= 1"
            if success else "FAIL: proxy_variable_count < 1"
        ),
    )
    return success, proof



def check_confounder_count_nonnegative(data: ProxyCausalClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Confounder count is non-negative.

    Standard: arXiv 2604.09135v1 (stat.ML) claim operationalization.
    Falsifies if: confounder_count < 0.
    falsifies_if: confounder_count < 0.

    Returns:
        Tuple of (success, proof).
    """
    success = data.confounder_count >= Fraction(0)
    proof = ProofObject(
        rule="check_confounder_count_nonnegative",
        premises=[
            f"paper_id=2604.09135v1",
            f'confounder_count={data.confounder_count}',
        ],
        conclusion=(
            "PASS: confounder count is non-negative"
            if success else "FAIL: confounder_count < 0"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09135v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_identifiability", check_identifiability),
        ("check_consistency", check_consistency),
        ("check_proxy_relevance_valid", check_proxy_relevance_valid),
        ("check_proxy_count_positive", check_proxy_count_positive),
        ("check_confounder_count_nonnegative", check_confounder_count_nonnegative),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
