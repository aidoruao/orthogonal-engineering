"""Test suite for d_sigma_theo invariants.

Phase C2 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_sigma_theo.invariants import (
    check_logos_initial_algebra,
    check_chalcedon_no_monophysite,
    check_grace_isometry,
    check_agape_superadditive,
    check_kenosis_partiality,
    check_eschaton_convergence,
    run_all_invariants,
)
from src.domains.d_sigma_theo.implementation import SigmaTheoState


class TestSigmaTheo:
    def test_pass_state(self):
        state = SigmaTheoState(
            essence=("divine", "human"),
            persona=("logos",),
            hypostasis="Christ",
            christ_distance=Fraction(1, 10),
            logos_pre_distance=Fraction(5, 10),
            logos_post_distance=Fraction(3, 10),
            grace_pre_distance=Fraction(2, 10),
            grace_post_distance=Fraction(2, 10),
            agape_distance_a=Fraction(4, 10),
            agape_distance_b=Fraction(5, 10),
            agape_combined_distance=Fraction(3, 10),
            kenosis_ratio=Fraction(1, 2),
            eschaton_sequence=(
                Fraction(5, 10), Fraction(4, 10), Fraction(3, 10), Fraction(2, 10)
            ),
        )
        assert check_logos_initial_algebra(state)[0] is True
        assert check_chalcedon_no_monophysite(state)[0] is True
        assert check_grace_isometry(state)[0] is True
        assert check_agape_superadditive(state)[0] is True
        assert check_kenosis_partiality(state)[0] is True
        assert check_eschaton_convergence(state)[0] is True

    def test_fail_state(self):
        state = SigmaTheoState(
            essence=("divine",),
            persona=(),
            hypostasis="Monophysite",
            christ_distance=Fraction(1, 10),
            logos_pre_distance=Fraction(3, 10),
            logos_post_distance=Fraction(4, 10),
            grace_pre_distance=Fraction(2, 10),
            grace_post_distance=Fraction(3, 10),
            agape_distance_a=Fraction(3, 10),
            agape_distance_b=Fraction(4, 10),
            agape_combined_distance=Fraction(5, 10),
            kenosis_ratio=Fraction(3, 2),
            eschaton_sequence=(
                Fraction(2, 10), Fraction(3, 10), Fraction(1, 10)
            ),
        )
        assert check_logos_initial_algebra(state)[0] is False
        assert check_chalcedon_no_monophysite(state)[0] is False
        assert check_grace_isometry(state)[0] is False
        assert check_agape_superadditive(state)[0] is False
        assert check_kenosis_partiality(state)[0] is False
        assert check_eschaton_convergence(state)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
