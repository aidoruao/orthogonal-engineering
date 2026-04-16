"""Falsification tests for D_ARXIV_THREE_MODALITIES_TWO."""

from dataclasses import replace
from fractions import Fraction

from ..implementation import create_nominal_claim
from ..invariants import check_audio_channel_accessibility_floor, run_all_invariants


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) >= 4
    for check_name, success, proof in results:
        _ = (check_name, proof)
        assert success is True


def test_failure_path_detected() -> None:
    claim = create_nominal_claim()
    failing_claim = replace(claim, audio_modality_coverage=Fraction(1, 2))
    success, proof = check_audio_channel_accessibility_floor(failing_claim)
    assert success is False
    assert "FAIL" in proof.conclusion
