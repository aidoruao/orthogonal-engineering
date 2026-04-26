"""Invariant checks for D_ARXIV_INV_DEFENSE_TRILEMMA — Yeshua Inversion.

Paper: arXiv 2604.06436v2 (cs.CR)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    DefenseModel,
    DefenseTrilemmaClaim,
    DefenseTrilemmaEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: DefenseTrilemmaClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, completeness is achievable.

    Standard: arXiv 2604.06436v2 Yeshua Inversion operationalization.
    Falsifies if: unsafe_inputs_detected / total_inputs < safety_threshold.
    falsifies_if: unsafe detection rate is below safety_threshold after restriction.
    """
    if claim.total_inputs == Fraction(0):
        return True, ProofObject(
            rule="check_inversion_holds",
            premises=["total_inputs=0"],
            conclusion="No inputs to evaluate — inversion vacuously holds",
        )

    detection_rate = claim.unsafe_inputs_detected / claim.total_inputs
    if detection_rate < claim.safety_threshold:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"unsafe_inputs_detected={claim.unsafe_inputs_detected}",
                f"total_inputs={claim.total_inputs}",
                f"detection_rate={detection_rate}",
                f"safety_threshold={claim.safety_threshold}",
            ],
            conclusion="VIOLATION: Detection rate below safety threshold — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"detection_rate={detection_rate}",
            f"safety_threshold={claim.safety_threshold}",
        ],
        conclusion="Inversion holds: completeness achievable under discrete restriction",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: DefenseTrilemmaClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2604.06436v2 domain restriction operationalization.
    Falsifies if: prompt space is not finite or defense does not use allow-list.
    falsifies_if: prompt space is not finite or defense does not use allow-list.
    """
    d = claim.defense
    violations = []
    if not d.prompt_space_finite:
        violations.append("prompt_space_finite=False")
    if not d.uses_allow_list:
        violations.append("uses_allow_list=False")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"defense={d.defense_name}",
            "prompt_space_finite=True",
            "uses_allow_list=True",
        ],
        conclusion="Domain restriction satisfied: discrete finite prompt space with allow-list",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: DefenseTrilemmaClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted defenses.

    Standard: arXiv 2604.06436v2 original theorem preservation.
    Falsifies if: the original theorem is contradicted for unrestricted defenses.
    falsifies_if: the original theorem is contradicted for unrestricted defenses.
    """
    d = claim.defense
    # Unrestricted = continuous + utility-preserving + complete on connected space
    if d.is_continuous and d.preserves_utility and d.is_complete and not d.prompt_space_finite:
        return False, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "defense=unrestricted",
                "continuous=True",
                "preserves_utility=True",
                "is_complete=True",
                "prompt_space_finite=False",
            ],
            conclusion="VIOLATION: Original impossibility contradicted — trilemma violated",
        )

    if not d.prompt_space_finite:
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "defense=unrestricted",
                "original_theorem=preserves_trilemma",
            ],
            conclusion="Original impossibility holds for unrestricted defenses",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["defense=restricted", "check=vacuous"],
        conclusion="Original impossibility check vacuous for restricted defenses",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_DEFENSE_TRILEMMA invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: discrete defense with allow-list, high detection rate
    defense_discrete = DefenseModel(
        defense_name="discrete_allow_list",
        is_continuous=False,
        preserves_utility=False,
        is_complete=True,
        prompt_space_finite=True,
        uses_allow_list=True,
    )
    claim_safe = DefenseTrilemmaClaim(
        defense=defense_discrete,
        unsafe_inputs_detected=Fraction(99),
        total_inputs=Fraction(100),
        safety_threshold=Fraction(9, 10),
    )

    # FAIL case: unrestricted defense (continuous, utility-preserving, complete)
    defense_unrestricted = DefenseModel(
        defense_name="continuous_wrapper",
        is_continuous=True,
        preserves_utility=True,
        is_complete=True,
        prompt_space_finite=False,
        uses_allow_list=False,
    )
    claim_bad = DefenseTrilemmaClaim(
        defense=defense_unrestricted,
        unsafe_inputs_detected=Fraction(99),
        total_inputs=Fraction(100),
        safety_threshold=Fraction(9, 10),
    )

    # FAIL case 2: discrete defense but detection rate too low
    claim_low_detection = DefenseTrilemmaClaim(
        defense=defense_discrete,
        unsafe_inputs_detected=Fraction(5),
        total_inputs=Fraction(100),
        safety_threshold=Fraction(9, 10),
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_low_detection", lambda: check_inversion_holds(claim_low_detection)),
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
    print("All D_ARXIV_INV_DEFENSE_TRILEMMA invariants: PASS")
