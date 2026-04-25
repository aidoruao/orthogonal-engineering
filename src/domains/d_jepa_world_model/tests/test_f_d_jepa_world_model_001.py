"""Tests for D_JEPA_WORLD_MODEL invariants.

Standard: OE test pattern — PASS and FAIL cases for each invariant.
"""

from __future__ import annotations

from fractions import Fraction

from axioms.logic import ProofObject
from domains.d_jepa_world_model.implementation import (
    LatentState,
    LatentTrajectory,
    PredictorOutput,
    TrainingStep,
    TrainingRun,
    WorldModelConfig,
    SIGRegConfig,
    PlanningResult,
    SurpriseEvent,
)
from domains.d_jepa_world_model.invariants import (
    check_prediction_loss_bounded,
    check_sigreg_convergence,
    check_latent_isotropy,
    check_no_representation_collapse,
    check_planning_convergence,
    check_surprise_plausible,
    run_all_invariants,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_states():
    z1 = LatentState(components=(Fraction(1), Fraction(2), Fraction(3)), timestep=0, trajectory_id="T1")
    z2 = LatentState(components=(Fraction(2), Fraction(1), Fraction(4)), timestep=1, trajectory_id="T1")
    z3 = LatentState(components=(Fraction(3), Fraction(3), Fraction(2)), timestep=2, trajectory_id="T1")
    return z1, z2, z3


def make_collapsed_states():
    z1 = LatentState(components=(Fraction(0), Fraction(0), Fraction(0)), timestep=0, trajectory_id="T2")
    z2 = LatentState(components=(Fraction(0), Fraction(0), Fraction(0)), timestep=1, trajectory_id="T2")
    return z1, z2


def make_training_run():
    z1, z2, z3 = make_states()
    step1 = TrainingStep(step_id="S1", prediction_loss=Fraction(1, 10), sigreg_loss=Fraction(5), total_loss=Fraction(51, 10), lambda_weight=Fraction(1, 10))
    step2 = TrainingStep(step_id="S2", prediction_loss=Fraction(1, 20), sigreg_loss=Fraction(3), total_loss=Fraction(31, 20), lambda_weight=Fraction(1, 10))
    step3 = TrainingStep(step_id="S3", prediction_loss=Fraction(1, 50), sigreg_loss=Fraction(2), total_loss=Fraction(101, 50), lambda_weight=Fraction(1, 10))
    return TrainingRun(run_id="R1", steps=(step1, step2, step3), config=WorldModelConfig(), sigreg_config=SIGRegConfig())


def make_bad_training_run():
    step1 = TrainingStep(step_id="S1", prediction_loss=Fraction(1, 10), sigreg_loss=Fraction(5), total_loss=Fraction(51, 10), lambda_weight=Fraction(1, 10))
    step_bad = TrainingStep(step_id="SB", prediction_loss=Fraction(1, 1000), sigreg_loss=Fraction(10), total_loss=Fraction(101, 1000), lambda_weight=Fraction(1, 10))
    return TrainingRun(run_id="RB", steps=(step1, step_bad), config=WorldModelConfig(), sigreg_config=SIGRegConfig())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_prediction_loss_bounded_pass():
    z1, z2, z3 = make_states()
    z_pred = LatentState(components=(Fraction(21, 10), Fraction(11, 10), Fraction(41, 10)), timestep=1, trajectory_id="T1")
    out = PredictorOutput(predicted_next=z_pred, target_next=z2)
    success, proof = check_prediction_loss_bounded(out)
    assert success is True
    assert "within bounded range" in proof.conclusion


def test_prediction_loss_bounded_fail():
    z1, z2, z3 = make_states()
    z_pred = LatentState(components=(Fraction(1000), Fraction(1000), Fraction(1000)), timestep=1, trajectory_id="T1")
    out = PredictorOutput(predicted_next=z_pred, target_next=z2)
    success, proof = check_prediction_loss_bounded(out)
    assert success is False
    assert "exceeds upper bound" in proof.conclusion


def test_sigreg_convergence_pass():
    run = make_training_run()
    success, proof = check_sigreg_convergence(run)
    assert success is True
    assert "monotonically decreasing" in proof.conclusion


def test_sigreg_convergence_fail():
    run = make_bad_training_run()
    success, proof = check_sigreg_convergence(run)
    assert success is False
    assert "non-monotonic" in proof.conclusion


def test_latent_isotropy_pass():
    z1, z2, z3 = make_states()
    success, proof = check_latent_isotropy((z1, z2, z3))
    assert success is True
    assert "isotropic" in proof.conclusion


def test_latent_isotropy_fail_collapse():
    z1, z2 = make_collapsed_states()
    success, proof = check_latent_isotropy((z1, z2))
    assert success is False
    assert "zero variance" in proof.conclusion


def test_no_representation_collapse_pass():
    z1, z2, z3 = make_states()
    success, proof = check_no_representation_collapse((z1, z2, z3))
    assert success is True
    assert "no collapse" in proof.conclusion


def test_no_representation_collapse_fail():
    z1, z2 = make_collapsed_states()
    success, proof = check_no_representation_collapse((z1, z2))
    assert success is False
    assert "collapsed" in proof.conclusion


def test_planning_convergence_pass():
    z1, z2, z3 = make_states()
    result = PlanningResult(
        optimal_actions=None,
        final_cost=Fraction(5),
        converged=True,
        iterations_used=10,
        goal_state=z3,
    )
    success, proof = check_planning_convergence(result)
    assert success is True
    assert "converged" in proof.conclusion


def test_planning_convergence_fail_not_converged():
    z1, z2, z3 = make_states()
    result = PlanningResult(
        optimal_actions=None,
        final_cost=Fraction(5),
        converged=False,
        iterations_used=30,
        goal_state=z3,
    )
    success, proof = check_planning_convergence(result)
    assert success is False
    assert "did not converge" in proof.conclusion


def test_planning_convergence_fail_cost_too_high():
    z1, z2, z3 = make_states()
    result = PlanningResult(
        optimal_actions=None,
        final_cost=Fraction(5000),
        converged=True,
        iterations_used=10,
        goal_state=z3,
    )
    success, proof = check_planning_convergence(result)
    assert success is False
    assert "exceeds threshold" in proof.conclusion


def test_surprise_plausible_pass():
    z1, z2, z3 = make_states()
    event = SurpriseEvent(
        event_id="E1",
        trajectory_id="T1",
        timestep=2,
        surprise_score=Fraction(3),
        expected_state=z2,
        observed_state=z3,
    )
    success, proof = check_surprise_plausible(event)
    assert success is True
    assert "within physical plausibility" in proof.conclusion


def test_surprise_plausible_fail():
    z1, z2, z3 = make_states()
    event = SurpriseEvent(
        event_id="E2",
        trajectory_id="T1",
        timestep=2,
        surprise_score=Fraction(50),
        expected_state=z2,
        observed_state=z3,
    )
    success, proof = check_surprise_plausible(event)
    assert success is False
    assert "implausible" in proof.conclusion


def test_run_all_invariants():
    results = run_all_invariants()
    # All _pass entries should be PASS
    for name, result in results.items():
        if name.endswith("_pass"):
            assert result == "PASS", f"{name} failed: {result}"
        elif name.endswith("_fail"):
            assert result.startswith("FAIL"), f"{name} should fail but got: {result}"
        else:
            assert result == "PASS", f"{name} failed: {result}"
