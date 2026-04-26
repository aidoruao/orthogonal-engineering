"""Tests for D_ARXIV_INV_LIKELIHOOD_HACKING Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_likelihood_hacking.implementation import (
    ProbabilisticProgram,
    TrainingSetup,
    LikelihoodHackingClaim,
)
from domains.d_arxiv_inv_likelihood_hacking.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_safe_program():
    return ProbabilisticProgram(
        program_name="safestan_model",
        language_fragment="L_safe",
        enforces_normalisation=True,
        has_syntactic_safety_checks=True,
    )


def make_unsafe_program():
    return ProbabilisticProgram(
        program_name="pymc_model",
        language_fragment="full_pymc",
        enforces_normalisation=False,
        has_syntactic_safety_checks=False,
    )


def make_rl_training():
    return TrainingSetup(
        uses_rl_training=True,
        optimisation_pressure=Fraction(9, 10),
        violation_rate_threshold=Fraction(1, 100),
    )


def make_safe_claim():
    return LikelihoodHackingClaim(
        program=make_safe_program(),
        training=make_rl_training(),
        observed_violation_rate=Fraction(0),
    )


def make_bad_claim():
    return LikelihoodHackingClaim(
        program=make_unsafe_program(),
        training=make_rl_training(),
        observed_violation_rate=Fraction(0),
    )


def make_high_violation_claim():
    return LikelihoodHackingClaim(
        program=make_safe_program(),
        training=make_rl_training(),
        observed_violation_rate=Fraction(10),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_high_violation():
    claim = make_high_violation_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "exceeds threshold" in proof.conclusion


def test_check_domain_restriction_satisfied_pass():
    claim = make_safe_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is True
    assert "Domain restriction satisfied" in proof.conclusion


def test_check_domain_restriction_satisfied_fail():
    claim = make_bad_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is False
    assert "Domain restriction not satisfied" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_vacuous():
    claim = make_safe_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is True
    assert "vacuous" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass") or name.endswith("_vacuous"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
