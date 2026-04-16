"""Invariant checks for d_arxiv_visor_agentic_visual."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import VisorAgenticVragClaim, create_nominal_claim


def check_iterative_search_depth(data: VisorAgenticVragClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Agentic VRAG should execute multi-round retrieval for complex queries.

    Standard: arXiv 2604.09508v1 (cs.AI) claim operationalization.
    falsifies_if: iterative_search_rounds < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.iterative_search_rounds >= Fraction(2)
    proof = ProofObject(
        rule="check_iterative_search_depth",
        premises=[
            "paper_id=2604.09508v1",
            f"iterative_search_rounds={data.iterative_search_rounds}",
            f"over_horizon_reasoning_depth={data.over_horizon_reasoning_depth}",
        ],
        conclusion=(
            "PASS: iterative search depth is sufficient"
            if success else "FAIL: iterative search is too shallow"
        ),
    )
    return success, proof

def check_cross_page_reasoning_connectivity(data: VisorAgenticVragClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Retrieved evidence should enable cross-page reasoning links.

    Standard: arXiv 2604.09508v1 (cs.AI) claim operationalization.
    falsifies_if: cross_page_link_density < 1/3.

    Returns:
        Tuple of (success, proof).
    """
    success = data.cross_page_link_density >= Fraction(1, 3)
    proof = ProofObject(
        rule="check_cross_page_reasoning_connectivity",
        premises=[
            "paper_id=2604.09508v1",
            f"retrieved_evidence_pages={data.retrieved_evidence_pages}",
            f"cross_page_link_density={data.cross_page_link_density}",
        ],
        conclusion=(
            "PASS: cross-page reasoning connectivity is adequate"
            if success else "FAIL: cross-page evidence connectivity is sparse"
        ),
    )
    return success, proof

def check_over_horizon_alignment(data: VisorAgenticVragClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Reasoning horizon should not exceed available iterative retrieval depth.

    Standard: arXiv 2604.09508v1 (cs.AI) claim operationalization.
    falsifies_if: over_horizon_reasoning_depth > iterative_search_rounds.

    Returns:
        Tuple of (success, proof).
    """
    success = data.over_horizon_reasoning_depth <= data.iterative_search_rounds
    proof = ProofObject(
        rule="check_over_horizon_alignment",
        premises=[
            "paper_id=2604.09508v1",
            f"over_horizon_reasoning_depth={data.over_horizon_reasoning_depth}",
            f"iterative_search_rounds={data.iterative_search_rounds}",
        ],
        conclusion=(
            "PASS: horizon reasoning aligns with retrieval depth"
            if success else "FAIL: horizon reasoning exceeds available retrieval support"
        ),
    )
    return success, proof

def check_visual_recall_floor(data: VisorAgenticVragClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Visual retrieval recall should satisfy deployment floor.

    Standard: arXiv 2604.09508v1 (cs.AI) claim operationalization.
    falsifies_if: visual_recall_at_k < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = data.visual_recall_at_k >= Fraction(3, 4)
    proof = ProofObject(
        rule="check_visual_recall_floor",
        premises=[
            "paper_id=2604.09508v1",
            f"visual_recall_at_k={data.visual_recall_at_k}",
        ],
        conclusion=(
            "PASS: visual recall meets floor"
            if success else "FAIL: visual recall below floor"
        ),
    )
    return success, proof

def check_grounding_over_hallucination(data: VisorAgenticVragClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: Grounded answer quality should dominate hallucination rate.

    Standard: arXiv 2604.09508v1 (cs.AI) claim operationalization.
    falsifies_if: answer_grounding_score <= hallucination_rate OR final_consistency_score < 3/4.

    Returns:
        Tuple of (success, proof).
    """
    success = (data.answer_grounding_score > data.hallucination_rate) and (data.final_consistency_score >= Fraction(3, 4))
    proof = ProofObject(
        rule="check_grounding_over_hallucination",
        premises=[
            "paper_id=2604.09508v1",
            f"answer_grounding_score={data.answer_grounding_score}",
            f"hallucination_rate={data.hallucination_rate}",
            f"final_consistency_score={data.final_consistency_score}",
        ],
        conclusion=(
            "PASS: grounding dominates hallucination"
            if success else "FAIL: grounding signal is too weak"
        ),
    )
    return success, proof

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09508v1 (cs.AI) nominal executable check set.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_iterative_search_depth", check_iterative_search_depth),
        ("check_cross_page_reasoning_connectivity", check_cross_page_reasoning_connectivity),
        ("check_over_horizon_alignment", check_over_horizon_alignment),
        ("check_visual_recall_floor", check_visual_recall_floor),
        ("check_grounding_over_hallucination", check_grounding_over_hallucination),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
