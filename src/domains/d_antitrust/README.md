# D_ANTITRUST: Antitrust Law

**Layer:** 2 (Statutory)  
**CardinalStrength:** PREDICATIVE  
**Authority:** Sherman Act (15 U.S.C. §1), Clayton Act (15 U.S.C. §18),
FTC Act (15 U.S.C. §45), DOJ/FTC Horizontal Merger Guidelines

## Description

Domain implementing antitrust analysis including market concentration metrics
(Herfindahl-Hirschman Index), horizontal merger review, and Sherman Act §1
violations. Antitrust law preserves competitive markets and prevents
concentrations of economic power that harm consumers.

## Invariants

1. **HHI Range**: Herfindahl-Hirschman Index ranges from 0 (perfect competition)
   to 10,000 (monopoly).

2. **Per Se Illegal Conduct**: Price-fixing, market allocation, and bid-rigging
   are per se illegal under Sherman Act §1 (no justification defense).

3. **Merger Increases Concentration**: Horizontal mergers increase HHI
   (delta HHI = 2 × s1 × s2).

4. **Structural Presumption**: Mergers producing HHI > 2500 with delta > 100
   trigger presumption of illegality.

5. **Market Share Validity**: Market shares must sum to approximately 100%.

6. **Concentration Thresholds**: HHI < 1500 (unconcentrated), 1500-2500
   (moderately concentrated), > 2500 (highly concentrated).

## Key Classes

- `HHIAnalyzer`: Calculates HHI and merger effects
- `ShermanActAnalyzer`: Detects per se violations
- `MergerReview`: Comprehensive merger analysis
- `RelevantMarket`: Defines product and geographic market
- `MarketParticipant`: Firm with market share
- `HorizontalAgreement`: Agreement between competitors

## Usage

```python
from fractions import Fraction
from src.domains.d_antitrust import (
    HHIAnalyzer,
    RelevantMarket,
    MarketParticipant,
)

# Define market
market = RelevantMarket(
    market_name="Widget Manufacturing",
    product_market="Industrial widgets",
    geographic_market="United States",
    participants=[
        MarketParticipant(name="Corp A", firm_id="1", market_share=Fraction(40, 100)),
        MarketParticipant(name="Corp B", firm_id="2", market_share=Fraction(30, 100)),
        MarketParticipant(name="Corp C", firm_id="3", market_share=Fraction(20, 100)),
        MarketParticipant(name="Corp D", firm_id="4", market_share=Fraction(10, 100)),
    ],
)

# Analyze merger
analyzer = HHIAnalyzer()
result = analyzer.is_merger_problematic(market, ["Corp A", "Corp B"])

print(f"Pre-merger HHI: {result['pre_merger_hhi']}")
print(f"Post-merger HHI: {result['post_merger_hhi']}")
print(f"Structural presumption: {result['structural_presumption']}")
```

## Biblical Inspiration

Deuteronomy 17:14-20 — Limits on the king's accumulation of wealth and horses,
requiring him to read the law daily and not consider himself above his
fellow citizens.

Antitrust law reflects this biblical concern with unchecked concentrations
of power. Just as Israelite kings faced limits on their economic accumulation,
modern corporations face limits on market concentration to preserve freedom
and prevent oppression.

## Falsification Tests

- `F_ANTITRUST_001`: Verify price-fixing detected as per se illegal
- `F_ANTITRUST_002`: Verify HHI calculation correct for monopoly
- `F_ANTITRUST_003`: Verify merger delta HHI calculation
- `F_ANTITRUST_004`: Verify structural presumption threshold
- `F_ANTITRUST_005`: Verify market share validation
