#!/usr/bin/env python3
"""
Antitrust Domain — Sherman Act, Clayton Act, HSR

Key statutes:
- Sherman Act § 1: Contracts in restraint of trade
- Sherman Act § 2: Monopolization
- Clayton Act § 7: Mergers substantially lessening competition
"""

from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum, auto


class ViolationType(Enum):
    PRICE_FIXING = auto()
    MARKET_ALLOCATION = auto()
    BID_RIGGING = auto()
    MONOPOLIZATION = auto()
    MERGER = auto()


@dataclass
class MarketParticipant:
    """Firm in a relevant market."""
    firm_id: str
    market_share_pct: Fraction = Fraction(0)  # 0-100
    
    def get_share(self) -> Fraction:
        return self.market_share_pct


@dataclass
class Market:
    """Relevant antitrust market."""
    market_id: str
    product_definition: str
    geographic_scope: str
    participants: List[MarketParticipant] = field(default_factory=list)
    
    def total_market_size(self) -> Fraction:
        """Sum of all participant shares (should be <= 100)."""
        return sum(p.get_share() for p in self.participants)
    
    def get_hhi(self) -> int:
        """
        Calculate Herfindahl-Hirschman Index.
        HHI = sum of squared market shares (0-10,000).
        """
        total = Fraction(0)
        for p in self.participants:
            # Convert percentage to whole number (e.g., 30% -> 30)
            share = p.get_share()
            total += share * share
        return int(total)
    
    def get_concentration_level(self) -> str:
        """HHI concentration categories."""
        hhi = self.get_hhi()
        if hhi < 1500:
            return "unconcentrated"
        if hhi < 2500:
            return "moderately_concentrated"
        return "highly_concentrated"


@dataclass
class Merger:
    """Proposed merger between firms."""
    merger_id: str
    acquirer: MarketParticipant
    target: MarketParticipant
    market: Market
    
    MERGER_THRESHOLD_PCT = Fraction(30)  # HSR threshold
    
    def combined_share(self) -> Fraction:
        return self.acquirer.get_share() + self.target.get_share()
    
    def exceeds_threshold(self) -> bool:
        return self.combined_share() >= self.MERGER_THRESHOLD_PCT
    
    def post_merger_hhi(self) -> int:
        """Calculate HHI after merger."""
        # Remove acquirer and target, add combined
        other_shares = [
            p.get_share() for p in self.market.participants
            if p.firm_id not in [self.acquirer.firm_id, self.target.firm_id]
        ]
        combined = self.combined_share()
        hhi = sum(s * s for s in other_shares) + combined * combined
        return int(hhi)
    
    def hhi_increase(self) -> int:
        """Delta HHI from merger."""
        return self.post_merger_hhi() - self.market.get_hhi()


@dataclass
class PriceData:
    """Pricing data for collusion detection."""
    firm_id: str
    product_id: str
    price: Fraction
    date: str


@dataclass
class CollusionDetector:
    """Detect potential price-fixing."""
    price_data: List[PriceData]
    
    def find_identical_pricing(self) -> List[Tuple[str, str]]:
        """Find firms with identical prices for same product."""
        identical = []
        by_product: Dict[str, Dict[Fraction, List[str]]] = {}
        
        for pd in self.price_data:
            if pd.product_id not in by_product:
                by_product[pd.product_id] = {}
            if pd.price not in by_product[pd.product_id]:
                by_product[pd.product_id][pd.price] = []
            by_product[pd.product_id][pd.price].append(pd.firm_id)
        
        for product, prices in by_product.items():
            for price, firms in prices.items():
                if len(firms) > 1:
                    identical.append((product, price))
        
        return identical


# Antitrust thresholds
HHI_HIGHLY_CONCENTRATED = 2500
HHI_MODERATELY_CONCENTRATED = 1500
HHI_MERGER_CONCERN_DELTA = 200  # Delta HHI that raises concern
