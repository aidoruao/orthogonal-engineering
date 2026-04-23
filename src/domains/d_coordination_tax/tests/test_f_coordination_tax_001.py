"""Test suite for d_coordination_tax invariants.

Phase P3 of Depositive Campaign.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from fractions import Fraction

from src.domains.d_coordination_tax.invariants import (
    check_brooks_law,
    check_coordination_tax_monotonic,
    check_sovereign_zero_tax,
    check_alignment_channel_scaling,
    check_decision_latency_invariant,
    check_institutional_overhead_ratio,
    run_all_invariants,
)
from src.domains.d_coordination_tax.implementation import CoordinationState, SovereignEntity


class TestCoordinationTax:
    def test_pass_state(self):
        state = CoordinationState(
            team_size=1,
            previous_team_size=1,
            linear_output=Fraction(10, 1),
            actual_output=Fraction(10, 1),
            coordination_tax_rate=Fraction(0, 1),
            previous_coordination_tax_rate=Fraction(0, 1),
            alignment_channels=0,
            decision_latency_hours=Fraction(0, 1),
            authority_type="mathematical",
            governance_overhead=Fraction(1, 1),
            investigation_output=Fraction(10, 1),
        )
        assert check_brooks_law(state)[0] is True
        assert check_coordination_tax_monotonic(state)[0] is True
        assert check_sovereign_zero_tax(state)[0] is True
        assert check_alignment_channel_scaling(state)[0] is True
        assert check_decision_latency_invariant(state)[0] is True
        assert check_institutional_overhead_ratio(state)[0] is True

    def test_fail_state(self):
        state = CoordinationState(
            team_size=10,
            previous_team_size=5,
            linear_output=Fraction(10, 1),
            actual_output=Fraction(12, 1),
            coordination_tax_rate=Fraction(7, 10),
            previous_coordination_tax_rate=Fraction(8, 10),
            alignment_channels=44,
            decision_latency_hours=Fraction(72, 1),
            authority_type="mathematical",
            governance_overhead=Fraction(100, 1),
            investigation_output=Fraction(5, 1),
        )
        assert check_brooks_law(state)[0] is False
        assert check_coordination_tax_monotonic(state)[0] is False
        assert check_sovereign_zero_tax(state)[0] is False
        assert check_alignment_channel_scaling(state)[0] is False
        assert check_decision_latency_invariant(state)[0] is False
        assert check_institutional_overhead_ratio(state)[0] is False

    def test_run_all(self):
        results = run_all_invariants()
        for name, result in results.items():
            assert result.startswith("PASS") or result.startswith("FAIL"), f"{name}: {result}"
