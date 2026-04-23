"""Test suite for logic paradigm invariants.

Phase 3C of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.software.logic.invariants import (
    check_horn_clause_definite,
    check_unification_occurs,
    check_resolution_soundness,
    check_resolution_completeness,
    check_constraint_arc_consistency,
    check_negation_as_failure,
    run_all_invariants,
)
from src.software.logic.implementation import (
    HornClause, UnificationResult, ResolutionProof, ConstraintSatisfaction
)


class TestLogic:
    def test_pass_cases(self):
        clause = HornClause(
            head="P", body=("Q", "R"), is_definite=True, is_goal=False, is_fact=False,
        )
        unif = UnificationResult(
            term_a="f(X)", term_b="f(a)", unifier_exists=True,
            substitution_count=1, occurs_check_passed=True,
        )
        proof = ResolutionProof(
            clauses=4, resolution_steps=3, empty_clause_derived=True,
            is_sound=True, is_complete=True,
        )
        csp = ConstraintSatisfaction(
            variables=3, constraints=2, domain_size=Fraction(8, 1),
            solutions_found=2, arc_consistent=True,
        )
        assert check_horn_clause_definite(clause)[0] is True
        assert check_unification_occurs(unif)[0] is True
        assert check_resolution_soundness(proof)[0] is True
        assert check_resolution_completeness(proof)[0] is True
        assert check_constraint_arc_consistency(csp)[0] is True
        assert check_negation_as_failure(clause)[0] is True

    def test_fail_cases(self):
        clause = HornClause(
            head="", body=("Q",), is_definite=True, is_goal=True, is_fact=True,
        )
        unif = UnificationResult(
            term_a="f(X)", term_b="f(g(X))", unifier_exists=True,
            substitution_count=1, occurs_check_passed=False,
        )
        sound_proof = ResolutionProof(
            clauses=4, resolution_steps=3, empty_clause_derived=True,
            is_sound=False, is_complete=False,
        )
        complete_proof = ResolutionProof(
            clauses=4, resolution_steps=3, empty_clause_derived=True,
            is_sound=True, is_complete=False,
        )
        csp = ConstraintSatisfaction(
            variables=3, constraints=2, domain_size=Fraction(8, 1),
            solutions_found=0, arc_consistent=True,
        )
        assert check_horn_clause_definite(clause)[0] is False
        assert check_unification_occurs(unif)[0] is False
        assert check_resolution_soundness(sound_proof)[0] is False
        assert check_resolution_completeness(complete_proof)[0] is False
        assert check_constraint_arc_consistency(csp)[0] is False
        assert check_negation_as_failure(clause)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
