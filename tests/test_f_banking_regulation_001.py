"""Falsification tests for D_BANKING_REGULATION"""
from fractions import Fraction
from src.domains.d_banking_regulation import (
    BankExaminer,
    CapitalAdequacyCalculator,
    FDICInsuranceCalculator,
    LendingComplianceChecker,
    Bank,
    Loan,
    LoanType,
    check_tier1_capital_minimum,
    check_fdic_insurance_per_depositor,
    check_usury_limit_by_state,
)


def test_tier1_capital_minimum():
    """Tier 1 capital ratio must be at least 6%."""
    result = check_tier1_capital_minimum()
    assert result is True


def test_fdic_insurance_limits():
    """FDIC insurance covers up to $250k per depositor."""
    result = check_fdic_insurance_per_depositor()
    assert result is True


def test_usury_limits():
    """Interest rates must comply with state usury limits."""
    result = check_usury_limit_by_state()
    assert result is True


def test_well_capitalized_bank_passes():
    """Well capitalized bank passes capital adequacy check."""
    calc = CapitalAdequacyCalculator()
    
    bank = Bank(
        bank_id="B001",
        bank_name="Well Capitalized Bank",
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
    
    result = calc.check_capital_adequacy(bank)
    assert result["compliant"] is True


def test_undercapitalized_bank_fails():
    """Undercapitalized bank fails capital adequacy check."""
    calc = CapitalAdequacyCalculator()
    
    bank = Bank(
        bank_id="B002",
        bank_name="Undercapitalized Bank",
        charter_type="national",
        tier1_capital=Fraction(3_000_000),  # Only 3.75% ratio
        tier2_capital=Fraction(1_000_000),
        total_assets=Fraction(100_000_000),
        risk_weighted_assets=Fraction(80_000_000),
        total_deposits=Fraction(80_000_000),
        insured_deposits=Fraction(75_000_000),
        vault_cash=Fraction(2_000_000),
        reserves_at_fed=Fraction(2_000_000),
    )
    
    result = calc.check_capital_adequacy(bank)
    assert result["compliant"] is False
    assert result["prompt_corrective_action"] == "UNDERCAPITALIZED"


def test_fdic_full_coverage():
    """Deposits up to $250k are fully insured."""
    calc = FDICInsuranceCalculator()
    
    result = calc.calculate_insurance_coverage(Fraction(200_000))
    assert result["fully_insured"] is True
    assert result["uninsured_amount"] == 0


def test_fdic_partial_coverage():
    """Deposits over $250k have uninsured portion."""
    calc = FDICInsuranceCalculator()
    
    result = calc.calculate_insurance_coverage(Fraction(500_000))
    assert result["fully_insured"] is False
    assert result["insured_amount"] == Fraction(250_000)
    assert result["uninsured_amount"] == Fraction(250_000)


def test_usury_compliant_loan():
    """Compliant loan passes usury check."""
    checker = LendingComplianceChecker()
    
    loan = Loan(
        loan_id="L001",
        borrower_name="Borrower",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10_000),
        interest_rate=Fraction(8, 100),  # 8%
        term_months=36,
    )
    
    result = checker.check_usury_compliance(loan, "california")
    assert result["compliant"] is True


def test_usurious_loan_fails():
    """Usurious loan fails usury check."""
    checker = LendingComplianceChecker()
    
    loan = Loan(
        loan_id="L002",
        borrower_name="Borrower",
        loan_type=LoanType.CONSUMER_INSTALLMENT,
        principal=Fraction(10_000),
        interest_rate=Fraction(20, 100),  # 20%
        term_months=36,
    )
    
    result = checker.check_usury_compliance(loan, "california")
    assert result["compliant"] is False
    assert result["excess"] > 0


def test_atr_compliant_loan():
    """Loan with documented income passes ATR."""
    checker = LendingComplianceChecker()
    
    loan = Loan(
        loan_id="L003",
        borrower_name="Borrower",
        loan_type=LoanType.RESIDENTIAL_MORTGAGE,
        principal=Fraction(300_000),
        interest_rate=Fraction(6, 100),
        term_months=360,
        credit_score=720,
        debt_to_income=Fraction(35, 100),
        documented_income=True,
        ability_to_repay_verified=True,
    )
    
    result = checker.check_ability_to_repay(loan)
    assert result["compliant"] is True


def test_atr_noncompliant_loan():
    """No-doc loan fails ATR check."""
    checker = LendingComplianceChecker()
    
    loan = Loan(
        loan_id="L004",
        borrower_name="Borrower",
        loan_type=LoanType.RESIDENTIAL_MORTGAGE,
        principal=Fraction(300_000),
        interest_rate=Fraction(6, 100),
        term_months=360,
        documented_income=False,
        ability_to_repay_verified=False,
    )
    
    result = checker.check_ability_to_repay(loan)
    assert result["compliant"] is False


if __name__ == "__main__":
    test_tier1_capital_minimum()
    test_fdic_insurance_limits()
    test_usury_limits()
    test_well_capitalized_bank_passes()
    test_undercapitalized_bank_fails()
    test_fdic_full_coverage()
    test_fdic_partial_coverage()
    test_usury_compliant_loan()
    test_usurious_loan_fails()
    test_atr_compliant_loan()
    test_atr_noncompliant_loan()
    print("All D_BANKING_REGULATION tests: PASS")
