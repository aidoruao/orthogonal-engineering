#!/usr/bin/env python3
"""Insurance Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    InsurableInterest,
    InsurancePolicy,
    PolicyType,
)

def check_duty_to_defend(policy: InsurancePolicy) -> Tuple[bool, ProofObject]:
    """Duty to defend when claim potentially covered.

    Falsifies if: duty_to_defend_owed is True but defense_provided is False.
    falsifies_if: duty_to_defend_owed is True but defense_provided is False.
    """
    if not policy.duty_to_defend_owed():
        return True, ProofObject(
            conclusion="No duty to defend triggered",
            premises=[],
            rule="duty_to_defend_applicability"
        )
    
    if policy.defense_provided:
        return True, ProofObject(
            conclusion="Duty to defend satisfied",
            premises=[],
            rule="duty_to_defend"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Breach of duty to defend",
        premises=["Claim made", "Defense not provided"],
        rule="duty_to_defend"
    )

def check_insurable_interest(interest: InsurableInterest) -> Tuple[bool, ProofObject]:
    """Must have insurable interest at time of loss.

    Falsifies if: insurable interest does not exist when evaluated.
    falsifies_if: insurable interest does not exist when evaluated.
    """
    if interest.has_insurable_interest():
        return True, ProofObject(
            conclusion="Insurable interest exists",
            premises=[f"Financial stake: {interest.financial_stake}"],
            rule="insurable_interest"
        )
    return False, ProofObject(
        conclusion="VIOLATION: No insurable interest",
        premises=[],
        rule="insurable_interest"
    )

def check_uberimmae_fidei(policy: InsurancePolicy) -> Tuple[bool, ProofObject]:
    """Utmost good faith — premiums must be paid.

    Falsifies if: premiums_current returns False.
    falsifies_if: premiums_current returns False.
    """
    if policy.premiums_current():
        return True, ProofObject(
            conclusion="Good faith — premiums current",
            premises=[],
            rule="uberrimae_fidei"
        )
    return False, ProofObject(
        conclusion="VIOLATION: Premiums not paid",
        premises=[],
        rule="uberrimae_fidei"
    )


def run_all_invariants() -> dict:
    """Run all D_INSURANCE invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    insurance_policy = InsurancePolicy(
        policy_number="SAMPLE",
        insured="SAMPLE",
        insurer="SAMPLE",
        policy_type=PolicyType.LIABILITY,
        coverage_limit=Fraction(100),
        deductible=Fraction(1),
    )
    insurable_interest = InsurableInterest(
        policyholder="SAMPLE",
        subject_matter="SAMPLE",
        financial_stake=Fraction(1),
    )

    checks = [
        ("check_duty_to_defend", lambda: check_duty_to_defend(insurance_policy)),
        ("check_insurable_interest", lambda: check_insurable_interest(insurable_interest)),
        ("check_uberimmae_fidei", lambda: check_uberimmae_fidei(insurance_policy)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_INSURANCE invariants: PASS")
