#!/usr/bin/env python3
"""Tax Law Invariants — IRC compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import BracketCalculator, DeductionValidator, WithholdingChecker


def check_bracket_monotonicity(calc: BracketCalculator) -> Tuple[bool, ProofObject]:
    """Tax brackets must be monotonic (higher income → higher rate).
    
    falsifies_if: condition_evaluated_to_false"""
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
    
    falsifies_if: condition_evaluated_to_false"""
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
    
    falsifies_if: condition_evaluated_to_false"""
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
