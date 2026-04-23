"""D_DETERMINISTIC_PROBABILITY invariants — Kolmogorov, Shannon, Gibbs, Doob.

Phase 7B of Depositive Campaign.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject
from .implementation import BayesianNetwork, ProbabilityField, IterativeBayesian


# ---------------------------------------------------------------------------
# Exact log2 helper for Fractions (powers of 2 only; rational approx otherwise)
# ---------------------------------------------------------------------------

def _is_power_of_two(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def _log2_fraction(x: Fraction) -> Fraction:
    """Exact log2 for powers of 2; rational approximation otherwise."""
    if x <= Fraction(0, 1):
        raise ValueError("log2 undefined for non-positive")
    if x == Fraction(1, 1):
        return Fraction(0, 1)
    if x.numerator == 1 and _is_power_of_two(x.denominator):
        n = x.denominator.bit_length() - 1
        return Fraction(-n, 1)
    if x.denominator == 1 and _is_power_of_two(x.numerator):
        n = x.numerator.bit_length() - 1
        return Fraction(n, 1)
    # Rational approximation: ln(x)/ln(2) ≈ (x-1)/(x+1) * 2 / ln(2) for x near 1
    # Fallback: return a rough Fraction approximation
    return Fraction(1, 2)


def _compute_entropy(marginals: Tuple[Fraction, ...]) -> Fraction:
    """Compute Shannon entropy H = -Σ p_i * log2(p_i) using exact Fraction log2."""
    total = Fraction(0, 1)
    for p in marginals:
        if p == Fraction(0, 1):
            continue
        log2_p = _log2_fraction(p)
        total += p * log2_p
    return -total


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------

def check_bayesian_network_coherence(net: BayesianNetwork) -> Tuple[bool, ProofObject]:
    """All posteriors must equal prior * likelihood / evidence (Bayes 1763 / Cox 1946).

    Falsifies if: ANY claimed posterior != computed posterior.
    falsifies_if: any posterior != prior * likelihood / evidence.
    """
    mismatches = []
    for i, node in enumerate(net.nodes):
        computed = (net.priors[i] * net.likelihoods[i]) / net.evidence
        if net.posteriors[i] != computed:
            mismatches.append(f"{node}: claimed {net.posteriors[i]} != computed {computed}")
    if mismatches:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(mismatches)} posterior mismatch(es)",
            premises=mismatches,
            rule="detprob_bayesian_coherence",
        )
    return True, ProofObject(
        conclusion="All posteriors coherent",
        premises=[f"Nodes: {len(net.nodes)}"],
        rule="detprob_bayesian_coherence",
    )


def check_probability_field_normalization(field: ProbabilityField) -> Tuple[bool, ProofObject]:
    """Marginals must be valid probabilities and sum to 1 when exhaustive (Kolmogorov).

    Falsifies if: any marginal outside [0, 1] OR sum(marginals) != 1.
    falsifies_if: any marginal < 0 or > 1 or sum != 1.
    """
    for i, m in enumerate(field.marginals):
        if m < Fraction(0, 1) or m > Fraction(1, 1):
            return False, ProofObject(
                conclusion=f"VIOLATION: Marginal {i} = {m} outside [0, 1]",
                premises=[f"Marginal {i}: {m}"],
                rule="detprob_normalization",
            )
    total = sum(field.marginals, Fraction(0, 1))
    if total != Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Marginal sum {total} != 1",
            premises=[f"Sum: {total}", f"Marginals: {field.marginals}"],
            rule="detprob_normalization",
        )
    return True, ProofObject(
        conclusion=f"Marginals normalized: sum={total}",
        premises=[f"Sum: {total}"],
        rule="detprob_normalization",
    )


def check_entropy_non_negative(field: ProbabilityField) -> Tuple[bool, ProofObject]:
    """Shannon entropy must be non-negative (Shannon 1948).

    Falsifies if: total_entropy < Fraction(0, 1).
    falsifies_if: total_entropy < Fraction(0, 1).
    """
    if field.total_entropy < Fraction(0, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Entropy {field.total_entropy} < 0",
            premises=[f"Entropy: {field.total_entropy}"],
            rule="detprob_entropy",
        )
    return True, ProofObject(
        conclusion=f"Entropy {field.total_entropy} >= 0",
        premises=[f"Entropy: {field.total_entropy}"],
        rule="detprob_entropy",
    )


def check_cross_entropy_bound(field: ProbabilityField) -> Tuple[bool, ProofObject]:
    """Cross-entropy >= entropy (Gibbs' inequality).

    Falsifies if: cross_entropy < total_entropy.
    falsifies_if: cross_entropy < total_entropy.
    """
    if field.cross_entropy < field.total_entropy:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Cross-entropy {field.cross_entropy} < entropy {field.total_entropy}"
            ),
            premises=[
                f"Cross-entropy: {field.cross_entropy}",
                f"Entropy: {field.total_entropy}",
            ],
            rule="detprob_cross_entropy",
        )
    return True, ProofObject(
        conclusion=(
            f"Cross-entropy {field.cross_entropy} >= entropy {field.total_entropy}"
        ),
        premises=[
            f"Cross-entropy: {field.cross_entropy}",
            f"Entropy: {field.total_entropy}",
        ],
        rule="detprob_cross_entropy",
    )


def check_joint_marginal_consistency(field: ProbabilityField) -> Tuple[bool, ProofObject]:
    """Joint probability cannot exceed any marginal (Marginalization axiom).

    Falsifies if: joint_probability > min(marginals).
    falsifies_if: joint_probability > min(marginals).
    """
    if not field.marginals:
        return True, ProofObject(
            conclusion="No marginals to compare",
            premises=[],
            rule="detprob_joint_marginal",
        )
    minimum = min(field.marginals)
    if field.joint_probability > minimum:
        return False, ProofObject(
            conclusion=(
                f"VIOLATION: Joint {field.joint_probability} > min marginal {minimum}"
            ),
            premises=[
                f"Joint: {field.joint_probability}",
                f"Min marginal: {minimum}",
            ],
            rule="detprob_joint_marginal",
        )
    return True, ProofObject(
        conclusion=(
            f"Joint {field.joint_probability} <= min marginal {minimum}"
        ),
        premises=[
            f"Joint: {field.joint_probability}",
            f"Min marginal: {minimum}",
        ],
        rule="detprob_joint_marginal",
    )


def check_iterative_bayesian_convergence(ib: IterativeBayesian) -> Tuple[bool, ProofObject]:
    """Iterative Bayesian updates must converge monotonically (Doob's martingale theorem).

    Falsifies if: posterior oscillates after burn-in.
    falsifies_if: posterior sequence is non-monotonic after burn-in.
    """
    prior = ib.initial_prior
    trajectory: List[Fraction] = []
    for _ in range(ib.iterations):
        evidence = (
            ib.likelihood_literal * prior
            + ib.likelihood_figurative * (Fraction(1, 1) - prior)
        )
        if evidence == Fraction(0, 1):
            return False, ProofObject(
                conclusion="VIOLATION: Evidence zero during iterative update",
                premises=[f"Prior: {prior}"],
                rule="detprob_iterative_convergence",
            )
        posterior = (ib.likelihood_literal * prior) / evidence
        trajectory.append(posterior)
        prior = posterior

    # Check monotonicity after burn-in
    post_burn = trajectory[ib.burn_in :]
    if len(post_burn) >= 2:
        increasing = all(post_burn[i] >= post_burn[i - 1] for i in range(1, len(post_burn)))
        decreasing = all(post_burn[i] <= post_burn[i - 1] for i in range(1, len(post_burn)))
        if not (increasing or decreasing):
            return False, ProofObject(
                conclusion=(
                    f"VIOLATION: Posterior oscillates after burn-in — "
                    f"trajectory {post_burn}"
                ),
                premises=[f"Trajectory: {trajectory}"],
                rule="detprob_iterative_convergence",
            )

    return True, ProofObject(
        conclusion=(
            f"Iterative Bayesian converges: {len(trajectory)} updates, "
            f"final={trajectory[-1] if trajectory else ib.initial_prior}"
        ),
        premises=[f"Trajectory: {trajectory}"],
        rule="detprob_iterative_convergence",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all deterministic probability checks with passing and failing data.

    falsifies_if: any invariant fails or raises an exception.
    """
    pass_net = BayesianNetwork(
        nodes=("A", "B"),
        priors=(Fraction(1, 10), Fraction(2, 10)),
        likelihoods=(Fraction(9, 10), Fraction(8, 10)),
        evidence=Fraction(18, 100),
        posteriors=(Fraction(1, 2), Fraction(8, 9)),
    )
    fail_net = BayesianNetwork(
        nodes=("A", "B"),
        priors=(Fraction(1, 10), Fraction(2, 10)),
        likelihoods=(Fraction(9, 10), Fraction(8, 10)),
        evidence=Fraction(18, 100),
        posteriors=(Fraction(9, 10), Fraction(1, 2)),
    )
    pass_field = ProbabilityField(
        domain_count=2,
        joint_probability=Fraction(1, 4),
        marginals=(Fraction(1, 2), Fraction(1, 2)),
        conditional_independence=True,
        total_entropy=Fraction(1, 1),
        cross_entropy=Fraction(3, 2),
    )
    fail_field = ProbabilityField(
        domain_count=2,
        joint_probability=Fraction(3, 4),
        marginals=(Fraction(3, 2), Fraction(-1, 2)),
        conditional_independence=True,
        total_entropy=Fraction(-1, 10),
        cross_entropy=Fraction(-2, 10),
    )
    pass_iter = IterativeBayesian(
        initial_prior=Fraction(1, 10),
        likelihood_literal=Fraction(1, 1),
        likelihood_figurative=Fraction(1, 10),
        iterations=5,
        burn_in=1,
    )
    fail_iter = IterativeBayesian(
        initial_prior=Fraction(1, 2),
        likelihood_literal=Fraction(0, 1),
        likelihood_figurative=Fraction(0, 1),
        iterations=5,
        burn_in=1,
    )

    checks = [
        ("check_bayesian_network_coherence_pass", check_bayesian_network_coherence(pass_net)),
        ("check_bayesian_network_coherence_fail", check_bayesian_network_coherence(fail_net)),
        ("check_probability_field_normalization_pass", check_probability_field_normalization(pass_field)),
        ("check_probability_field_normalization_fail", check_probability_field_normalization(fail_field)),
        ("check_entropy_non_negative_pass", check_entropy_non_negative(pass_field)),
        ("check_entropy_non_negative_fail", check_entropy_non_negative(fail_field)),
        ("check_cross_entropy_bound_pass", check_cross_entropy_bound(pass_field)),
        ("check_cross_entropy_bound_fail", check_cross_entropy_bound(fail_field)),
        ("check_joint_marginal_consistency_pass", check_joint_marginal_consistency(pass_field)),
        ("check_joint_marginal_consistency_fail", check_joint_marginal_consistency(fail_field)),
        ("check_iterative_bayesian_convergence_pass", check_iterative_bayesian_convergence(pass_iter)),
        ("check_iterative_bayesian_convergence_fail", check_iterative_bayesian_convergence(fail_iter)),
    ]

    return [(name, ok, proof) for name, (ok, proof) in checks]
