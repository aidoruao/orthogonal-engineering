"""D_CONSUMER_PROTECTION invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: FTC Act §5, TILA, Magnuson-Moss Warranty Act
"""

from fractions import Fraction
from src.domains.d_consumer_protection.implementation import (
    DeceptivePracticeAnalyzer,
    DisclosureRequirementsChecker,
    WarrantyAnalyzer,
    ConsumerTransaction,
    Advertisement,
    Product,
    DeceptivePracticeType,
    WarrantyType,
)
from datetime import datetime, timedelta


def check_deceptive_practices_prohibited() -> bool:
    """
    Invariant: Deceptive practices under FTC Act §5 are detected.
    Falsification: If bait-and-switch ad passes as compliant.
    """
    analyzer = DeceptivePracticeAnalyzer()
    
    # Create product
    product = Product(
        product_id="P001",
        name="Widget",
        manufacturer="Acme Corp",
        category="electronics",
        msrp=Fraction(199),
    )
    
    # Deceptive ad (bait and switch)
    deceptive_ad = Advertisement(
        ad_id="A001",
        product=product,
        media_type="digital",
        claims=["Amazing deal! Starting at $99!"],
        advertised_price=Fraction(99),
        fine_print="Limited quantities. Most pay $199.",
    )
    
    result = analyzer.analyze_advertisement(deceptive_ad)
    
    # Should flag potential deceptive practice
    assert len(result["issues"]) > 0, (
        "Should flag bait-and-switch indicators"
    )
    
    # Compliant ad
    compliant_ad = Advertisement(
        ad_id="A002",
        product=product,
        media_type="digital",
        claims=["Quality widget, $199"],
        advertised_price=Fraction(199),
    )
    
    result2 = analyzer.analyze_advertisement(compliant_ad)
    
    # Should pass
    assert result2["compliant"] is True, (
        "Straightforward ad should be compliant"
    )
    
    return True


def check_disclosure_requirements_met() -> bool:
    """
    Invariant: Required disclosures must be provided.
    Falsification: If transaction missing TILA disclosures passes.
    """
    checker = DisclosureRequirementsChecker()
    
    # Complete disclosures
    complete = {
        "annual_percentage_rate": "5.99%",
        "finance_charge": "$1,200",
        "amount_financed": "$10,000",
        "total_payments": "$11,200",
        "payment_schedule": "36 months @ $311",
    }
    
    result = checker.check_tila_disclosures(complete)
    
    assert result["compliant"] is True, (
        "Complete disclosures should pass"
    )
    
    # Incomplete disclosures
    incomplete = {
        "annual_percentage_rate": "5.99%",
        # Missing finance charge, amount financed, etc.
    }
    
    result2 = checker.check_tila_disclosures(incomplete)
    
    assert result2["compliant"] is False, (
        "Incomplete disclosures should fail"
    )
    assert len(result2["missing_disclosures"]) > 0, (
        "Should identify missing disclosures"
    )
    
    return True


def check_warranty_honored() -> bool:
    """
    Invariant: Valid warranty claims must be honored.
    Falsification: If claim within warranty period is denied.
    """
    analyzer = WarrantyAnalyzer()
    
    product = Product(
        product_id="P002",
        name="Appliance",
        manufacturer="HomeCo",
        category="appliances",
        msrp=Fraction(500),
        warranties=[{"type": "LIMITED", "period_days": 365}],
    )
    
    purchase_date = datetime(2024, 1, 1)
    claim_date = datetime(2024, 6, 1)  # 5 months later
    
    result = analyzer.analyze_warranty_coverage(
        product=product,
        defect_description="Motor failure",
        purchase_date=purchase_date,
        claim_date=claim_date,
    )
    
    assert result["covered"] is True, (
        "Claim within warranty period should be covered"
    )
    
    # Claim outside warranty period
    late_claim_date = datetime(2025, 6, 1)  # 17 months later
    
    result2 = analyzer.analyze_warranty_coverage(
        product=product,
        defect_description="Motor failure",
        purchase_date=purchase_date,
        claim_date=late_claim_date,
    )
    
    assert result2["covered"] is False, (
        "Claim outside warranty period should be denied"
    )
    assert "expired" in result2["reason"].lower(), (
        "Should indicate warranty expired"
    )
    
    return True


def check_unfair_practices_detected() -> bool:
    """
    Invariant: Unfair practices causing substantial injury detected.
    Falsification: If hidden fee transaction passes as compliant.
    """
    analyzer = DeceptivePracticeAnalyzer()
    
    product = Product(
        product_id="P003",
        name="Service",
        manufacturer="ServiceCo",
        category="services",
        msrp=Fraction(100),
    )
    
    # Transaction with hidden fees
    transaction = ConsumerTransaction(
        transaction_id="T001",
        consumer_name="Consumer",
        product=product,
        agreed_price=Fraction(100),
        final_price=Fraction(150),  # $50 in hidden fees
        disclosures_provided=["price"],  # Missing fee disclosure
    )
    
    result = analyzer.analyze_transaction(transaction)
    
    assert result["compliant"] is False, (
        "Should flag hidden fees"
    )
    
    has_hidden_fee_issue = any(
        issue["type"] == "HIDDEN_FEES" for issue in result["issues"]
    )
    assert has_hidden_fee_issue, (
        "Should specifically flag hidden fees"
    )
    
    return True


def check_cooling_off_period() -> bool:
    """
    Invariant: Cooling-off period allows cancellation.
    Falsification: If consumer cannot cancel within cooling-off period.
    """
    product = Product(
        product_id="P004",
        name="Door-to-door sale",
        manufacturer="SalesCo",
        category="services",
        msrp=Fraction(1000),
    )
    
    transaction_date = datetime(2024, 1, 1)
    
    transaction = ConsumerTransaction(
        transaction_id="T002",
        consumer_name="Consumer",
        product=product,
        agreed_price=Fraction(1000),
        final_price=Fraction(1000),
        transaction_date=transaction_date,
    )
    
    # Should be able to cancel day after
    next_day = transaction_date + timedelta(days=1)
    assert transaction.can_cancel(as_of=next_day) is True, (
        "Should be able to cancel day after purchase"
    )
    
    # Should be able to cancel 2 days after
    two_days = transaction_date + timedelta(days=2)
    assert transaction.can_cancel(as_of=two_days) is True, (
        "Should be able to cancel 2 days after"
    )
    
    # Should not be able to cancel after 5 days
    five_days = transaction_date + timedelta(days=5)
    assert transaction.can_cancel(as_of=five_days) is False, (
        "Should not be able to cancel after cooling-off period"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all invariant checks and return results."""
    results = {}
    
    checks = [
        ("deceptive_practices", check_deceptive_practices_prohibited),
        ("disclosure_requirements", check_disclosure_requirements_met),
        ("warranty_honored", check_warranty_honored),
        ("unfair_practices", check_unfair_practices_detected),
        ("cooling_off_period", check_cooling_off_period),
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
