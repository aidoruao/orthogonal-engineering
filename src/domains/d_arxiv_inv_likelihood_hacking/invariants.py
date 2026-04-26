"""Invariant checks for D_ARXIV_INV_LIKELIHOOD_HACKING — Yeshua Inversion.

Paper: arXiv 2603.24126v1 (cs.PL / cs.LG)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    ProbabilisticProgram,
    TrainingSetup,
    LikelihoodHackingClaim,
    LikelihoodHackingEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: LikelihoodHackingClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, violation rate is bounded.

    Standard: arXiv 2603.24126v1 Yeshua Inversion operationalization.
    Falsifies if: observed_violation_rate > training.violation_rate_threshold.
    falsifies_if: observed_violation_rate exceeds violation_rate_threshold after restriction.
    """
    if claim.observed_violation_rate > claim.training.violation_rate_threshold:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"observed_violation_rate={claim.observed_violation_rate}",
                f"violation_rate_threshold={claim.training.violation_rate_threshold}",
            ],
            conclusion="VIOLATION: Violation rate exceeds threshold — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"observed_violation_rate={claim.observed_violation_rate}",
            f"violation_rate_threshold={claim.training.violation_rate_threshold}",
        ],
        conclusion="Inversion holds: likelihood hacking prevented by syntactic restriction",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: LikelihoodHackingClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2603.24126v1 domain restriction operationalization.
    Falsifies if: program does not enforce normalisation or lacks syntactic safety checks.
    falsifies_if: program does not enforce normalisation or lacks syntactic safety checks.
    """
    prog = claim.program
    violations = []
    if not prog.enforces_normalisation:
        violations.append("enforces_normalisation=False")
    if not prog.has_syntactic_safety_checks:
        violations.append("has_syntactic_safety_checks=False")

    if violations:
        return False, ProofObject(
            rule="check_domain_restriction_satisfied",
            premises=violations,
            conclusion="VIOLATION: Domain restriction not satisfied — inversion does not apply",
        )

    return True, ProofObject(
        rule="check_domain_restriction_satisfied",
        premises=[
            f"program={prog.program_name}",
            f"language_fragment={prog.language_fragment}",
            "enforces_normalisation=True",
            "has_syntactic_safety_checks=True",
        ],
        conclusion="Domain restriction satisfied: program is in L_safe fragment",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: LikelihoodHackingClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted programs.

    Standard: arXiv 2603.24126v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for unrestricted programs.
    falsifies_if: the original theorem is contradicted for unrestricted programs.
    """
    prog = claim.program
    train = claim.training

    unrestricted = not prog.enforces_normalisation and not prog.has_syntactic_safety_checks

    if unrestricted and train.uses_rl_training:
        if claim.observed_violation_rate <= train.violation_rate_threshold:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "program=unrestricted",
                    "uses_rl_training=True",
                    f"observed_violation_rate={claim.observed_violation_rate}",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — unrestricted program shows no LH",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "program=unrestricted",
                "uses_rl_training=True",
                "original_theorem=preserves_lh_vulnerability",
            ],
            conclusion="Original impossibility holds for unrestricted programs",
        )

    return True, ProofObject(
        rule="check_original_impossibility_holds_without_restriction",
        premises=["program=restricted", "check=vacuous"],
        conclusion="Original impossibility check vacuous for restricted programs",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_invariants() -> dict:
    """Run all D_ARXIV_INV_LIKELIHOOD_HACKING invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: SafeStan fragment with low violation rate
    prog_safe = ProbabilisticProgram(
        program_name="safestan_model",
        language_fragment="L_safe",
        enforces_normalisation=True,
        has_syntactic_safety_checks=True,
    )
    train_rl = TrainingSetup(
        uses_rl_training=True,
        optimisation_pressure=Fraction(9, 10),
        violation_rate_threshold=Fraction(1, 100),
    )
    claim_safe = LikelihoodHackingClaim(
        program=prog_safe,
        training=train_rl,
        observed_violation_rate=Fraction(0),
    )

    # FAIL case: unrestricted PyMC fragment
    prog_unsafe = ProbabilisticProgram(
        program_name="pymc_model",
        language_fragment="full_pymc",
        enforces_normalisation=False,
        has_syntactic_safety_checks=False,
    )
    claim_bad = LikelihoodHackingClaim(
        program=prog_unsafe,
        training=train_rl,
        observed_violation_rate=Fraction(0),
    )

    # FAIL case 2: safe fragment but violation rate too high
    claim_high_violation = LikelihoodHackingClaim(
        program=prog_safe,
        training=train_rl,
        observed_violation_rate=Fraction(10),
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_inversion_holds_fail_high_violation", lambda: check_inversion_holds(claim_high_violation)),
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
    print("All D_ARXIV_INV_LIKELIHOOD_HACKING invariants: PASS")
