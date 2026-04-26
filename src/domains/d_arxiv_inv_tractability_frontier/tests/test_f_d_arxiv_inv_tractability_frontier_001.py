"""Tests for D_ARXIV_INV_TRACTABILITY_FRONTIER Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_tractability_frontier.implementation import (
    DecisionProblem,
    CertificationResult,
    TractabilityFrontierClaim,
)
from domains.d_arxiv_inv_tractability_frontier.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_restricted_problem():
    return DecisionProblem(
        problem_name="bounded_influence_problem",
        has_bounded_coordinate_influence=True,
        has_separable_quotient_structure=True,
        coordinate_count=10,
    )


def make_unrestricted_problem():
    return DecisionProblem(
        problem_name="arbitrary_closure_closed",
        has_bounded_coordinate_influence=False,
        has_separable_quotient_structure=False,
        coordinate_count=100,
    )


def make_exact_certification():
    return CertificationResult(
        is_exact=True,
        is_efficiently_checkable=True,
        obstruction_family_present=False,
    )


def make_inexact_certification():
    return CertificationResult(
        is_exact=False,
        is_efficiently_checkable=True,
        obstruction_family_present=True,
    )


def make_safe_claim():
    return TractabilityFrontierClaim(
        problem=make_restricted_problem(),
        certification=make_exact_certification(),
    )


def make_bad_claim():
    return TractabilityFrontierClaim(
        problem=make_unrestricted_problem(),
        certification=make_exact_certification(),
    )


def make_inexact_claim():
    return TractabilityFrontierClaim(
        problem=make_restricted_problem(),
        certification=make_inexact_certification(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_inexact():
    claim = make_inexact_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "not exact" in proof.conclusion


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
