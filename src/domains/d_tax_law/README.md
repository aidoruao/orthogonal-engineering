# D_TAX_LAW: Tax Law (IRC)

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Internal Revenue Code (IRC) Title 26

## Description

Domain implementing federal income tax calculation with progressive tax brackets,
standard and itemized deductions, and tax credits. The progressive tax structure
reflects the principle that those with greater ability to pay bear proportionally
greater responsibility.

## Invariants

1. **Progressive Rates**: Tax rates increase with income brackets (marginal rates
   rise from 10% to 37%).

2. **Non-Negative Taxable Income**: Taxable income is floored at zero (deductions
   cannot create negative income).

3. **Standard Deduction Structure**: Married filing joint standard deduction equals
   approximately twice the single filer amount.

4. **Tax Liability Monotonicity**: Higher gross income produces equal or higher
   tax liability (holding deductions constant).

5. **Credit Application**: Tax credits reduce liability but cannot produce
   negative tax (non-refundable in this simplified model).

## Key Classes

- `ProgressiveTaxSystem`: Core tax calculation with 2024 brackets
- `TaxReturn`: Represents a tax filing with income, deductions, credits
- `TaxBracket`: Single bracket with lower/upper bounds and rate
- `FilingStatus`: SINGLE, MARRIED_JOINT, MARRIED_SEPARATE, HEAD_OF_HOUSEHOLD
- `TaxComplianceChecker`: Validates filing requirements and deduction limits

## Usage

```python
from fractions import Fraction
from src.domains.d_tax_law import ProgressiveTaxSystem, TaxReturn, FilingStatus

tax_system = ProgressiveTaxSystem()

tax_return = TaxReturn(
    filing_status=FilingStatus.MARRIED_JOINT,
    gross_income=Fraction(150_000),
    deductions=[("mortgage_interest", Fraction(12_000))],
    credits=[("child_tax_credit", Fraction(4_000))],
)

liability = tax_system.calculate_tax_liability(tax_return)
effective_rate = tax_system.get_effective_rate(tax_return)

print(f"Tax owed: ${float(liability):,.2f}")
print(f"Effective rate: {float(effective_rate) * 100:.1f}%")
```

## Biblical Inspiration

Luke 12:48 — "From everyone who has been given much, much will be demanded;
and from the one who has been entrusted with much, much more will be asked."

The progressive tax system embodies this principle of proportionate responsibility—
those blessed with greater resources contribute more to the common good. This
mirrors the biblical pattern of tithes and offerings given in proportion to
blessing received.

## Falsification Tests

- `F_TAX_001`: Verify higher income produces higher tax
- `F_TAX_002`: Verify taxable income floored at zero
- `F_TAX_003`: Verify marginal rate does not exceed statutory maximum
- `F_TAX_004`: Verify standard deduction non-negative
- `F_TAX_005`: Verify credits cannot produce negative tax
