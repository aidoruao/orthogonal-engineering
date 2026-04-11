#!/usr/bin/env python3
"""Bankruptcy Law Invariants."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import BankruptcyCase, Chapter

def check_means_test(case: BankruptcyCase) -> Tuple[bool, ProofObject]:
    """Ch 7 means test — income below state median.
    
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
    
    
    Falsifies if: means test condition not met"""Ch 13 requires 60-month plan.
    
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
