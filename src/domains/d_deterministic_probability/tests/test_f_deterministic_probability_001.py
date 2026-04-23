"""Test suite for d_deterministic_probability invariants.

Phase 7B of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_deterministic_probability.invariants import (
    check_bayesian_network_coherence,
    check_probability_field_normalization,
    check_entropy_non_negative,
    check_cross_entropy_bound,
    check_joint_marginal_consistency,
    check_iterative_bayesian_convergence,
    run_all_invariants,
)
from src.domains.d_deterministic_probability.implementation import (
    BayesianNetwork, ProbabilityField, IterativeBayesian
)


class TestDeterministicProbability:
    def test_pass_cases(self):
        net = BayesianNetwork(
            nodes=("A", "B"),
            priors=(Fraction(1, 10), Fraction(2, 10)),
            likelihoods=(Fraction(9, 10), Fraction(8, 10)),
            evidence=Fraction(18, 100),
            posteriors=(Fraction(1, 2), Fraction(8, 9)),
        )
        field = ProbabilityField(
            domain_count=2, joint_probability=Fraction(1, 4),
            marginals=(Fraction(1, 2), Fraction(1, 2)),
            conditional_independence=True,
            total_entropy=Fraction(1, 1), cross_entropy=Fraction(3, 2),
        )
        ib = IterativeBayesian(
            initial_prior=Fraction(1, 10),
            likelihood_literal=Fraction(1, 1),
            likelihood_figurative=Fraction(1, 10),
            iterations=5, burn_in=1,
        )
        assert check_bayesian_network_coherence(net)[0] is True
        assert check_probability_field_normalization(field)[0] is True
        assert check_entropy_non_negative(field)[0] is True
        assert check_cross_entropy_bound(field)[0] is True
        assert check_joint_marginal_consistency(field)[0] is True
        assert check_iterative_bayesian_convergence(ib)[0] is True

    def test_fail_cases(self):
        net = BayesianNetwork(
            nodes=("A", "B"),
            priors=(Fraction(1, 10), Fraction(2, 10)),
            likelihoods=(Fraction(9, 10), Fraction(8, 10)),
            evidence=Fraction(18, 100),
            posteriors=(Fraction(9, 10), Fraction(1, 2)),
        )
        field = ProbabilityField(
            domain_count=2, joint_probability=Fraction(3, 4),
            marginals=(Fraction(3, 2), Fraction(-1, 2)),
            conditional_independence=True,
            total_entropy=Fraction(-1, 10), cross_entropy=Fraction(-2, 10),
        )
        ib = IterativeBayesian(
            initial_prior=Fraction(1, 2),
            likelihood_literal=Fraction(0, 1),
            likelihood_figurative=Fraction(0, 1),
            iterations=5, burn_in=1,
        )
        assert check_bayesian_network_coherence(net)[0] is False
        assert check_probability_field_normalization(field)[0] is False
        assert check_entropy_non_negative(field)[0] is False
        assert check_cross_entropy_bound(field)[0] is False
        assert check_joint_marginal_consistency(field)[0] is False
        assert check_iterative_bayesian_convergence(ib)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, ok, proof in results:
            assert isinstance(ok, bool), f"{name}: {proof.conclusion}"
