"""Tests for D_ARXIV_BLOCK_ENCODING_DOG.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_block_encoding_dog.implementation import (
    GridConfig,
    BlockEncoding,
    DoGOperator,
    DoGClaim,
)
from domains.d_arxiv_block_encoding_dog.invariants import (
    check_constant_subnormalisation,
    check_no_black_box_oracles,
    check_o_h4_scaling,
    check_success_probability_bounded,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_grid():
    return GridConfig(
        grid_size_n=256,
        spatial_dimension_d=2,
        grid_spacing_h=Fraction(1, 100),
    )


def make_good_encoding():
    return BlockEncoding(
        subnormalisation_lambda=Fraction(2),
        uses_qram=False,
        uses_signed_amplitude_loading=False,
        success_probability=Fraction(9, 10),
    )


def make_operator():
    return DoGOperator(
        sigma_1=Fraction(1),
        sigma_2=Fraction(2),
        stencil_width=5,
    )


def make_safe_claim():
    return DoGClaim(
        grid=make_grid(),
        encoding=make_good_encoding(),
        operator=make_operator(),
        scaling_order=Fraction(4),
    )


def make_bad_lambda_claim():
    return DoGClaim(
        grid=make_grid(),
        encoding=BlockEncoding(
            subnormalisation_lambda=Fraction(3),
            uses_qram=False,
            uses_signed_amplitude_loading=False,
            success_probability=Fraction(9, 10),
        ),
        operator=make_operator(),
        scaling_order=Fraction(4),
    )


def make_bad_qram_claim():
    return DoGClaim(
        grid=make_grid(),
        encoding=BlockEncoding(
            subnormalisation_lambda=Fraction(2),
            uses_qram=True,
            uses_signed_amplitude_loading=False,
            success_probability=Fraction(9, 10),
        ),
        operator=make_operator(),
        scaling_order=Fraction(4),
    )


def make_bad_scaling_claim():
    return DoGClaim(
        grid=make_grid(),
        encoding=make_good_encoding(),
        operator=make_operator(),
        scaling_order=Fraction(5),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_constant_subnormalisation_pass():
    claim = make_safe_claim()
    success, proof = check_constant_subnormalisation(claim)
    assert success is True
    assert "constant λ=2" in proof.conclusion


def test_check_constant_subnormalisation_fail():
    claim = make_bad_lambda_claim()
    success, proof = check_constant_subnormalisation(claim)
    assert success is False
    assert "not constant" in proof.conclusion


def test_check_no_black_box_oracles_pass():
    claim = make_safe_claim()
    success, proof = check_no_black_box_oracles(claim)
    assert success is True
    assert "No black-box" in proof.conclusion


def test_check_no_black_box_oracles_fail():
    claim = make_bad_qram_claim()
    success, proof = check_no_black_box_oracles(claim)
    assert success is False
    assert "black-box" in proof.conclusion


def test_check_o_h4_scaling_pass():
    claim = make_safe_claim()
    success, proof = check_o_h4_scaling(claim)
    assert success is True
    assert "O(h^4)" in proof.conclusion


def test_check_o_h4_scaling_fail():
    claim = make_bad_scaling_claim()
    success, proof = check_o_h4_scaling(claim)
    assert success is False
    assert "exceeds O(h^4)" in proof.conclusion


def test_check_success_probability_bounded_pass():
    claim = make_safe_claim()
    success, proof = check_success_probability_bounded(claim)
    assert success is True
    assert "valid range" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
