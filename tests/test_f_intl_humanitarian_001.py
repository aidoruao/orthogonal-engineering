"""Falsification tests for D_INTERNATIONAL_HUMANITARIAN

Test ID: F_INTL_HUMANITARIAN_001 through F_INTL_HUMANITARIAN_006
Domain: D_INTERNATIONAL_HUMANITARIAN (International Humanitarian Law)
Layer: 0 (Supranational)
"""

from fractions import Fraction

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_intl_humanitarian.implementation import (
    IHLChecker,
    UseOfForceEvaluation,
)
from src.domains.d_intl_humanitarian.invariants import (
    check_distinction_principle,
    check_proportionality_principle,
    check_checker_proportionality_method,
    check_fraction_precision,
)


class TestDistinction:
    """Test suite for distinction principle."""
    
    def test_cannot_target_civilians(self):
        """F_INTL_HUMANITARIAN_001: Cannot target non-combatants."""
        checker = IHLChecker()
        
        result = checker.check_distinction(
            target_is_combatant=False,
            civilian_presence=False,
        )
        assert result is False
    
    def test_can_target_combatants(self):
        """F_INTL_HUMANITARIAN_002: Can target combatants."""
        checker = IHLChecker()
        
        result = checker.check_distinction(
            target_is_combatant=True,
            civilian_presence=False,
        )
        assert result is True
    
    def test_can_target_combatants_with_civilian_presence(self):
        """F_INTL_HUMANITARIAN_003: Can target combatants with civilian presence
        (requires proportionality check)."""
        checker = IHLChecker()
        
        result = checker.check_distinction(
            target_is_combatant=True,
            civilian_presence=True,
        )
        assert result is True


class TestProportionality:
    """Test suite for proportionality principle."""
    
    def test_proportional_high_gain_low_harm(self):
        """F_INTL_HUMANITARIAN_004: High military gain vs low harm is proportional."""
        evaluation = UseOfForceEvaluation(
            military_objective_value=Fraction(100, 1),
            civilian_harm_risk=Fraction(1, 1),
        )
        assert evaluation.is_proportional()
    
    def test_not_proportional_low_gain_high_harm(self):
        """F_INTL_HUMANITARIAN_005: Low military gain vs high harm is not proportional."""
        evaluation = UseOfForceEvaluation(
            military_objective_value=Fraction(1, 1),
            civilian_harm_risk=Fraction(100, 1),
        )
        assert not evaluation.is_proportional()
    
    def test_not_proportional_equal_values(self):
        """F_INTL_HUMANITARIAN_006: Equal gain and harm is not proportional
        (must be strictly greater)."""
        evaluation = UseOfForceEvaluation(
            military_objective_value=Fraction(50, 1),
            civilian_harm_risk=Fraction(50, 1),
        )
        assert not evaluation.is_proportional()
    
    def test_proportional_via_checker(self):
        """F_INTL_HUMANITARIAN_007: IHLChecker correctly evaluates proportionality."""
        checker = IHLChecker()
        
        result = checker.check_proportionality(
            military_gain=Fraction(10, 1),
            civilian_harm=Fraction(1, 1),
        )
        assert result is True
    
    def test_not_proportional_via_checker(self):
        """F_INTL_HUMANITARIAN_008: IHLChecker correctly rejects disproportionate."""
        checker = IHLChecker()
        
        result = checker.check_proportionality(
            military_gain=Fraction(1, 1),
            civilian_harm=Fraction(10, 1),
        )
        assert result is False


class TestFractionPrecision:
    """Test suite for fraction arithmetic."""
    
    def test_exact_fraction_calculation(self):
        """F_INTL_HUMANITARIAN_009: Calculations use exact fractions."""
        evaluation = UseOfForceEvaluation(
            military_objective_value=Fraction(1, 3),
            civilian_harm_risk=Fraction(1, 7),
        )
        
        # 1/3 > 1/7, so should be proportional
        assert evaluation.is_proportional()
    
    def test_fraction_comparison_avoids_float_errors(self):
        """F_INTL_HUMANITARIAN_010: Fraction arithmetic avoids floating point errors."""
        # These would have precision issues in floating point
        evaluation1 = UseOfForceEvaluation(
            military_objective_value=Fraction(1, 10),
            civilian_harm_risk=Fraction(1, 3),
        )
        assert not evaluation1.is_proportional()
        
        evaluation2 = UseOfForceEvaluation(
            military_objective_value=Fraction(2, 3),
            civilian_harm_risk=Fraction(1, 3),
        )
        assert evaluation2.is_proportional()


class TestInvariants:
    """Test invariant checks."""
    
    def test_distinction_principle(self):
        """Test check_distinction_principle invariant."""
        result = check_distinction_principle()
        assert result is True
    
    def test_proportionality_principle(self):
        """Test check_proportionality_principle invariant."""
        result = check_proportionality_principle()
        assert result is True
    
    def test_checker_proportionality_method(self):
        """Test check_checker_proportionality_method invariant."""
        result = check_checker_proportionality_method()
        assert result is True
    
    def test_fraction_precision(self):
        """Test check_fraction_precision invariant."""
        result = check_fraction_precision()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestDistinction().test_cannot_target_civilians,
        TestDistinction().test_can_target_combatants,
        TestProportionality().test_proportional_high_gain_low_harm,
        TestProportionality().test_not_proportional_low_gain_high_harm,
        TestProportionality().test_not_proportional_equal_values,
        TestFractionPrecision().test_exact_fraction_calculation,
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
