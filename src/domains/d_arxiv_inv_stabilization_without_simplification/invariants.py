"""Invariant checks for D_ARXIV_INV_STABILIZATION_WITHOUT_SIMPLIFICATION — Yeshua Inversion.

Paper: arXiv 2604.06709v1 (cs.SE)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    SoftwareSystem,
    EvolutionMetrics,
    StabilizationClaim,
    StabilizationEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: StabilizationClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: uncertainty decreases while burden does not.

    Standard: arXiv 2604.06709v1 Yeshua Inversion operationalization.
    Falsifies if: uncertainty does not decrease or burden decreases.
    falsifies_if: uncertainty does not decrease or burden decreases.
    """
    m = claim.metrics
    if m.uncertainty_change >= Fraction(0):
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"uncertainty_change={m.uncertainty_change}",
            ],
            conclusion="VIOLATION: Uncertainty does not decrease — inversion fails",
        )
    if m.burden_change < Fraction(0):
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"burden_change={m.burden_change}",
            ],
            conclusion="VIOLATION: Structural burden decreases — this is simplification, not stabilization without simplification",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"uncertainty_change={m.uncertainty_change}",
            f"burden_change={m.burden_change}",
        ],
        conclusion="Inversion holds: uncertainty decreases while structural burden does not",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: StabilizationClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.06709v1 domain restriction operationalization.
    Falsifies if: system lacks structural regularization, process stabilization, or covariance control.
    falsifies_if: system lacks structural regularization, process stabilization, or covariance control.
    """
    sys = claim.system
    violations = []
    if not sys.has_structural_regularization:
        violations.append("has_structural_regularization=False")
    if not sys.has_process_stabilization:
        violations.append("has_process_stabilization=False")
    if not sys.has_covariance_control:
        violations.append("has_covariance_control=False")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"system={sys.system_name}",
            "has_structural_regularization=True",
            "has_process_stabilization=True",
            "has_covariance_control=True",
        ],
        conclusion="Domain restriction satisfied: system has regularization, stabilization, and covariance control",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: StabilizationClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted systems.

    Standard: arXiv 2604.06709v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for unrestricted systems.
    falsifies_if: the original theorem is contradicted for unrestricted systems.
    """
    sys = claim.system
    m = claim.metrics

    unrestricted = (
        not sys.has_structural_regularization
        and not sys.has_process_stabilization
        and not sys.has_covariance_control
    )

    if unrestricted:
        # Original impossibility: uncertainty cannot decrease without burden decreasing
        if m.uncertainty_change < Fraction(0) and m.burden_change >= Fraction(0):
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "system=unrestricted",
                    f"uncertainty_change={m.uncertainty_change}",
                    f"burden_change={m.burden_change}",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — unrestricted system shows stabilization without simplification",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "system=unrestricted",
                "original_theorem=preserves_coupling",
            ],
            conclusion="Original impossibility holds for unrestricted systems",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["system=restricted", "check=vacuous"],
        conclusion="Original impossibility check vacuous for restricted systems",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_STABILIZATION_WITHOUT_SIMPLIFICATION invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: restricted system with decreasing uncertainty, stable burden
    sys_restricted = SoftwareSystem(
        system_name="regulated_codebase",
        has_structural_regularization=True,
        has_process_stabilization=True,
        has_covariance_control=True,
    )
    metrics_safe = EvolutionMetrics(
        structural_burden=Fraction(100),
        uncertainty=Fraction(10),
        burden_change=Fraction(0),
        uncertainty_change=Fraction(-3),
    )
    claim_safe = StabilizationClaim(
        system=sys_restricted,
        metrics=metrics_safe,
    )

    # FAIL case: unrestricted system
    sys_unrestricted = SoftwareSystem(
        system_name="legacy_codebase",
        has_structural_regularization=False,
        has_process_stabilization=False,
        has_covariance_control=False,
    )
    metrics_bad = EvolutionMetrics(
        structural_burden=Fraction(100),
        uncertainty=Fraction(10),
        burden_change=Fraction(0),
        uncertainty_change=Fraction(-3),
    )
    claim_bad = StabilizationClaim(
        system=sys_unrestricted,
        metrics=metrics_bad,
    )

    # FAIL case 2: restricted system but burden decreases
    metrics_simplification = EvolutionMetrics(
        structural_burden=Fraction(100),
        uncertainty=Fraction(10),
        burden_change=Fraction(-5),
        uncertainty_change=Fraction(-3),
    )
    claim_simplification = StabilizationClaim(
        system=sys_restricted,
        metrics=metrics_simplification,
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_simplification", lambda: check_inversion_holds(claim_simplification)),
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
    print("All D_ARXIV_INV_STABILIZATION_WITHOUT_SIMPLIFICATION invariants: PASS")
