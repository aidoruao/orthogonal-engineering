"""Tests for D_ARXIV_INV_STABILIZATION_WITHOUT_SIMPLIFICATION Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_stabilization_without_simplification.implementation import (
    SoftwareSystem,
    EvolutionMetrics,
    StabilizationClaim,
)
from domains.d_arxiv_inv_stabilization_without_simplification.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_restricted_system():
    return SoftwareSystem(
        system_name="regulated_codebase",
        has_structural_regularization=True,
        has_process_stabilization=True,
        has_covariance_control=True,
    )


def make_unrestricted_system():
    return SoftwareSystem(
        system_name="legacy_codebase",
        has_structural_regularization=False,
        has_process_stabilization=False,
        has_covariance_control=False,
    )


def make_safe_metrics():
    return EvolutionMetrics(
        structural_burden=Fraction(100),
        uncertainty=Fraction(10),
        burden_change=Fraction(0),
        uncertainty_change=Fraction(-3),
    )


def make_bad_metrics():
    return EvolutionMetrics(
        structural_burden=Fraction(100),
        uncertainty=Fraction(10),
        burden_change=Fraction(0),
        uncertainty_change=Fraction(-3),
    )


def make_simplification_metrics():
    return EvolutionMetrics(
        structural_burden=Fraction(100),
        uncertainty=Fraction(10),
        burden_change=Fraction(-5),
        uncertainty_change=Fraction(-3),
    )


def make_safe_claim():
    return StabilizationClaim(
        system=make_restricted_system(),
        metrics=make_safe_metrics(),
    )


def make_bad_claim():
    return StabilizationClaim(
        system=make_unrestricted_system(),
        metrics=make_bad_metrics(),
    )


def make_simplification_claim():
    return StabilizationClaim(
        system=make_restricted_system(),
        metrics=make_simplification_metrics(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_simplification():
    claim = make_simplification_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "simplification" in proof.conclusion


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


def test_check_original_impossibility_holds_without_restriction_fail():
    claim = make_bad_claim()
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
