"""Falsification tests for D_SEPARATION_OF_POWERS

Test ID: F_SOP_001 through F_SOP_008
Domain: D_SEPARATION_OF_POWERS
Layer: 1 (Constitutional)
"""

from fractions import Fraction

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_separation_of_powers.implementation import (
    Branch,
    GovernmentPower,
    SeparationOfPowersChecker,
    BranchAuthority,
    SeparationViolation,
    check_non_delegation_doctrine,
)
from src.domains.d_separation_of_powers.invariants import (
    check_executive_cannot_legislate,
    check_legislative_non_delegation,
)


class TestBranchAuthority:
    """Test suite for BranchAuthority."""
    
    def test_executive_can_enforce_laws(self):
        """F_SOP_001: Executive can enforce laws."""
        executive = BranchAuthority(Branch.EXECUTIVE)
        assert executive.can_exercise(GovernmentPower.ENFORCING_LAWS) is True
    
    def test_executive_cannot_make_laws(self):
        """F_SOP_002: Executive cannot make laws."""
        executive = BranchAuthority(Branch.EXECUTIVE)
        assert executive.can_exercise(GovernmentPower.MAKING_LAWS) is False
    
    def test_legislature_can_make_laws(self):
        """F_SOP_003: Legislature can make laws."""
        legislature = BranchAuthority(Branch.LEGISLATIVE)
        assert legislature.can_exercise(GovernmentPower.MAKING_LAWS) is True
    
    def test_judiciary_can_interpret_laws(self):
        """F_SOP_004: Judiciary can interpret laws."""
        judicial = BranchAuthority(Branch.JUDICIAL)
        assert judicial.can_exercise(GovernmentPower.INTERPRETING_LAWS) is True


class TestSeparationOfPowersChecker:
    """Test suite for SeparationOfPowersChecker."""
    
    def test_executive_legislating_flagged(self):
        """F_SOP_005: Executive legislating is flagged."""
        checker = SeparationOfPowersChecker()
        result = checker.check_executive_action(
            power=GovernmentPower.MAKING_LAWS,
            description="Executive order creating penalties",
            claimed_authority="Emergency",
        )
        assert result.constitutional is False
        assert SeparationViolation.EXECUTIVE_LEGISLATING in result.violations
    
    def test_legislature_adjudicating_flagged(self):
        """F_SOP_006: Legislature adjudicating is flagged."""
        checker = SeparationOfPowersChecker()
        result = checker.check_legislative_action(
            power=GovernmentPower.INTERPRETING_LAWS,
            description="Reversing court decision",
            claimed_authority="Oversight",
        )
        assert result.constitutional is False
    
    def test_proper_executive_action_allowed(self):
        """F_SOP_007: Proper executive action is allowed."""
        checker = SeparationOfPowersChecker()
        result = checker.check_executive_action(
            power=GovernmentPower.ENFORCING_LAWS,
            description="Prosecuting crime",
            claimed_authority="Article II",
        )
        assert result.constitutional is True


class TestNonDelegation:
    """Test suite for non-delegation doctrine."""
    
    def test_delegating_legislative_power_unconstitutional(self):
        """F_SOP_008: Delegating legislative power is unconstitutional."""
        result = check_non_delegation_doctrine(
            legislative_power=GovernmentPower.MAKING_LAWS,
            delegated_to=Branch.EXECUTIVE,
        )
        assert result is False
    
    def test_legislature_retaining_power_constitutional(self):
        """Legislature keeping law-making power is constitutional."""
        result = check_non_delegation_doctrine(
            legislative_power=GovernmentPower.MAKING_LAWS,
            delegated_to=Branch.LEGISLATIVE,
        )
        assert result is True


class TestInvariants:
    """Test invariant checks."""
    
    def test_executive_cannot_legislate(self):
        """Test check_executive_cannot_legislate."""
        result = check_executive_cannot_legislate()
        assert result is True
    
    def test_legislative_non_delegation(self):
        """Test check_legislative_non_delegation."""
        result = check_legislative_non_delegation()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestBranchAuthority().test_executive_can_enforce_laws,
        TestBranchAuthority().test_executive_cannot_make_laws,
        TestSeparationOfPowersChecker().test_executive_legislating_flagged,
        TestNonDelegation().test_delegating_legislative_power_unconstitutional,
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
