"""Invariant checks for d_arxiv_statml_learning_to_defer."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import LearningToDeferClaim, create_nominal_claim


def check_expert_count_positive(data: LearningToDeferClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Expert count is >= 1.

    Standard: arXiv 2604.09414v1 (stat.ML) claim operationalization.
    Falsifies if: expert_count < 1.
    falsifies_if: expert_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.expert_count >= Fraction(1)
    proof = ProofObject(
        rule="check_expert_count_positive",
        premises=[
            f"paper_id=2604.09414v1",
            f'expert_count={data.expert_count}',
        ],
        conclusion=(
            "PASS: expert count is >= 1"
            if success else "FAIL: expert_count < 1"
        ),
    )
    return success, proof



def check_deferral_rate_valid(data: LearningToDeferClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Deferral rate is in [0, 1].

    Standard: arXiv 2604.09414v1 (stat.ML) claim operationalization.
    Falsifies if: deferral_rate < 0 or deferral_rate > 1.
    falsifies_if: deferral_rate < 0 or deferral_rate > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.deferral_rate <= Fraction(1)
    proof = ProofObject(
        rule="check_deferral_rate_valid",
        premises=[
            f"paper_id=2604.09414v1",
            f'deferral_rate={data.deferral_rate}',
        ],
        conclusion=(
            "PASS: deferral rate is in [0, 1]"
            if success else "FAIL: deferral_rate < 0 or deferral_rate > 1"
        ),
    )
    return success, proof



def check_system_accuracy_valid(data: LearningToDeferClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: System accuracy is in [0, 1].

    Standard: arXiv 2604.09414v1 (stat.ML) claim operationalization.
    Falsifies if: system_accuracy < 0 or system_accuracy > 1.
    falsifies_if: system_accuracy < 0 or system_accuracy > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.system_accuracy <= Fraction(1)
    proof = ProofObject(
        rule="check_system_accuracy_valid",
        premises=[
            f"paper_id=2604.09414v1",
            f'system_accuracy={data.system_accuracy}',
        ],
        conclusion=(
            "PASS: system accuracy is in [0, 1]"
            if success else "FAIL: system_accuracy < 0 or system_accuracy > 1"
        ),
    )
    return success, proof



def check_human_accuracy_valid(data: LearningToDeferClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Human (expert) accuracy is in [0, 1].

    Standard: arXiv 2604.09414v1 (stat.ML) claim operationalization.
    Falsifies if: human_accuracy < 0 or human_accuracy > 1.
    falsifies_if: human_accuracy < 0 or human_accuracy > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.human_accuracy <= Fraction(1)
    proof = ProofObject(
        rule="check_human_accuracy_valid",
        premises=[
            f"paper_id=2604.09414v1",
            f'human_accuracy={data.human_accuracy}',
        ],
        conclusion=(
            "PASS: human (expert) accuracy is in [0, 1]"
            if success else "FAIL: human_accuracy < 0 or human_accuracy > 1"
        ),
    )
    return success, proof



def check_system_outperforms_ai_alone(data: LearningToDeferClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: System accuracy is at least as high as ai-alone accuracy.

    Standard: arXiv 2604.09414v1 (stat.ML) claim operationalization.
    Falsifies if: system_accuracy < ai_accuracy.
    falsifies_if: system_accuracy < ai_accuracy.

    Returns:
        Tuple of (success, proof).
    """
    success = data.system_accuracy >= data.ai_accuracy
    proof = ProofObject(
        rule="check_system_outperforms_ai_alone",
        premises=[
            f"paper_id=2604.09414v1",
            f'system_accuracy={data.system_accuracy}',
            f'ai_accuracy={data.ai_accuracy}',
        ],
        conclusion=(
            "PASS: system accuracy is at least as high as AI-alone accuracy"
            if success else "FAIL: system_accuracy < ai_accuracy"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09414v1 (stat.ML) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_expert_count_positive", check_expert_count_positive),
        ("check_deferral_rate_valid", check_deferral_rate_valid),
        ("check_system_accuracy_valid", check_system_accuracy_valid),
        ("check_human_accuracy_valid", check_human_accuracy_valid),
        ("check_system_outperforms_ai_alone", check_system_outperforms_ai_alone),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
