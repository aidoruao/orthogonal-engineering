"""Falsification tests for D_TREATIES

Test ID: F_TREATIES_001 through F_TREATIES_005
Domain: D_TREATIES (Treaty Obligations)
Layer: 0 (Supranational)
"""

from datetime import datetime, timedelta

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_treaties.implementation import (
    TreatyRegistry,
    TreatyStatus,
    check_treaty_supremacy,
)


class TestTreatySupremacy:
    """Test treaty supremacy over domestic law."""
    
    def test_ratified_treaty_overrides_domestic(self):
        """F_TREATIES_001: Ratified treaty should override conflicting domestic law."""
        registry = TreatyRegistry()
        
        registry.register_treaty(
            treaty_name="Human Rights Treaty",
            signed_date=datetime(2020, 1, 1),
            domestic_law_reference="PL 116-1",
        )
        registry.ratify_treaty(
            treaty_name="Human Rights Treaty",
            ratified_date=datetime(2020, 6, 1),
        )
        
        result = registry.check_supremacy(
            treaty_name="Human Rights Treaty",
            domestic_law_name="Conflicting Domestic Act",
            conflict_description="Conflict",
        )
        
        assert result["supremacy_applies"] is True
        assert result["domestic_law_amendment_required"] is True
    
    def test_unratified_treaty_no_supremacy(self):
        """F_TREATIES_002: Unratified treaty should not have supremacy."""
        registry = TreatyRegistry()
        
        registry.register_treaty(
            treaty_name="Unsigned Treaty",
            signed_date=None,
            domestic_law_reference="N/A",
        )
        
        result = registry.check_supremacy(
            treaty_name="Unsigned Treaty",
            domestic_law_name="Domestic Act",
            conflict_description="Conflict",
        )
        
        assert result["supremacy_applies"] is False
    
    def test_withdrawal_insufficient_notice(self):
        """F_TREATIES_003: Insufficient notice should be flagged."""
        registry = TreatyRegistry()
        registry.register_treaty("Test", datetime(2020, 1, 1), "PL 1")
        registry.ratify_treaty("Test", datetime(2020, 6, 1))
        
        notice = registry.initiate_withdrawal(
            treaty_name="Test",
            notice_date=datetime.now(),
            effective_date=datetime.now() + timedelta(days=30),
            reason="Test",
        )
        
        assert notice.proper_notice_given is False
    
    def test_withdrawal_sufficient_notice(self):
        """F_TREATIES_004: Sufficient notice should be accepted."""
        registry = TreatyRegistry()
        registry.register_treaty("Test", datetime(2020, 1, 1), "PL 1")
        registry.ratify_treaty("Test", datetime(2020, 6, 1))
        
        notice = registry.initiate_withdrawal(
            treaty_name="Test",
            notice_date=datetime.now(),
            effective_date=datetime.now() + timedelta(days=400),
            reason="Test",
        )
        
        assert notice.proper_notice_given is True
    
    def test_binding_treaties_list(self):
        """F_TREATIES_005: Only IN_FORCE treaties should be binding."""
        registry = TreatyRegistry()
        
        registry.register_treaty("Binding", datetime(2020, 1, 1), "PL 1")
        registry.ratify_treaty("Binding", datetime(2020, 6, 1))
        
        registry.register_treaty("NonBinding", datetime(2021, 1, 1), "PL 2")
        # Not ratified
        
        binding = registry.get_binding_treaties()
        assert len(binding) == 1
        assert binding[0].treaty_name == "Binding"


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestTreatySupremacy().test_ratified_treaty_overrides_domestic,
        TestTreatySupremacy().test_unratified_treaty_no_supremacy,
        TestTreatySupremacy().test_withdrawal_insufficient_notice,
        TestTreatySupremacy().test_withdrawal_sufficient_notice,
        TestTreatySupremacy().test_binding_treaties_list,
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
