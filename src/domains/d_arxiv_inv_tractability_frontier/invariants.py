"""Invariant checks for D_ARXIV_INV_TRACTABILITY_FRONTIER — Yeshua Inversion.

Paper: arXiv 2604.07349v1 (cs.LO / cs.CC / cs.AI)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    DecisionProblem,
    CertificationResult,
    TractabilityFrontierClaim,
    TractabilityFrontierEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: TractabilityFrontierClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, exact certification is possible.

    Standard: arXiv 2604.07349v1 Yeshua Inversion operationalization.
    Falsifies if: certification is not exact or not efficiently checkable.
    falsifies_if: certification is not exact or not efficiently checkable.
    """
    cert = claim.certification
    if not cert.is_exact:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=["is_exact=False"],
            conclusion="VIOLATION: Certification is not exact — inversion fails",
        )
    if not cert.is_efficiently_checkable:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=["is_efficiently_checkable=False"],
            conclusion="VIOLATION: Certification is not efficiently checkable — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            "is_exact=True",
            "is_efficiently_checkable=True",
        ],
        conclusion="Inversion holds: exact relevance certification achievable under bounded influence",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: TractabilityFrontierClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.07349v1 domain restriction operationalization.
    Falsifies if: problem lacks bounded coordinate influence or separable quotient structure.
    falsifies_if: problem lacks bounded coordinate influence or separable quotient structure.
    """
    prob = claim.problem
    violations = []
    if not prob.has_bounded_coordinate_influence:
        violations.append("has_bounded_coordinate_influence=False")
    if not prob.has_separable_quotient_structure:
        violations.append("has_separable_quotient_structure=False")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"problem={prob.problem_name}",
            f"coordinate_count={prob.coordinate_count}",
            "has_bounded_coordinate_influence=True",
            "has_separable_quotient_structure=True",
        ],
        conclusion="Domain restriction satisfied: bounded influence with separable quotient",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: TractabilityFrontierClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted problems.

    Standard: arXiv 2604.07349v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for unrestricted problems.
    falsifies_if: the original theorem is contradicted for unrestricted problems.
    """
    prob = claim.problem
    cert = claim.certification

    unrestricted = (
        not prob.has_bounded_coordinate_influence
        and not prob.has_separable_quotient_structure
    )

    if unrestricted:
        if cert.is_exact and cert.is_efficiently_checkable:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "problem=unrestricted",
                    "is_exact=True",
                    "is_efficiently_checkable=True",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — unrestricted problem has exact certification",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "problem=unrestricted",
                "original_theorem=preserves_impossibility",
            ],
            conclusion="Original impossibility holds for unrestricted problems",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["problem=restricted", "check=vacuous"],
        conclusion="Original impossibility check vacuous for restricted problems",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_TRACTABILITY_FRONTIER invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: bounded influence + separable quotient, exact certification
    prob_restricted = DecisionProblem(
        problem_name="bounded_influence_problem",
        has_bounded_coordinate_influence=True,
        has_separable_quotient_structure=True,
        coordinate_count=10,
    )
    cert_exact = CertificationResult(
        is_exact=True,
        is_efficiently_checkable=True,
        obstruction_family_present=False,
    )
    claim_safe = TractabilityFrontierClaim(
        problem=prob_restricted,
        certification=cert_exact,
    )

    # FAIL case: unrestricted problem
    prob_unrestricted = DecisionProblem(
        problem_name="arbitrary_closure_closed",
        has_bounded_coordinate_influence=False,
        has_separable_quotient_structure=False,
        coordinate_count=100,
    )
    claim_bad = TractabilityFrontierClaim(
        problem=prob_unrestricted,
        certification=cert_exact,
    )

    # FAIL case 2: restricted problem but inexact certification
    cert_inexact = CertificationResult(
        is_exact=False,
        is_efficiently_checkable=True,
        obstruction_family_present=True,
    )
    claim_inexact = TractabilityFrontierClaim(
        problem=prob_restricted,
        certification=cert_inexact,
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_inexact", lambda: check_inversion_holds(claim_inexact)),
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
    print("All D_ARXIV_INV_TRACTABILITY_FRONTIER invariants: PASS")
