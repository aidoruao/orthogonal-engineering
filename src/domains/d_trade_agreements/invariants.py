"""D_TRADE_AGREEMENTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: WTO Agreements, GATT 1994
"""

from fractions import Fraction
from src.domains.d_trade_agreements.implementation import (
    TradeAgreement,
    TariffSchedule,
)


def check_mfn_rate_application() -> bool:
    """
    Invariant: Tariff is calculated correctly using MFN or preferential rate.
    Falsification: If calculate_tariff returns wrong amount.
    """
    schedule = TariffSchedule(
        product_code="TEST-001",
        mfn_rate=Fraction(5, 100),  # 5%
        preferential_rate=Fraction(2, 100),  # 2%
    )
    
    value = Fraction(1000, 1)  # $1000
    
    # MFN rate: 5% of $1000 = $50
    mfn_tariff = schedule.calculate_tariff(value, preferential=False)
    assert mfn_tariff == Fraction(50, 1), (
        f"MFN tariff should be $50, got {mfn_tariff}"
    )
    
    # Preferential rate: 2% of $1000 = $20
    pref_tariff = schedule.calculate_tariff(value, preferential=True)
    assert pref_tariff == Fraction(20, 1), (
        f"Preferential tariff should be $20, got {pref_tariff}"
    )
    
    return True


def check_mfn_clause_enforcement() -> bool:
    """
    Invariant: MFN clause applies lowest rate to all parties.
    Falsification: If apply_mfn_clause doesn't update MFN rate when lower rate offered.
    """
    agreement = TradeAgreement("Test FTA")
    
    schedule = TariffSchedule(
        product_code="WIDGET-001",
        mfn_rate=Fraction(10, 100),  # 10%
        preferential_rate=Fraction(5, 100),  # 5%
    )
    agreement.add_tariff_schedule(schedule)
    
    initial_mfn = agreement.tariff_schedules["WIDGET-001"].mfn_rate
    assert initial_mfn == Fraction(10, 100), (
        "Initial MFN rate should be 10%"
    )
    
    # Apply MFN clause with lower rate (3%)
    agreement.apply_mfn_clause("WIDGET-001", Fraction(3, 100))
    
    new_mfn = agreement.tariff_schedules["WIDGET-001"].mfn_rate
    assert new_mfn == Fraction(3, 100), (
        f"MFN rate should drop to 3%, got {new_mfn}"
    )
    
    return True


def check_mfn_clause_no_increase() -> bool:
    """
    Invariant: MFN clause never increases tariff rates.
    Falsification: If apply_mfn_clause increases rate when higher rate offered.
    """
    agreement = TradeAgreement("Test FTA")
    
    schedule = TariffSchedule(
        product_code="GADGET-001",
        mfn_rate=Fraction(5, 100),  # 5%
        preferential_rate=Fraction(2, 100),  # 2%
    )
    agreement.add_tariff_schedule(schedule)
    
    # Apply MFN clause with HIGHER rate (10%)
    agreement.apply_mfn_clause("GADGET-001", Fraction(10, 100))
    
    # MFN rate should NOT increase
    mfn_rate = agreement.tariff_schedules["GADGET-001"].mfn_rate
    assert mfn_rate == Fraction(5, 100), (
        f"MFN rate should stay at 5%, not increase to {mfn_rate}"
    )
    
    return True


def check_fraction_precision_in_tariffs() -> bool:
    """
    Invariant: Tariff calculations use exact Fraction arithmetic.
    Falsification: If floating point rounding errors occur.
    """
    # Use rates that would cause floating point issues
    schedule = TariffSchedule(
        product_code="PRECISE-001",
        mfn_rate=Fraction(1, 3),  # 33.333...%
        preferential_rate=Fraction(1, 7),  # 14.285...%
    )
    
    value = Fraction(100, 1)
    
    # MFN: 100 * 1/3 = 33.333... (exactly 100/3)
    mfn_tariff = schedule.calculate_tariff(value, preferential=False)
    assert mfn_tariff == Fraction(100, 3), (
        f"Tariff should be exactly 100/3, got {mfn_tariff}"
    )
    
    # Preferential: 100 * 1/7 = 14.285... (exactly 100/7)
    pref_tariff = schedule.calculate_tariff(value, preferential=True)
    assert pref_tariff == Fraction(100, 7), (
        f"Tariff should be exactly 100/7, got {pref_tariff}"
    )
    
    return True


def check_trade_agreement_party_management() -> bool:
    """
    Invariant: TradeAgreement correctly manages parties and schedules.
    Falsification: If parties or schedules are not tracked correctly.
    """
    agreement = TradeAgreement("Regional FTA")
    
    # Initially empty
    assert len(agreement.tariff_schedules) == 0, (
        "New agreement should have no schedules"
    )
    
    # Add schedule
    schedule1 = TariffSchedule(
        product_code="PROD-001",
        mfn_rate=Fraction(5, 100),
        preferential_rate=Fraction(0, 100),
    )
    agreement.add_tariff_schedule(schedule1)
    
    assert "PROD-001" in agreement.tariff_schedules, (
        "Schedule should be added to agreement"
    )
    assert agreement.tariff_schedules["PROD-001"].mfn_rate == Fraction(5, 100), (
        "Schedule should have correct MFN rate"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_TRADE_AGREEMENTS invariants."""
    checks = [
        check_mfn_rate_application,
        check_mfn_clause_enforcement,
        check_mfn_clause_no_increase,
        check_fraction_precision_in_tariffs,
        check_trade_agreement_party_management,
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
    print("All D_TRADE_AGREEMENTS invariants: PASS")
