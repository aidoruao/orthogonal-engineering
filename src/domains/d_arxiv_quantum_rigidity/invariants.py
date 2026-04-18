"""Invariant checks for d_arxiv_quantum_rigidity."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import CHSHRigidityClaim, create_nominal_claim


def check_chsh_classical_bound(data: CHSHRigidityClaim) -> Tuple[bool, ProofObject]:
    """Classical CHSH strategies are bounded by 2.

    Standard: arXiv 2604.03884v1 (cs.LO) claim operationalization.
    Falsifies if: not is_quantum_strategy and chsh_value > 2.
    falsifies_if: not is_quantum_strategy and chsh_value > 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_quantum_strategy or data.chsh_value <= Fraction(2)
    proof = ProofObject(
        rule="check_chsh_classical_bound",
        premises=[
            "paper_id=2604.03884v1",
            f"is_quantum_strategy={data.is_quantum_strategy}",
            f"chsh_value={data.chsh_value}",
        ],
        conclusion=(
            "PASS: classical CHSH bound satisfied"
            if success
            else "FAIL: classical CHSH bound violated"
        ),
    )
    return success, proof


def check_chsh_quantum_bound(data: CHSHRigidityClaim) -> Tuple[bool, ProofObject]:
    """CHSH value must not exceed quantum maximum.

    Standard: arXiv 2604.03884v1 (cs.LO) claim operationalization.
    Falsifies if: chsh_value > quantum_max.
    falsifies_if: chsh_value > quantum_max.

    Returns:
        Tuple of (success, proof).
    """
    success = data.chsh_value <= data.quantum_max
    proof = ProofObject(
        rule="check_chsh_quantum_bound",
        premises=[
            "paper_id=2604.03884v1",
            f"chsh_value={data.chsh_value}",
            f"quantum_max={data.quantum_max}",
        ],
        conclusion=(
            "PASS: quantum CHSH bound satisfied"
            if success
            else "FAIL: quantum CHSH bound violated"
        ),
    )
    return success, proof


def check_quantum_requires_entanglement(data: CHSHRigidityClaim) -> Tuple[bool, ProofObject]:
    """Quantum advantage requires entanglement.

    Standard: arXiv 2604.03884v1 (cs.LO) claim operationalization.
    Falsifies if: is_quantum_strategy and chsh_value > 2 and not entanglement_used.
    falsifies_if: is_quantum_strategy and chsh_value > 2 and not entanglement_used.

    Returns:
        Tuple of (success, proof).
    """
    success = not (data.is_quantum_strategy and data.chsh_value > Fraction(2)) or data.entanglement_used
    proof = ProofObject(
        rule="check_quantum_requires_entanglement",
        premises=[
            "paper_id=2604.03884v1",
            f"is_quantum_strategy={data.is_quantum_strategy}",
            f"chsh_value={data.chsh_value}",
            f"entanglement_used={data.entanglement_used}",
        ],
        conclusion=(
            "PASS: entanglement requirement satisfied"
            if success
            else "FAIL: quantum advantage without entanglement"
        ),
    )
    return success, proof


def check_rigidity(data: CHSHRigidityClaim) -> Tuple[bool, ProofObject]:
    """Near-maximal CHSH strategies must be rigid.

    Standard: arXiv 2604.03884v1 (cs.LO) claim operationalization.
    Falsifies if: chsh_value >= quantum_max * Fraction(9, 10) and not is_rigid.
    falsifies_if: chsh_value >= quantum_max * Fraction(9, 10) and not is_rigid.

    Returns:
        Tuple of (success, proof).
    """
    threshold = data.quantum_max * Fraction(9, 10)
    success = not (data.chsh_value >= threshold) or data.is_rigid
    proof = ProofObject(
        rule="check_rigidity",
        premises=[
            "paper_id=2604.03884v1",
            f"chsh_value={data.chsh_value}",
            f"threshold={threshold}",
            f"is_rigid={data.is_rigid}",
        ],
        conclusion=(
            "PASS: rigidity holds for near-maximal strategy"
            if success
            else "FAIL: near-maximal strategy is not rigid"
        ),
    )
    return success, proof


def check_quantum_advantage(data: CHSHRigidityClaim) -> Tuple[bool, ProofObject]:
    """Quantum maximum must exceed classical bound of 2.

    Standard: arXiv 2604.03884v1 (cs.LO) claim operationalization.
    Falsifies if: quantum_max <= 2.
    falsifies_if: quantum_max <= 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.quantum_max > Fraction(2)
    proof = ProofObject(
        rule="check_quantum_advantage",
        premises=["paper_id=2604.03884v1", f"quantum_max={data.quantum_max}"],
        conclusion=(
            "PASS: quantum advantage confirmed"
            if success
            else "FAIL: no quantum advantage"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.03884v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_chsh_classical_bound", check_chsh_classical_bound),
        ("check_chsh_quantum_bound", check_chsh_quantum_bound),
        ("check_quantum_requires_entanglement", check_quantum_requires_entanglement),
        ("check_rigidity", check_rigidity),
        ("check_quantum_advantage", check_quantum_advantage),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
