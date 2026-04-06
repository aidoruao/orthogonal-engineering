"""Falsification tests for D_ANTITRUST"""
from fractions import Fraction
from src.domains.d_antitrust import (
    HHIAnalyzer,
    ShermanActAnalyzer,
    RelevantMarket,
    MarketParticipant,
    HorizontalAgreement,
    AntitrustViolationType,
    calculate_market_hhi,
)


def test_hhi_increases_with_concentration():
    """HHI increases as market becomes more concentrated."""
    # Equal market (lower HHI)
    equal_shares = [Fraction(25, 100), Fraction(25, 100), Fraction(25, 100), Fraction(25, 100)]
    equal_result = calculate_market_hhi(equal_shares)
    
    # Concentrated market (higher HHI)
    concentrated_shares = [Fraction(60, 100), Fraction(20, 100), Fraction(10, 100), Fraction(10, 100)]
    concentrated_result = calculate_market_hhi(concentrated_shares)
    
    assert concentrated_result["hhi"] > equal_result["hhi"]


def test_price_fixing_per_se_illegal():
    """Price-fixing agreements are per se illegal."""
    analyzer = ShermanActAnalyzer()
    
    agreement = HorizontalAgreement(
        agreement_id="A001",
        participants=["Firm A", "Firm B", "Firm C"],
        agreement_type="price_fixing",
        fixed_price=Fraction(100),
        evidence_of_communication=True,
        economic_evidence=True,
    )
    
    result = analyzer.analyze_price_fixing(agreement)
    assert result["is_violation"] is True
    assert result["standard"].name == "PER_SE_ILLEGAL"


def test_merger_increases_hhi():
    """Horizontal merger increases market concentration (delta HHI)."""
    analyzer = HHIAnalyzer()
    
    participants = [
        MarketParticipant(name="Firm A", firm_id="A", market_share=Fraction(30, 100)),
        MarketParticipant(name="Firm B", firm_id="B", market_share=Fraction(30, 100)),
        MarketParticipant(name="Firm C", firm_id="C", market_share=Fraction(20, 100)),
        MarketParticipant(name="Firm D", firm_id="D", market_share=Fraction(20, 100)),
    ]
    
    market = RelevantMarket(
        market_name="Test Market",
        product_market="Widgets",
        geographic_market="US",
        participants=participants,
    )
    
    pre_hhi = analyzer.calculate_hhi(market)
    delta = analyzer.calculate_delta_hhi(market, ["Firm A", "Firm B"])
    
    assert delta > 0


def test_concentration_level_classification():
    """HHI correctly classifies market concentration levels."""
    analyzer = HHIAnalyzer()
    
    # Unconcentrated (HHI < 1500) - 10 firms at 10% each = 1000
    unconcentrated = [Fraction(10, 100)] * 10
    result = calculate_market_hhi(unconcentrated)
    assert result["level"] == "UNCONCENTRATED"
    
    # Highly concentrated (HHI > 2500)
    highly = [Fraction(60, 100), Fraction(30, 100), Fraction(10, 100)]
    result = calculate_market_hhi(highly)
    assert result["level"] == "HIGHLY_CONCENTRATED"


if __name__ == "__main__":
    test_hhi_increases_with_concentration()
    test_price_fixing_per_se_illegal()
    test_merger_increases_hhi()
    test_concentration_level_classification()
    print("All D_ANTITRUST tests: PASS")
