"""Tests for axioms/philosophy_of_science.py."""

from fractions import Fraction

import pytest

from axioms.philosophy_of_science import (
    ScientificTheory,
    check_computational_exactness_invariant,
    check_demarcation_criterion,
    check_inference_to_best_explanation,
    check_paradigm_incommensurability_bound,
    check_token_cost_information_bound,
    check_underdetermination_of_theory,
    check_verisimilitude_ordering,
    run_all_invariants,
)


def _make_t1() -> ScientificTheory:
    """Nominal theory — passes all single-theory checks."""
    return ScientificTheory(
        name="test_t1",
        is_falsifiable=True,
        true_consequence_count=Fraction(10),
        false_consequence_count=Fraction(1),
        paradigm_shift_decided_in_constant_time=False,
        compatible_theory_count=Fraction(5),
        explanatory_power=Fraction(4, 5),
        complexity=Fraction(2),
        uses_float=False,
        token_count=Fraction(100),
        vocab_size=Fraction(1024),
        information_bits_claimed=Fraction(500),
    )


def _make_t2() -> ScientificTheory:
    """Weaker theory — t1 > t2 in verisimilitude."""
    return ScientificTheory(
        name="test_t2",
        is_falsifiable=True,
        true_consequence_count=Fraction(5),
        false_consequence_count=Fraction(3),
        paradigm_shift_decided_in_constant_time=False,
        compatible_theory_count=Fraction(3),
        explanatory_power=Fraction(1, 2),
        complexity=Fraction(3),
        uses_float=False,
        token_count=Fraction(100),
        vocab_size=Fraction(1024),
        information_bits_claimed=Fraction(500),
    )


# ---------------------------------------------------------------------------
# Pass-path tests
# ---------------------------------------------------------------------------

def test_demarcation_criterion_pass() -> None:
    ok, proof = check_demarcation_criterion(_make_t1())
    assert ok is True
    assert proof.is_valid()


def test_verisimilitude_ordering_pass() -> None:
    ok, proof = check_verisimilitude_ordering(_make_t1(), _make_t2())
    assert ok is True
    assert proof.is_valid()


def test_paradigm_incommensurability_bound_pass() -> None:
    ok, proof = check_paradigm_incommensurability_bound(_make_t1())
    assert ok is True
    assert proof.is_valid()


def test_underdetermination_of_theory_pass() -> None:
    ok, proof = check_underdetermination_of_theory(_make_t1())
    assert ok is True
    assert proof.is_valid()


def test_inference_to_best_explanation_pass() -> None:
    ok, proof = check_inference_to_best_explanation(_make_t1())
    assert ok is True
    assert proof.is_valid()


def test_computational_exactness_invariant_pass() -> None:
    ok, proof = check_computational_exactness_invariant(_make_t1())
    assert ok is True
    assert proof.is_valid()


def test_token_cost_information_bound_pass() -> None:
    ok, proof = check_token_cost_information_bound(_make_t1())
    assert ok is True
    assert proof.is_valid()


# ---------------------------------------------------------------------------
# Fail-path tests
# ---------------------------------------------------------------------------

def test_demarcation_criterion_fail() -> None:
    t = ScientificTheory(**{**_make_t1().__dict__, "is_falsifiable": False})
    ok, proof = check_demarcation_criterion(t)
    assert ok is False
    assert proof.is_valid()


def test_verisimilitude_ordering_fail_equal_truths() -> None:
    """t1 with same true count as t2 should fail."""
    t1 = ScientificTheory(**{**_make_t1().__dict__, "true_consequence_count": Fraction(5)})
    ok, proof = check_verisimilitude_ordering(t1, _make_t2())
    assert ok is False
    assert proof.is_valid()


def test_paradigm_incommensurability_bound_fail() -> None:
    t = ScientificTheory(
        **{**_make_t1().__dict__, "paradigm_shift_decided_in_constant_time": True}
    )
    ok, proof = check_paradigm_incommensurability_bound(t)
    assert ok is False
    assert proof.is_valid()


def test_underdetermination_of_theory_fail() -> None:
    t = ScientificTheory(**{**_make_t1().__dict__, "compatible_theory_count": Fraction(1)})
    ok, proof = check_underdetermination_of_theory(t)
    assert ok is False
    assert proof.is_valid()


def test_inference_to_best_explanation_fail_zero_complexity() -> None:
    t = ScientificTheory(**{**_make_t1().__dict__, "complexity": Fraction(0)})
    ok, proof = check_inference_to_best_explanation(t)
    assert ok is False
    assert proof.is_valid()


def test_computational_exactness_invariant_fail() -> None:
    t = ScientificTheory(**{**_make_t1().__dict__, "uses_float": True})
    ok, proof = check_computational_exactness_invariant(t)
    assert ok is False
    assert proof.is_valid()


def test_token_cost_information_bound_fail() -> None:
    """Claim information exceeding the Shannon bound should fail."""
    # vocab_size=4 → bit_length=3, token_count=10 → bound=30; claim 100 > 30
    t = ScientificTheory(
        **{
            **_make_t1().__dict__,
            "vocab_size": Fraction(4),
            "token_count": Fraction(10),
            "information_bits_claimed": Fraction(100),
        }
    )
    ok, proof = check_token_cost_information_bound(t)
    assert ok is False
    assert proof.is_valid()


# ---------------------------------------------------------------------------
# run_all_invariants
# ---------------------------------------------------------------------------

def test_run_all_invariants_pass() -> None:
    """run_all_invariants() must produce all-True results for nominal theories."""
    results = run_all_invariants()
    assert len(results) == 7
    for name, ok, proof in results:
        assert ok is True, f"Invariant {name!r} failed"
        assert proof.is_valid(), f"Proof for {name!r} is invalid"
