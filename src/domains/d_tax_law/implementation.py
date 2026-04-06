"""D_TAX_LAW implementation — Tax Law (IRC)

Implements federal income tax calculation with progressive brackets,
deductions (standard and itemized), and filing status adjustments.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Internal Revenue Code (IRC) Title 26
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum, auto
from fractions import Fraction


class FilingStatus(Enum):
    """IRS filing statuses per IRC §1."""
    SINGLE = auto()
    MARRIED_JOINT = auto()
    MARRIED_SEPARATE = auto()
    HEAD_OF_HOUSEHOLD = auto()


class DeductionType(Enum):
    """Types of deductions available."""
    STANDARD = auto()
    ITEMIZED = auto()


@dataclass(frozen=True)
class TaxBracket:
    """Single tax bracket with rate and income bounds.
    
    Uses Fraction for exact arithmetic to avoid floating-point errors
    in tax calculations.
    """
    lower_bound: Fraction
    upper_bound: Optional[Fraction]  # None means no upper limit
    rate: Fraction  # As fraction (e.g., 22/100 for 22%)
    
    def tax_for_range(self, taxable_income: Fraction) -> Fraction:
        """Calculate tax for income falling within this bracket."""
        if taxable_income <= self.lower_bound:
            return Fraction(0)
        
        # Income within this bracket
        income_in_bracket = min(
            taxable_income - self.lower_bound,
            (self.upper_bound - self.lower_bound) if self.upper_bound else taxable_income
        )
        
        return income_in_bracket * self.rate


@dataclass
class TaxReturn:
    """Represents a tax return with all relevant data."""
    filing_status: FilingStatus
    gross_income: Fraction
    deductions: List[Tuple[str, Fraction]] = field(default_factory=list)
    credits: List[Tuple[str, Fraction]] = field(default_factory=list)
    
    @property
    def total_deductions(self) -> Fraction:
        """Sum of all deductions."""
        return sum((amount for _, amount in self.deductions), Fraction(0))
    
    @property
    def total_credits(self) -> Fraction:
        """Sum of all tax credits."""
        return sum((amount for _, amount in self.credits), Fraction(0))
    
    @property
    def taxable_income(self) -> Fraction:
        """Calculate taxable income (cannot be negative)."""
        income = self.gross_income - self.total_deductions
        return max(income, Fraction(0))


class ProgressiveTaxSystem:
    """Implements progressive tax calculation per IRC §1.
    
    Progressive taxation applies increasing marginal rates to
    successive brackets of income—reflecting the biblical principle
    that those with more capacity bear greater responsibility
    (Luke 12:48: "To whom much is given, much will be required").
    """
    
    # 2024 Tax brackets (simplified) per IRC §1
    BRACKETS_2024: Dict[FilingStatus, List[TaxBracket]] = {
        FilingStatus.SINGLE: [
            TaxBracket(Fraction(0), Fraction(11_600), Fraction(10, 100)),
            TaxBracket(Fraction(11_600), Fraction(47_150), Fraction(12, 100)),
            TaxBracket(Fraction(47_150), Fraction(100_525), Fraction(22, 100)),
            TaxBracket(Fraction(100_525), Fraction(191_950), Fraction(24, 100)),
            TaxBracket(Fraction(191_950), Fraction(243_725), Fraction(32, 100)),
            TaxBracket(Fraction(243_725), Fraction(609_350), Fraction(35, 100)),
            TaxBracket(Fraction(609_350), None, Fraction(37, 100)),
        ],
        FilingStatus.MARRIED_JOINT: [
            TaxBracket(Fraction(0), Fraction(23_200), Fraction(10, 100)),
            TaxBracket(Fraction(23_200), Fraction(94_300), Fraction(12, 100)),
            TaxBracket(Fraction(94_300), Fraction(201_050), Fraction(22, 100)),
            TaxBracket(Fraction(201_050), Fraction(383_900), Fraction(24, 100)),
            TaxBracket(Fraction(383_900), Fraction(487_450), Fraction(32, 100)),
            TaxBracket(Fraction(487_450), Fraction(731_200), Fraction(35, 100)),
            TaxBracket(Fraction(731_200), None, Fraction(37, 100)),
        ],
        FilingStatus.MARRIED_SEPARATE: [
            TaxBracket(Fraction(0), Fraction(11_600), Fraction(10, 100)),
            TaxBracket(Fraction(11_600), Fraction(47_150), Fraction(12, 100)),
            TaxBracket(Fraction(47_150), Fraction(100_525), Fraction(22, 100)),
            TaxBracket(Fraction(100_525), Fraction(191_950), Fraction(24, 100)),
            TaxBracket(Fraction(191_950), Fraction(243_725), Fraction(32, 100)),
            TaxBracket(Fraction(243_725), Fraction(365_600), Fraction(35, 100)),
            TaxBracket(Fraction(365_600), None, Fraction(37, 100)),
        ],
        FilingStatus.HEAD_OF_HOUSEHOLD: [
            TaxBracket(Fraction(0), Fraction(16_550), Fraction(10, 100)),
            TaxBracket(Fraction(16_550), Fraction(63_100), Fraction(12, 100)),
            TaxBracket(Fraction(63_100), Fraction(100_500), Fraction(22, 100)),
            TaxBracket(Fraction(100_500), Fraction(191_950), Fraction(24, 100)),
            TaxBracket(Fraction(191_950), Fraction(243_700), Fraction(32, 100)),
            TaxBracket(Fraction(243_700), Fraction(609_350), Fraction(35, 100)),
            TaxBracket(Fraction(609_350), None, Fraction(37, 100)),
        ],
    }
    
    # 2024 Standard deductions per IRC §63
    STANDARD_DEDUCTIONS_2024: Dict[FilingStatus, Fraction] = {
        FilingStatus.SINGLE: Fraction(14_600),
        FilingStatus.MARRIED_JOINT: Fraction(29_200),
        FilingStatus.MARRIED_SEPARATE: Fraction(14_600),
        FilingStatus.HEAD_OF_HOUSEHOLD: Fraction(21_900),
    }
    
    def __init__(self):
        self.brackets = self.BRACKETS_2024
        self.standard_deductions = self.STANDARD_DEDUCTIONS_2024
    
    def calculate_tax_liability(self, tax_return: TaxReturn) -> Fraction:
        """Calculate total tax liability using progressive brackets.
        
        Args:
            tax_return: The tax return to calculate liability for
            
        Returns:
            Total tax liability as Fraction (exact)
        """
        taxable_income = tax_return.taxable_income
        brackets = self.brackets.get(tax_return.filing_status, [])
        
        total_tax = Fraction(0)
        for bracket in brackets:
            tax_from_bracket = bracket.tax_for_range(taxable_income)
            total_tax += tax_from_bracket
            if bracket.upper_bound and taxable_income <= bracket.upper_bound:
                break
        
        # Apply credits (non-refundable in this simplified model)
        total_tax = max(total_tax - tax_return.total_credits, Fraction(0))
        
        return total_tax
    
    def get_marginal_rate(self, filing_status: FilingStatus, income: Fraction) -> Fraction:
        """Get the marginal tax rate for a given income level.
        
        Args:
            filing_status: The filing status
            income: The taxable income
            
        Returns:
            The marginal tax rate as Fraction
        """
        brackets = self.brackets.get(filing_status, [])
        for bracket in brackets:
            if bracket.upper_bound is None or income <= bracket.upper_bound:
                return bracket.rate
        return Fraction(0)
    
    def get_effective_rate(self, tax_return: TaxReturn) -> Fraction:
        """Calculate effective tax rate (total tax / gross income).
        
        Returns:
            Effective rate as Fraction, or 0 if no income
        """
        if tax_return.gross_income <= 0:
            return Fraction(0)
        
        tax_liability = self.calculate_tax_liability(tax_return)
        return tax_liability / tax_return.gross_income
    
    def get_standard_deduction(self, filing_status: FilingStatus) -> Fraction:
        """Get the standard deduction amount for filing status."""
        return self.standard_deductions.get(filing_status, Fraction(0))
    
    def should_itemize(self, tax_return: TaxReturn) -> bool:
        """Determine if taxpayer should itemize deductions.
        
        Args:
            tax_return: The tax return
            
        Returns:
            True if itemizing is beneficial
        """
        standard = self.get_standard_deduction(tax_return.filing_status)
        itemized = tax_return.total_deductions
        return itemized > standard


class TaxComplianceChecker:
    """Checks tax compliance with IRC requirements."""
    
    def __init__(self):
        self.tax_system = ProgressiveTaxSystem()
    
    def check_filing_requirement(
        self,
        gross_income: Fraction,
        filing_status: FilingStatus,
        age: int = 35,
    ) -> bool:
        """Check if filing is required based on income thresholds.
        
        Args:
            gross_income: Total gross income
            filing_status: Filing status
            age: Age of taxpayer (affects thresholds for some statuses)
            
        Returns:
            True if filing is required
        """
        # Simplified 2024 filing thresholds
        thresholds = {
            FilingStatus.SINGLE: Fraction(13_850) if age < 65 else Fraction(15_700),
            FilingStatus.MARRIED_JOINT: Fraction(27_700) if age < 65 else Fraction(29_200),
            FilingStatus.MARRIED_SEPARATE: Fraction(5),
            FilingStatus.HEAD_OF_HOUSEHOLD: Fraction(20_800) if age < 65 else Fraction(22_650),
        }
        
        threshold = thresholds.get(filing_status, Fraction(0))
        return gross_income >= threshold
    
    def validate_deduction(self, deduction_name: str, amount: Fraction) -> bool:
        """Validate a deduction is reasonable (basic checks).
        
        Args:
            deduction_name: Name/description of deduction
            amount: Deduction amount
            
        Returns:
            True if deduction appears valid
        """
        # Deductions cannot be negative
        if amount < 0:
            return False
        
        # Some deductions have caps (simplified)
        capped_deductions = {
            "state_and_local_tax": Fraction(10_000),
            "mortgage_interest": Fraction(750_000),  # Loan limit
        }
        
        for key, cap in capped_deductions.items():
            if key in deduction_name.lower():
                return amount <= cap
        
        return True


def calculate_income_tax(
    gross_income: Fraction,
    filing_status: FilingStatus,
    deductions: Optional[List[Tuple[str, Fraction]]] = None,
    credits: Optional[List[Tuple[str, Fraction]]] = None,
) -> Dict[str, Fraction]:
    """Convenience function to calculate income tax.
    
    Usage:
        result = calculate_income_tax(
            gross_income=Fraction(75000),
            filing_status=FilingStatus.SINGLE,
            deductions=[("charitable", Fraction(5000))],
        )
        print(f"Tax owed: ${float(result['tax_liability']):.2f}")
    """
    tax_return = TaxReturn(
        filing_status=filing_status,
        gross_income=gross_income,
        deductions=deductions or [],
        credits=credits or [],
    )
    
    tax_system = ProgressiveTaxSystem()
    
    tax_liability = tax_system.calculate_tax_liability(tax_return)
    effective_rate = tax_system.get_effective_rate(tax_return)
    marginal_rate = tax_system.get_marginal_rate(filing_status, tax_return.taxable_income)
    
    return {
        "tax_liability": tax_liability,
        "taxable_income": tax_return.taxable_income,
        "effective_rate": effective_rate,
        "marginal_rate": marginal_rate,
        "total_deductions": tax_return.total_deductions,
        "total_credits": tax_return.total_credits,
    }
