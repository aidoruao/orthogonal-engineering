"""D_ISO_STANDARDS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ISO/IEC Directives
"""

import hashlib
from datetime import datetime
from src.domains.d_iso_standards.implementation import (
    ISOStandardsRegistry,
    ISOStandard,
)


def check_standard_integrity_verification() -> bool:
    """
    Invariant: verify_integrity returns True only for exact content match.
    Falsification: If verify_integrity returns True for modified content.
    """
    registry = ISOStandardsRegistry()
    
    # Pin a standard
    content = b"Test standard content v1.0"
    standard = registry.pin_standard(
        standard_id="ISO-TEST-001",
        name="Test Standard",
        version="1.0",
        content=content,
        release_date=datetime(2024, 1, 1),
    )
    
    # Original content should verify
    assert standard.verify_integrity(content), (
        "Original content should pass integrity check"
    )
    
    # Modified content should fail
    modified_content = b"Modified content"
    assert not standard.verify_integrity(modified_content), (
        "Modified content should fail integrity check"
    )
    
    # Even single byte change should fail
    modified_content2 = b"Test standard content v1.1"
    assert not standard.verify_integrity(modified_content2), (
        "Any content change should fail integrity check"
    )
    
    return True


def check_compliance_requires_integrity() -> bool:
    """
    Invariant: Compliance check fails if integrity check fails.
    Falsification: If compliance returns compliant=True when integrity is False.
    """
    registry = ISOStandardsRegistry()
    
    content = b"Standard requirements: section_A, section_B"
    registry.pin_standard(
        standard_id="ISO-COMP-001",
        name="Compliance Test Standard",
        version="1.0",
        content=content,
        release_date=datetime(2024, 1, 1),
        required_sections=["section_A", "section_B"],
    )
    
    # Check with wrong content (integrity fails)
    wrong_content = b"Wrong content"
    result = registry.check_compliance("ISO-COMP-001", wrong_content)
    
    assert not result["compliant"], (
        "Compliance should fail when integrity check fails"
    )
    assert not result["integrity_check"], (
        "Integrity check should be False for wrong content"
    )
    
    return True


def check_compliance_sections_required() -> bool:
    """
    Invariant: Compliance requires all required sections to be present.
    Falsification: If compliance passes when required sections are missing.
    """
    registry = ISOStandardsRegistry()
    
    content = b"Standard spec with required parts"
    registry.pin_standard(
        standard_id="ISO-SECT-001",
        name="Section Test Standard",
        version="1.0",
        content=content,
        release_date=datetime(2024, 1, 1),
        required_sections=["part_one", "part_two", "part_three"],
    )
    
    # Implementation missing required sections
    incomplete_impl = b"This has part_one but not others"
    result = registry.check_compliance("ISO-SECT-001", incomplete_impl)
    
    assert not result["compliant"], (
        "Compliance should fail when required sections are missing"
    )
    assert "part_two" in result["missing_sections"] or "part_three" in result["missing_sections"], (
        "Missing sections should be reported"
    )
    
    # Implementation with all required sections (plus integrity match)
    # Note: content hash won't match, so we test section detection separately
    section_results = registry.standards["ISO-SECT-001"].check_section_compliance(
        b"This has part_one and part_two and part_three"
    )
    assert all(section_results.values()), (
        "All required sections should be detected when present"
    )
    
    return True


def check_nonexistent_standard_compliance() -> bool:
    """
    Invariant: Checking compliance for non-existent standard returns proper error.
    Falsification: If check_compliance raises exception or returns wrong format.
    """
    registry = ISOStandardsRegistry()
    
    result = registry.check_compliance("ISO-NONEXISTENT", b"any content")
    
    assert not result["compliant"], (
        "Non-existent standard should return compliant=False"
    )
    assert "Standard not found" in result["missing_sections"], (
        "Non-existent standard should report 'Standard not found'"
    )
    
    return True


def check_hash_consistency() -> bool:
    """
    Invariant: Same content always produces same hash; different content produces different hash.
    Falsification: If hash collision occurs or same content produces different hashes.
    """
    content1 = b"Test content A"
    content2 = b"Test content B"
    
    hash1a = hashlib.sha256(content1).hexdigest()
    hash1b = hashlib.sha256(content1).hexdigest()
    hash2 = hashlib.sha256(content2).hexdigest()
    
    # Same content produces same hash
    assert hash1a == hash1b, (
        "Same content should produce identical hashes"
    )
    
    # Different content produces different hashes
    assert hash1a != hash2, (
        "Different content should produce different hashes"
    )
    
    # Hash length is correct (SHA-256 = 64 hex chars)
    assert len(hash1a) == 64, (
        "SHA-256 hash should be 64 hexadecimal characters"
    )
    
    return True


def run_all_invariants() -> dict:
    """Run all D_ISO_STANDARDS invariants."""
    checks = [
        check_standard_integrity_verification,
        check_compliance_requires_integrity,
        check_compliance_sections_required,
        check_nonexistent_standard_compliance,
        check_hash_consistency,
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
    print("All D_ISO_STANDARDS invariants: PASS")
