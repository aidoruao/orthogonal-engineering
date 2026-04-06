"""Falsification tests for D_TRADE_AGREEMENTS

Test ID: F_TRADE_AGREEMENTS_001 through F_TRADE_AGREEMENTS_008
Domain: D_TRADE_AGREEMENTS (Trade & Commerce Agreements)
Layer: 0 (Supranational)
"""

from fractions import Fraction

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_trade_agreements.implementation import (
    TradeAgreement,
    TariffSchedule,
)
from src.domains.d_trade_agreements.invariants import (
    check_mfn_rate_application,
    check_mfn_clause_enforcement,
    check_mfn_clause_no_increase,
    check_fraction_precision_in_tariffs,
    check_trade_agreement_party_management,
)


class TestTariffSchedule:
    """Test suite for TariffSchedule calculations."""
    
    def test_mfn_rate_calculation(self):
        """F_TRADE_AGREEMENTS_001: MFN tariff calculated correctly."""
        schedule = TariffSchedule(
            product_code="TEST-001",
            mfn_rate=Fraction(5, 100),  # 5%
            preferential_rate=Fraction(2, 100),
        )
        
        value = Fraction(1000, 1)
        tariff = schedule.calculate_tariff(value, preferential=False)
        
        assert tariff == Fraction(50, 1)  # 5% of $1000 = $50
    
    def test_preferential_rate_calculation(self):
        """F_TRADE_AGREEMENTS_002: Preferential tariff calculated correctly."""
        schedule = TariffSchedule(
            product_code="TEST-002",
            mfn_rate=Fraction(10, 100),
            preferential_rate=Fraction(3, 100),  # 3%
        )
        
        value = Fraction(1000, 1)
        tariff = schedule.calculate_tariff(value, preferential=True)
        
        assert tariff == Fraction(30, 1)  # 3% of $1000 = $30
    
    def test_zero_tariff(self):
        """F_TRADE_AGREEMENTS_003: Zero tariff calculated correctly."""
        schedule = TariffSchedule(
            product_code="TEST-003",
            mfn_rate=Fraction(0, 100),
            preferential_rate=Fraction(0, 100),
        )
        
        value = Fraction(5000, 1)
        tariff = schedule.calculate_tariff(value, preferential=False)
        
        assert tariff == Fraction(0, 1)


class TestMFNClause:
    """Test suite for MFN clause enforcement."""
    
    def test_mfn_clause_reduces_rate(self):
        """F_TRADE_AGREEMENTS_004: MFN clause reduces MFN rate when lower offered."""
        agreement = TradeAgreement("Test FTA")
        
        schedule = TariffSchedule(
            product_code="WIDGET-001",
            mfn_rate=Fraction(10, 100),  # 10%
            preferential_rate=Fraction(5, 100),
        )
        agreement.add_tariff_schedule(schedule)
        
        # Apply lower rate via MFN clause
        agreement.apply_mfn_clause("WIDGET-001", Fraction(3, 100))
        
        new_rate = agreement.tariff_schedules["WIDGET-001"].mfn_rate
        assert new_rate == Fraction(3, 100)
    
    def test_mfn_clause_never_increases_rate(self):
        """F_TRADE_AGREEMENTS_005: MFN clause never increases MFN rate."""
        agreement = TradeAgreement("Test FTA")
        
        schedule = TariffSchedule(
            product_code="GADGET-001",
            mfn_rate=Fraction(5, 100),  # 5%
            preferential_rate=Fraction(2, 100),
        )
        agreement.add_tariff_schedule(schedule)
        
        # Try to apply higher rate via MFN clause
        agreement.apply_mfn_clause("GADGET-001", Fraction(15, 100))
        
        # Rate should NOT increase
        new_rate = agreement.tariff_schedules["GADGET-001"].mfn_rate
        assert new_rate == Fraction(5, 100)
    
    def test_mfn_clause_equal_rate_no_change(self):
        """F_TRADE_AGREEMENTS_006: MFN clause with equal rate keeps same."""
        agreement = TradeAgreement("Test FTA")
        
        schedule = TariffSchedule(
            product_code="ITEM-001",
            mfn_rate=Fraction(8, 100),
            preferential_rate=Fraction(4, 100),
        )
        agreement.add_tariff_schedule(schedule)
        
        # Apply same rate via MFN clause
        agreement.apply_mfn_clause("ITEM-001", Fraction(8, 100))
        
        new_rate = agreement.tariff_schedules["ITEM-001"].mfn_rate
        assert new_rate == Fraction(8, 100)


