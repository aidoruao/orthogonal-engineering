"""Invariant checks for D_ARXIV_INV_SOLVABILITY_COMPLEXITY — Yeshua Inversion.

Paper: arXiv 2603.18955v1 (math.LO / cs.LO / math.SP)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    ComputationalProblem,
    ComplexityMeasure,
    SolvabilityComplexityClaim,
    SolvabilityComplexityEvidence,
    IMPOSSIBLE_CLAIM,
    YESHUA_INVERSION,
)


# ---------------------------------------------------------------------------
# 1. Inversion holds
# ---------------------------------------------------------------------------

def check_inversion_holds(
    claim: SolvabilityComplexityClaim,
) -> Tuple[bool, ProofObject]:
    """The Yeshua Inversion must hold: under domain restriction, ranks are comparable.

    Standard: arXiv 2603.18955v1 Yeshua Inversion operationalization.
    Falsifies if: complexity.rank_comparable is False.
    falsifies_if: complexity.rank_comparable is False.
    """
    if not claim.complexity.rank_comparable:
        return False, ProofObject(
            rule="check_inversion_holds",
            premises=[
                f"sci_height={claim.complexity.sci_height}",
                f"weihrauch_sci_rank={claim.complexity.weihrauch_sci_rank}",
                "rank_comparable=False",
            ],
            conclusion="VIOLATION: Ranks are not comparable — inversion fails",
        )

    return True, ProofObject(
        rule="check_inversion_holds",
        premises=[
            f"sci_height={claim.complexity.sci_height}",
            f"weihrauch_sci_rank={claim.complexity.weihrauch_sci_rank}",
            "rank_comparable=True",
        ],
        conclusion="Inversion holds: SCI and Weihrauch ranks comparable under regularity restriction",
    )


# ---------------------------------------------------------------------------
# 2. Domain restriction satisfied
# ---------------------------------------------------------------------------

def check_domain_restriction_satisfied(
    claim: SolvabilityComplexityClaim,
) -> Tuple[bool, ProofObject]:
    """The domain restriction must be satisfied for the inversion to apply.

    Standard: arXiv 2603.18955v1 domain restriction operationalization.
    Falsifies if: base_regularity_class is not in {continuous, borel, baire} or no query policy is specified.
    falsifies_if: base_regularity_class is not in {continuous, borel, baire} or no query policy is specified.
    """
    prob = claim.problem
    valid_classes = {"continuous", "borel", "baire"}
    violations = []

    if prob.base_regularity_class not in valid_classes:
        violations.append(f"base_regularity_class={prob.base_regularity_class}")
    if not prob.uses_fixed_query_policy and not prob.uses_adaptive_query_policy:
        violations.append("no_query_policy_specified")

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
            f"base_regularity_class={prob.base_regularity_class}",
            f"uses_fixed_query_policy={prob.uses_fixed_query_policy}",
            f"uses_adaptive_query_policy={prob.uses_adaptive_query_policy}",
        ],
        conclusion="Domain restriction satisfied: regularity class with query policy",
    )


# ---------------------------------------------------------------------------
# 3. Original impossibility holds without restriction
# ---------------------------------------------------------------------------

def check_original_impossibility_holds_without_restriction(
    claim: SolvabilityComplexityClaim,
) -> Tuple[bool, ProofObject]:
    """The original impossibility claim must still hold for unrestricted problems.

    Standard: arXiv 2603.18955v1 original theorem preservation.
    Falsifies if: the original theorem is contradicted for unrestricted problems.
    falsifies_if: the original theorem is contradicted for unrestricted problems.
    """
    prob = claim.problem
    comp = claim.complexity

    unrestricted = prob.base_regularity_class == "unrestricted"

    if unrestricted:
        if comp.rank_comparable:
            return False, ProofObject(
                rule="check_original_impossibility_holds_without_restriction",
                premises=[
                    "problem=unrestricted",
                    "rank_comparable=True",
                ],
                conclusion="VIOLATION: Original impossibility contradicted — unrestricted problem has comparable ranks",
            )
        return True, ProofObject(
            rule="check_original_impossibility_holds_without_restriction",
            premises=[
                "problem=unrestricted",
                "original_theorem=preserves_incomparability",
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
    """Run all D_ARXIV_INV_SOLVABILITY_COMPLEXITY invariants with nominal data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS case: Borel regularity with fixed-query policy, comparable ranks
    prob_restricted = ComputationalProblem(
        problem_name="borel_fixed_query",
        base_regularity_class="borel",
        uses_fixed_query_policy=True,
        uses_adaptive_query_policy=False,
    )
    comp_comparable = ComplexityMeasure(
        sci_height=2,
        weihrauch_sci_rank=2,
        rank_comparable=True,
    )
    claim_safe = SolvabilityComplexityClaim(
        problem=prob_restricted,
        complexity=comp_comparable,
    )

    # FAIL case: unrestricted problem
    prob_unrestricted = ComputationalProblem(
        problem_name="unrestricted_type_g",
        base_regularity_class="unrestricted",
        uses_fixed_query_policy=False,
        uses_adaptive_query_policy=False,
    )
    claim_bad = SolvabilityComplexityClaim(
        problem=prob_unrestricted,
        complexity=comp_comparable,
    )

    # FAIL case 2: restricted problem but incomparable ranks
    comp_incomparable = ComplexityMeasure(
        sci_height=0,
        weihrauch_sci_rank=-1,  # sentinel for infinite
        rank_comparable=False,
    )
    claim_incomparable = SolvabilityComplexityClaim(
        problem=prob_restricted,
        complexity=comp_incomparable,
    )

    checks = [
        ("check_inversion_holds_pass", lambda: check_inversion_holds(claim_safe)),
        ("check_domain_restriction_satisfied_pass", lambda: check_domain_restriction_satisfied(claim_safe)),
        ("check_original_impossibility_holds_without_restriction_vacuous", lambda: check_original_impossibility_holds_without_restriction(claim_safe)),
        ("check_domain_restriction_satisfied_fail", lambda: check_domain_restriction_satisfied(claim_bad)),
        ("check_original_impossibility_holds_without_restriction_fail", lambda: check_original_impossibility_holds_without_restriction(claim_bad)),
        ("check_inversion_holds_fail_incomparable", lambda: check_inversion_holds(claim_incomparable)),
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
    print("All D_ARXIV_INV_SOLVABILITY_COMPLEXITY invariants: PASS")
