"""Falsification tests for D_ARXIV_RAYS_AS_PIXELS."""

from dataclasses import replace
from fractions import Fraction

from ..implementation import create_nominal_claim
from ..invariants import check_joint_pose_error_improvement, run_all_invariants


def test_all_invariants_pass() -> None:
    results = run_all_invariants()
    assert len(results) >= 4
    for check_name, success, proof in results:
        _ = (check_name, proof)
        assert success is True


def test_failure_path_detected() -> None:
    claim = create_nominal_claim()
    failing_claim = replace(claim, joint_model_pose_error=Fraction(3, 10))
    success, proof = check_joint_pose_error_improvement(failing_claim)
    assert success is False
    assert "FAIL" in proof.conclusion
