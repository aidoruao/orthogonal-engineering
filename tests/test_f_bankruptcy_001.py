"""Falsification tests for D_BANKRUPTCY"""
from fractions import Fraction
from src.domains.d_bankruptcy import (
    BankruptcyAnalyzer, Debtor, Debt, DebtType
)

def test_means_test_eligibility():
    analyzer = BankruptcyAnalyzer()
    
    low_income = Debtor(
        name="Low Income",
        income_monthly=Fraction(3000)
    )
    
    result = analyzer.check_chapter_7_eligibility(low_income)
    assert result["above_means_test"] is False

def test_debt_priority():
    analyzer = BankruptcyAnalyzer()
    
    debtor = Debtor(
        name="Debtor",
        debts=[
            Debt("Secured", Fraction(100000), DebtType.SECURED, "House"),
            Debt("Tax", Fraction(50000), DebtType.UNSECURED_PRIORITY),
            Debt("Credit", Fraction(30000), DebtType.UNSECURED_GENERAL),
        ]
    )
    
    result = analyzer.calculate_distribution(debtor, Fraction(150000))
    assert result["secured_paid"] >= Fraction(100000)
    assert result["priority_paid"] > result["general_paid"]

if __name__ == "__main__":
    test_means_test_eligibility()
    test_debt_priority()
    print("All D_BANKRUPTCY tests: PASS")
