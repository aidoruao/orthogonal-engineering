#!/usr/bin/env python3
"""Antitrust Domain Invariants — Sherman Act, Clayton Act compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    CollusionDetector,
    HHI_MERGER_CONCERN_DELTA,
    Market,
    MarketParticipant,
    Merger,
    PriceData,
)


def check_hhi_concentration(market: Market) -> Tuple[bool, ProofObject]:
    """HHI must accurately reflect market concentration.

    Falsifies if: market.get_hhi() exceeds 10,000.
    falsifies_if: market.get_hhi() exceeds 10,000.
    """
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
    """Clayton Act § 7: Mergers exceeding threshold require review.

    Falsifies if: merger exceeds threshold and HHI delta surpasses HHI_MERGER_CONCERN_DELTA.
    falsifies_if: merger exceeds threshold and HHI delta surpasses HHI_MERGER_CONCERN_DELTA.
    """
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

    Falsifies if: detector.find_identical_pricing() returns any products.
    falsifies_if: detector.find_identical_pricing() returns any products.
    """
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
    """Market shares should sum to approximately 100%.

    Falsifies if: market total market size exceeds 100%.
    falsifies_if: market total market size exceeds 100%.
    """
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


def run_all_invariants() -> dict:
    """Run all D_ANTITRUST invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    market = Market(
        market_id="ANTITRUS-001",
        product_definition="SAMPLE",
        geographic_scope="SAMPLE",
    )
    merger = Merger(
        merger_id="ANTITRUS-001",
        acquirer=MarketParticipant(
        firm_id="ANTITRUS-001",
    ),
        target=MarketParticipant(
        firm_id="ANTITRUS-001",
    ),
        market=Market(
        market_id="ANTITRUS-001",
        product_definition="SAMPLE",
        geographic_scope="SAMPLE",
    ),
    )
    collusion_detector = CollusionDetector(
        price_data=[PriceData(
        firm_id="ANTITRUS-001",
        product_id="ANTITRUS-001",
        price=Fraction(1),
        date="SAMPLE",
    )],
    )

    checks = [
        ("check_hhi_concentration", lambda: check_hhi_concentration(market)),
        ("check_market_shares_sum", lambda: check_market_shares_sum(market)),
        ("check_merger_threshold", lambda: check_merger_threshold(merger)),
        ("check_price_filing_collusion", lambda: check_price_filing_collusion(collusion_detector)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ANTITRUST invariants: PASS")
