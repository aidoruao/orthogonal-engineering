"""Invariant checks for d_arxiv_quantum_property_testing."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import QuantumPropertyTestingClaim, create_nominal_claim


def check_vertex_count_positive(data: QuantumPropertyTestingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: graph_vertex_count must be at least 1.

    Standard: arXiv 2604.07954v1 (quant-ph) claim operationalization.
    Falsifies if: Graph vertex count is less than 1.
    falsifies_if: graph_vertex_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.graph_vertex_count >= Fraction(1)
    proof = ProofObject(
        rule="check_vertex_count_positive",
        premises=[
            "paper_id=2604.07954v1",
            f"graph_vertex_count={data.graph_vertex_count}",
        ],
        conclusion=(
            "PASS: graph_vertex_count >= 1"
            if success else "FAIL: graph_vertex_count is less than 1"
        ),
    )
    return success, proof


def check_max_degree_positive(data: QuantumPropertyTestingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: max_degree must be at least 1.

    Standard: arXiv 2604.07954v1 (quant-ph) claim operationalization.
    Falsifies if: Max degree is less than 1.
    falsifies_if: max_degree < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.max_degree >= Fraction(1)
    proof = ProofObject(
        rule="check_max_degree_positive",
        premises=[
            "paper_id=2604.07954v1",
            f"max_degree={data.max_degree}",
        ],
        conclusion=(
            "PASS: max_degree >= 1"
            if success else "FAIL: max_degree is less than 1"
        ),
    )
    return success, proof


def check_query_complexity_positive(data: QuantumPropertyTestingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: query_complexity must be at least 1.

    Standard: arXiv 2604.07954v1 (quant-ph) claim operationalization.
    Falsifies if: Query complexity is less than 1.
    falsifies_if: query_complexity < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.query_complexity >= Fraction(1)
    proof = ProofObject(
        rule="check_query_complexity_positive",
        premises=[
            "paper_id=2604.07954v1",
            f"query_complexity={data.query_complexity}",
        ],
        conclusion=(
            "PASS: query_complexity >= 1"
            if success else "FAIL: query_complexity is less than 1"
        ),
    )
    return success, proof


def check_epsilon_valid(data: QuantumPropertyTestingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: epsilon must satisfy 0 < epsilon <= 1.

    Standard: arXiv 2604.07954v1 (quant-ph) claim operationalization.
    Falsifies if: Epsilon is out of valid range.
    falsifies_if: epsilon <= 0 or epsilon > 1.

    Returns:
        Tuple of (success, proof).
    """
    success = Fraction(0) < data.epsilon <= Fraction(1)
    proof = ProofObject(
        rule="check_epsilon_valid",
        premises=[
            "paper_id=2604.07954v1",
            f"epsilon={data.epsilon}",
        ],
        conclusion=(
            "PASS: epsilon in (0, 1]"
            if success else "FAIL: epsilon out of valid range"
        ),
    )
    return success, proof


def check_quantum_speedup(data: QuantumPropertyTestingClaim) -> Tuple[bool, ProofObject]:
    """
    Invariant: quantum_speedup_factor must be at least 1.

    Standard: arXiv 2604.07954v1 (quant-ph) claim operationalization.
    Falsifies if: Quantum speedup factor is less than 1.
    falsifies_if: quantum_speedup_factor < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.quantum_speedup_factor >= Fraction(1)
    proof = ProofObject(
        rule="check_quantum_speedup",
        premises=[
            "paper_id=2604.07954v1",
            f"quantum_speedup_factor={data.quantum_speedup_factor}",
        ],
        conclusion=(
            "PASS: quantum_speedup_factor >= 1"
            if success else "FAIL: quantum_speedup_factor is less than 1"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain and print PASS/FAIL.

    Standard: arXiv 2604.07954v1 (quant-ph) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()

    checks = [
        ("check_vertex_count_positive", check_vertex_count_positive),
        ("check_max_degree_positive", check_max_degree_positive),
        ("check_query_complexity_positive", check_query_complexity_positive),
        ("check_epsilon_valid", check_epsilon_valid),
        ("check_quantum_speedup", check_quantum_speedup),
    ]

    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
