"""Tests for D_ARXIV_INV_SHARP_LOCAL_MINIMA Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_sharp_local_minima.implementation import (
    NetworkArchitecture,
    OptimizationDynamics,
    SharpLocalMinimaClaim,
)
from domains.d_arxiv_inv_sharp_local_minima.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_overparameterised_architecture():
    return NetworkArchitecture(
        network_name="wide_relu",
        width=100,
        teacher_dimensionality=10,
        is_overparameterised=True,
    )


def make_well_specified_architecture():
    return NetworkArchitecture(
        network_name="narrow_relu",
        width=5,
        teacher_dimensionality=10,
        is_overparameterised=False,
    )


def make_good_dynamics():
    return OptimizationDynamics(
        uses_sgd=True,
        converged_to_global_minimum=True,
        spurious_solution_rate=Fraction(1, 100),
    )


def make_high_spurious_dynamics():
    return OptimizationDynamics(
        uses_sgd=True,
        converged_to_global_minimum=False,
        spurious_solution_rate=Fraction(20),
    )


def make_safe_claim():
    return SharpLocalMinimaClaim(
        architecture=make_overparameterised_architecture(),
        dynamics=make_good_dynamics(),
        spurious_rate_threshold=Fraction(5, 100),
    )


def make_bad_claim():
    return SharpLocalMinimaClaim(
        architecture=make_well_specified_architecture(),
        dynamics=make_good_dynamics(),
        spurious_rate_threshold=Fraction(5, 100),
    )


def make_high_spurious_claim():
    return SharpLocalMinimaClaim(
        architecture=make_overparameterised_architecture(),
        dynamics=make_high_spurious_dynamics(),
        spurious_rate_threshold=Fraction(5, 100),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_high_spurious():
    claim = make_high_spurious_claim()
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
