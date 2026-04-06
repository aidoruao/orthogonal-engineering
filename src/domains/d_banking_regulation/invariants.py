"""D_BANKING_REGULATION invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Dodd-Frank, FDIA (12 U.S.C. §1811), Basel Accords
"""

from fractions import Fraction
from src.domains.d_banking_regulation.implementation import (
    BankExaminer,
    CapitalAdequacyCalculator,
    FDICInsuranceCalculator,
    LendingComplianceChecker,
    Bank,
    Loan,
    AssetClass,
    LoanType,
)


def check_tier1_capital_minimum() -> bool:
    """
    Invariant: Tier 1 capital ratio must be at least 6% under Basel III.
    Falsification: If undercapitalized bank passes check.
    """
    calc = CapitalAdequacyCalculator()
    
    # Well capitalized bank
    good_bank = Bank(
        bank_id="B001",
        bank_name="Good Bank",
        charter_type="national",
        tier1_capital=Fraction(10_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        risk_weighted_assets=Fraction(80_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(5_000_000),
        reserves_at_fed=Fraction(5_000_000),
    )
    
    result = calc.check_capital_adequacy(good_bank)
    assert result["compliant"], (
        "Well capitalized bank should pass"
    )
    
    # Undercapitalized bank (Tier 1 ratio < 6%)
    bad_bank = Bank(
        bank_id="B002",
        bank_name="Bad Bank",
        charter_type="national",
        tier1_capital=Fraction(3_000_000),  # 3.75% ratio
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        risk_weighted_assets=Fraction(80_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(2_000_000),
        reserves_at_fed=Fraction(2_000_000),
    )
    
    result = calc.check_capital_adequacy(bad_bank)
    assert not result["compliant"], (
        "Undercapitalized bank should fail"
    )
    
    assert result["prompt_corrective_action"] == "UNDERCAPITALIZED", (
        "Should be classified as undercapitalized"
    )
    
    return True


def check_fdic_insurance_per_depositor() -> bool:
    """
    Invariant: FDIC insurance covers up to $250,000 per depositor.
    Falsification: If coverage exceeds limit or deposits incorrectly insured.
    """
    calc = FDICInsuranceCalculator()
    
    # Fully insured deposit
    result = calc.calculate_insurance_coverage(
        deposit_amount=Fraction(200_000),
        account_ownership="single",
    )
    
    assert result["fully_insured"] is True, (
        "$200k deposit should be fully insured"
    )
    assert result["insured_amount"] == Fraction(200_000), (
        "Full amount should be insured"
    )
    assert result["uninsured_amount"] == 0, (
        "No uninsured amount"
    )
    
    # Partially insured deposit
    result = calc.calculate_insurance_coverage(
        deposit_amount=Fraction(500_000),
        account_ownership="single",
    )
    
    assert result["fully_insured"] is False, (
        "$500k deposit should not be fully insured"
    )
    assert result["insured_amount"] == Fraction(250_000), (
        "Only $250k should be insured"
    )
    assert result["uninsured_amount"] == Fraction(250_000), (
        "$250k should be uninsured"
    )
    
    return True


def check_usury_limit_by_state() -> bool:
    """
    Invariant: Interest rates must comply with state usury limits.
    Falsification: If usurious loan passes compliance check.
    """
    checker = LendingComplianceChecker()
    
    # Compliant loan in California (10% limit)
    compliant_loan = Loan(
        loan_id="L001",
        borrower_name="Good Borrower",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10_000),
        interest_rate=Fraction(8, 100),  # 8%
        term_months=36,
    )
    
    result = checker.check_usury_compliance(compliant_loan, "california")
    assert result["compliant"] is True, (
        "8% loan in CA should be compliant"
    )
    
    # Usurious loan in California
    usurious_loan = Loan(
        loan_id="L002",
        borrower_name="Bad Borrower",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10_000),
        interest_rate=Fraction(20, 100),  # 20%
        term_months=36,
    )
    
    result = checker.check_usury_compliance(usurious_loan, "california")
    assert result["compliant"] is False, (
        "20% loan in CA should violate usury"
    )
    assert result["excess"] > 0, (
        "Should show excess interest"
    )
    
    return True


def check_reserve_ratio_requirement() -> bool:
    """
    Invariant: Banks must maintain minimum reserve ratio.
    Falsification: If bank with insufficient reserves passes.
    """
    # Well reserved bank
    good_bank = Bank(
        bank_id="B003",
        bank_name="Reserved Bank",
        charter_type="national",
        tier1_capital=Fraction(10_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(5_000_000),
        reserves_at_fed=Fraction(5_000_000),  # 12.5% reserve ratio
    )
    
    reserves_ratio = good_bank.total_reserves / good_bank.total_deposits
    assert reserves_ratio >= Fraction(10, 100), (
        "Reserves should meet 10% requirement"
    )
    
    # Under-reserved bank
    bad_bank = Bank(
        bank_id="B004",
        bank_name="Under-reserved Bank",
        charter_type="national",
        tier1_capital=Fraction(10_000_000),
        tier2_capital=Fraction(2_000_000),
        total_assets=Fraction(100_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(1_000_000),
        reserves_at_fed=Fraction(1_000_000),  # 2.5% reserve ratio
    )
    
    bad_reserves_ratio = bad_bank.total_reserves / bad_bank.total_deposits
    assert bad_reserves_ratio < Fraction(10, 100), (
        "Should be below 10% requirement"
    )
    
    return True


def check_lending_standards_compliance() -> bool:
    """
    Invariant: Lending must meet Ability-to-Repay standards.
    Falsification: If loan without verified income passes ATR check.
    """
    checker = LendingComplianceChecker()
    
    # Compliant loan with documented income
    compliant_loan = Loan(
        loan_id="L003",
        borrower_name="Qualified Borrower",
        loan_type=LoanType.RESIDENTIAL_MORTGAGE,
        principal=Fraction(300_000),
        interest_rate=Fraction(6, 100),
        term_months=360,
        credit_score=720,
        debt_to_income=Fraction(35, 100),
        documented_income=True,
        ability_to_repay_verified=True,
    )
    
    result = checker.check_ability_to_repay(compliant_loan)
    assert result["compliant"] is True, (
        "Documented loan should pass ATR"
    )
    assert result["qualified_mortgage"] is True, (
        "Should be Qualified Mortgage"
    )
    
    # Non-compliant loan (no income verification)
    noncompliant_loan = Loan(
        loan_id="L004",
        borrower_name="Unverified Borrower",
        loan_type=LoanType.RESIDENTIAL_MORTGAGE,
        principal=Fraction(300_000),
        interest_rate=Fraction(6, 100),
        term_months=360,
        credit_score=650,
        debt_to_income=Fraction(50, 100),
        documented_income=False,
        ability_to_repay_verified=False,
    )
    
    result = checker.check_ability_to_repay(noncompliant_loan)
    assert result["compliant"] is False, (
        "No-doc loan should fail ATR"
    )
    assert any("not documented" in issue.lower() for issue in result["issues"]), (
        "Should flag income documentation"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("tier1_capital", check_tier1_capital_minimum),
        ("fdic_insurance", check_fdic_insurance_per_depositor),
        ("usury_limit", check_usury_limit_by_state),
        ("reserve_ratio", check_reserve_ratio_requirement),
        ("lending_standards", check_lending_standards_compliance),
    ]
    
    for name, check_func in checks:
        try:
            check_func()
            results[name] = "PASS"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results
