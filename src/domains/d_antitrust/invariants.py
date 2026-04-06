"""D_ANTITRUST invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: Sherman Act (15 U.S.C. §1), Clayton Act (15 U.S.C. §18),
        DOJ/FTC Horizontal Merger Guidelines
"""

from src.domains.d_antitrust.implementation import (
    HHIAnalyzer,
    ShermanActAnalyzer,
    RelevantMarket,
    MarketParticipant,
    HorizontalAgreement,
    calculate_market_hhi,
    AntitrustViolationType,
)
from fractions import Fraction


def check_hhi_increases_with_concentration() -> bool:
    """
    Invariant: HHI increases as market becomes more concentrated.
    Falsification: If equal-shares market has higher HHI than dominated market.
    """
    # Two firms with 50% each: HHI = 50² + 50² = 5000
    equal_shares = calculate_market_hhi([Fraction(50, 100), Fraction(50, 100)])
    
    # One firm with 90%, ten with 1%: HHI = 8100 + 10 = 8110
    dominated = calculate_market_hhi([Fraction(90, 100)] + [Fraction(1, 100)] * 10)
    
    assert dominated["hhi"] > equal_shares["hhi"], (
        f"Dominated market HHI ({dominated['hhi']}) should exceed equal shares ({equal_shares['hhi']})"
    )
    
    return True


def check_hhi_range_0_to_10000() -> bool:
    """
    Invariant: HHI ranges from 0 (atomistic) to 10000 (monopoly).
    Falsification: If HHI calculation produces value outside [0, 10000].
    """
    analyzer = HHIAnalyzer()
    
    # Monopoly: one firm with 100%
    monopoly = RelevantMarket(
        market_name="Monopoly",
        product_market="Widget",
        geographic_market="US",
        participants=[MarketParticipant(name="Only", firm_id="1", market_share=Fraction(100, 100))],
    )
    
    hhi = analyzer.calculate_hhi(monopoly)
    assert hhi == 10000, (
        f"Monopoly HHI should be 10000, got {hhi}"
    )
    
    # Many small firms
    atomistic = RelevantMarket(
        market_name="Competitive",
        product_market="Widget",
        geographic_market="US",
        participants=[MarketParticipant(name=f"F{i}", firm_id=str(i), market_share=Fraction(1, 100)) for i in range(100)],
    )
    
    hhi = analyzer.calculate_hhi(atomistic)
    assert hhi == 100, (
        f"100 equal firms HHI should be 100, got {hhi}"
    )
    
    return True


def check_price_fixing_per_se_illegal() -> bool:
    """
    Invariant: Price-fixing is per se illegal under Sherman Act §1.
    Falsification: If price-fixing is analyzed under rule of reason.
    """
    analyzer = ShermanActAnalyzer()
    
    agreement = HorizontalAgreement(
        agreement_id="A001",
        participants=["Firm A", "Firm B"],
        agreement_type="price_fixing",
        fixed_price=Fraction(100),
        evidence_of_communication=True,
        economic_evidence=True,
    )
    
    result = analyzer.analyze_price_fixing(agreement)
    
    assert result["is_violation"], (
        "Price-fixing with evidence should be violation"
    )
    assert result["standard"].name == "PER_SE_ILLEGAL", (
        "Price-fixing should be per se illegal"
    )
    
    return True


def check_merger_increases_hhi() -> bool:
    """
    Invariant: Merging firms increases HHI (delta HHI > 0).
    Falsification: If merger calculation shows delta HHI <= 0.
    """
    market = RelevantMarket(
        market_name="Test",
        product_market="Product",
        geographic_market="US",
        participants=[
            MarketParticipant(name="A", firm_id="1", market_share=Fraction(30, 100)),
            MarketParticipant(name="B", firm_id="2", market_share=Fraction(25, 100)),
            MarketParticipant(name="C", firm_id="3", market_share=Fraction(20, 100)),
            MarketParticipant(name="D", firm_id="4", market_share=Fraction(25, 100)),
        ],
    )
    
    analyzer = HHIAnalyzer()
    delta = analyzer.calculate_delta_hhi(market, ["A", "B"])
    
    assert delta > 0, (
        f"Merger delta HHI should be positive, got {delta}"
    )
    
    # Expected: 2 * 30 * 25 = 1500
    expected = Fraction(1500)
    assert delta == expected, (
        f"Delta HHI should be {expected}, got {delta}"
    )
    
    return True


def check_structural_presumption_threshold() -> bool:
    """
    Invariant: HHI > 2500 with delta > 100 triggers structural presumption.
    Falsification: If highly concentrated merger with large delta doesn't trigger presumption.
    """
    # Highly concentrated market (HHI > 2500)
    market = RelevantMarket(
        market_name="Concentrated",
        product_market="Product",
        geographic_market="US",
        participants=[
            MarketParticipant(name="A", firm_id="1", market_share=Fraction(50, 100)),
            MarketParticipant(name="B", firm_id="2", market_share=Fraction(30, 100)),
            MarketParticipant(name="C", firm_id="3", market_share=Fraction(20, 100)),
        ],
    )
    
    analyzer = HHIAnalyzer()
    result = analyzer.is_merger_problematic(market, ["A", "B"])
    
    assert result["post_concentration"] == "HIGHLY_CONCENTRATED", (
        "Post-merger should be highly concentrated"
    )
    assert result["structural_presumption"], (
        "Should trigger structural presumption"
    )
    
    return True


def check_market_shares_sum_to_100_percent() -> bool:
    """
    Invariant: Market shares must sum to approximately 100%.
    Falsification: If market shares don't sum to valid total.
    """
    # Valid market
    valid_market = RelevantMarket(
        market_name="Valid",
        product_market="Product",
        geographic_market="US",
        participants=[
            MarketParticipant(name="A", firm_id="1", market_share=Fraction(60, 100)),
            MarketParticipant(name="B", firm_id="2", market_share=Fraction(40, 100)),
        ],
    )
    
    assert valid_market.is_valid, (
        "Market with 100% shares should be valid"
    )
    
    # Invalid market (over 100%)
    invalid_market = RelevantMarket(
        market_name="Invalid",
        product_market="Product",
        geographic_market="US",
        participants=[
            MarketParticipant(name="A", firm_id="1", market_share=Fraction(60, 100)),
            MarketParticipant(name="B", firm_id="2", market_share=Fraction(60, 100)),
        ],
    )
    
    assert not invalid_market.is_valid, (
        "Market with 120% shares should be invalid"
    )
    
    return True


def check_concentration_levels_thresholds() -> bool:
    """
    Invariant: HHI thresholds define correct concentration levels.
    Falsification: If HHI levels don't match threshold definitions.
    """
    analyzer = HHIAnalyzer()
    
    # Unconcentrated: < 1500
    assert analyzer.get_concentration_level(Fraction(1400)) == "UNCONCENTRATED"
    
    # Moderately concentrated: 1500-2500
    assert analyzer.get_concentration_level(Fraction(2000)) == "MODERATELY_CONCENTRATED"
    
    # Highly concentrated: > 2500
    assert analyzer.get_concentration_level(Fraction(3000)) == "HIGHLY_CONCENTRATED"
    
    return True


def run_all_invariants() -> dict:
    """Run all D_ANTITRUST invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_hhi_increases_with_concentration,
        check_hhi_range_0_to_10000,
        check_price_fixing_per_se_illegal,
        check_merger_increases_hhi,
        check_structural_presumption_threshold,
        check_market_shares_sum_to_100_percent,
        check_concentration_levels_thresholds,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ANTITRUST invariants: PASS")
