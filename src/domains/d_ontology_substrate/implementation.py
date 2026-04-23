"""D_ONTOLOGY_SUBSTRATE implementation — Ontological substrate.

Phase B2 of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class OntologicalState:
    """Ontological state representing reality precedents.

    falsifies_if: total_precedents != 10.
    falsifies_if: precedent_ratio < Fraction(1, 1).
    """
    reality_consistent: bool
    structural_order_present: bool
    deterministic_causality: bool
    truth_anchorable: bool
    knowledge_possible: bool
    patterns_detectable: bool
    code_executes_predictably: bool
    hashing_works: bool
    precedent_count: int
    total_precedents: int
    precedent_ratio: Fraction
    grounding_model: str
    lawvere_fixed_point_exists: bool


DOMAIN_METADATA = {
    "id": "ONTOLOGY_SUBSTRATE",
    "claim_model": "OntologicalState",
    "check_functions": [
        "check_all_precedents_satisfied",
        "check_consistent_reality",
        "check_structural_order",
        "check_deterministic_causality",
        "check_lawvere_convergence",
        "check_operational_necessities",
    ],
}
