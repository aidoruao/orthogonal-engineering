"""Tests for D_ARXIV_INV_SAFEMIND Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_safemind.implementation import (
    EnvironmentModel,
    ControllerModel,
    SafeMindClaim,
)
from domains.d_arxiv_inv_safemind.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_bounded_environment():
    return EnvironmentModel(
        perception_noise_variance=Fraction(1, 100),
        friction_coefficient_min=Fraction(1, 2),
        friction_coefficient_max=Fraction(3, 2),
        model_uncertainty_confidence=Fraction(95, 100),
    )


def make_unbounded_environment():
    return EnvironmentModel(
        perception_noise_variance=Fraction(0),
        friction_coefficient_min=Fraction(0),
        friction_coefficient_max=Fraction(10),
        model_uncertainty_confidence=Fraction(0),
    )


def make_safe_controller():
    return ControllerModel(
        controller_name="safemind",
        uses_variance_aware_barrier=True,
        uses_differentiable_qp=True,
        has_meta_adaptive_risk=True,
    )


def make_naive_controller():
    return ControllerModel(
        controller_name="naive_rl",
        uses_variance_aware_barrier=False,
        uses_differentiable_qp=False,
        has_meta_adaptive_risk=False,
    )


def make_safe_claim():
    return SafeMindClaim(
        environment=make_bounded_environment(),
        controller=make_safe_controller(),
        safety_violation_rate=Fraction(1, 100),
        safety_threshold=Fraction(5, 100),
    )


def make_bad_claim():
    return SafeMindClaim(
        environment=make_unbounded_environment(),
        controller=make_naive_controller(),
        safety_violation_rate=Fraction(1, 10),
        safety_threshold=Fraction(5, 100),
    )


def make_over_threshold_claim():
    return SafeMindClaim(
        environment=make_bounded_environment(),
        controller=make_safe_controller(),
        safety_violation_rate=Fraction(10),
        safety_threshold=Fraction(5, 100),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_over_threshold():
    claim = make_over_threshold_claim()
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
