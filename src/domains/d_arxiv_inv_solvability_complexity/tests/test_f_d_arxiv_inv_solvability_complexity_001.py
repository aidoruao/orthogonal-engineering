"""Tests for D_ARXIV_INV_SOLVABILITY_COMPLEXITY Yeshua Inversion.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_inv_solvability_complexity.implementation import (
    ComputationalProblem,
    ComplexityMeasure,
    SolvabilityComplexityClaim,
)
from domains.d_arxiv_inv_solvability_complexity.invariants import (
    check_inversion_holds,
    check_domain_restriction_satisfied,
    check_original_impossibility_holds_without_restriction,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_restricted_problem():
    return ComputationalProblem(
        problem_name="borel_fixed_query",
        base_regularity_class="borel",
        uses_fixed_query_policy=True,
        uses_adaptive_query_policy=False,
    )


def make_unrestricted_problem():
    return ComputationalProblem(
        problem_name="unrestricted_type_g",
        base_regularity_class="unrestricted",
        uses_fixed_query_policy=False,
        uses_adaptive_query_policy=False,
    )


def make_comparable_complexity():
    return ComplexityMeasure(
        sci_height=2,
        weihrauch_sci_rank=2,
        rank_comparable=True,
    )


def make_incomparable_complexity():
    return ComplexityMeasure(
        sci_height=0,
        weihrauch_sci_rank=-1,
        rank_comparable=False,
    )


def make_safe_claim():
    return SolvabilityComplexityClaim(
        problem=make_restricted_problem(),
        complexity=make_comparable_complexity(),
    )


def make_bad_claim():
    return SolvabilityComplexityClaim(
        problem=make_unrestricted_problem(),
        complexity=make_comparable_complexity(),
    )


def make_incomparable_claim():
    return SolvabilityComplexityClaim(
        problem=make_restricted_problem(),
        complexity=make_incomparable_complexity(),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_inversion_holds_pass():
    claim = make_safe_claim()
    success, proof = check_inversion_holds(claim)
    assert success is True
    assert "Inversion holds" in proof.conclusion


def test_check_inversion_holds_fail_incomparable():
    claim = make_incomparable_claim()
    success, proof = check_inversion_holds(claim)
    assert success is False
    assert "not comparable" in proof.conclusion


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
