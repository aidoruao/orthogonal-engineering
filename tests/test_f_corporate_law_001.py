"""Falsification tests for D_CORPORATE_LAW"""
from fractions import Fraction
from src.domains.d_corporate_law import (
    FiduciaryDutyAnalyzer,
    CorporateVeilAnalyzer,
    Director,
    CorporateTransaction,
    Shareholder,
    check_self_dealing,
)


def test_self_dealing_requires_disclosure():
    """Self-dealing without disclosure is non-compliant."""
    analyzer = FiduciaryDutyAnalyzer()
    
    director = Director(
        name="John Director",
        director_id="D001",
        financial_interests={"ABC Corp": Fraction(100)},
    )
    
    transaction = CorporateTransaction(
        transaction_id="T001",
        description="Sale of assets",
        counterparty="ABC Corp",
        value=Fraction(500000),
        directors_involved=[director],
        disclosure_complete=False,  # No disclosure
        approved_by_disinterested=False,
    )
    
    result = analyzer.check_self_dealing_compliance(transaction)
    assert result["is_self_dealing"] is True
    assert result["compliant"] is None  # Requires entire fairness review


def test_self_dealing_safe_harbor_with_approval():
    """Self-dealing with disinterested director approval is compliant."""
    result = check_self_dealing(
        director_name="Jane Director",
        counterparty="XYZ LLC",
        transaction_value=Fraction(100000),
        director_has_interest=True,
        approved_by_disinterested=True,
        full_disclosure=True,
    )
    
    assert result["is_self_dealing"] is True
    assert result["compliant"] is True
    assert result["safe_harbor"] == "DGCL_144_a"


def test_corporate_veil_piercing_risk():
    """Multiple factors increase veil piercing risk."""
    analyzer = CorporateVeilAnalyzer()
    
    shareholder = Shareholder(
        name="Major Shareholder",
        shares_owned=100,
        total_shares_outstanding=100,  # 100% ownership
    )
    
    result = analyzer.analyze_veil_piercing_risk(
        corporation="Test Corp",
        shareholder=shareholder,
        commingling_of_funds=True,
        inadequate_capitalization=True,
        failure_to_follow_formalities=True,
        siphoning_of_funds=True,
        sole_shareholder=True,
    )
    
    assert result["risk_level"] in ("HIGH", "EXTREME")
    assert result["piercing_likely"] is True


def test_duty_of_loyalty_blocks_self_dealing():
    """Duty of loyalty prevents undisclosed self-dealing."""
    analyzer = FiduciaryDutyAnalyzer()
    
    director = Director(
        name="Conflicted Director",
        director_id="D002",
        financial_interests={"Vendor Inc": Fraction(50)},
    )
    
    transaction = CorporateTransaction(
        transaction_id="T002",
        description="Purchase from vendor",
        counterparty="Vendor Inc",
        value=Fraction(1000000),
        directors_involved=[director],
        disclosure_complete=False,
        approved_by_disinterested=False,
        fairness_opinion_obtained=False,
    )
    
    result = analyzer.analyze_duty_of_loyalty(transaction)
    assert not result["compliant"]
    assert any("disclosure" in issue.lower() for issue in result["issues"])


if __name__ == "__main__":
    test_self_dealing_requires_disclosure()
    test_self_dealing_safe_harbor_with_approval()
    test_corporate_veil_piercing_risk()
    test_duty_of_loyalty_blocks_self_dealing()
    print("All D_CORPORATE_LAW tests: PASS")
