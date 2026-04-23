"""Test suite for d_ontology_substrate invariants.

Phase B2 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_ontology_substrate.invariants import (
    check_all_precedents_satisfied,
    check_consistent_reality,
    check_structural_order,
    check_deterministic_causality,
    check_lawvere_convergence,
    check_operational_necessities,
    run_all_invariants,
)
from src.domains.d_ontology_substrate.implementation import OntologicalState


class TestOntologySubstrate:
    def test_pass_state(self):
        state = OntologicalState(
            reality_consistent=True,
            structural_order_present=True,
            deterministic_causality=True,
            truth_anchorable=True,
            knowledge_possible=True,
            patterns_detectable=True,
            code_executes_predictably=True,
            hashing_works=True,
            precedent_count=10,
            total_precedents=10,
            precedent_ratio=Fraction(1, 1),
            grounding_model="G5",
            lawvere_fixed_point_exists=True,
        )
        assert check_all_precedents_satisfied(state)[0] is True
        assert check_consistent_reality(state)[0] is True
        assert check_structural_order(state)[0] is True
        assert check_deterministic_causality(state)[0] is True
        assert check_lawvere_convergence(state)[0] is True
        assert check_operational_necessities(state)[0] is True

    def test_fail_state(self):
        state = OntologicalState(
            reality_consistent=False,
            structural_order_present=False,
            deterministic_causality=False,
            truth_anchorable=True,
            knowledge_possible=True,
            patterns_detectable=True,
            code_executes_predictably=False,
            hashing_works=True,
            precedent_count=8,
            total_precedents=10,
            precedent_ratio=Fraction(4, 5),
            grounding_model="G5",
            lawvere_fixed_point_exists=False,
        )
        assert check_all_precedents_satisfied(state)[0] is False
        assert check_consistent_reality(state)[0] is False
        assert check_structural_order(state)[0] is False
        assert check_deterministic_causality(state)[0] is False
        assert check_lawvere_convergence(state)[0] is False
        assert check_operational_necessities(state)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
