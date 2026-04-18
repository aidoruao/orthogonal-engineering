"""axioms/epistemology.py — Epistemological invariant checks.

Implements Popperian falsifiability, Bayesian update consistency,
information gain positivity, epistemic closure (modal K), and
Gettier immunity checks with full ProofObject evidence.

Standard: Yeshua / Orthogonal Engineering
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject


@dataclass(frozen=True)
class Claim:
    """A scientific/epistemic claim with its domain-restricting conditions."""

    name: str
    has_falsifying_condition: bool  # True if there exists a condition under which it returns False
    prior: Fraction  # prior probability in [0,1]
    likelihood: Fraction  # P(evidence|hypothesis) in [0,1]
    evidence_probability: Fraction  # P(evidence) in [0,1] — must be > 0
    posterior: Fraction  # claimed posterior
    initial_entropy: Fraction  # entropy before observation (in bits)
    final_entropy: Fraction  # entropy after observation (in bits)
    agent_knows_antecedent: bool  # does agent know A?
    antecedent_implies_consequent: bool  # does A -> B hold?
    agent_knows_consequent: bool  # does agent know B?
    is_justified: bool  # is the belief justified?
    is_true: bool  # is the belief true?
    has_gettier_situation: bool  # is there a Gettier-type situation (justified+true but not knowledge)?


def check_popperian_falsifiability(claim: Claim) -> Tuple[bool, ProofObject]:
    """A claim is scientific iff it has a domain-restricting condition under which it returns False.

    Standard: Popper (1959) — The Logic of Scientific Discovery
    Falsifies if: claim.has_falsifying_condition is False (no condition under which claim fails).
    falsifies_if: claim.has_falsifying_condition is False.
    """
    success = claim.has_falsifying_condition
    proof = ProofObject(
        rule="PopperianFalsifiability",
        premises=[
            f"claim.name = {claim.name!r}",
            f"claim.has_falsifying_condition = {claim.has_falsifying_condition}",
        ],
        conclusion=(
            f"Claim {claim.name!r} is scientific: has a falsifying condition"
            if success
            else f"FAIL: Claim {claim.name!r} lacks a falsifying condition — not scientific"
        ),
    )
    return success, proof


def check_bayesian_update_consistency(claim: Claim) -> Tuple[bool, ProofObject]:
    """Posterior = prior * likelihood / evidence_probability (Bayes theorem), exact Fraction arithmetic.

    Standard: Bayes (1763) — An Essay towards solving a Problem in the Doctrine of Chances
    Falsifies if: |claimed_posterior - computed_posterior| > 0 (any deviation).
    falsifies_if: |claimed_posterior - computed_posterior| > 0.
    """
    if claim.evidence_probability == Fraction(0):
        proof = ProofObject(
            rule="BayesianUpdate",
            premises=[
                f"claim.evidence_probability = 0",
                "Division by zero is undefined",
            ],
            conclusion="FAIL: evidence_probability is 0 — Bayesian update undefined",
        )
        return False, proof

    computed_posterior = claim.prior * claim.likelihood / claim.evidence_probability
    success = claim.posterior == computed_posterior
    proof = ProofObject(
        rule="BayesianUpdate",
        premises=[
            f"prior = {claim.prior}",
            f"likelihood = {claim.likelihood}",
            f"evidence_probability = {claim.evidence_probability}",
            f"computed_posterior = {computed_posterior}",
            f"claimed_posterior = {claim.posterior}",
        ],
        conclusion=(
            f"Bayesian update consistent: posterior = {computed_posterior}"
            if success
            else f"FAIL: claimed posterior {claim.posterior} != computed {computed_posterior}"
        ),
    )
    return success, proof


def check_information_gain_positivity(claim: Claim) -> Tuple[bool, ProofObject]:
    """Observation reduces entropy: final_entropy <= initial_entropy.

    Standard: Shannon (1948) — A Mathematical Theory of Communication
    Falsifies if: claim.final_entropy > claim.initial_entropy.
    falsifies_if: claim.final_entropy > claim.initial_entropy.
    """
    success = claim.final_entropy <= claim.initial_entropy
    proof = ProofObject(
        rule="InformationGainPositivity",
        premises=[
            f"initial_entropy = {claim.initial_entropy} bits",
            f"final_entropy = {claim.final_entropy} bits",
            f"delta = {claim.initial_entropy - claim.final_entropy} bits",
        ],
        conclusion=(
            f"Information gain non-negative: H_final ({claim.final_entropy}) <= H_initial ({claim.initial_entropy})"
            if success
            else f"FAIL: entropy increased from {claim.initial_entropy} to {claim.final_entropy}"
        ),
    )
    return success, proof


def check_epistemic_closure(claim: Claim) -> Tuple[bool, ProofObject]:
    """Modal K axiom: if agent knows A and A->B then agent knows B.

    Standard: Hintikka (1962) — Knowledge and Belief (Modal Axiom K)
    Falsifies if: agent_knows_antecedent and antecedent_implies_consequent but not agent_knows_consequent.
    falsifies_if: agent_knows_antecedent and antecedent_implies_consequent and not agent_knows_consequent.
    """
    if claim.agent_knows_antecedent and claim.antecedent_implies_consequent:
        success = claim.agent_knows_consequent
    else:
        success = True  # antecedent of the closure rule is not triggered

    proof = ProofObject(
        rule="EpistemicClosure",
        premises=[
            f"agent_knows_antecedent = {claim.agent_knows_antecedent}",
            f"antecedent_implies_consequent = {claim.antecedent_implies_consequent}",
            f"agent_knows_consequent = {claim.agent_knows_consequent}",
        ],
        conclusion=(
            "Epistemic closure holds: K(A) ∧ (A→B) → K(B)"
            if success
            else "FAIL: K(A) ∧ (A→B) but ¬K(B) — closure violated"
        ),
    )
    return success, proof


def check_gettier_immunity(claim: Claim) -> Tuple[bool, ProofObject]:
    """Justified true belief is not sufficient for knowledge; the Gettier counterexample.

    Standard: Gettier (1963) — Is Justified True Belief Knowledge?
    Falsifies if: is_justified and is_true and has_gettier_situation (JTB is not always knowledge).
    falsifies_if: is_justified and is_true and has_gettier_situation.
    """
    gettier_violation = claim.is_justified and claim.is_true and claim.has_gettier_situation
    success = not gettier_violation
    proof = ProofObject(
        rule="GettierImmunity",
        premises=[
            f"is_justified = {claim.is_justified}",
            f"is_true = {claim.is_true}",
            f"has_gettier_situation = {claim.has_gettier_situation}",
        ],
        conclusion=(
            "No Gettier situation: JTB is not undermined by epistemic luck"
            if success
            else "FAIL: Gettier situation detected — justified + true but not knowledge"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for the epistemology axiom module.

    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.
    """
    # Nominal claim: prior=1/2, likelihood=4/5, evidence=2/5 → posterior=1
    # posterior = (1/2 * 4/5) / (2/5) = (2/5) / (2/5) = 1
    # Use a simpler set: prior=1/4, likelihood=2/3, evidence=1/6 → (1/4 * 2/3)/(1/6) = (1/6)/(1/6) = 1
    # Even simpler: prior=3/10, likelihood=2/3, evidence=1/5 → (3/10*2/3)/(1/5) = (1/5)/(1/5) = 1
    # Let's just make it clean: prior=1/3, likelihood=1/2, evidence=1/6
    # posterior = (1/3 * 1/2) / (1/6) = (1/6)/(1/6) = 1 — but posterior must be in [0,1]
    # Use: prior=1/5, likelihood=1/2, evidence=1/10 → (1/5*1/2)/(1/10) = (1/10)/(1/10) = 1
    # posterior=1 is valid. Good.
    prior = Fraction(1, 5)
    likelihood = Fraction(1, 2)
    evidence_probability = Fraction(1, 10)
    posterior = prior * likelihood / evidence_probability  # = 1

    nominal = Claim(
        name="nominal_epistemology_claim",
        has_falsifying_condition=True,
        prior=prior,
        likelihood=likelihood,
        evidence_probability=evidence_probability,
        posterior=posterior,
        initial_entropy=Fraction(2),
        final_entropy=Fraction(1),
        agent_knows_antecedent=True,
        antecedent_implies_consequent=True,
        agent_knows_consequent=True,
        is_justified=True,
        is_true=True,
        has_gettier_situation=False,
    )

    results: List[Tuple[str, bool, ProofObject]] = []
    checks = [
        ("popperian_falsifiability", check_popperian_falsifiability(nominal)),
        ("bayesian_update_consistency", check_bayesian_update_consistency(nominal)),
        ("information_gain_positivity", check_information_gain_positivity(nominal)),
        ("epistemic_closure", check_epistemic_closure(nominal)),
        ("gettier_immunity", check_gettier_immunity(nominal)),
    ]
    for name, (ok, proof) in checks:
        results.append((name, ok, proof))
    return results
