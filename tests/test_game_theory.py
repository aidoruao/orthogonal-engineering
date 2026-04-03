#!/usr/bin/env python3
# @falsification_id: F_GAMETH_001
"""Tests for PR #83 game-theory layer."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from axioms.game_theory import (
    StrategyProfile,
    analyze_iterated_prisoners_dilemma,
    evolutionary_stable,
    find_nash_equilibria,
    prove_minimax,
    shapley_value,
    verify_incentive_compatibility,
    vickrey_auction,
)


def test_game_theory_suite():
    pd = StrategyProfile(
        players=("alice", "bob"),
        strategies=(("C", "D"), ("C", "D")),
        payoffs={("C", "C"): (3, 3), ("C", "D"): (0, 5), ("D", "C"): (5, 0), ("D", "D"): (1, 1)},
    )
    assert find_nash_equilibria(pd)[0] == [("D", "D")]
    zero_sum = StrategyProfile(
        players=("row", "col"),
        strategies=(("U", "D"), ("L", "R")),
        payoffs={("U", "L"): (1, -1), ("U", "R"): (-1, 1), ("D", "L"): (-1, 1), ("D", "R"): (1, -1)},
    )
    assert "theorem" in prove_minimax(zero_sum).conclusion.lower()
    assert analyze_iterated_prisoners_dilemma(2, {"a": lambda own, opp: "C", "b": lambda own, opp: "D"}).is_valid()
    assert verify_incentive_compatibility({"high": {"high": 5, "low": 1}, "low": {"high": 4, "low": 1}}, [{"high": 5, "low": 1}])[0]
    majority_game = {
        frozenset(): 0.0,
        frozenset({"alice"}): 0.0,
        frozenset({"bob"}): 0.0,
        frozenset({"carol"}): 0.0,
        frozenset({"alice", "bob"}): 1.0,
        frozenset({"alice", "carol"}): 1.0,
        frozenset({"bob", "carol"}): 1.0,
        frozenset({"alice", "bob", "carol"}): 1.0,
    }
    assert shapley_value(("alice", "bob", "carol"), majority_game)[0] == {
        "alice": 0.333333,
        "bob": 0.333333,
        "carol": 0.333333,
    }
    assert vickrey_auction({"alice": 10, "bob": 7, "carol": 5})[0]["payment"] == 7
    assert set(evolutionary_stable({"Stag": {"Stag": 4, "Hare": 0}, "Hare": {"Stag": 3, "Hare": 3}})[0]) == {"Stag", "Hare"}
    assert evolutionary_stable({"A": {"A": 3, "B": 1}, "B": {"A": 2, "B": 1}})[0] == ["A"]


def main():
    test_game_theory_suite()
    print("PASS test_game_theory_suite")


if __name__ == "__main__":
    main()
