"""Falsification tests for D_SECURITIES_LAW"""
from fractions import Fraction
from datetime import datetime
from src.domains.d_securities_law import (
    SecuritiesRegistrationChecker,
    InsiderTradingAnalyzer,
    AntiFraudCompliance,
    Security,
    Transaction,
    SecurityType,
    TransactionType,
)

def test_registration_required():
    checker = SecuritiesRegistrationChecker()
    
    unregistered = Security(
        cusip="123", issuer_name="Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=False
    )
    
    result = checker.check_registration_requirement(
        unregistered, Fraction(10_000_000), 100
    )
    assert result["registration_required"] is True

def test_insider_trading_prohibited():
    analyzer = InsiderTradingAnalyzer()
    
    security = Security(
        cusip="123", issuer_name="Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=True
    )
    
    insider_tx = Transaction(
        transaction_id="T1", security=security,
        transaction_type=TransactionType.SALE,
        buyer="B", seller="CEO",
        quantity=1000, price_per_share=Fraction(50),
        transaction_date=datetime.now(),
        seller_is_insider=True,
        material_nonpublic_info_known=True
    )
    
    result = analyzer.analyze_transaction(insider_tx)
    assert result["insider_trading_suspected"] is True

def test_antifraud_compliance():
    checker = AntiFraudCompliance()
    
    result = checker.check_material_misstatement(
        statement="Guaranteed returns",
        material_facts_omitted=["Risk of loss"]
    )
    assert result["compliant"] is False

if __name__ == "__main__":
    test_registration_required()
    test_insider_trading_prohibited()
    test_antifraud_compliance()
    print("All D_SECURITIES_LAW tests: PASS")
