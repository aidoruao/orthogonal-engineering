"""Invariant checks for D_ARXIV_INV_SHARP_LOCAL_MINIMA — Yeshua Inversion.

Paper: arXiv 2604.09412v1 (stat.ML / cs.LG)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    NetworkArchitecture,
    OptimizationDynamics,
    SharpLocalMinimaClaim,
    SharpLocalMinimaEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: SharpLocalMinimaClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, spurious rate is bounded.

    Standard: arXiv 2604.09412v1 Yeshua Inversion operationalization.
    Falsifies if: dynamics.spurious_solution_rate > spurious_rate_threshold.
    falsifies_if: spurious_solution_rate exceeds spurious_rate_threshold after restriction.
    """
    if claim.dynamics.spurious_solution_rate > claim.spurious_rate_threshold:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"spurious_solution_rate={claim.dynamics.spurious_solution_rate}",
                f"spurious_rate_threshold={claim.spurious_rate_threshold}",
            ],
            conclusion="VIOLATION: Spurious solution rate exceeds threshold — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"spurious_solution_rate={claim.dynamics.spurious_solution_rate}",
            f"spurious_rate_threshold={claim.spurious_rate_threshold}",
        ],
        conclusion="Inversion holds: global minima accessible under overparameterisation",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: SharpLocalMinimaClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.09412v1 domain restriction operationalization.
    Falsifies if: network is not overparameterised.
    falsifies_if: network is not overparameterised.
    """
    arch = claim.architecture
    if not arch.is_overparameterised:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=[
                f"width={arch.width}",
                f"teacher_dimensionality={arch.teacher_dimensionality}",
                "is_overparameterised=False",
            ],
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"network={arch.network_name}",
            f"width={arch.width}",
            f"teacher_dimensionality={arch.teacher_dimensionality}",
            "is_overparameterised=True",
        ],
        conclusion="Domain restriction satisfied: network is overparameterised",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: SharpLocalMinimaClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for well-specified (non-overparameterised) networks.

    Standard: arXiv 2604.09412v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for well-specified networks.
    falsifies_if: the original theorem is contradicted for well-specified networks.
    """
    arch = claim.architecture
    dyn = claim.dynamics

    well_specified = not arch.is_overparameterised

    if well_specified and dyn.uses_sgd:
        if dyn.converged_to_global_minimum:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "regime=well_specified",
                    "uses_sgd=True",
                    "converged_to_global_minimum=True",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — well-specified network reaches global minimum",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "regime=well_specified",
                "uses_sgd=True",
                "original_theorem=preserves_isolated_minima",
            ],
            conclusion="Original impossibility holds for well-specified networks",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["regime=overparameterised", "check=vacuous"],
        conclusion="Original impossibility check vacuous for overparameterised networks",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_SHARP_LOCAL_MINIMA invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: overparameterised network, low spurious rate
    arch_over = NetworkArchitecture(
        network_name="wide_relu",
        width=100,
        teacher_dimensionality=10,
        is_overparameterised=True,
    )
    dyn_good = OptimizationDynamics(
        uses_sgd=True,
        converged_to_global_minimum=True,
        spurious_solution_rate=Fraction(1, 100),
    )
    claim_safe = SharpLocalMinimaClaim(
        architecture=arch_over,
        dynamics=dyn_good,
        spurious_rate_threshold=Fraction(5, 100),
    )

    # FAIL case: well-specified network
    arch_well = NetworkArchitecture(
        network_name="narrow_relu",
        width=5,
        teacher_dimensionality=10,
        is_overparameterised=False,
    )
    dyn_bad = OptimizationDynamics(
        uses_sgd=True,
        converged_to_global_minimum=True,
        spurious_solution_rate=Fraction(1, 100),
    )
    claim_bad = SharpLocalMinimaClaim(
        architecture=arch_well,
        dynamics=dyn_bad,
        spurious_rate_threshold=Fraction(5, 100),
    )

    # FAIL case 2: overparameterised but spurious rate too high
    dyn_high_spurious = OptimizationDynamics(
        uses_sgd=True,
        converged_to_global_minimum=False,
        spurious_solution_rate=Fraction(20),
    )
    claim_high_spurious = SharpLocalMinimaClaim(
        architecture=arch_over,
        dynamics=dyn_high_spurious,
        spurious_rate_threshold=Fraction(5, 100),
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_high_spurious", lambda: check_inversion_holds(claim_high_spurious)),
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
    print("All D_ARXIV_INV_SHARP_LOCAL_MINIMA invariants: PASS")
