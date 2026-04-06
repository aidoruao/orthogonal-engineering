"""Falsification tests for D_DIPLOMATIC

Test ID: F_DIPLOMATIC_001 through F_DIPLOMATIC_005
Domain: D_DIPLOMATIC (Diplomatic Law)
Layer: 0 (Supranational)
"""

from datetime import datetime, timedelta

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_diplomatic.implementation import (
    DiplomaticLaw,
    Diplomat,
    PersonaNonGrata,
)
from src.domains.d_diplomatic.invariants import (
    check_diplomatic_immunity_exists,
    check_persona_non_grata_validity,
    check_immunity_scope_lookup,
)


class TestDiplomat:
    """Test suite for Diplomat class."""
    
    def test_diplomat_has_immunity_in_scope(self):
        """F_DIPLOMATIC_001: Diplomat has immunity for actions in scope."""
        diplomat = Diplomat(
            name="Test Ambassador",
            country="Testland",
            rank="Ambassador",
            immunity_scope=["official_acts", "diplomatic_communications"],
        )
        
        assert diplomat.has_immunity("official_acts")
        assert diplomat.has_immunity("diplomatic_communications")
    
    def test_diplomat_no_immunity_outside_scope(self):
        """F_DIPLOMATIC_002: Diplomat has no immunity for actions outside scope."""
        diplomat = Diplomat(
            name="Test Ambassador",
            country="Testland",
            rank="Ambassador",
            immunity_scope=["official_acts"],
        )
        
        assert not diplomat.has_immunity("personal_crimes")
        assert not diplomat.has_immunity("commercial_activity")
    
    def test_default_immunity_scope_empty(self):
        """F_DIPLOMATIC_003: Default immunity scope is empty."""
        diplomat = Diplomat(
            name="Minimal Diplomat",
            country="Testland",
            rank="Attache",
        )
        
        assert not diplomat.has_immunity("anything")


class TestPersonaNonGrata:
    """Test suite for PersonaNonGrata declarations."""
    
    def test_png_valid_with_reason_and_future_deadline(self):
        """F_DIPLOMATIC_004: PNG is valid with reason and future deadline."""
        now = datetime.now()
        png = PersonaNonGrata(
            diplomat_name="Offending Diplomat",
            declaring_country="Hostland",
            declaration_date=now,
            reason="Engaged in espionage",
            departure_deadline=now + timedelta(days=30),
        )
        
        assert png.is_valid()
    
    def test_png_invalid_with_empty_reason(self):
        """F_DIPLOMATIC_005: PNG is invalid with empty reason."""
        now = datetime.now()
        png = PersonaNonGrata(
            diplomat_name="Diplomat",
            declaring_country="Hostland",
            declaration_date=now,
            reason="",
            departure_deadline=now + timedelta(days=30),
        )
        
        assert not png.is_valid()
    
    def test_png_invalid_with_past_deadline(self):
        """F_DIPLOMATIC_006: PNG is invalid if deadline is before declaration."""
        now = datetime.now()
        png = PersonaNonGrata(
            diplomat_name="Diplomat",
            declaring_country="Hostland",
            declaration_date=now,
            reason="Valid reason",
            departure_deadline=now - timedelta(days=1),
        )
        
        assert not png.is_valid()


class TestDiplomaticLaw:
    """Test suite for DiplomaticLaw registry."""
    
    def test_register_and_lookup_diplomat(self):
        """F_DIPLOMATIC_007: Can register diplomat and check immunity."""
        law = DiplomaticLaw()
        
        diplomat = Diplomat(
            name="Registered Diplomat",
            country="Testland",
            rank="Counselor",
            immunity_scope=["official_acts"],
        )
        law.register_diplomat(diplomat)
        
        assert law.check_immunity_scope("Registered Diplomat", "official_acts")
        assert not law.check_immunity_scope("Registered Diplomat", "personal_crimes")
    
    def test_lookup_unregistered_diplomat(self):
        """F_DIPLOMATIC_008: Lookup for unregistered diplomat returns False."""
        law = DiplomaticLaw()
        
        assert not law.check_immunity_scope("Non Existent", "anything")
    
    def test_declare_persona_non_grata(self):
        """F_DIPLOMATIC_009: Can declare persona non grata."""
        law = DiplomaticLaw()
        
        png = law.declare_persona_non_grata(
            diplomat_name="Bad Actor",
            declaring_country="Host Country",
            reason="Incompatible activities",
            departure_days=48,
        )
        
        assert png.diplomat_name == "Bad Actor"
        assert png.declaring_country == "Host Country"
        assert png.reason == "Incompatible activities"
        assert png.is_valid()
        assert len(law.png_declarations) == 1


class TestInvariants:
    """Test invariant checks."""
    
    def test_diplomatic_immunity_exists(self):
        """Test check_diplomatic_immunity_exists invariant."""
        result = check_diplomatic_immunity_exists()
        assert result is True
    
    def test_persona_non_grata_validity(self):
        """Test check_persona_non_grata_validity invariant."""
        result = check_persona_non_grata_validity()
        assert result is True
    
    def test_immunity_scope_lookup(self):
        """Test check_immunity_scope_lookup invariant."""
        result = check_immunity_scope_lookup()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestDiplomat().test_diplomat_has_immunity_in_scope,
        TestDiplomat().test_diplomat_no_immunity_outside_scope,
        TestPersonaNonGrata().test_png_valid_with_reason_and_future_deadline,
        TestPersonaNonGrata().test_png_invalid_with_empty_reason,
        TestDiplomaticLaw().test_register_and_lookup_diplomat,
        TestDiplomaticLaw().test_lookup_unregistered_diplomat,
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
