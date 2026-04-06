"""Falsification tests for D_AMENDMENT_PROCESS

Test ID: F_AMENDMENT_001 through F_AMENDMENT_008
Domain: D_AMENDMENT_PROCESS
Layer: 1 (Constitutional)
"""

from fractions import Fraction
from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_amendment_process.implementation import (
    AmendmentProcess,
    IndelibleClause,
    RatificationStatus,
    check_amendment_threshold,
)


class TestAmendmentProcess:
    """Test suite for AmendmentProcess."""
    
    def test_congressional_supermajority_required(self):
        """F_AMENDMENT_001: Congressional supermajority (2/3) required."""
        process = AmendmentProcess()
        
        # Should work with 2/3
        proposal = process.propose_amendment(
            proposal_id="TEST-001",
            text="Test amendment",
            congressional_support=Fraction(2, 3),
        )
        assert proposal.status == RatificationStatus.CONGRESSIONALLY_APPROVED
    
    def test_simple_majority_insufficient(self):
        """F_AMENDMENT_002: Simple majority (1/2) is insufficient."""
        process = AmendmentProcess()
        
        try:
            process.propose_amendment(
                proposal_id="TEST-002",
                text="Test amendment",
                congressional_support=Fraction(1, 2),
            )
            assert False, "Should have rejected simple majority"
        except ValueError:
            pass  # Expected
    
    def test_state_ratification_threshold(self):
        """F_AMENDMENT_003: 38 states required for ratification (3/4 of 50)."""
        process = AmendmentProcess()
        
        process.propose_amendment(
            proposal_id="STATE-TEST",
            text="State test",
            congressional_support=Fraction(2, 3),
        )
        
        # Ratify with 37 states - not enough
        for i in range(37):
            ratified = process.ratify_by_state("STATE-TEST", f"State-{i}")
            assert ratified is False
        
        # 38th state triggers ratification
        ratified = process.ratify_by_state("STATE-TEST", "State-37")
        assert ratified is True
    
    def test_indelible_senate_suffrage(self):
        """F_AMENDMENT_004: Equal state suffrage in Senate is indelible."""
        process = AmendmentProcess()
        
        indelible = process.check_indelible_clause(
            "Remove equal suffrage in Senate for all states"
        )
        assert indelible == IndelibleClause.EQUAL_STATE_SUFFRAGE_IN_SENATE
    
    def test_indelible_amendment_process(self):
        """F_AMENDMENT_005: Amendment process itself is indelible."""
        process = AmendmentProcess()
        
        indelible = process.check_indelible_clause(
            "Abolish the amendment process"
        )
        assert indelible == IndelibleClause.AMENDMENT_PROCESS_ITSELF


class TestThresholdCalculation:
    """Test suite for threshold calculation."""
    
    def test_37_states_insufficient(self):
        """F_AMENDMENT_006: 37 states is insufficient."""
        assert check_amendment_threshold(37) is False
    
    def test_38_states_sufficient(self):
        """F_AMENDMENT_007: 38 states is sufficient (3/4 of 50)."""
        assert check_amendment_threshold(38) is True
    
    def test_50_states_sufficient(self):
        """F_AMENDMENT_008: 50 states is sufficient."""
        assert check_amendment_threshold(50) is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestAmendmentProcess().test_congressional_supermajority_required,
        TestAmendmentProcess().test_simple_majority_insufficient,
        TestAmendmentProcess().test_state_ratification_threshold,
        TestThresholdCalculation().test_37_states_insufficient,
        TestThresholdCalculation().test_38_states_sufficient,
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
