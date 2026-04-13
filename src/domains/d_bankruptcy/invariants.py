#!/usr/bin/env python3
"""Bankruptcy Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    BankruptcyCase,
    Chapter,
    Debtor,
)

def check_means_test(case: BankruptcyCase) -> Tuple[bool, ProofObject]:
    """Ch 7 means test — income must be below state median.

    Falsifies if: case.chapter is CH_7 and case.passes_means_test() is False.
    falsifies_if: case.chapter is CH_7 and case.passes_means_test() is False.
    """
    if case.chapter != Chapter.CH_7:
        return True, ProofObject(
            conclusion="Means test not applicable",
            premises=[f"Chapter {case.chapter.value}"],
            rule="means_test_applicability"
        )
    
    if case.passes_means_test():
        return True, ProofObject(
            conclusion="Means test satisfied",
            premises=[f"Income: {case.debtor.monthly_income}"],
            rule="ch7_means_test"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Income exceeds state median",
        premises=[f"Income: {case.debtor.monthly_income}", f"Median: {case.debtor.state_median_income}"],
        rule="ch7_means_test"
    )

def check_ch13_plan(case: BankruptcyCase) -> Tuple[bool, ProofObject]:
    """Ch 13 requires 60-month plan.

    Falsifies if: case.chapter is CH_13 and case.has_adequate_plan() is False.
    falsifies_if: case.chapter is CH_13 and case.has_adequate_plan() is False.
    """
    if case.chapter != Chapter.CH_13:
        return True, ProofObject(
            conclusion="Ch 13 plan not applicable",
            premises=[],
            rule="ch13_plan_applicability"
        )
    
    if case.has_adequate_plan():
        return True, ProofObject(
            conclusion="Ch 13 plan requirements satisfied",
            premises=[f"Duration: {case.plan_duration_months} months"],
            rule="ch13_plan"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Ch 13 plan inadequate",
        premises=[f"Duration: {case.plan_duration_months}"],
        rule="ch13_plan"
    )

def check_automatic_stay(case: BankruptcyCase) -> Tuple[bool, ProofObject]:
    """Automatic stay effective upon filing.

    Falsifies if: not applicable (function reports status and returns True).
    falsifies_if: not applicable (function reports status and returns True).
    """
    if case.automatic_stay_active:
        return True, ProofObject(
            conclusion="Automatic stay in effect",
            premises=[],
            rule="automatic_stay"
        )
    return True, ProofObject(
        conclusion="Automatic stay lifted or not applicable",
        premises=[],
        rule="automatic_stay"
    )


def run_all_invariants() -> dict:
    """Run all D_BANKRUPTCY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    bankruptcy_case = BankruptcyCase(
        case_number="SAMPLE",
        debtor=Debtor(
        name="Sample BANKRUPT",
    ),
        chapter=Chapter.CH_7,
        filing_date=None,
    )

    checks = [
        ("check_automatic_stay", lambda: check_automatic_stay(bankruptcy_case)),
        ("check_ch13_plan", lambda: check_ch13_plan(bankruptcy_case)),
        ("check_means_test", lambda: check_means_test(bankruptcy_case)),
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
    print("All D_BANKRUPTCY invariants: PASS")
