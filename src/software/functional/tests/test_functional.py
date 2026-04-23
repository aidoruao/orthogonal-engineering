"""Test suite for functional paradigm invariants.

Phase 3A of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.software.functional.invariants import (
    check_referential_transparency,
    check_no_side_effects,
    check_beta_reduction_termination,
    check_hindley_milner_principal,
    check_fold_associativity,
    check_closure_capture,
    run_all_invariants,
)
from src.software.functional.implementation import (
    LambdaTerm, PureFunction, TypeInference, FoldOperation
)


class TestFunctional:
    def test_pass_cases(self):
        func = PureFunction(
            input_hash="a" * 64, output_hash="b" * 64,
            side_effects=0, calls_with_same_input=5, outputs_for_same_input=5,
        )
        term = LambdaTerm(
            free_variables=frozenset(), bound_variables=frozenset({"x", "y"}),
            beta_reductions=3, is_normal_form=True,
        )
        inf = TypeInference(
            term_id="t1", principal_type="Int -> Int", has_principal_type=True,
            type_variables=1, constraints_solved=4, constraints_total=4,
        )
        fold = FoldOperation(
            elements=4, associative=True, commutative=True, identity_exists=True,
            fold_left_result=Fraction(10, 1), fold_right_result=Fraction(10, 1),
        )
        assert check_referential_transparency(func)[0] is True
        assert check_no_side_effects(func)[0] is True
        assert check_beta_reduction_termination(term)[0] is True
        assert check_hindley_milner_principal(inf)[0] is True
        assert check_fold_associativity(fold)[0] is True
        assert check_closure_capture(term)[0] is True

    def test_fail_cases(self):
        func = PureFunction(
            input_hash="a" * 64, output_hash="c" * 64,
            side_effects=2, calls_with_same_input=5, outputs_for_same_input=3,
        )
        term = LambdaTerm(
            free_variables=frozenset({"z"}), bound_variables=frozenset({"x"}),
            beta_reductions=1500, is_normal_form=False,
        )
        closed_term = LambdaTerm(
            free_variables=frozenset({"z"}), bound_variables=frozenset({"x"}),
            beta_reductions=2, is_normal_form=True,
        )
        inf = TypeInference(
            term_id="t2", principal_type="?", has_principal_type=True,
            type_variables=2, constraints_solved=2, constraints_total=5,
        )
        fold = FoldOperation(
            elements=4, associative=True, commutative=False, identity_exists=True,
            fold_left_result=Fraction(10, 1), fold_right_result=Fraction(12, 1),
        )
        assert check_referential_transparency(func)[0] is False
        assert check_no_side_effects(func)[0] is False
        assert check_beta_reduction_termination(term)[0] is False
        assert check_hindley_milner_principal(inf)[0] is False
        assert check_fold_associativity(fold)[0] is False
        assert check_closure_capture(closed_term)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
