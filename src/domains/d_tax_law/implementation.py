#!/usr/bin/env python3
"""Tax Law — IRC, progressive taxation, deductions."""

from fractions import Fraction
from dataclasses import dataclass
from typing import List, Tuple, Dict


@dataclass
class TaxBracket:
    """Single tax bracket."""
    min_income: Fraction
    max_income: Fraction
    rate: Fraction


@dataclass
class BracketCalculator:
    """Calculate tax using progressive brackets."""
    brackets: List[TaxBracket]
    income: Fraction
    
    def calculate_tax(self) -> Fraction:
        """Apply progressive tax calculation."""
        tax = Fraction(0)
        remaining = self.income
        
        for bracket in sorted(self.brackets, key=lambda b: b.min_income):
            if remaining <= 0:
                break
            taxable_in_bracket = min(
                remaining,
                bracket.max_income - bracket.min_income
            )
            tax += taxable_in_bracket * bracket.rate
            remaining -= taxable_in_bracket
        
        return tax
    
    def marginal_rate(self) -> Fraction:
        """Tax rate on next dollar earned."""
        for bracket in sorted(self.brackets, key=lambda b: b.min_income):
            if self.income < bracket.max_income:
                return bracket.rate
        return Fraction(0)
    
    def is_monotonic(self) -> bool:
        """Higher brackets must have equal or higher rates."""
        sorted_brackets = sorted(self.brackets, key=lambda b: b.min_income)
        for i in range(len(sorted_brackets) - 1):
            if sorted_brackets[i].rate > sorted_brackets[i + 1].rate:
                return False
        return True


@dataclass
class DeductionValidator:
    """Validate deductions against caps."""
    salt_deduction: Fraction  # State and local tax
    standard_deduction: Fraction
    itemized_deductions: Fraction
    
    SALT_CAP = Fraction(10000)
    
    def salt_within_cap(self) -> bool:
        return self.salt_deduction <= self.SALT_CAP
    
    def optimal_deduction(self) -> Fraction:
        """Choose larger of standard or itemized."""
        # TODO: Expand optimal_deduction() - stub detected by Yeshua Agent
        return max(self.standard_deduction, self.itemized_deductions)


@dataclass
class WithholdingChecker:
    """Check withholding adequacy."""
    annual_withheld: Fraction
    estimated_tax_liability: Fraction
    
    SAFE_HARBOR_PCT = Fraction(90)  # Must withhold 90% of liability
    
    def is_adequate(self) -> bool:
        """Withholding must cover at least 90% of liability."""
        if self.estimated_tax_liability == 0:
            return True
        withheld_pct = Fraction(self.annual_withheld * 100, self.estimated_tax_liability)
        return withheld_pct >= self.SAFE_HARBOR_PCT
