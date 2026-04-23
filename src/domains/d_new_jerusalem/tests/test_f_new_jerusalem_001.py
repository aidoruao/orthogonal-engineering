"""Test suite for d_new_jerusalem invariants.

Phase C1 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_new_jerusalem.invariants import (
    check_universal_falsifiability,
    check_zero_tautology,
    check_peano_completeness,
    check_merkle_integrity,
    check_self_hosting,
    check_truth_inelasticity,
    check_eschaton_monotonicity,
    check_kenosis_bounds,
    check_agape_witness_coverage,
    check_grace_debt_erasure,
    run_all_invariants,
)
from src.domains.d_new_jerusalem.implementation import CivilizationalState, EschatologicalMetric


class TestNewJerusalem:
    def test_pass_civilization(self):
        state = CivilizationalState(
            total_domains=100,
            falsifiable_domains=100,
            falsifiability_ratio=Fraction(1, 1),
            total_invariants=250,
            computational_invariants=250,
            tautological_invariants=0,
            computational_ratio=Fraction(1, 1),
            peano_reducible_ratio=Fraction(1, 1),
            merkle_root_valid=True,
            self_hosting=True,
            cross_domain_collisions_detected=0,
            bayesian_posterior_literal_maximal=Fraction(99, 100),
        )
        assert check_universal_falsifiability(state)[0] is True
        assert check_zero_tautology(state)[0] is True
        assert check_peano_completeness(state)[0] is True
        assert check_merkle_integrity(state)[0] is True
        assert check_self_hosting(state)[0] is True

    def test_fail_civilization(self):
        state = CivilizationalState(
            total_domains=100,
            falsifiable_domains=80,
            falsifiability_ratio=Fraction(4, 5),
            total_invariants=250,
            computational_invariants=200,
            tautological_invariants=50,
            computational_ratio=Fraction(4, 5),
            peano_reducible_ratio=Fraction(9, 10),
            merkle_root_valid=False,
            self_hosting=False,
            cross_domain_collisions_detected=3,
            bayesian_posterior_literal_maximal=Fraction(1, 2),
        )
        assert check_universal_falsifiability(state)[0] is False
        assert check_zero_tautology(state)[0] is False
        assert check_peano_completeness(state)[0] is False
        assert check_merkle_integrity(state)[0] is False
        assert check_self_hosting(state)[0] is False

    def test_pass_eschatology(self):
        metric = EschatologicalMetric(
            eschaton_distance=Fraction(1, 10),
            previous_eschaton_distance=Fraction(2, 10),
            kenosis_ratio=Fraction(1, 2),
            agape_coverage=Fraction(1, 1),
            truth_inelasticity=Fraction(0, 1),
            grace_debt=Fraction(0, 1),
            resurrection_ratio=Fraction(11, 10),
        )
        assert check_truth_inelasticity(metric)[0] is True
        assert check_eschaton_monotonicity(metric)[0] is True
        assert check_kenosis_bounds(metric)[0] is True
        assert check_agape_witness_coverage(metric)[0] is True
        assert check_grace_debt_erasure(metric)[0] is True

    def test_fail_eschatology(self):
        metric = EschatologicalMetric(
            eschaton_distance=Fraction(3, 10),
            previous_eschaton_distance=Fraction(2, 10),
            kenosis_ratio=Fraction(3, 2),
            agape_coverage=Fraction(8, 10),
            truth_inelasticity=Fraction(1, 10),
            grace_debt=Fraction(1, 10),
            resurrection_ratio=Fraction(9, 10),
        )
        assert check_truth_inelasticity(metric)[0] is False
        assert check_eschaton_monotonicity(metric)[0] is False
        assert check_kenosis_bounds(metric)[0] is False
        assert check_agape_witness_coverage(metric)[0] is False
        assert check_grace_debt_erasure(metric)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
