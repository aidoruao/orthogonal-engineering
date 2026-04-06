"""Falsification tests for D_ISO_STANDARDS

Test ID: F_ISO_STANDARDS_001 through F_ISO_STANDARDS_008
Domain: D_ISO_STANDARDS (International Standards)
Layer: 0 (Supranational)
"""

import hashlib
from datetime import datetime

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from src.domains.d_iso_standards.implementation import (
    ISOStandardsRegistry,
    ISOStandard,
)
from src.domains.d_iso_standards.invariants import (
    check_standard_integrity_verification,
    check_compliance_requires_integrity,
    check_compliance_sections_required,
    check_nonexistent_standard_compliance,
    check_hash_consistency,
)


class TestStandardIntegrity:
    """Test suite for standard integrity verification."""
    
    def test_original_content_verifies(self):
        """F_ISO_STANDARDS_001: Original content passes integrity check."""
        registry = ISOStandardsRegistry()
        content = b"Test standard v1.0"
        
        standard = registry.pin_standard(
            standard_id="ISO-TEST-001",
            name="Test Standard",
            version="1.0",
            content=content,
            release_date=datetime(2024, 1, 1),
        )
        
        assert standard.verify_integrity(content)
    
    def test_modified_content_fails(self):
        """F_ISO_STANDARDS_002: Modified content fails integrity check."""
        registry = ISOStandardsRegistry()
        content = b"Test standard v1.0"
        
        standard = registry.pin_standard(
            standard_id="ISO-TEST-002",
            name="Test Standard",
            version="1.0",
            content=content,
            release_date=datetime(2024, 1, 1),
        )
        
        modified = b"Modified content"
        assert not standard.verify_integrity(modified)
    
    def test_single_byte_change_fails(self):
        """F_ISO_STANDARDS_003: Single byte change fails integrity check."""
        registry = ISOStandardsRegistry()
        content = b"Test standard v1.0"
        
        standard = registry.pin_standard(
            standard_id="ISO-TEST-003",
            name="Test Standard",
            version="1.0",
            content=content,
            release_date=datetime(2024, 1, 1),
        )
        
        modified = b"Test standard v1.1"  # One byte changed
        assert not standard.verify_integrity(modified)


class TestCompliance:
    """Test suite for compliance checking."""
    
    def test_compliance_fails_without_integrity(self):
        """F_ISO_STANDARDS_004: Compliance fails when integrity check fails."""
        registry = ISOStandardsRegistry()
        content = b"Standard content"
        
        registry.pin_standard(
            standard_id="ISO-COMP-001",
            name="Compliance Test",
            version="1.0",
            content=content,
            release_date=datetime(2024, 1, 1),
        )
        
        wrong_content = b"Wrong implementation"
        result = registry.check_compliance("ISO-COMP-001", wrong_content)
        
        assert not result["compliant"]
        assert not result["integrity_check"]
    
    def test_compliance_checks_required_sections(self):
        """F_ISO_STANDARDS_005: Compliance checks for required sections."""
        registry = ISOStandardsRegistry()
        content = b"Standard spec"
        
        registry.pin_standard(
            standard_id="ISO-SECT-001",
            name="Section Test",
            version="1.0",
            content=content,
            release_date=datetime(2024, 1, 1),
            required_sections=["part_A", "part_B"],
        )
        
        # Implementation missing required sections
        incomplete = b"Only has part_A"
        result = registry.check_compliance("ISO-SECT-001", incomplete)
        
        assert not result["compliant"]
        assert "part_B" in result["missing_sections"]
    
    def test_section_detection_finds_present_sections(self):
        """F_ISO_STANDARDS_006: Section detection finds present sections."""
        registry = ISOStandardsRegistry()
        content = b"Standard spec"
        
        registry.pin_standard(
            standard_id="ISO-SECT-002",
            name="Section Test",
            version="1.0",
            content=content,
            release_date=datetime(2024, 1, 1),
            required_sections=["section_one", "section_two"],
        )
        
        impl = b"This contains section_one and section_two"
        sections = registry.standards["ISO-SECT-002"].check_section_compliance(impl)
        
        assert sections["section_one"] is True
        assert sections["section_two"] is True
    
    def test_nonexistent_standard_returns_error(self):
        """F_ISO_STANDARDS_007: Non-existent standard returns proper error."""
        registry = ISOStandardsRegistry()
        
        result = registry.check_compliance("ISO-NONEXISTENT", b"content")
        
        assert not result["compliant"]
        assert "Standard not found" in result["missing_sections"]


class TestHashConsistency:
    """Test suite for hash consistency."""
    
    def test_same_content_same_hash(self):
        """F_ISO_STANDARDS_008: Same content produces same hash."""
        content = b"Identical content"
        hash1 = hashlib.sha256(content).hexdigest()
        hash2 = hashlib.sha256(content).hexdigest()
        
        assert hash1 == hash2
    
    def test_different_content_different_hash(self):
        """F_ISO_STANDARDS_009: Different content produces different hash."""
        content1 = b"Content A"
        content2 = b"Content B"
        
        hash1 = hashlib.sha256(content1).hexdigest()
        hash2 = hashlib.sha256(content2).hexdigest()
        
        assert hash1 != hash2
    
    def test_hash_length_is_64(self):
        """F_ISO_STANDARDS_010: SHA-256 hash is 64 hex characters."""
        content = b"Any content"
        hash_value = hashlib.sha256(content).hexdigest()
        
        assert len(hash_value) == 64


class TestInvariants:
    """Test invariant checks."""
    
    def test_standard_integrity_verification(self):
        """Test check_standard_integrity_verification invariant."""
        result = check_standard_integrity_verification()
        assert result is True
    
    def test_compliance_requires_integrity(self):
        """Test check_compliance_requires_integrity invariant."""
        result = check_compliance_requires_integrity()
        assert result is True
    
    def test_compliance_sections_required(self):
        """Test check_compliance_sections_required invariant."""
        result = check_compliance_sections_required()
        assert result is True
    
    def test_nonexistent_standard_compliance(self):
        """Test check_nonexistent_standard_compliance invariant."""
        result = check_nonexistent_standard_compliance()
        assert result is True
    
    def test_hash_consistency(self):
        """Test check_hash_consistency invariant."""
        result = check_hash_consistency()
        assert result is True


if __name__ == "__main__":
    import sys
    
    test_cases = [
        TestStandardIntegrity().test_original_content_verifies,
        TestStandardIntegrity().test_modified_content_fails,
        TestCompliance().test_compliance_fails_without_integrity,
        TestCompliance().test_compliance_checks_required_sections,
        TestCompliance().test_nonexistent_standard_returns_error,
        TestHashConsistency().test_same_content_same_hash,
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
