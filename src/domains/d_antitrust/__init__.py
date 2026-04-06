"""D_ANTITRUST: Antitrust (Sherman Act, price-fixing, merger review, HHI)

Layer 2 (Statutory) domain implementing antitrust analysis including
market concentration metrics and Sherman Act compliance.

Biblical: Deuteronomy 17:14-20 — Limits on king's accumulation of
wealth and horses, restraining concentration of power.
"""

from src.domains.d_antitrust.implementation import (
    HHIAnalyzer,
    ShermanActAnalyzer,
    MergerReview,
    RelevantMarket,
    MarketParticipant,
    HorizontalAgreement,
    AntitrustViolationType,
    AnalysisStandard,
    calculate_market_hhi,
)
from src.domains.d_antitrust.invariants import (
    check_hhi_increases_with_concentration,
    check_price_fixing_per_se_illegal,
    check_merger_increases_hhi,
)

__all__ = [
    "HHIAnalyzer",
    "ShermanActAnalyzer",
    "MergerReview",
    "RelevantMarket",
    "MarketParticipant",
    "HorizontalAgreement",
    "AntitrustViolationType",
    "AnalysisStandard",
    "calculate_market_hhi",
    "check_hhi_increases_with_concentration",
    "check_price_fixing_per_se_illegal",
    "check_merger_increases_hhi",
]
