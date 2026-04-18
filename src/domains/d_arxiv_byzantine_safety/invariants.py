"""Invariant checks for d_arxiv_byzantine_safety."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import ByzantineSafetyClaim, create_nominal_claim


def check_byzantine_fault_tolerance(data: ByzantineSafetyClaim) -> Tuple[bool, ProofObject]:
    """Faulty nodes must not exceed safety threshold.

    Standard: arXiv 2604.03844v1 (cs.LO) claim operationalization.
    Falsifies if: faulty_nodes > safety_threshold.
    falsifies_if: faulty_nodes > safety_threshold.

    Returns:
        Tuple of (success, proof).
    """
    success = data.faulty_nodes <= data.safety_threshold
    proof = ProofObject(
        rule="check_byzantine_fault_tolerance",
        premises=[
            "paper_id=2604.03844v1",
            f"faulty_nodes={data.faulty_nodes}",
            f"safety_threshold={data.safety_threshold}",
        ],
        conclusion=(
            "PASS: Byzantine fault tolerance holds"
            if success
            else "FAIL: too many faulty nodes"
        ),
    )
    return success, proof


def check_safety_property(data: ByzantineSafetyClaim) -> Tuple[bool, ProofObject]:
    """Safety property must hold.

    Standard: arXiv 2604.03844v1 (cs.LO) claim operationalization.
    Falsifies if: not is_safe.
    falsifies_if: not is_safe.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_safe
    proof = ProofObject(
        rule="check_safety_property",
        premises=["paper_id=2604.03844v1", f"is_safe={data.is_safe}"],
        conclusion=(
            "PASS: safety property holds"
            if success
            else "FAIL: safety property violated"
        ),
    )
    return success, proof


def check_liveness_property(data: ByzantineSafetyClaim) -> Tuple[bool, ProofObject]:
    """Liveness property must hold.

    Standard: arXiv 2604.03844v1 (cs.LO) claim operationalization.
    Falsifies if: not is_live.
    falsifies_if: not is_live.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_live
    proof = ProofObject(
        rule="check_liveness_property",
        premises=["paper_id=2604.03844v1", f"is_live={data.is_live}"],
        conclusion=(
            "PASS: liveness property holds"
            if success
            else "FAIL: liveness property violated"
        ),
    )
    return success, proof


def check_threshold_formula(data: ByzantineSafetyClaim) -> Tuple[bool, ProofObject]:
    """Safety threshold must satisfy 3f+1 <= n.

    Standard: arXiv 2604.03844v1 (cs.LO) claim operationalization.
    Falsifies if: safety_threshold * 3 + 1 > total_nodes.
    falsifies_if: safety_threshold * 3 + 1 > total_nodes.

    Returns:
        Tuple of (success, proof).
    """
    lhs = data.safety_threshold * Fraction(3) + Fraction(1)
    success = lhs <= data.total_nodes
    proof = ProofObject(
        rule="check_threshold_formula",
        premises=[
            "paper_id=2604.03844v1",
            f"safety_threshold={data.safety_threshold}",
            f"total_nodes={data.total_nodes}",
            f"3f+1={lhs}",
        ],
        conclusion=(
            "PASS: threshold formula 3f+1<=n holds"
            if success
            else "FAIL: threshold formula violated"
        ),
    )
    return success, proof


def check_quorum_validity(data: ByzantineSafetyClaim) -> Tuple[bool, ProofObject]:
    """Quorum must be at least 2/3 of total nodes.

    Standard: arXiv 2604.03844v1 (cs.LO) claim operationalization.
    Falsifies if: quorum_size * 3 < total_nodes * 2.
    falsifies_if: quorum_size * 3 < total_nodes * 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.quorum_size * Fraction(3) >= data.total_nodes * Fraction(2)
    proof = ProofObject(
        rule="check_quorum_validity",
        premises=[
            "paper_id=2604.03844v1",
            f"quorum_size={data.quorum_size}",
            f"total_nodes={data.total_nodes}",
        ],
        conclusion=(
            "PASS: quorum is valid"
            if success
            else "FAIL: quorum too small"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.03844v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_byzantine_fault_tolerance", check_byzantine_fault_tolerance),
        ("check_safety_property", check_safety_property),
        ("check_liveness_property", check_liveness_property),
        ("check_threshold_formula", check_threshold_formula),
        ("check_quorum_validity", check_quorum_validity),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
