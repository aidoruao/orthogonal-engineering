"""D_ANTITRUST implementation — Antitrust Law

Implements antitrust analysis including Sherman Act violations,
price-fixing detection, merger review, and HHI calculation.

Layer: 2 (Statutory)
CardinalStrength: PREDICATIVE
Source: Sherman Act (15 U.S.C. §1), Clayton Act (15 U.S.C. §18),
        FTC Act (15 U.S.C. §45), DOJ/FTC Horizontal Merger Guidelines
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum, auto
from fractions import Fraction


class AntitrustViolationType(Enum):
    """Types of antitrust violations."""
    PRICE_FIXING = auto()           # Sherman Act §1 - per se illegal
    MARKET_ALLOCATION = auto()      # Sherman Act §1 - per se illegal
    BID_RIGGING = auto()            # Sherman Act §1 - per se illegal
    TYING_ARRANGEMENT = auto()      # Sherman Act §1 - rule of reason
    MONOPOLIZATION = auto()         # Sherman Act §2
    ATTEMPTED_MONOPOLIZATION = auto()  # Sherman Act §2
    MERGER_TO_MONOPOLY = auto()     # Clayton Act §7
    EXCLUSIVE_DEALING = auto()      # Clayton Act §3


class AnalysisStandard(Enum):
    """Legal standards for antitrust analysis."""
    PER_SE_ILLEGAL = auto()         # No justification defense
    RULE_OF_REASON = auto()         # Balancing test
    QUICK_LOOK = auto()             # Abbreviated rule of reason
    STRUCTURAL_PRESUMPTION = auto()  # Based on market concentration


@dataclass
class MarketParticipant:
    """A participant in a relevant market."""
    name: str
    firm_id: str
    market_share: Fraction  # As decimal (e.g., 25/100 for 25%)
    
    def __post_init__(self):
        """Ensure market share is valid."""
        if self.market_share < 0 or self.market_share > 1:
            raise ValueError("Market share must be between 0 and 1 (as Fraction)")


@dataclass
class RelevantMarket:
    """Defines a relevant antitrust market."""
    market_name: str
    product_market: str
    geographic_market: str
    participants: List[MarketParticipant] = field(default_factory=list)
    
    @property
    def total_market_share(self) -> Fraction:
        """Sum of all participant shares (should be ~1.0)."""
        return sum((p.market_share for p in self.participants), Fraction(0))
    
    @property
    def is_valid(self) -> bool:
        """Check if market definition is valid."""
        # Market shares should sum to approximately 100%
        total = self.total_market_share
        return Fraction(95, 100) <= total <= Fraction(105, 100)
    
    def get_participant_share(self, firm_name: str) -> Fraction:
        """Get market share for a specific firm."""
        for p in self.participants:
            if p.name == firm_name:
                return p.market_share
        return Fraction(0)
    
    def get_top_firms(self, n: int = 4) -> List[MarketParticipant]:
        """Get top n firms by market share."""
        sorted_participants = sorted(
            self.participants,
            key=lambda p: p.market_share,
            reverse=True,
        )
        return sorted_participants[:n]


@dataclass
class HorizontalAgreement:
    """Agreement between horizontal competitors."""
    agreement_id: str
    participants: List[str]  # Names of participating firms
    agreement_type: str  # e.g., "price_fixing", "market_allocation"
    fixed_price: Optional[Fraction] = None
    allocated_territories: Optional[List[str]] = None
    evidence_of_communication: bool = False
    economic_evidence: bool = False  # Parallel pricing, etc.


class HHIAnalyzer:
    """Herfindahl-Hirschman Index calculator for market concentration.
    
    HHI is the sum of squared market shares—reflecting both the
    number of firms and size distribution. Biblical wisdom warns
    against concentrations of power (Deuteronomy 17:14-20 limits
    king's accumulation of wealth and horses).
    """
    
    # HHI thresholds per DOJ/FTC Horizontal Merger Guidelines
    UNCONCENTRATED_THRESHOLD = Fraction(1_500)  # Below: unconcentrated
    MODERATELY_CONCENTRATED_THRESHOLD = Fraction(2_500)  # 1500-2500: moderate
    # Above 2500: highly concentrated
    
    def __init__(self):
        self.calculated_hhi: Optional[Fraction] = None
    
    def calculate_hhi(self, market: RelevantMarket) -> Fraction:
        """Calculate HHI for a market.
        
        HHI = sum of (market_share * 100)^2 for all firms
        
        Args:
            market: The relevant market
            
        Returns:
            HHI as Fraction
        """
        hhi = Fraction(0)
        for participant in market.participants:
            # Convert share (0.25) to percentage (25), then square
            share_percentage = participant.market_share * 100
            hhi += share_percentage * share_percentage
        
        self.calculated_hhi = hhi
        return hhi
    
    def calculate_delta_hhi(
        self,
        market: RelevantMarket,
        merging_firms: List[str],
    ) -> Fraction:
        """Calculate change in HHI from merger.
        
        Delta HHI = 2 * s1 * s2 (for two firms with shares s1, s2)
        
        Args:
            market: Pre-merger market
            merging_firms: Names of firms merging
            
        Returns:
            Change in HHI
        """
        shares = []
        for firm_name in merging_firms:
            share = market.get_participant_share(firm_name)
            shares.append(share * 100)  # Convert to percentage
        
        if len(shares) == 2:
            # Delta HHI = 2 * s1 * s2
            return 2 * shares[0] * shares[1]
        
        # For more than 2 firms, sum all pairwise combinations
        delta = Fraction(0)
        for i in range(len(shares)):
            for j in range(i + 1, len(shares)):
                delta += 2 * shares[i] * shares[j]
        
        return delta
    
    def get_concentration_level(self, hhi: Optional[Fraction] = None) -> str:
        """Get concentration level description."""
        if hhi is None:
            hhi = self.calculated_hhi
        
        if hhi is None:
            return "UNKNOWN"
        
        if hhi < self.UNCONCENTRATED_THRESHOLD:
            return "UNCONCENTRATED"
        elif hhi < self.MODERATELY_CONCENTRATED_THRESHOLD:
            return "MODERATELY_CONCENTRATED"
        else:
            return "HIGHLY_CONCENTRATED"
    
    def is_merger_problematic(
        self,
        market: RelevantMarket,
        merging_firms: List[str],
        post_merger_hhi: Optional[Fraction] = None,
    ) -> Dict:
        """Check if merger raises competitive concerns.
        
        Args:
            market: Pre-merger market
            merging_firms: Firms proposing to merge
            post_merger_hhi: Pre-calculated post-merger HHI
            
        Returns:
            Analysis result
        """
        pre_hhi = self.calculate_hhi(market)
        delta_hhi = self.calculate_delta_hhi(market, merging_firms)
        
        if post_merger_hhi is None:
            post_hhi = pre_hhi + delta_hhi
        else:
            post_hhi = post_merger_hhi
        
        pre_level = self.get_concentration_level(pre_hhi)
        post_level = self.get_concentration_level(post_hhi)
        
        # Structural presumption thresholds
        structurally_presumed = False
        issues = []
        
        if post_hhi > self.MODERATELY_CONCENTRATED_THRESHOLD:
            if delta_hhi >= 100:  # 100 points in highly concentrated market
                structurally_presumed = True
                issues.append("Merger creates structural presumption (highly concentrated + delta >= 100)")
        elif post_hhi > self.UNCONCENTRATED_THRESHOLD:
            if delta_hhi >= 100:  # 100 points in moderately concentrated market
                structurally_presumed = True
                issues.append("Merger creates structural presumption (moderately concentrated + delta >= 100)")
        
        return {
            "pre_merger_hhi": pre_hhi,
            "post_merger_hhi": post_hhi,
            "delta_hhi": delta_hhi,
            "pre_concentration": pre_level,
            "post_concentration": post_level,
            "structural_presumption": structurally_presumed,
            "issues": issues,
        }


class ShermanActAnalyzer:
    """Analyzer for Sherman Act violations."""
    
    def __init__(self):
        self.violations_found: List[Dict] = []
    
    def analyze_price_fixing(
        self,
        agreement: HorizontalAgreement,
    ) -> Dict:
        """Analyze potential price-fixing agreement.
        
        Price-fixing is per se illegal under Sherman Act §1.
        No justification defense is available.
        
        Args:
            agreement: The horizontal agreement to analyze
            
        Returns:
            Analysis result
        """
        is_price_fixing = agreement.agreement_type.lower() in [
            "price_fixing", "price fixing", "price-fixing"
        ]
        
        if not is_price_fixing:
            return {
                "violation_type": AntitrustViolationType.PRICE_FIXING,
                "is_violation": False,
                "standard": AnalysisStandard.PER_SE_ILLEGAL,
                "reason": "Not a price-fixing agreement",
            }
        
        # Price-fixing is per se illegal
        evidence_score = 0
        if agreement.evidence_of_communication:
            evidence_score += 2
        if agreement.economic_evidence:
            evidence_score += 1
        if len(agreement.participants) >= 2:
            evidence_score += 1
        
        is_violation = evidence_score >= 3  # Strong evidence required
        
        return {
            "violation_type": AntitrustViolationType.PRICE_FIXING,
            "is_violation": is_violation,
            "standard": AnalysisStandard.PER_SE_ILLEGAL,
            "evidence_score": evidence_score,
            "evidence_factors": {
                "communication": agreement.evidence_of_communication,
                "economic_parallelism": agreement.economic_evidence,
                "multiple_participants": len(agreement.participants) >= 2,
            },
        }
    
    def analyze_market_allocation(
        self,
        agreement: HorizontalAgreement,
    ) -> Dict:
        """Analyze potential market allocation agreement.
        
        Market allocation is per se illegal under Sherman Act §1.
        
        Args:
            agreement: The horizontal agreement to analyze
            
        Returns:
            Analysis result
        """
        is_allocation = agreement.agreement_type.lower() in [
            "market_allocation", "market allocation", "territorial_allocation"
        ]
        
        if not is_allocation:
            return {
                "violation_type": AntitrustViolationType.MARKET_ALLOCATION,
                "is_violation": False,
                "standard": AnalysisStandard.PER_SE_ILLEGAL,
                "reason": "Not a market allocation agreement",
            }
        
        has_territories = (
            agreement.allocated_territories is not None and
            len(agreement.allocated_territories) > 0
        )
        
        return {
            "violation_type": AntitrustViolationType.MARKET_ALLOCATION,
            "is_violation": has_territories and agreement.evidence_of_communication,
            "standard": AnalysisStandard.PER_SE_ILLEGAL,
            "allocated_territories": agreement.allocated_territories or [],
        }


class MergerReview:
    """Comprehensive merger review system."""
    
    def __init__(self):
        self.hhi_analyzer = HHIAnalyzer()
        self.sherman_analyzer = ShermanActAnalyzer()
    
    def review_horizontal_merger(
        self,
        market: RelevantMarket,
        acquiring_firm: str,
        target_firm: str,
    ) -> Dict:
        """Complete horizontal merger review.
        
        Args:
            market: Relevant antitrust market
            acquiring_firm: Name of acquiring firm
            target_firm: Name of target firm
            
        Returns:
            Comprehensive review results
        """
        # HHI Analysis
        hhi_analysis = self.hhi_analyzer.is_merger_problematic(
            market,
            [acquiring_firm, target_firm],
        )
        
        # Market share analysis
        acquirer_share = market.get_participant_share(acquiring_firm)
        target_share = market.get_participant_share(target_firm)
        combined_share = acquirer_share + target_share
        
        return {
            "transaction": f"{acquiring_firm} acquiring {target_firm}",
            "hhi_analysis": hhi_analysis,
            "acquirer_share": acquirer_share,
            "target_share": target_share,
            "combined_share": combined_share,
            "recommendation": "CHALLENGE" if hhi_analysis["structural_presumption"] else "CLEAR",
        }


def calculate_market_hhi(participant_shares: List[Fraction]) -> Dict:
    """Convenience function to calculate HHI from shares.
    
    Usage:
        result = calculate_market_hhi([
            Fraction(40, 100),  # 40%
            Fraction(30, 100),  # 30%
            Fraction(20, 100),  # 20%
            Fraction(10, 100),  # 10%
        ])
        print(f"HHI: {result['hhi']}, Level: {result['level']}")
    """
    participants = [
        MarketParticipant(name=f"Firm_{i}", firm_id=str(i), market_share=share)
        for i, share in enumerate(participant_shares)
    ]
    
    market = RelevantMarket(
        market_name="Generic Market",
        product_market="Products",
        geographic_market="US",
        participants=participants,
    )
    
    analyzer = HHIAnalyzer()
    hhi = analyzer.calculate_hhi(market)
    level = analyzer.get_concentration_level(hhi)
    
    return {
        "hhi": hhi,
        "level": level,
        "is_valid_market": market.is_valid,
    }
