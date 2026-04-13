#!/usr/bin/env python3
"""Tax Law Invariants — IRC compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    BracketCalculator,
    DeductionValidator,
    TaxBracket,
    WithholdingChecker,
)


def check_bracket_monotonicity(calc: BracketCalculator) -> Tuple[bool, ProofObject]:
    """Tax brackets must be monotonic (higher income → higher rate).

    Falsifies if: is_monotonic returns False (regressive bracket detected).
    falsifies_if: is_monotonic returns False (regressive bracket detected).
    """
    if not calc.is_monotonic():
        return False, ProofObject(
            conclusion="VIOLATION: Tax brackets not monotonic (regressive detected)",
            premises=[],
            rule="tax_bracket_monotonicity"
        )
    
    return True, ProofObject(
        conclusion="Tax brackets monotonic",
        premises=[f"Brackets: {len(calc.brackets)}"],
        rule="tax_bracket_monotonicity"
    )


def check_salt_cap(validator: DeductionValidator) -> Tuple[bool, ProofObject]:
    """SALT deduction must not exceed $10,000 cap.

    Falsifies if: salt_within_cap returns False.
    falsifies_if: salt_within_cap returns False.
    """
    if not validator.salt_within_cap():
        return False, ProofObject(
            conclusion=f"VIOLATION: SALT deduction {validator.salt_deduction} exceeds cap {validator.SALT_CAP}",
            premises=[],
            rule="salt_deduction_cap"
        )
    
    return True, ProofObject(
        conclusion="SALT deduction within cap",
        premises=[],
        rule="salt_deduction_cap"
    )


def check_withholding_adequacy(checker: WithholdingChecker) -> Tuple[bool, ProofObject]:
    """Withholding must meet safe harbor (90% of liability).

    Falsifies if: is_adequate returns False for withholding safe harbor.
    falsifies_if: is_adequate returns False for withholding safe harbor.
    """
    if not checker.is_adequate():
        return False, ProofObject(
            conclusion=f"VIOLATION: Withholding inadequate for safe harbor",
            premises=[f"Withheld: {checker.annual_withheld}", f"Liability: {checker.estimated_tax_liability}"],
            rule="withholding_safe_harbor"
        )
    
    return True, ProofObject(
        conclusion="Withholding meets safe harbor",
        premises=[],
        rule="withholding_safe_harbor"
    )


def run_all_invariants() -> dict:
    """Run all D_TAX_LAW invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    bracket_calculator = BracketCalculator(
        brackets=[TaxBracket(
        min_income=Fraction(1),
        max_income=Fraction(1000),
        rate=Fraction(1),
    )],
        income=Fraction(1),
    )
    deduction_validator = DeductionValidator(
        salt_deduction=Fraction(1),
        standard_deduction=Fraction(1),
        itemized_deductions=Fraction(1),
    )
    withholding_checker = WithholdingChecker(
        annual_withheld=Fraction(1),
        estimated_tax_liability=Fraction(1),
    )

    checks = [
        ("check_bracket_monotonicity", lambda: check_bracket_monotonicity(bracket_calculator)),
        ("check_salt_cap", lambda: check_salt_cap(deduction_validator)),
        ("check_withholding_adequacy", lambda: check_withholding_adequacy(withholding_checker)),
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
    print("All D_TAX_LAW invariants: PASS")
