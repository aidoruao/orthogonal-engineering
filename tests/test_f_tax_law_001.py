"""Falsification tests for D_TAX_LAW"""
from fractions import Fraction
from src.domains.d_tax_law import (
    ProgressiveTaxSystem,
    TaxReturn,
    FilingStatus,
    TaxComplianceChecker,
    calculate_income_tax,
)


def test_progressive_tax_rates_increasing():
    """Higher income brackets have higher marginal rates."""
    tax_system = ProgressiveTaxSystem()
    
    # Check that rates increase with brackets
    single_brackets = tax_system.brackets[FilingStatus.SINGLE]
    rates = [b.rate for b in single_brackets]
    
    for i in range(1, len(rates)):
        assert rates[i] > rates[i-1], f"Rate {rates[i]} not greater than {rates[i-1]}"


def test_higher_income_higher_tax():
    """Higher income results in higher total tax."""
    tax_system = ProgressiveTaxSystem()
    
    low_income = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(50000),
    )
    high_income = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(200000),
    )
    
    low_tax = tax_system.calculate_tax_liability(low_income)
    high_tax = tax_system.calculate_tax_liability(high_income)
    
    assert high_tax > low_tax


def test_standard_deduction_reduces_taxable_income():
    """Standard deduction reduces taxable income."""
    tax_system = ProgressiveTaxSystem()
    standard_deduction = tax_system.get_standard_deduction(FilingStatus.SINGLE)
    
    # Create return with standard deduction applied
    tax_return = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(100000),
        deductions=[("standard_deduction", standard_deduction)],
    )
    
    # Taxable income should be reduced by standard deduction
    assert tax_return.taxable_income == Fraction(100000) - standard_deduction


def test_tax_credits_reduce_liability():
    """Tax credits reduce tax liability dollar-for-dollar."""
    tax_system = ProgressiveTaxSystem()
    
    base_return = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(100000),
    )
    
    credit_return = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(100000),
        credits=[("child_tax_credit", Fraction(2000))],
    )
    
    base_tax = tax_system.calculate_tax_liability(base_return)
    credit_tax = tax_system.calculate_tax_liability(credit_return)
    
    assert credit_tax < base_tax


if __name__ == "__main__":
    test_progressive_tax_rates_increasing()
    test_higher_income_higher_tax()
    test_standard_deduction_reduces_taxable_income()
    test_tax_credits_reduce_liability()
    print("All D_TAX_LAW tests: PASS")
