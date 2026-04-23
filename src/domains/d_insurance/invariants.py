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

    Falsifies if: duty-to-defend ratio is strictly below unity when duty is triggered.
    falsifies_if: policy.duty_to_defend_ratio() < Fraction(1, 1).
    """
    ratio = policy.duty_to_defend_ratio()
    if ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion="VIOLATION: Breach of duty to defend (defense ratio below unity)",
            premises=[
                f"claim_made={policy.claim_made}",
                f"duty_triggered={policy.duty_to_defend_triggered}",
                f"ratio={ratio}",
            ],
            rule="duty_to_defend",
            falsifies_if="policy.duty_to_defend_ratio() < Fraction(1, 1)"
        )

    return True, ProofObject(
        conclusion="Duty to defend satisfied",
        premises=[f"ratio={ratio}"],
        rule="duty_to_defend",
        falsifies_if="policy.duty_to_defend_ratio() < Fraction(1, 1)"
    )


def check_insurable_interest(interest: InsurableInterest) -> Tuple[bool, ProofObject]:
    """Must have insurable interest at time of loss.

    Falsifies if: insurable interest ratio is zero or negative.
    falsifies_if: interest.insurable_interest_ratio() <= Fraction(0, 1).
    """
    ratio = interest.insurable_interest_ratio()
    if ratio <= Fraction(0, 1):
        return False, ProofObject(
            conclusion="VIOLATION: No insurable interest (ratio zero or negative)",
            premises=[
                f"financial_stake={interest.financial_stake}",
                f"coverage_limit={interest.coverage_limit}",
                f"ratio={ratio}",
            ],
            rule="insurable_interest",
            falsifies_if="interest.insurable_interest_ratio() <= Fraction(0, 1)"
        )

    return True, ProofObject(
        conclusion="Insurable interest exists",
        premises=[f"ratio={ratio}"],
        rule="insurable_interest",
        falsifies_if="interest.insurable_interest_ratio() <= Fraction(0, 1)"
    )


def check_uberimmae_fidei(policy: InsurancePolicy) -> Tuple[bool, ProofObject]:
    """Utmost good faith — premiums must be paid.

    Falsifies if: premium payment ratio is strictly below unity.
    falsifies_if: policy.premium_payment_ratio() < Fraction(1, 1).
    """
    ratio = policy.premium_payment_ratio()
    if ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion="VIOLATION: Premiums not fully paid (payment ratio below unity)",
            premises=[
                f"premiums_paid={len(policy.premiums_paid)}",
                f"expected={policy.expected_premium_count}",
                f"ratio={ratio}",
            ],
            rule="uberrimae_fidei",
            falsifies_if="policy.premium_payment_ratio() < Fraction(1, 1)"
        )

    return True, ProofObject(
        conclusion="Good faith — premiums current",
        premises=[f"ratio={ratio}"],
        rule="uberrimae_fidei",
        falsifies_if="policy.premium_payment_ratio() < Fraction(1, 1)"
    )


def run_all_invariants() -> dict:
    """Run all D_INSURANCE invariants with passing and failing sample data.

    Falsifies if: any invariant fails or raises an exception.
    falsifies_if: any invariant fails or raises an exception.
    """
    # PASS: duty triggered and defense provided
    policy_defend_pass = InsurancePolicy(
        policy_number="INS-PASS-001",
        insured="Alice",
        insurer="Acme Insurance",
        policy_type=PolicyType.LIABILITY,
        coverage_limit=Fraction(1000000),
        deductible=Fraction(1000),
        expected_premium_count=4,
        premiums_paid=[Fraction(250), Fraction(250), Fraction(250), Fraction(250)],
        claim_made=True,
        duty_to_defend_triggered=True,
        defense_provided=True,
    )
    # FAIL: duty triggered but defense withheld
    policy_defend_fail = InsurancePolicy(
        policy_number="INS-FAIL-001",
        insured="Bob",
        insurer="Acme Insurance",
        policy_type=PolicyType.LIABILITY,
        coverage_limit=Fraction(1000000),
        deductible=Fraction(1000),
        expected_premium_count=4,
        premiums_paid=[Fraction(250), Fraction(250), Fraction(250), Fraction(250)],
        claim_made=True,
        duty_to_defend_triggered=True,
        defense_provided=False,
    )

    # PASS: positive financial stake
    interest_pass = InsurableInterest(
        policyholder="Alice",
        subject_matter="Warehouse",
        financial_stake=Fraction(500000),
        coverage_limit=Fraction(1000000),
    )
    # FAIL: zero financial stake
    interest_fail = InsurableInterest(
        policyholder="Bob",
        subject_matter="Warehouse",
        financial_stake=Fraction(0),
        coverage_limit=Fraction(1000000),
    )

    # PASS: all premiums paid
    policy_premium_pass = InsurancePolicy(
        policy_number="INS-PASS-002",
        insured="Charlie",
        insurer="Acme Insurance",
        policy_type=PolicyType.PROPERTY,
        coverage_limit=Fraction(500000),
        deductible=Fraction(500),
        expected_premium_count=2,
        premiums_paid=[Fraction(100), Fraction(100)],
    )
    # FAIL: missing premiums
    policy_premium_fail = InsurancePolicy(
        policy_number="INS-FAIL-002",
        insured="Dana",
        insurer="Acme Insurance",
        policy_type=PolicyType.PROPERTY,
        coverage_limit=Fraction(500000),
        deductible=Fraction(500),
        expected_premium_count=2,
        premiums_paid=[Fraction(100)],
    )

    checks = [
        ("check_duty_to_defend_pass", lambda: check_duty_to_defend(policy_defend_pass)),
        ("check_duty_to_defend_fail", lambda: check_duty_to_defend(policy_defend_fail)),
        ("check_insurable_interest_pass", lambda: check_insurable_interest(interest_pass)),
        ("check_insurable_interest_fail", lambda: check_insurable_interest(interest_fail)),
        ("check_uberimmae_fidei_pass", lambda: check_uberimmae_fidei(policy_premium_pass)),
        ("check_uberimmae_fidei_fail", lambda: check_uberimmae_fidei(policy_premium_fail)),
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
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS") and not k.endswith("_fail")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_INSURANCE invariants: PASS")
