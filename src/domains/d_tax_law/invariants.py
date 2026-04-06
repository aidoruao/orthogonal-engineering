"""D_TAX_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Internal Revenue Code (IRC) Title 26
"""

from src.domains.d_tax_law.implementation import (
    ProgressiveTaxSystem,
    TaxReturn,
    FilingStatus,
    TaxBracket,
    calculate_income_tax,
)
from fractions import Fraction


def check_progressive_tax_rates_increasing() -> bool:
    """
    Invariant: Tax rates increase with income brackets (progressivity).
    Falsification: If a higher bracket has lower rate than previous bracket.
    """
    tax_system = ProgressiveTaxSystem()
    
    for filing_status, brackets in tax_system.brackets.items():
        prev_rate = Fraction(0)
        for i, bracket in enumerate(brackets):
            assert bracket.rate >= prev_rate, (
                f"{filing_status.name} bracket {i}: rate {bracket.rate} < previous {prev_rate}"
            )
            prev_rate = bracket.rate
    
    return True


def check_standard_deduction_non_negative() -> bool:
    """
    Invariant: Standard deductions must be positive amounts.
    Falsification: If any standard deduction is zero or negative.
    """
    tax_system = ProgressiveTaxSystem()
    
    for status, deduction in tax_system.standard_deductions.items():
        assert deduction > 0, (
            f"Standard deduction for {status.name} must be positive, got {deduction}"
        )
    
    return True


def check_married_joint_double_single() -> bool:
    """
    Invariant: Married filing joint standard deduction ≈ 2x single deduction.
    Falsification: If MFJ deduction is not approximately double single.
    """
    tax_system = ProgressiveTaxSystem()
    
    single = tax_system.get_standard_deduction(FilingStatus.SINGLE)
    married_joint = tax_system.get_standard_deduction(FilingStatus.MARRIED_JOINT)
    
    expected = single * 2
    assert married_joint == expected, (
        f"MFJ deduction {married_joint} != 2x single {expected}"
    )
    
    return True


def check_taxable_income_non_negative() -> bool:
    """
    Invariant: Taxable income cannot be negative (floored at zero).
    Falsification: If deductions exceed income and produce negative taxable income.
    """
    tax_return = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(10_000),
        deductions=[("charitable", Fraction(50_000))],  # Exceeds income
    )
    
    assert tax_return.taxable_income == Fraction(0), (
        f"Taxable income should be floored at 0, got {tax_return.taxable_income}"
    )
    
    return True


def check_higher_income_higher_tax() -> bool:
    """
    Invariant: Higher income always results in equal or higher tax liability.
    Falsification: If incremental income produces lower total tax.
    """
    tax_system = ProgressiveTaxSystem()
    
    low_income = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(50_000),
    )
    high_income = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(100_000),
    )
    
    low_tax = tax_system.calculate_tax_liability(low_income)
    high_tax = tax_system.calculate_tax_liability(high_income)
    
    assert high_tax > low_tax, (
        f"Tax on $100k ({high_tax}) should exceed tax on $50k ({low_tax})"
    )
    
    return True


def check_marginal_rate_not_exceed_37_percent() -> bool:
    """
    Invariant: Marginal tax rate cannot exceed 37% (current statutory max).
    Falsification: If marginal rate calculation exceeds 37%.
    """
    tax_system = ProgressiveTaxSystem()
    
    max_rate = Fraction(37, 100)
    
    for status in FilingStatus:
        rate = tax_system.get_marginal_rate(status, Fraction(1_000_000))
        assert rate <= max_rate, (
            f"Marginal rate {rate} for {status.name} exceeds maximum {max_rate}"
        )
    
    return True


def check_tax_credits_reduce_liability() -> bool:
    """
    Invariant: Tax credits reduce tax liability (not below zero).
    Falsification: If credit application produces negative tax.
    """
    tax_return = TaxReturn(
        filing_status=FilingStatus.SINGLE,
        gross_income=Fraction(50_000),
        credits=[("child_tax_credit", Fraction(10_000))],  # Large credit
    )
    
    tax_system = ProgressiveTaxSystem()
    tax = tax_system.calculate_tax_liability(tax_return)
    
    assert tax >= 0, (
        f"Tax liability should not be negative after credits, got {tax}"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_TAX_LAW invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_progressive_tax_rates_increasing,
        check_standard_deduction_non_negative,
        check_married_joint_double_single,
        check_taxable_income_non_negative,
        check_higher_income_higher_tax,
        check_marginal_rate_not_exceed_37_percent,
        check_tax_credits_reduce_liability,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_TAX_LAW invariants: PASS")
