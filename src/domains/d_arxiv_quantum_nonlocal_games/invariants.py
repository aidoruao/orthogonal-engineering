"""Invariant checks for d_arxiv_quantum_nonlocal_games."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumNonlocalGameClaim, create_nominal_claim


def check_classical_probability_valid(data: QuantumNonlocalGameClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: classical_winning_probability must satisfy 0 <= value <= 1.

    Standard: arXiv 2604.09458v1 (quant-ph) claim operationalization.
    Falsifies if: Classical winning probability is outside [0, 1].
    falsifies_if: classical_winning_probability < 0 or classical_winning_probability > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.classical_winning_probability <= Fraction(1)
    proof = ProofObject(
        rule="check_classical_probability_valid",
        premises=[
            "paper_id=2604.09458v1",
            f"classical_winning_probability={data.classical_winning_probability}",
        ],
        conclusion=(
            "PASS: classical_winning_probability in [0, 1]"
            if success else "FAIL: classical_winning_probability outside [0, 1]"
        ),
    )
    return success, proof


def check_quantum_probability_valid(data: QuantumNonlocalGameClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: quantum_winning_probability must satisfy 0 <= value <= 1.

    Standard: arXiv 2604.09458v1 (quant-ph) claim operationalization.
    Falsifies if: Quantum winning probability is outside [0, 1].
    falsifies_if: quantum_winning_probability < 0 or quantum_winning_probability > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) <= data.quantum_winning_probability <= Fraction(1)
    proof = ProofObject(
        rule="check_quantum_probability_valid",
        premises=[
            "paper_id=2604.09458v1",
            f"quantum_winning_probability={data.quantum_winning_probability}",
        ],
        conclusion=(
            "PASS: quantum_winning_probability in [0, 1]"
            if success else "FAIL: quantum_winning_probability outside [0, 1]"
        ),
    )
    return success, proof


def check_quantum_advantage(data: QuantumNonlocalGameClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: if is_quantum_advantage then quantum_winning_probability > classical_winning_probability.

    Standard: arXiv 2604.09458v1 (quant-ph) claim operationalization.
    Falsifies if: Quantum advantage claimed but quantum probability does not exceed classical.
    falsifies_if: is_quantum_advantage and quantum_winning_probability <= classical_winning_probability.

    Returns:
        Tuple of (success, proof).
    """
    if data.is_quantum_advantage:
        success = data.quantum_winning_probability > data.classical_winning_probability
    else:
        success = True
    proof = ProofObject(
        rule="check_quantum_advantage",
        premises=[
            "paper_id=2604.09458v1",
            f"is_quantum_advantage={data.is_quantum_advantage}",
            f"quantum_winning_probability={data.quantum_winning_probability}",
            f"classical_winning_probability={data.classical_winning_probability}",
        ],
        conclusion=(
            "PASS: quantum advantage condition satisfied"
            if success else "FAIL: quantum advantage claimed but not demonstrated"
        ),
    )
    return success, proof


def check_entanglement_dimension_positive(data: QuantumNonlocalGameClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: entanglement_dimension must be at least 1.

    Standard: arXiv 2604.09458v1 (quant-ph) claim operationalization.
    Falsifies if: Entanglement dimension is less than 1.
    falsifies_if: entanglement_dimension < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.entanglement_dimension >= Fraction(1)
    proof = ProofObject(
        rule="check_entanglement_dimension_positive",
        premises=[
            "paper_id=2604.09458v1",
            f"entanglement_dimension={data.entanglement_dimension}",
        ],
        conclusion=(
            "PASS: entanglement_dimension >= 1"
            if success else "FAIL: entanglement_dimension is less than 1"
        ),
    )
    return success, proof


def check_pseudo_telepathy_consistency(data: QuantumNonlocalGameClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: if is_pseudo_telepathy then quantum_winning_probability == 1.

    Standard: arXiv 2604.09458v1 (quant-ph) claim operationalization.
    Falsifies if: Pseudo-telepathy claimed but quantum winning probability is not 1.
    falsifies_if: is_pseudo_telepathy and quantum_winning_probability != 1.

    Returns:
        Tuple of (success, proof).
    """
    if data.is_pseudo_telepathy:
        success = data.quantum_winning_probability == Fraction(1)
    else:
        success = True
    proof = ProofObject(
        rule="check_pseudo_telepathy_consistency",
        premises=[
            "paper_id=2604.09458v1",
            f"is_pseudo_telepathy={data.is_pseudo_telepathy}",
            f"quantum_winning_probability={data.quantum_winning_probability}",
        ],
        conclusion=(
            "PASS: pseudo-telepathy consistency holds"
            if success else "FAIL: pseudo-telepathy requires quantum_winning_probability == 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.09458v1 (quant-ph) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_classical_probability_valid", check_classical_probability_valid),
        ("check_quantum_probability_valid", check_quantum_probability_valid),
        ("check_quantum_advantage", check_quantum_advantage),
        ("check_entanglement_dimension_positive", check_entanglement_dimension_positive),
        ("check_pseudo_telepathy_consistency", check_pseudo_telepathy_consistency),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
