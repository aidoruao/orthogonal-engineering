"""Implementation models for d_arxiv_quantum_property_testing."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class QuantumPropertyTestingClaim:
    """Structured claim parameters derived from arXiv paper 2604.07954v1 (quant-ph)."""

    graph_vertex_count: Fraction
    max_degree: Fraction
    query_complexity: Fraction
    epsilon: Fraction
    quantum_speedup_factor: Fraction


def create_nominal_claim() -> QuantumPropertyTestingClaim:
    """Create nominal claim data used by run_all_invariants().

    falsifies_if: nominal claim data cannot be constructed.
    """
    return QuantumPropertyTestingClaim(
        graph_vertex_count=Fraction(1000),
        max_degree=Fraction(10),
        query_complexity=Fraction(100),
        epsilon=Fraction(1, 3),
        quantum_speedup_factor=Fraction(3, 2),
    )


DOMAIN_METADATA = {
    "id": "D_ARXIV_QUANTUM_PROPERTY_TESTING",
    "paper_id": "2604.07954v1",
    "claim_model": "QuantumPropertyTestingClaim",
    "check_functions": [
        "check_vertex_count_positive",
        "check_max_degree_positive",
        "check_query_complexity_positive",
        "check_epsilon_valid",
        "check_quantum_speedup",
    ],
}
