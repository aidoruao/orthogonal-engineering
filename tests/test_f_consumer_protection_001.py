"""Falsification tests for D_CONSUMER_PROTECTION"""
from fractions import Fraction
from datetime import datetime, timedelta
from src.domains.d_consumer_protection import (
    DeceptivePracticeAnalyzer,
    DisclosureRequirementsChecker,
    WarrantyAnalyzer,
    ConsumerTransaction,
    Advertisement,
    Product,
    check_deceptive_practices_prohibited,
    check_disclosure_requirements_met,
    check_warranty_honored,
)


def test_deceptive_practices_detected():
    """Deceptive advertising practices are detected."""
    analyzer = DeceptivePracticeAnalyzer()
    
    product = Product(
        product_id="P001",
        name="Widget",
        manufacturer="Acme",
        category="electronics",
        msrp=Fraction(150),
    )
    
    # Transaction with hidden fees
    transaction = ConsumerTransaction(
        transaction_id="T001",
        consumer_name="Consumer",
        product=product,
        agreed_price=Fraction(100),
        final_price=Fraction(150),  # Hidden fees
    )
    
    result = analyzer.analyze_transaction(transaction)
    assert result["compliant"] is False  # Hidden fees detected


def test_disclosure_requirements():
    """Required disclosures must be provided."""
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
    assert result["compliant"] is True


def test_warranty_honored():
    """Valid warranty claims are honored."""
    analyzer = WarrantyAnalyzer()
    
    product = Product(
        product_id="P003",
        name="Appliance",
        manufacturer="HomeCo",
        category="appliances",
        msrp=Fraction(500),
        warranties=[{"type": "LIMITED", "period_days": 365}],
    )
    
    # Within warranty
    result = analyzer.analyze_warranty_coverage(
        product=product,
        defect_description="Motor failure",
        purchase_date=datetime(2024, 1, 1),
        claim_date=datetime(2024, 4, 1),  # 3 months later
    )
    assert result["covered"] is True


def test_hidden_fees_detected():
    """Hidden fees in transactions are flagged."""
    analyzer = DeceptivePracticeAnalyzer()
    
    product = Product(
        product_id="P001",
        name="Service",
        manufacturer="ServiceCo",
        category="services",
        msrp=Fraction(100),
    )
    
    transaction = ConsumerTransaction(
        transaction_id="T001",
        consumer_name="Consumer",
        product=product,
        agreed_price=Fraction(100),
        final_price=Fraction(150),  # $50 hidden fees
    )
    
    result = analyzer.analyze_transaction(transaction)
    assert result["compliant"] is False


def test_tila_disclosures_required():
    """TILA requires specific credit disclosures."""
    checker = DisclosureRequirementsChecker()
    
    # Missing disclosures
    incomplete = {"annual_percentage_rate": "5.99%"}
    result = checker.check_tila_disclosures(incomplete)
    
    assert result["compliant"] is False
    assert len(result["missing_disclosures"]) > 0


def test_cooling_off_period():
    """Cooling-off period allows cancellation."""
    product = Product(
        product_id="P002",
        name="Door-to-door",
        manufacturer="SalesCo",
        category="services",
        msrp=Fraction(1000),
    )
    
    transaction = ConsumerTransaction(
        transaction_id="T002",
        consumer_name="Consumer",
        product=product,
        agreed_price=Fraction(1000),
        final_price=Fraction(1000),
        transaction_date=datetime(2024, 1, 1),
    )
    
    # Can cancel next day
    assert transaction.can_cancel(as_of=datetime(2024, 1, 2)) is True
    
    # Cannot cancel after period
    assert transaction.can_cancel(as_of=datetime(2024, 1, 5)) is False


def test_warranty_coverage():
    """Warranty covers defects within period."""
    analyzer = WarrantyAnalyzer()
    
    product = Product(
        product_id="P003",
        name="Appliance",
        manufacturer="HomeCo",
        category="appliances",
        msrp=Fraction(500),
        warranties=[{"type": "LIMITED", "period_days": 365}],
    )
    
    # Within warranty
    result = analyzer.analyze_warranty_coverage(
        product=product,
        defect_description="Motor failure",
        purchase_date=datetime(2024, 1, 1),
        claim_date=datetime(2024, 6, 1),
    )
    assert result["covered"] is True
    
    # Outside warranty
    result2 = analyzer.analyze_warranty_coverage(
        product=product,
        defect_description="Motor failure",
        purchase_date=datetime(2024, 1, 1),
        claim_date=datetime(2025, 6, 1),
    )
    assert result2["covered"] is False


def test_bait_and_switch_detected():
    """Bait-and-switch advertising is detected."""
    analyzer = DeceptivePracticeAnalyzer()
    
    product = Product(
        product_id="P004",
        name="Widget",
        manufacturer="Acme",
        category="electronics",
        msrp=Fraction(199),
    )
    
    ad = Advertisement(
        ad_id="A001",
        product=product,
        media_type="digital",
        claims=["Amazing deal! Starting at $99!"],
        advertised_price=Fraction(99),
        fine_print="Limited quantities.",
    )
    
    result = analyzer.analyze_advertisement(ad)
    # Should have issues with bait-and-switch indicators
    assert len(result["issues"]) > 0


if __name__ == "__main__":
    test_deceptive_practices_detected()
    test_disclosure_requirements()
    test_warranty_honored()
    test_hidden_fees_detected()
    test_tila_disclosures_required()
    test_cooling_off_period()
    test_warranty_coverage()
    test_bait_and_switch_detected()
    print("All D_CONSUMER_PROTECTION tests: PASS")
