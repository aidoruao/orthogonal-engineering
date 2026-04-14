"""arXiv-derived domain invariants for Case-Grounded Evidence Verification: A Framework for Constructing Evidence-Sensitive Supervision."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class CaseGroundedVerificationClaim:
    """Structured claim parameters derived from arXiv paper 2604.09537v1 (cs.AI)."""

    supported_case_count: Fraction
    evaluated_case_count: Fraction
    evidence_dependency_drop: Fraction
    counterfactual_flip_rate: Fraction
    retrieval_leakage_rate: Fraction
    case_specific_evidence_ratio: Fraction
    label_only_baseline_score: Fraction
    evidence_conditioned_score: Fraction


def check_case_support_coverage(data: CaseGroundedVerificationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Most evaluated cases should be directly supported by aligned evidence.

    Standard: arXiv 2604.09537v1 (cs.AI) claim operationalization.
    falsifies_if: supported_case_count / evaluated_case_count < 4/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.supported_case_count * Fraction(5) >= data.evaluated_case_count * Fraction(4)
    proof = ProofObject(
        rule="check_case_support_coverage",
        premises=[
            "paper_id=2604.09537v1",
            f"supported_case_count={data.supported_case_count}",
            f"evaluated_case_count={data.evaluated_case_count}",
        ],
        conclusion=(
            "PASS: evidence support coverage is high"
            if success else "FAIL: evidence support coverage is insufficient"
        ),
    )
    return success, proof

def check_evidence_sensitivity(data: CaseGroundedVerificationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Prediction quality should decrease when evidence is removed.

    Standard: arXiv 2604.09537v1 (cs.AI) claim operationalization.
    falsifies_if: evidence_dependency_drop < 1/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.evidence_dependency_drop >= Fraction(1, 4)
    proof = ProofObject(
        rule="check_evidence_sensitivity",
        premises=[
            "paper_id=2604.09537v1",
            f"evidence_dependency_drop={data.evidence_dependency_drop}",
        ],
        conclusion=(
            "PASS: model behavior is evidence-sensitive"
            if success else "FAIL: model appears insensitive to provided evidence"
        ),
    )
    return success, proof

def check_counterfactual_consistency(data: CaseGroundedVerificationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Counterfactual evidence replacement should flip predictions at meaningful rate.

    Standard: arXiv 2604.09537v1 (cs.AI) claim operationalization.
    falsifies_if: counterfactual_flip_rate < 2/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.counterfactual_flip_rate >= Fraction(2, 5)
    proof = ProofObject(
        rule="check_counterfactual_consistency",
        premises=[
            "paper_id=2604.09537v1",
            f"counterfactual_flip_rate={data.counterfactual_flip_rate}",
        ],
        conclusion=(
            "PASS: counterfactual evidence impacts predictions"
            if success else "FAIL: counterfactual evidence has weak influence"
        ),
    )
    return success, proof

def check_retrieval_leakage_control(data: CaseGroundedVerificationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Loose retrieval shortcuts should remain bounded.

    Standard: arXiv 2604.09537v1 (cs.AI) claim operationalization.
    falsifies_if: retrieval_leakage_rate > 1/5.

    Returns:
        Tuple of (success, proof).
    """
    success = data.retrieval_leakage_rate <= Fraction(1, 5)
    proof = ProofObject(
        rule="check_retrieval_leakage_control",
        premises=[
            "paper_id=2604.09537v1",
            f"retrieval_leakage_rate={data.retrieval_leakage_rate}",
            f"case_specific_evidence_ratio={data.case_specific_evidence_ratio}",
        ],
        conclusion=(
            "PASS: retrieval leakage is controlled"
            if success else "FAIL: retrieval leakage is too high"
        ),
    )
    return success, proof

def check_evidence_conditioning_gain(data: CaseGroundedVerificationClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Evidence-conditioned supervision should outperform label-only baseline.

    Standard: arXiv 2604.09537v1 (cs.AI) claim operationalization.
    falsifies_if: evidence_conditioned_score <= label_only_baseline_score.

    Returns:
        Tuple of (success, proof).
    """
    success = data.evidence_conditioned_score > data.label_only_baseline_score
    proof = ProofObject(
        rule="check_evidence_conditioning_gain",
        premises=[
            "paper_id=2604.09537v1",
            f"evidence_conditioned_score={data.evidence_conditioned_score}",
            f"label_only_baseline_score={data.label_only_baseline_score}",
        ],
        conclusion=(
            "PASS: evidence-conditioned supervision improves performance"
            if success else "FAIL: no gain over label-only baseline"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """
    Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09537v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = CaseGroundedVerificationClaim(
        supported_case_count=Fraction(88),
        evaluated_case_count=Fraction(100),
        evidence_dependency_drop=Fraction(3, 10),
        counterfactual_flip_rate=Fraction(1, 2),
        retrieval_leakage_rate=Fraction(1, 10),
        case_specific_evidence_ratio=Fraction(4, 5),
        label_only_baseline_score=Fraction(7, 10),
        evidence_conditioned_score=Fraction(17, 20),
    )

    checks = [
        ("check_case_support_coverage", check_case_support_coverage),
        ("check_evidence_sensitivity", check_evidence_sensitivity),
        ("check_counterfactual_consistency", check_counterfactual_consistency),
        ("check_retrieval_leakage_control", check_retrieval_leakage_control),
        ("check_evidence_conditioning_gain", check_evidence_conditioning_gain),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
