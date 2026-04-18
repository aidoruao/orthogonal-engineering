"""Invariant checks for d_arxiv_game_endgame_verification."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import EndgameVerificationClaim, create_nominal_claim


def check_tablebase_completeness(data: EndgameVerificationClaim) -> Tuple[bool, ProofObject]:
    """Tablebase must cover all positions.

    Standard: arXiv 2604.07907v1 (cs.LO) claim operationalization.
    Falsifies if: not is_complete.
    falsifies_if: not is_complete.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_complete
    proof = ProofObject(
        rule="check_tablebase_completeness",
        premises=["paper_id=2604.07907v1", f"is_complete={data.is_complete}"],
        conclusion=(
            "PASS: tablebase is complete"
            if success
            else "FAIL: tablebase is incomplete"
        ),
    )
    return success, proof


def check_tablebase_consistency(data: EndgameVerificationClaim) -> Tuple[bool, ProofObject]:
    """Tablebase must have no conflicting evaluations.

    Standard: arXiv 2604.07907v1 (cs.LO) claim operationalization.
    Falsifies if: not is_consistent.
    falsifies_if: not is_consistent.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_consistent
    proof = ProofObject(
        rule="check_tablebase_consistency",
        premises=["paper_id=2604.07907v1", f"is_consistent={data.is_consistent}"],
        conclusion=(
            "PASS: tablebase is consistent"
            if success
            else "FAIL: tablebase is inconsistent"
        ),
    )
    return success, proof


def check_positions_positive(data: EndgameVerificationClaim) -> Tuple[bool, ProofObject]:
    """At least one position must be verified.

    Standard: arXiv 2604.07907v1 (cs.LO) claim operationalization.
    Falsifies if: positions_verified < 1.
    falsifies_if: positions_verified < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.positions_verified >= Fraction(1)
    proof = ProofObject(
        rule="check_positions_positive",
        premises=["paper_id=2604.07907v1", f"positions_verified={data.positions_verified}"],
        conclusion=(
            "PASS: positions verified is positive"
            if success
            else "FAIL: positions verified is zero or negative"
        ),
    )
    return success, proof


def check_capture_quiet_ratio_valid(data: EndgameVerificationClaim) -> Tuple[bool, ProofObject]:
    """Capture-quiet ratio must be in [0, 1].

    Standard: arXiv 2604.07907v1 (cs.LO) claim operationalization.
    Falsifies if: capture_quiet_ratio < 0 or capture_quiet_ratio > 1.
    falsifies_if: capture_quiet_ratio < 0 or capture_quiet_ratio > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.capture_quiet_ratio <= Fraction(1)
    proof = ProofObject(
        rule="check_capture_quiet_ratio_valid",
        premises=["paper_id=2604.07907v1", f"capture_quiet_ratio={data.capture_quiet_ratio}"],
        conclusion=(
            "PASS: capture-quiet ratio is valid"
            if success
            else "FAIL: capture-quiet ratio out of range"
        ),
    )
    return success, proof


def check_decomposition_depth_positive(data: EndgameVerificationClaim) -> Tuple[bool, ProofObject]:
    """Decomposition depth must be at least 1.

    Standard: arXiv 2604.07907v1 (cs.LO) claim operationalization.
    Falsifies if: decomposition_depth < 1.
    falsifies_if: decomposition_depth < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.decomposition_depth >= Fraction(1)
    proof = ProofObject(
        rule="check_decomposition_depth_positive",
        premises=["paper_id=2604.07907v1", f"decomposition_depth={data.decomposition_depth}"],
        conclusion=(
            "PASS: decomposition depth is positive"
            if success
            else "FAIL: decomposition depth is zero or negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.07907v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_tablebase_completeness", check_tablebase_completeness),
        ("check_tablebase_consistency", check_tablebase_consistency),
        ("check_positions_positive", check_positions_positive),
        ("check_capture_quiet_ratio_valid", check_capture_quiet_ratio_valid),
        ("check_decomposition_depth_positive", check_decomposition_depth_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
