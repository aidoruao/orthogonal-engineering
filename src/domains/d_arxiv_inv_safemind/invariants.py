"""Invariant checks for D_ARXIV_INV_SAFEMIND — Yeshua Inversion.

Paper: arXiv 2604.09474v1 (cs.AI / cs.RO)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    EnvironmentModel,
    ControllerModel,
    SafeMindClaim,
    SafeMindEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: SafeMindClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, safety is guaranteed.

    Standard: arXiv 2604.09474v1 Yeshua Inversion operationalization.
    Falsifies if: safety_violation_rate > safety_threshold.
    falsifies_if: safety_violation_rate exceeds safety_threshold after restriction.
    """
    if claim.safety_violation_rate > claim.safety_threshold:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"safety_violation_rate={claim.safety_violation_rate}",
                f"safety_threshold={claim.safety_threshold}",
            ],
            conclusion="VIOLATION: Safety violation rate exceeds threshold — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"safety_violation_rate={claim.safety_violation_rate}",
            f"safety_threshold={claim.safety_threshold}",
        ],
        conclusion="Inversion holds: safety guarantees achievable under bounded uncertainty",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: SafeMindClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.09474v1 domain restriction operationalization.
    Falsifies if: uncertainty is unbounded or controller lacks variance-aware barrier.
    falsifies_if: uncertainty is unbounded or controller lacks variance-aware barrier.
    """
    env = claim.environment
    ctrl = claim.controller
    violations = []

    # Environment must have bounded uncertainty
    if env.perception_noise_variance <= Fraction(0):
        violations.append("perception_noise_variance_unbounded")
    if env.friction_coefficient_min <= Fraction(0):
        violations.append("friction_unbounded")
    if env.model_uncertainty_confidence <= Fraction(0):
        violations.append("model_uncertainty_unbounded")

    # Controller must have required components
    if not ctrl.uses_variance_aware_barrier:
        violations.append("uses_variance_aware_barrier=False")
    if not ctrl.uses_differentiable_qp:
        violations.append("uses_differentiable_qp=False")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"perception_noise_variance={env.perception_noise_variance}",
            f"friction_range=[{env.friction_coefficient_min}, {env.friction_coefficient_max}]",
            f"model_uncertainty_confidence={env.model_uncertainty_confidence}",
            f"controller={ctrl.controller_name}",
            "uses_variance_aware_barrier=True",
            "uses_differentiable_qp=True",
        ],
        conclusion="Domain restriction satisfied: bounded uncertainty with variance-aware CBF",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: SafeMindClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted environments.

    Standard: arXiv 2604.09474v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for unrestricted environments.
    falsifies_if: the original theorem is contradicted for unrestricted environments.
    """
    env = claim.environment
    ctrl = claim.controller

    # Unrestricted = unbounded uncertainty AND no variance-aware barrier
    unbounded = (
        env.perception_noise_variance <= Fraction(0)
        or env.friction_coefficient_min <= Fraction(0)
        or env.model_uncertainty_confidence <= Fraction(0)
    )
    no_barrier = not ctrl.uses_variance_aware_barrier

    if unbounded and no_barrier:
        # Original impossibility: safety guarantees cannot hold
        if claim.safety_violation_rate <= claim.safety_threshold:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "environment=unrestricted",
                    "controller=no_variance_barrier",
                    f"safety_violation_rate={claim.safety_violation_rate}",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — unrestricted environment appears safe",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "environment=unrestricted",
                "original_theorem=preserves_impossibility",
            ],
            conclusion="Original impossibility holds for unrestricted environments",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["environment=restricted", "check=vacuous"],
        conclusion="Original impossibility check vacuous for restricted environments",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_SAFEMIND invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: bounded environment + variance-aware controller
    env_bounded = EnvironmentModel(
        perception_noise_variance=Fraction(1, 100),
        friction_coefficient_min=Fraction(1, 2),
        friction_coefficient_max=Fraction(3, 2),
        model_uncertainty_confidence=Fraction(95, 100),
    )
    ctrl_safe = ControllerModel(
        controller_name="safemind",
        uses_variance_aware_barrier=True,
        uses_differentiable_qp=True,
        has_meta_adaptive_risk=True,
    )
    claim_safe = SafeMindClaim(
        environment=env_bounded,
        controller=ctrl_safe,
        safety_violation_rate=Fraction(1, 100),
        safety_threshold=Fraction(5, 100),
    )

    # FAIL case: unbounded environment
    env_unbounded = EnvironmentModel(
        perception_noise_variance=Fraction(0),
        friction_coefficient_min=Fraction(0),
        friction_coefficient_max=Fraction(10),
        model_uncertainty_confidence=Fraction(0),
    )
    ctrl_naive = ControllerModel(
        controller_name="naive_rl",
        uses_variance_aware_barrier=False,
        uses_differentiable_qp=False,
        has_meta_adaptive_risk=False,
    )
    claim_bad = SafeMindClaim(
        environment=env_unbounded,
        controller=ctrl_naive,
        safety_violation_rate=Fraction(1, 10),
        safety_threshold=Fraction(5, 100),
    )

    # FAIL case 2: bounded environment but violation rate too high
    claim_over_threshold = SafeMindClaim(
        environment=env_bounded,
        controller=ctrl_safe,
        safety_violation_rate=Fraction(10),
        safety_threshold=Fraction(5, 100),
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_inversion_holds_fail_over_threshold", lambda: check_inversion_holds(claim_over_threshold)),
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
        if not v.startswith("PASS") and not k.endswith("_fail") and not k.endswith("_vacuous")
    ]
    unexpected = [
        k for k, v in results.items()
        if k.endswith("_fail") and not v.startswith("FAIL")
    ]
    failures.extend(unexpected)
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ARXIV_INV_SAFEMIND invariants: PASS")