class TestFractionPrecision:
    """Test suite for fraction arithmetic in tariffs."""
    
    def test_exact_fraction_calculation(self):
        """F_TRADE_AGREEMENTS_007: Tariffs use exact fraction arithmetic."""
        schedule = TariffSchedule(
            product_code="PRECISE-001",
            mfn_rate=Fraction(1, 3),  # 33.333...%
            preferential_rate=Fraction(1, 7),
        )
        
        value = Fraction(100, 1)
        
        # 100 * 1/3 = 100/3 (exact)
        mfn_tariff = schedule.calculate_tariff(value, preferential=False)
        assert mfn_tariff == Fraction(100, 3)
        
        # 100 * 1/7 = 100/7 (exact)
        pref_tariff = schedule.calculate_tariff(value, preferential=True)
        assert pref_tariff == Fraction(100, 7)
    
    def test_avoids_floating_point_errors(self):
        """F_TRADE_AGREEMENTS_008: Fraction arithmetic avoids floating point issues."""
        schedule = TariffSchedule(
            product_code="PRECISE-002",
            mfn_rate=Fraction(1, 10),  # 0.1 (repeating in binary)
            preferential_rate=Fraction(1, 100),
        )
        
        value = Fraction(1, 1)
        
        # 1 * 0.1 = 0.1 exactly
        tariff = schedule.calculate_tariff(value, preferential=False)
        assert tariff == Fraction(1, 10)


class TestTradeAgreement:
    """Test suite for TradeAgreement management."""
    
    def test_add_tariff_schedule(self):
        """F_TRADE_AGREEMENTS_009: Can add tariff schedule to agreement."""
        agreement = TradeAgreement("Regional FTA")
        
        schedule = TariffSchedule(
            product_code="PROD-001",
            mfn_rate=Fraction(5, 100),
            preferential_rate=Fraction(0, 100),
        )
        agreement.add_tariff_schedule(schedule)
        
        assert "PROD-001" in agreement.tariff_schedules
    
    def test_initially_empty_schedules(self):
        """F_TRADE_AGREEMENTS_010: New agreement has empty schedules."""
        agreement = TradeAgreement("New FTA")
        
        assert len(agreement.tariff_schedules) == 0


class TestInvariants:
    """Test invariant checks."""
    
    def test_mfn_rate_application(self):
        """Test check_mfn_rate_application invariant."""
        result = check_mfn_rate_application()
        assert result is True
    
    def test_mfn_clause_enforcement(self):
        """Test check_mfn_clause_enforcement invariant."""
        result = check_mfn_clause_enforcement()
        assert result is True
    
    def test_mfn_clause_no_increase(self):
        """Test check_mfn_clause_no_increase invariant."""
        result = check_mfn_clause_no_increase()
        assert result is True
    
    def test_fraction_precision_in_tariffs(self):
        """Test check_fraction_precision_in_tariffs invariant."""
        result = check_fraction_precision_in_tariffs()
        assert result is True
    
    def test_trade_agreement_party_management(self):
        """Test check_trade_agreement_party_management invariant."""
        result = check_trade_agreement_party_management()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestTariffSchedule().test_mfn_rate_calculation,
        TestTariffSchedule().test_preferential_rate_calculation,
        TestMFNClause().test_mfn_clause_reduces_rate,
        TestMFNClause().test_mfn_clause_never_increases_rate,
        TestFractionPrecision().test_exact_fraction_calculation,
        TestTradeAgreement().test_add_tariff_schedule,
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
