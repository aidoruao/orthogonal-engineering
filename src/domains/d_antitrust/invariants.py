#!/usr/bin/env python3
"""Antitrust Domain Invariants — Sherman Act, Clayton Act compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import Market, Merger, CollusionDetector, HHI_MERGER_CONCERN_DELTA


def check_hhi_concentration(market: Market) -> Tuple[bool, ProofObject]:
    """HHI must accurately reflect market concentration.
    
    hhi = market.get_hhi()
    level = market.get_concentration_level()
    
    if hhi > 10000:
        return False, ProofObject(
            conclusion=f"VIOLATION: HHI {hhi} exceeds maximum 10,000",
            premises=[],
            rule="hhi_bounds"
        )
    
    return True, ProofObject(
        conclusion=f"HHI: {hhi} ({level})",
        premises=[f"Participants: {len(market.participants)}"],
        rule="hhi_calculation"
    )


def check_merger_threshold(merger: Merger) -> Tuple[bool, ProofObject]:
    
    
    Falsifies if: delta > HHI_MERGER_CONCERN_DELTA"""Clayton Act § 7: Mergers exceeding threshold require review.
    
    combined = merger.combined_share()
    threshold = merger.MERGER_THRESHOLD_PCT
    
    if merger.exceeds_threshold():
        delta = merger.hhi_increase()
        if delta > HHI_MERGER_CONCERN_DELTA:
            return False, ProofObject(
                conclusion=f"VIOLATION: Merger raises significant competitive concerns (delta HHI: {delta})",
                premises=[f"Combined share: {combined}%", f"Delta HHI: {delta}"],
                rule="clayton_act_merger"
            )
        return True, ProofObject(
            conclusion=f"Merger exceeds threshold but delta HHI acceptable ({delta})",
            premises=[f"Combined: {combined}%"],
            rule="clayton_act_merger"
        )
    
    return True, ProofObject(
        conclusion=f"Merger below threshold ({combined}% < {threshold}%)",
        premises=[],
        rule="clayton_act_merger"
    )


def check_price_filing_collusion(detector: CollusionDetector) -> Tuple[bool, ProofObject]:
    """Sherman Act § 1: Price-fixing detection via identical pricing.
    
    identical = detector.find_identical_pricing()
    
    if identical:
        return False, ProofObject(
            conclusion=f"VIOLATION: Potential price-fixing detected ({len(identical)} products)",
            premises=[f"Products: {identical}"],
            rule="sherman_act_price_fixing"
        )
    
    return True, ProofObject(
        conclusion="No identical pricing detected",
        premises=[],
        rule="sherman_act_price_fixing"
    )


def check_market_shares_sum(market: Market) -> Tuple[bool, ProofObject]:
    
    
    Falsifies if: total > Fraction(100)"""Market shares should sum to approximately 100%.
    
    total = market.total_market_size()
    
    if total > Fraction(100):
        return False, ProofObject(
            conclusion=f"VIOLATION: Market shares sum to {total}% > 100%",
            premises=[],
            rule="market_share_sum"
        )
    
    return True, ProofObject(
        conclusion=f"Market shares sum to {total}%",
        premises=[],
        rule="market_share_sum"
    )
