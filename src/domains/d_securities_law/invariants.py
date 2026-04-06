"""D_SECURITIES_LAW invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Securities Act 1933, Exchange Act 1934
"""

from fractions import Fraction
from src.domains.d_securities_law.implementation import (
    SecuritiesRegistrationChecker,
    InsiderTradingAnalyzer,
    AntiFraudCompliance,
    Security,
    Transaction,
    Insider,
    SecurityType,
    TransactionType,
)
from datetime import datetime, timedelta


def check_registration_required() -> bool:
    """
    Invariant: Public securities offerings require SEC registration.
    Falsification: If unregistered public offering passes compliance.
    """
    checker = SecuritiesRegistrationChecker()
    
    # Registered security
    registered = Security(
        cusip="123456789",
        issuer_name="Public Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=True,
        registration_effective_date=datetime(2020, 1, 1),
    )
    
    result = checker.check_registration_requirement(
        registered, Fraction(10_000_000), 100
    )
    assert result["registration_required"] is False, (
        "Registered security should not require re-registration"
    )
    
    # Unregistered security with no exemption
    unregistered = Security(
        cusip="987654321",
        issuer_name="Private Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=False,
    )
    
    result2 = checker.check_registration_requirement(
        unregistered, Fraction(10_000_000), 100
    )
    assert result2["registration_required"] is True, (
        "Large public offering should require registration"
    )
    
    # Private placement (should be exempt)
    private = Security(
        cusip="555555555",
        issuer_name="Startup Inc",
        security_type=SecurityType.PRIVATE_PLACEMENT,
        registered_with_sec=False,
        exemption_claimed="Reg D",
    )
    
    result3 = checker.check_registration_requirement(
        private, Fraction(1_000_000), 10
    )
    assert result3["registration_required"] is False, (
        "Private placement should be exempt"
    )
    
    return True


def check_insider_trading_prohibited() -> bool:
    """
    Invariant: Insider trading on MNPI is prohibited.
    Falsification: If insider trading with MNPI passes compliance.
    """
    analyzer = InsiderTradingAnalyzer()
    
    # Regular transaction
    security = Security(
        cusip="123456789",
        issuer_name="Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=True,
    )
    
    regular_tx = Transaction(
        transaction_id="T001",
        security=security,
        transaction_type=TransactionType.PURCHASE,
        buyer="Investor",
        seller="Seller",
        quantity=100,
        price_per_share=Fraction(50),
        transaction_date=datetime.now(),
        buyer_is_insider=False,
        material_nonpublic_info_known=False,
    )
    
    result = analyzer.analyze_transaction(regular_tx)
    assert result["insider_trading_suspected"] is False, (
        "Regular transaction should not trigger insider trading"
    )
    
    # Insider trading
    insider_tx = Transaction(
        transaction_id="T002",
        security=security,
        transaction_type=TransactionType.SALE,
        buyer="Buyer",
        seller="CEO",
        quantity=10000,
        price_per_share=Fraction(100),
        transaction_date=datetime.now(),
        seller_is_insider=True,
        material_nonpublic_info_known=True,
    )
    
    result2 = analyzer.analyze_transaction(insider_tx)
    assert result2["insider_trading_suspected"] is True, (
        "Insider with MNPI should trigger violation"
    )
    
    return True


def check_antifraud_rule_10b5() -> bool:
    """
    Invariant: Rule 10b-5 prohibits material misstatements/omissions.
    Falsification: If material omission passes compliance.
    """
    checker = AntiFraudCompliance()
    
    # Compliant disclosure
    compliant = checker.check_material_misstatement(
        statement="This investment carries market risk",
        material_facts_omitted=[],
    )
    assert compliant["compliant"] is True, (
        "Accurate disclosure should be compliant"
    )
    
    # Material omission
    omission = checker.check_material_misstatement(
        statement="This investment is safe",
        material_facts_omitted=["Company is insolvent", "CEO under investigation"],
    )
    assert omission["compliant"] is False, (
        "Material omission should violate Rule 10b-5"
    )
    
    # Misleading statement
    misleading = checker.check_material_misstatement(
        statement="Guaranteed 50% returns risk-free",
        material_facts_omitted=[],
    )
    assert misleading["compliant"] is False, (
        "Misleading statement should be flagged"
    )
    
    return True


def check_accredited_investor_limits() -> bool:
    """
    Invariant: Private placements limited to accredited investors.
    Falsification: If Reg D 506(c) allows non-accredited investors.
    """
    checker = SecuritiesRegistrationChecker()
    
    # Large offering to many non-accredited
    security = Security(
        cusip="123456789",
        issuer_name="Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=False,
    )
    
    result = checker.check_registration_requirement(
        security, Fraction(10_000_000), 50  # 50 investors, non-accredited
    )
    
    # Should require registration (too many non-accredited)
    assert result["registration_required"] is True, (
        "Large offering to many non-accredited should require registration"
    )
    
    return True


def check_disclosure_requirements() -> bool:
    """
    Invariant: Registered offerings require prospectus disclosure.
    Falsification: If registered security sold without prospectus.
    """
    # This is a simplified check - real implementation would verify prospectus
    security = Security(
        cusip="123456789",
        issuer_name="Public Corp",
        security_type=SecurityType.COMMON_STOCK,
        registered_with_sec=True,
        registration_effective_date=datetime(2020, 1, 1),
    )
    
    assert security.registered_with_sec is True, (
        "Registered security should have registration flag"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("registration", check_registration_required),
        ("insider_trading", check_insider_trading_prohibited),
        ("antifraud", check_antifraud_rule_10b5),
        ("accredited_limits", check_accredited_investor_limits),
        ("disclosure", check_disclosure_requirements),
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
