"""Falsification tests for PHENOMENOLOGY."""

from dataclasses import replace
from fractions import Fraction

from ..implementation import create_nominal_claim
from ..invariants import check_intentionality_directedness, run_all_invariants


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) >= 4
    for check_name, success, proof in results:
        _ = (check_name, proof)
        assert success is True


def test_failure_path_detected() -> None:
    claim = create_nominal_claim()
    failing_claim = replace(claim, intentionality_directed=False)
    success, proof = check_intentionality_directedness(failing_claim)
    assert success is False
    assert "FAIL" in proof.conclusion
