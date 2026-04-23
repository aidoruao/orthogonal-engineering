"""Test suite for d_yeshua_mathematics invariants.

Phase C3 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_yeshua_mathematics.invariants import (
    check_all_eight_axioms,
    check_peano_substrate,
    check_boolean_purity_substrate,
    check_pure_path_agreement,
    check_no_economic_gatekeeping,
    run_all_invariants,
)
from src.domains.d_yeshua_mathematics.implementation import YeshuaSubstrate


class TestYeshuaMathematics:
    def test_pass_state(self):
        state = YeshuaSubstrate(
            axiom_satisfaction=(True, True, True, True, True, True, True, True),
            axiom_count_satisfied=8,
            total_axioms=8,
            satisfaction_ratio=Fraction(1, 1),
            peano_violations=0,
            boolean_purity_violations=0,
            pure_path_disagreements=0,
            economic_gatekeeping_detected=False,
        )
        assert check_all_eight_axioms(state)[0] is True
        assert check_peano_substrate(state)[0] is True
        assert check_boolean_purity_substrate(state)[0] is True
        assert check_pure_path_agreement(state)[0] is True
        assert check_no_economic_gatekeeping(state)[0] is True

    def test_fail_state(self):
        state = YeshuaSubstrate(
            axiom_satisfaction=(True, True, True, False, False, True, True, True),
            axiom_count_satisfied=6,
            total_axioms=8,
            satisfaction_ratio=Fraction(3, 4),
            peano_violations=2,
            boolean_purity_violations=3,
            pure_path_disagreements=1,
            economic_gatekeeping_detected=True,
        )
        assert check_all_eight_axioms(state)[0] is False
        assert check_peano_substrate(state)[0] is False
        assert check_boolean_purity_substrate(state)[0] is False
        assert check_pure_path_agreement(state)[0] is False
        assert check_no_economic_gatekeeping(state)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
