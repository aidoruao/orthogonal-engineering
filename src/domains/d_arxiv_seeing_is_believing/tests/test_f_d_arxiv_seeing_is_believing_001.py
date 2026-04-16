"""Falsification tests for D_ARXIV_SEEING_IS_BELIEVING."""

from dataclasses import replace
from fractions import Fraction

from ..implementation import create_nominal_claim
from ..invariants import check_visual_signal_dominance, run_all_invariants


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) >= 4
    for check_name, success, proof in results:
        _ = (check_name, proof)
        assert success is True


def test_failure_path_detected() -> None:
    claim = create_nominal_claim()
    failing_claim = replace(claim, visual_semantic_stability=Fraction(7, 10))
    success, proof = check_visual_signal_dominance(failing_claim)
    assert success is False
    assert "FAIL" in proof.conclusion
