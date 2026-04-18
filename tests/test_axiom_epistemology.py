"""Tests for axioms/epistemology.py."""

from fractions import Fraction

import pytest

from axioms.epistemology import (
    Claim,
    check_bayesian_update_consistency,
    check_epistemic_closure,
    check_gettier_immunity,
    check_information_gain_positivity,
    check_popperian_falsifiability,
    run_all_invariants,
)


def _make_nominal() -> Claim:
    """Return a nominal claim that passes all checks."""
    prior = Fraction(1, 5)
    likelihood = Fraction(1, 2)
    evidence_probability = Fraction(1, 10)
    posterior = prior * likelihood / evidence_probability  # = 1
    return Claim(
        name="test_nominal",
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


# ---------------------------------------------------------------------------
# Pass-path tests
# ---------------------------------------------------------------------------

def test_popperian_falsifiability_pass() -> None:
    """Claim with a falsifying condition should pass."""
    ok, proof = check_popperian_falsifiability(_make_nominal())
    assert ok is True
    assert proof.is_valid()


def test_bayesian_update_consistency_pass() -> None:
    """Claim whose posterior equals prior*likelihood/evidence should pass."""
    ok, proof = check_bayesian_update_consistency(_make_nominal())
    assert ok is True
    assert proof.is_valid()


def test_information_gain_positivity_pass() -> None:
    """Claim where final_entropy <= initial_entropy should pass."""
    ok, proof = check_information_gain_positivity(_make_nominal())
    assert ok is True
    assert proof.is_valid()


def test_epistemic_closure_pass() -> None:
    """Claim that satisfies K(A) ∧ (A→B) → K(B) should pass."""
    ok, proof = check_epistemic_closure(_make_nominal())
    assert ok is True
    assert proof.is_valid()


def test_gettier_immunity_pass() -> None:
    """Claim without a Gettier situation should pass."""
    ok, proof = check_gettier_immunity(_make_nominal())
    assert ok is True
    assert proof.is_valid()


# ---------------------------------------------------------------------------
# Fail-path tests
# ---------------------------------------------------------------------------

def test_popperian_falsifiability_fail() -> None:
    """Claim without a falsifying condition should fail."""
    c = Claim(
        **{**_make_nominal().__dict__, "has_falsifying_condition": False},
    )
    ok, proof = check_popperian_falsifiability(c)
    assert ok is False
    assert proof.is_valid()


def test_bayesian_update_consistency_fail_wrong_posterior() -> None:
    """Claim with an incorrect posterior should fail."""
    nominal = _make_nominal()
    c = Claim(
        **{**nominal.__dict__, "posterior": Fraction(1, 2)},
    )
    ok, proof = check_bayesian_update_consistency(c)
    assert ok is False
    assert proof.is_valid()


def test_bayesian_update_consistency_fail_zero_evidence() -> None:
    """Claim with evidence_probability == 0 should fail (undefined)."""
    nominal = _make_nominal()
    c = Claim(
        **{**nominal.__dict__, "evidence_probability": Fraction(0)},
    )
    ok, proof = check_bayesian_update_consistency(c)
    assert ok is False
    assert proof.is_valid()


def test_information_gain_positivity_fail() -> None:
    """Claim where final_entropy > initial_entropy should fail."""
    nominal = _make_nominal()
    c = Claim(
        **{**nominal.__dict__, "final_entropy": Fraction(5), "initial_entropy": Fraction(2)},
    )
    ok, proof = check_information_gain_positivity(c)
    assert ok is False
    assert proof.is_valid()


def test_epistemic_closure_fail() -> None:
    """Claim where K(A) ∧ (A→B) but ¬K(B) should fail."""
    nominal = _make_nominal()
    c = Claim(
        **{**nominal.__dict__, "agent_knows_consequent": False},
    )
    ok, proof = check_epistemic_closure(c)
    assert ok is False
    assert proof.is_valid()


def test_gettier_immunity_fail() -> None:
    """Claim that is justified + true + has a Gettier situation should fail."""
    nominal = _make_nominal()
    c = Claim(
        **{**nominal.__dict__, "has_gettier_situation": True},
    )
    ok, proof = check_gettier_immunity(c)
    assert ok is False
    assert proof.is_valid()


# ---------------------------------------------------------------------------
# run_all_invariants
# ---------------------------------------------------------------------------

def test_run_all_invariants_pass() -> None:
    """run_all_invariants() must produce all-True results for nominal claim."""
    results = run_all_invariants()
    assert len(results) == 5
    for name, ok, proof in results:
        assert ok is True, f"Invariant {name!r} failed"
        assert proof.is_valid(), f"Proof for {name!r} is invalid"
