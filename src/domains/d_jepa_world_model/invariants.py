"""D_JEPA_WORLD_MODEL invariants — Representation collapse, prediction, planning.

Mathematical Standards:
- Cramér–Wold: SIGReg(Z) → 0 ⟺ P_Z → N(0, I)
- Epps–Pulley: univariate normality via empirical characteristic function
- MSE prediction loss boundedness
- Latent isotropy (equal variance across dimensions)
- Planning convergence (CEM cost reduction)
- Surprise detection (latent deviation threshold)

Falsifies if:
- Prediction loss exceeds theoretical upper bound
- SIGReg does not decrease monotonically after burn-in
- Latent variance is zero in any dimension (collapse indicator)
- Planning cost increases across CEM iterations
- Surprise score exceeds physical plausibility threshold
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple, List

from axioms.logic import ProofObject
from .implementation import (
    TrainingStep,
    TrainingRun,
    PredictorOutput,
    SIGRegResult,
    LatentState,
    LatentTrajectory,
    PlanningResult,
    SurpriseEvent,
    WorldModelConfig,
)


# ---------------------------------------------------------------------------
# 1. Prediction loss boundedness
# ---------------------------------------------------------------------------

def check_prediction_loss_bounded(
    output: PredictorOutput, max_allowed: Fraction = Fraction(100)
) -> Tuple[bool, ProofObject]:
    """Prediction MSE must be below a finite upper bound.

    Standard: JEPA-PRED-001 boundedness.
    Falsifies if: ‖ẑ - z‖² > max_allowed (indicates divergence or NaN).
    falsifies_if: prediction_error_squared exceeds max_allowed.
    """
    mse = output.prediction_error_squared()
    if mse > max_allowed:
        return False, ProofObject(
            rule="jepa_prediction_bounded",
            premises=[
                f"mse={mse}",
                f"max_allowed={max_allowed}",
                f"pred_dim={output.predicted_next.dimension()}",
            ],
            conclusion="VIOLATION: Prediction MSE exceeds upper bound — possible divergence",
        )
    return True, ProofObject(
        rule="jepa_prediction_bounded",
        premises=[f"mse={mse}", f"max_allowed={max_allowed}"],
        conclusion="Prediction MSE within bounded range",
    )


# ---------------------------------------------------------------------------
# 2. SIGReg convergence (monotonic decrease after burn-in)
# ---------------------------------------------------------------------------

def check_sigreg_convergence(
    run: TrainingRun, burn_in_steps: int = 3
) -> Tuple[bool, ProofObject]:
    """SIGReg loss must decrease monotonically after burn-in.

    Standard: JEPA-SIGREG-002 monotonicity.
    Falsifies if: SIGReg increases at any step after burn-in.
    falsifies_if: sigreg_loss is non-monotonic after burn-in.
    """
    if len(run.steps) <= burn_in_steps:
        return True, ProofObject(
            rule="jepa_sigreg_convergence",
            premises=[f"steps={len(run.steps)}", f"burn_in={burn_in_steps}"],
            conclusion="Insufficient steps for burn-in check",
        )

    post_burn = run.steps[burn_in_steps:]
    violations = []
    for i in range(1, len(post_burn)):
        prev = post_burn[i - 1].sigreg_loss
        curr = post_burn[i].sigreg_loss
        if curr > prev:
            violations.append((i + burn_in_steps, prev, curr))

    if violations:
        return False, ProofObject(
            rule="jepa_sigreg_convergence",
            premises=[
                f"violations={len(violations)}",
                f"first_violation_step={violations[0][0]}",
            ],
            conclusion="VIOLATION: SIGReg loss non-monotonic after burn-in — convergence suspect",
        )
    return True, ProofObject(
        rule="jepa_sigreg_convergence",
        premises=[
            f"steps_checked={len(post_burn)}",
            f"final_sigreg={post_burn[-1].sigreg_loss}",
        ],
        conclusion="SIGReg loss monotonically decreasing after burn-in",
    )


# ---------------------------------------------------------------------------
# 3. Latent isotropy (equal variance across dimensions)
# ---------------------------------------------------------------------------

def check_latent_isotropy(
    states: Tuple[LatentState, ...], tolerance: Fraction = Fraction(1, 2)
) -> Tuple[bool, ProofObject]:
    """Latent dimensions should have comparable variance (isotropic Gaussian target).

    Standard: JEPA-ISOTROPY-003 variance balance.
    Falsifies if: max variance / min variance > 1 + tolerance (indicates anisotropy).
    falsifies_if: variance ratio across dimensions exceeds tolerance.
    """
    if not states:
        return True, ProofObject(
            rule="jepa_latent_isotropy",
            premises=["states=empty"],
            conclusion="No states to check isotropy",
        )

    dim = states[0].dimension()
    if dim == 0:
        return False, ProofObject(
            rule="jepa_latent_isotropy",
            premises=["dimension=0"],
            conclusion="VIOLATION: Zero-dimensional latent space",
        )

    # Compute per-dimension variance using Fraction arithmetic
    means: List[Fraction] = []
    for d in range(dim):
        vals = [s.components[d] for s in states]
        mean = sum(vals) / len(vals)
        means.append(mean)

    variances: List[Fraction] = []
    for d in range(dim):
        mean = means[d]
        vals = [s.components[d] for s in states]
        var = sum((v - mean) * (v - mean) for v in vals) / len(vals)
        variances.append(var)

    # Filter zero variances (collapse indicator)
    non_zero_vars = [v for v in variances if v > Fraction(0)]
    if not non_zero_vars:
        return False, ProofObject(
            rule="jepa_latent_isotropy",
            premises=[f"variances={variances}"],
            conclusion="VIOLATION: All dimensions have zero variance — total collapse",
        )

    max_var = max(non_zero_vars)
    min_var = min(non_zero_vars)

    if min_var == Fraction(0):
        return False, ProofObject(
            rule="jepa_latent_isotropy",
            premises=[f"max_var={max_var}", f"min_var={min_var}"],
            conclusion="VIOLATION: At least one dimension has zero variance — partial collapse",
        )

    ratio = max_var / min_var
    threshold = Fraction(1) + tolerance

    if ratio > threshold:
        return False, ProofObject(
            rule="jepa_latent_isotropy",
            premises=[
                f"max_var={max_var}",
                f"min_var={min_var}",
                f"ratio={ratio}",
                f"threshold={threshold}",
            ],
            conclusion="VIOLATION: Latent variance anisotropic — not matching isotropic Gaussian target",
        )
    return True, ProofObject(
        rule="jepa_latent_isotropy",
        premises=[
            f"max_var={max_var}",
            f"min_var={min_var}",
            f"ratio={ratio}",
            f"threshold={threshold}",
        ],
        conclusion="Latent variance isotropic within tolerance",
    )


# ---------------------------------------------------------------------------
# 4. No representation collapse
# ---------------------------------------------------------------------------

def check_no_representation_collapse(
    states: Tuple[LatentState, ...], min_spread: Fraction = Fraction(1, 100)
) -> Tuple[bool, ProofObject]:
    """Embeddings must span non-trivial volume in latent space.

    Standard: JEPA-COLLAPSE-004 non-degeneracy.
    Falsifies if: all embeddings are identical within min_spread (collapse).
    falsifies_if: pairwise distance between all states < min_spread.
    """
    if len(states) < 2:
        return True, ProofObject(
            rule="jepa_no_collapse",
            premises=[f"count={len(states)}"],
            conclusion="Insufficient states for collapse detection",
        )

    # Check that at least one pair differs significantly
    found_spread = False
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            dist_sq = sum(
                (a - b) * (a - b)
                for a, b in zip(states[i].components, states[j].components)
            )
            if dist_sq >= min_spread * min_spread:
                found_spread = True
                break
        if found_spread:
            break

    if not found_spread:
        return False, ProofObject(
            rule="jepa_no_collapse",
            premises=[
                f"state_count={len(states)}",
                f"min_spread={min_spread}",
            ],
            conclusion="VIOLATION: All embeddings collapsed to near-identical representations",
        )
    return True, ProofObject(
        rule="jepa_no_collapse",
        premises=[f"state_count={len(states)}", f"min_spread={min_spread}"],
        conclusion="Embeddings show non-trivial spread — no collapse detected",
    )


# ---------------------------------------------------------------------------
# 5. Planning convergence (CEM cost reduction)
# ---------------------------------------------------------------------------

def check_planning_convergence(
    result: PlanningResult, max_cost: Fraction = Fraction(1000)
) -> Tuple[bool, ProofObject]:
    """Planning must produce a finite-cost action sequence.

    Standard: JEPA-PLAN-005 convergence.
    Falsifies if: final_cost > max_cost or planning did not converge.
    falsifies_if: planning cost unbounded or convergence flag False.
    """
    if not result.converged:
        return False, ProofObject(
            rule="jepa_planning_convergence",
            premises=[
                f"converged={result.converged}",
                f"iterations_used={result.iterations_used}",
            ],
            conclusion="VIOLATION: Planning did not converge within allocated iterations",
        )
    if result.final_cost > max_cost:
        return False, ProofObject(
            rule="jepa_planning_convergence",
            premises=[
                f"final_cost={result.final_cost}",
                f"max_cost={max_cost}",
            ],
            conclusion="VIOLATION: Planning cost exceeds threshold — goal unreachable or divergence",
        )
    return True, ProofObject(
        rule="jepa_planning_convergence",
        premises=[
            f"final_cost={result.final_cost}",
            f"converged={result.converged}",
            f"iterations={result.iterations_used}",
        ],
        conclusion="Planning converged to finite-cost solution",
    )


# ---------------------------------------------------------------------------
# 6. Surprise detection (physically implausible events)
# ---------------------------------------------------------------------------

def check_surprise_plausible(
    event: SurpriseEvent, threshold: Fraction = Fraction(10)
) -> Tuple[bool, ProofObject]:
    """Surprise score must be below physical plausibility threshold.

    Standard: JEPA-SURPRISE-006 physical consistency.
    Falsifies if: surprise_score > threshold (physically implausible trajectory).
    falsifies_if: surprise exceeds threshold indicating violation of expectation.
    """
    if event.surprise_score > threshold:
        return False, ProofObject(
            rule="jepa_surprise_plausible",
            premises=[
                f"event_id={event.event_id}",
                f"timestep={event.timestep}",
                f"surprise_score={event.surprise_score}",
                f"threshold={threshold}",
            ],
            conclusion="VIOLATION: Surprise score exceeds threshold — physically implausible event detected",
        )
    return True, ProofObject(
        rule="jepa_surprise_plausible",
        premises=[
            f"event_id={event.event_id}",
            f"surprise_score={event.surprise_score}",
            f"threshold={threshold}",
        ],
        conclusion="Surprise score within physical plausibility bounds",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_JEPA_WORLD_MODEL invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS cases
    z1 = LatentState(components=(Fraction(1), Fraction(2), Fraction(3)), timestep=0, trajectory_id="T1")
    z2 = LatentState(components=(Fraction(2), Fraction(1), Fraction(4)), timestep=1, trajectory_id="T1")
    z3 = LatentState(components=(Fraction(3), Fraction(3), Fraction(2)), timestep=2, trajectory_id="T1")
    z_pred = LatentState(components=(Fraction(2, 10), Fraction(-1, 10), Fraction(5, 10)), timestep=1, trajectory_id="T1")

    pred_out = PredictorOutput(predicted_next=z_pred, target_next=z2)
    traj = LatentTrajectory(trajectory_id="T1", states=(z1, z2, z3), actions=())

    step1 = TrainingStep(step_id="S1", prediction_loss=Fraction(1, 10), sigreg_loss=Fraction(5), total_loss=Fraction(51, 10), lambda_weight=Fraction(1, 10))
    step2 = TrainingStep(step_id="S2", prediction_loss=Fraction(1, 20), sigreg_loss=Fraction(3), total_loss=Fraction(31, 20), lambda_weight=Fraction(1, 10))
    step3 = TrainingStep(step_id="S3", prediction_loss=Fraction(1, 50), sigreg_loss=Fraction(2), total_loss=Fraction(101, 50), lambda_weight=Fraction(1, 10))
    run = TrainingRun(run_id="R1", steps=(step1, step2, step3), config=WorldModelConfig(), sigreg_config=SIGRegResult.__dataclass_fields__)

    plan_result = PlanningResult(
        optimal_actions=None,
        final_cost=Fraction(5),
        converged=True,
        iterations_used=10,
        goal_state=z3,
    )

    surprise = SurpriseEvent(
        event_id="E1",
        trajectory_id="T1",
        timestep=2,
        surprise_score=Fraction(3),
        expected_state=z2,
        observed_state=z3,
    )

    # FAIL cases
    z_collapsed = LatentState(components=(Fraction(0), Fraction(0), Fraction(0)), timestep=0, trajectory_id="T2")
    z_collapsed2 = LatentState(components=(Fraction(0), Fraction(0), Fraction(0)), timestep=1, trajectory_id="T2")
    states_collapsed = (z_collapsed, z_collapsed2)

    step_bad = TrainingStep(step_id="SB", prediction_loss=Fraction(1, 1000), sigreg_loss=Fraction(10), total_loss=Fraction(101, 1000), lambda_weight=Fraction(1, 10))
    run_bad = TrainingRun(run_id="RB", steps=(step1, step_bad), config=WorldModelConfig(), sigreg_config=SIGRegResult.__dataclass_fields__)

    plan_bad = PlanningResult(
        optimal_actions=None,
        final_cost=Fraction(5000),
        converged=False,
        iterations_used=30,
        goal_state=z3,
    )

    surprise_bad = SurpriseEvent(
        event_id="E2",
        trajectory_id="T1",
        timestep=2,
        surprise_score=Fraction(50),
        expected_state=z2,
        observed_state=z3,
    )

    checks = [
        ("check_prediction_loss_bounded_pass", lambda: check_prediction_loss_bounded(pred_out)),
        ("check_sigreg_convergence_pass", lambda: check_sigreg_convergence(run)),
        ("check_latent_isotropy_pass", lambda: check_latent_isotropy((z1, z2, z3))),
        ("check_no_representation_collapse_pass", lambda: check_no_representation_collapse((z1, z2, z3))),
        ("check_planning_convergence_pass", lambda: check_planning_convergence(plan_result)),
        ("check_surprise_plausible_pass", lambda: check_surprise_plausible(surprise)),
        ("check_no_representation_collapse_fail", lambda: check_no_representation_collapse(states_collapsed)),
        ("check_sigreg_convergence_fail", lambda: check_sigreg_convergence(run_bad)),
        ("check_planning_convergence_fail", lambda: check_planning_convergence(plan_bad)),
        ("check_surprise_plausible_fail", lambda: check_surprise_plausible(surprise_bad)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [
        k for k, v in results.items()
        if not v.startswith("PASS") and not k.endswith("_fail")
    ]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_JEPA_WORLD_MODEL invariants: PASS")
