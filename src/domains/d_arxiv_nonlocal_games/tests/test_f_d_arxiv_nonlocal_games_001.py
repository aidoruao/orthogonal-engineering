"""Tests for D_ARXIV_NONLOCAL_GAMES.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_arxiv_nonlocal_games.implementation import (
    GameConfig,
    Strategy,
    NonlocalGameClaim,
)
from domains.d_arxiv_nonlocal_games.invariants import (
    check_quantum_beats_classical,
    check_no_signaling_upper_bound,
    check_entanglement_required,
    check_winning_probability_bounded,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_game():
    return GameConfig(
        game_name="chsh",
        player_count=2,
        question_count=2,
        answer_count=2,
    )


def make_safe_claim():
    return NonlocalGameClaim(
        game=make_game(),
        strategy=Strategy(
            strategy_type="quantum",
            uses_entanglement=True,
            winning_probability=Fraction(85, 100),
        ),
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )


def make_weak_claim():
    return NonlocalGameClaim(
        game=make_game(),
        strategy=Strategy(
            strategy_type="quantum",
            uses_entanglement=True,
            winning_probability=Fraction(7, 10),
        ),
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )


def make_cheating_claim():
    return NonlocalGameClaim(
        game=make_game(),
        strategy=Strategy(
            strategy_type="quantum",
            uses_entanglement=True,
            winning_probability=Fraction(11, 10),
        ),
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )


def make_no_ent_claim():
    return NonlocalGameClaim(
        game=make_game(),
        strategy=Strategy(
            strategy_type="quantum",
            uses_entanglement=False,
            winning_probability=Fraction(85, 100),
        ),
        classical_bound=Fraction(75, 100),
        quantum_bound=Fraction(85, 100),
        no_signaling_bound=Fraction(1),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_check_quantum_beats_classical_pass():
    claim = make_safe_claim()
    success, proof = check_quantum_beats_classical(claim)
    assert success is True
    assert "beats" in proof.conclusion


def test_check_quantum_beats_classical_fail():
    claim = make_weak_claim()
    success, proof = check_quantum_beats_classical(claim)
    assert success is False
    assert "does not beat" in proof.conclusion


def test_check_no_signaling_upper_bound_pass():
    claim = make_safe_claim()
    success, proof = check_no_signaling_upper_bound(claim)
    assert success is True
    assert "within" in proof.conclusion


def test_check_no_signaling_upper_bound_fail():
    claim = make_cheating_claim()
    success, proof = check_no_signaling_upper_bound(claim)
    assert success is False
    assert "exceeds" in proof.conclusion


def test_check_entanglement_required_pass():
    claim = make_safe_claim()
    success, proof = check_entanglement_required(claim)
    assert success is True
    assert "uses entanglement" in proof.conclusion


def test_check_entanglement_required_fail():
    claim = make_no_ent_claim()
    success, proof = check_entanglement_required(claim)
    assert success is False
    assert "does not use" in proof.conclusion


def test_check_winning_probability_bounded_pass():
    claim = make_safe_claim()
    success, proof = check_winning_probability_bounded(claim)
    assert success is True
    assert "within" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    for name, result in results.items():
        if name.endswith("_pass"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
