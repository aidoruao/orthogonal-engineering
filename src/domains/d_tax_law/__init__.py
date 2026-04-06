"""D_TAX_LAW: Tax Law (IRC, progressive brackets, deductions)

Layer 2 (Statutory) domain implementing federal income tax calculation
with progressive tax brackets and deductions.

Biblical: Luke 12:48 — "From everyone who has been given much,
much will be demanded; and from the one who has been entrusted
with much, much more will be asked."
"""

from src.domains.d_tax_law.implementation import (
    ProgressiveTaxSystem,
    TaxReturn,
    TaxBracket,
    FilingStatus,
    DeductionType,
    TaxComplianceChecker,
    calculate_income_tax,
)
from src.domains.d_tax_law.invariants import (
    check_progressive_tax_rates_increasing,
    check_standard_deduction_non_negative,
    check_higher_income_higher_tax,
)

__all__ = [
    "ProgressiveTaxSystem",
    "TaxReturn",
    "TaxBracket",
    "FilingStatus",
    "DeductionType",
    "TaxComplianceChecker",
    "calculate_income_tax",
    "check_progressive_tax_rates_increasing",
    "check_standard_deduction_non_negative",
    "check_higher_income_higher_tax",
]
