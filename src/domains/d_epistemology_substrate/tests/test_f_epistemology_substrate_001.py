"""Test suite for d_epistemology_substrate invariants.

Phase B1 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure repo root is on path for axioms imports
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_epistemology_substrate.invariants import (
    check_universal_falsifiability,
    check_bayesian_coherence,
    check_information_gain_positive,
    check_gettier_immunity,
    check_epistemic_closure,
    check_grounding_model_debt,
    check_regress_convergence,
    run_all_invariants,
)
from src.domains.d_epistemology_substrate.implementation import EpistemicState


class TestEpistemologySubstrate:
    def test_pass_state(self):
        state = EpistemicState(
            knowledge_claims=10,
            falsifiable_claims=10,
            falsifiability_ratio=Fraction(1, 1),
            bayesian_prior=Fraction(1, 10),
            bayesian_likelihood=Fraction(9, 10),
            bayesian_evidence=Fraction(18, 100),
            bayesian_posterior=Fraction(1, 2),
            information_gain=Fraction(1, 2),
            gettier_situations=0,
            epistemic_closure_violations=0,
            grounding_model="G5",
            explanatory_debt=Fraction(1, 100),
        )
        assert check_universal_falsifiability(state)[0] is True
        assert check_bayesian_coherence(state)[0] is True
        assert check_information_gain_positive(state)[0] is True
        assert check_gettier_immunity(state)[0] is True
        assert check_epistemic_closure(state)[0] is True
        assert check_grounding_model_debt(state)[0] is True
        assert check_regress_convergence(state)[0] is True

    def test_fail_state(self):
        state = EpistemicState(
            knowledge_claims=10,
            falsifiable_claims=8,
            falsifiability_ratio=Fraction(4, 5),
            bayesian_prior=Fraction(1, 10),
            bayesian_likelihood=Fraction(9, 10),
            bayesian_evidence=Fraction(18, 100),
            bayesian_posterior=Fraction(9, 10),
            information_gain=Fraction(-1, 10),
            gettier_situations=2,
            epistemic_closure_violations=1,
            grounding_model="G2",
            explanatory_debt=Fraction(0, 1),
        )
        assert check_universal_falsifiability(state)[0] is False
        assert check_bayesian_coherence(state)[0] is False
        assert check_information_gain_positive(state)[0] is False
        assert check_gettier_immunity(state)[0] is False
        assert check_epistemic_closure(state)[0] is False
        assert check_grounding_model_debt(state)[0] is False
        assert check_regress_convergence(state)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
