"""D_BANKING_REGULATION: Banking Regulation (Dodd-Frank, FDIC, reserve requirements)

Layer 2 (Statutory) domain implementing banking regulation including
capital requirements, deposit insurance, and consumer lending protections.

Biblical: Exodus 22:25 — "If you lend money to one of my people among you
who is needy, do not treat it like a business deal; charge no interest."
"""

from src.domains.d_banking_regulation.implementation import (
    BankExaminer,
    CapitalAdequacyCalculator,
    FDICInsuranceCalculator,
    LendingComplianceChecker,
    Bank,
    Loan,
    AssetClass,
    LoanType,
    BankCapitalReport,
    LoanApplicationReport,
    check_capital_ratio_minimum,
    check_fdic_coverage_limits,
    check_usury_caps,
    check_reserve_requirements,
)
from src.domains.d_banking_regulation.invariants import (
    check_tier1_capital_minimum,
    check_fdic_insurance_per_depositor,
    check_usury_limit_by_state,
    check_reserve_ratio_requirement,
    check_lending_standards_compliance,
    check_capital_adequacy,
    check_usury_limit,
    check_trid_disclosure,
    run_all_invariants,
)

__all__ = [
    "BankExaminer",
    "CapitalAdequacyCalculator",
    "FDICInsuranceCalculator",
    "LendingComplianceChecker",
    "Bank",
    "Loan",
    "AssetClass",
    "LoanType",
    "BankCapitalReport",
    "LoanApplicationReport",
    "check_capital_ratio_minimum",
    "check_fdic_coverage_limits",
    "check_usury_caps",
    "check_reserve_requirements",
    "check_tier1_capital_minimum",
    "check_fdic_insurance_per_depositor",
    "check_usury_limit_by_state",
    "check_reserve_ratio_requirement",
    "check_lending_standards_compliance",
    "check_capital_adequacy",
    "check_usury_limit",
    "check_trid_disclosure",
    "run_all_invariants",
]
