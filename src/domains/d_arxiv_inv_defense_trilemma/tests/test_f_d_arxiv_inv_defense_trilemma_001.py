"""Tests for D_ARXIV_INV_DEFENSE_TRILEMMA Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_defense_trilemma.implementation import (
    DefenseModel,
    DefenseTrilemmaClaim,
)
from domains.d_arxiv_inv_defense_trilemma.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_discrete_defense():
    return DefenseModel(
        defense_name="discrete_allow_list",
        is_continuous=False,
        preserves_utility=False,
        is_complete=True,
        prompt_space_finite=True,
        uses_allow_list=True,
    )


def make_unrestricted_defense():
    return DefenseModel(
        defense_name="continuous_wrapper",
        is_continuous=True,
        preserves_utility=True,
        is_complete=True,
        prompt_space_finite=False,
        uses_allow_list=False,
    )


def make_safe_claim():
    return DefenseTrilemmaClaim(
        defense=make_discrete_defense(),
        unsafe_inputs_detected=Fraction(99),
        total_inputs=Fraction(100),
        safety_threshold=Fraction(9, 10),
    )


def make_unrestricted_claim():
    return DefenseTrilemmaClaim(
        defense=make_unrestricted_defense(),
        unsafe_inputs_detected=Fraction(99),
        total_inputs=Fraction(100),
        safety_threshold=Fraction(9, 10),
    )


def make_low_detection_claim():
    return DefenseTrilemmaClaim(
        defense=make_discrete_defense(),
        unsafe_inputs_detected=Fraction(5),
        total_inputs=Fraction(100),
        safety_threshold=Fraction(9, 10),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_low_detection():
    claim = make_low_detection_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "Detection rate below safety threshold" in proof.conclusion


def test_check_domain_restriction_satisfied_pass():
    claim = make_safe_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is True
    assert "Domain restriction satisfied" in proof.conclusion


def test_check_domain_restriction_satisfied_fail():
    claim = make_unrestricted_claim()
    success, proof = check_domain_restriction_satisfied(claim)
    assert success is False
    assert "Domain restriction not satisfied" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_vacuous():
    claim = make_safe_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is True
    assert "vacuous" in proof.conclusion


def test_check_original_impossibility_holds_without_restriction_fail():
    claim = make_unrestricted_claim()
    success, proof = check_original_impossibility_holds_without_restriction(claim)
    assert success is False
    assert "Original impossibility contradicted" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass") or name.endswith("_vacuous"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
