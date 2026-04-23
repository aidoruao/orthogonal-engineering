"""D_DETERMINISTIC_PROBABILITY implementation — Bayesian networks, entropy, convergence.

Phase 7B of Depositive Campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Tuple


@dataclass(frozen=True)
class BayesianNetwork:
    """Multi-node Bayesian network with exact Fraction inference.

    falsifies_if: evidence == Fraction(0, 1).
    falsifies_if: len(priors) != len(nodes) or len(likelihoods) != len(nodes).
    """
    nodes: Tuple[str, ...]
    priors: Tuple[Fraction, ...]
    likelihoods: Tuple[Fraction, ...]
    evidence: Fraction
    posteriors: Tuple[Fraction, ...]


@dataclass(frozen=True)
class ProbabilityField:
    """Cross-domain probability field with entropy measures.

    falsifies_if: any marginal < Fraction(0, 1) or > Fraction(1, 1).
    """
    domain_count: int
    joint_probability: Fraction
    marginals: Tuple[Fraction, ...]
    conditional_independence: bool
    total_entropy: Fraction
    cross_entropy: Fraction


@dataclass(frozen=True)
class IterativeBayesian:
    """Iterative Bayesian update trajectory for convergence testing.

    falsifies_if: initial_prior not in [0, 1].
    """
    initial_prior: Fraction
    likelihood_literal: Fraction
    likelihood_figurative: Fraction
    iterations: int
    burn_in: int


DOMAIN_METADATA = {
    "id": "DETERMINISTIC_PROBABILITY",
    "claim_model": "BayesianNetwork / ProbabilityField / IterativeBayesian",
    "check_functions": [
        "check_bayesian_network_coherence",
        "check_probability_field_normalization",
        "check_entropy_non_negative",
        "check_cross_entropy_bound",
        "check_joint_marginal_consistency",
        "check_iterative_bayesian_convergence",
    ],
}
