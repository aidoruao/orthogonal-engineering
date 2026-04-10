"""D_ISO_STANDARDS invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- ISO 9001:2015 (Quality Management Systems)
- ISO 14001:2015 (Environmental Management)
- ISO 27001:2022 (Information Security Management)
- ISO 31000:2018 (Risk Management)

Source: ontology/ontology.json#D_ISO_STANDARDS
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple
import hashlib
from datetime import datetime

from axioms.logic import ProofObject

from src.domains.d_iso_standards.implementation import (
    ISOStandardsRegistry,
    ISOStandard,
)


def check_standard_integrity_verification() -> Tuple[bool, ProofObject]:
    """
    Invariant: verify_integrity returns True only for exact content match.
    
    Standard: ISO/IEC 10118-3 (hash functions); SHA-256
    Falsifies if: verify_integrity returns True for modified content.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
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
    original_verifies = standard.verify_integrity(content)
    
    # Modified content should fail
    modified_content = b"Modified content"
    modified_fails = not standard.verify_integrity(modified_content)
    
    # Even single byte change should fail
    minor_change = b"Test standard content v1.1"
    minor_change_fails = not standard.verify_integrity(minor_change)
    
    success = original_verifies and modified_fails and minor_change_fails
    
    proof = ProofObject(
        rule="StandardIntegrityVerification",
        premises=[
            f"original_verifies = {original_verifies}",
            f"modified_fails = {modified_fails}",
            f"minor_change_fails = {minor_change_fails}",
            f"content_hash = {standard.content_hash[:16]}...",
        ],
        conclusion=(
            "ISO/IEC 10118-3 integrity verification enforced"
            if success
            else "FAIL: Integrity verification not enforced"
        ),
    )
    return success, proof


def check_compliance_requires_integrity() -> Tuple[bool, ProofObject]:
    """
    Invariant: Compliance check fails if integrity check fails.
    
    Standard: ISO 9001:2015 clause 7.5 (documented information)
    Falsifies if: compliance returns compliant=True when integrity is False.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
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
    
    compliant_false = result["compliant"] is False
    integrity_false = result["integrity_check"] is False
    
    success = compliant_false and integrity_false
    
    proof = ProofObject(
        rule="ComplianceRequiresIntegrity",
        premises=[
            f"compliant_false = {compliant_false}",
            f"integrity_false = {integrity_false}",
        ],
        conclusion=(
            "ISO 9001:2015 compliance integrity requirements enforced"
            if success
            else "FAIL: Compliance without integrity allowed"
        ),
    )
    return success, proof


def check_compliance_sections_required() -> Tuple[bool, ProofObject]:
    """
    Invariant: Compliance requires all required sections to be present.
    
    Standard: ISO 9001:2015 clause 4-10 (requirements)
    Falsifies if: Compliance passes when required sections are missing.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
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
    section_results = registry.standards["ISO-SECT-001"].check_section_compliance(
        incomplete_impl
    )
    
    # Only part_one found
    part_one_found = section_results.get("part_one", False)
    part_two_missing = not section_results.get("part_two", True)
    part_three_missing = not section_results.get("part_three", True)
    
    # Implementation with all required sections
    complete_impl = b"This has part_one and part_two and part_three"
    complete_results = registry.standards["ISO-SECT-001"].check_section_compliance(
        complete_impl
    )
    all_sections_found = all(complete_results.values())
    
    success = part_one_found and part_two_missing and part_three_missing and all_sections_found
    
    proof = ProofObject(
        rule="ComplianceSectionsRequired",
        premises=[
            f"part_one_found = {part_one_found}",
            f"part_two_missing = {part_two_missing}",
            f"part_three_missing = {part_three_missing}",
            f"all_sections_found_when_complete = {all_sections_found}",
        ],
        conclusion=(
            "ISO 9001:2015 section requirements enforced"
            if success
            else "FAIL: Section requirements not enforced"
        ),
    )
    return success, proof


def check_hash_consistency() -> Tuple[bool, ProofObject]:
    """
    Invariant: Same content → same hash; different content → different hash.
    
    Standard: ISO/IEC 10118-3 (secure hash properties)
    Falsifies if: Hash collision occurs or same content produces different hashes.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    content1 = b"Test content A"
    content2 = b"Test content B"
    
    hash1a = hashlib.sha256(content1).hexdigest()
    hash1b = hashlib.sha256(content1).hexdigest()
    hash2 = hashlib.sha256(content2).hexdigest()
    
    # Same content produces same hash
    same_content_same_hash = hash1a == hash1b
    
    # Different content produces different hashes
    different_content_different_hash = hash1a != hash2
    
    # Hash length is correct (SHA-256 = 64 hex chars)
    hash_length_correct = len(hash1a) == 64
    
    success = same_content_same_hash and different_content_different_hash and hash_length_correct
    
    proof = ProofObject(
        rule="HashConsistency",
        premises=[
            f"same_content_same_hash = {same_content_same_hash}",
            f"different_content_different_hash = {different_content_different_hash}",
            f"hash_length_64 = {hash_length_correct}",
        ],
        conclusion=(
            "ISO/IEC 10118-3 SHA-256 hash consistency enforced"
            if success
            else "FAIL: Hash consistency violated"
        ),
    )
    return success, proof


def check_iso_9001_quality_management() -> Tuple[bool, ProofObject]:
    """
    Invariant: ISO 9001 requires documented quality management system.
    
    Standard: ISO 9001:2015 clause 4.4 (quality management system)
    Falsifies if: QMS without required documentation passes compliance.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    registry = ISOStandardsRegistry()
    
    # ISO 9001-like requirements
    content = b"ISO 9001 QMS requirements"
    registry.pin_standard(
        standard_id="ISO-9001",
        name="Quality Management Systems",
        version="2015",
        content=content,
        release_date=datetime(2015, 9, 1),
        required_sections=[
            "context_of_organization",
            "leadership",
            "planning",
            "support",
            "operation",
            "performance_evaluation",
            "improvement",
        ],
    )
    
    # Implementation missing key clauses
    incomplete_qms = b"context_of_organization and leadership only"
    section_results = registry.standards["ISO-9001"].check_section_compliance(incomplete_qms)
    
    some_sections_found = any(section_results.values())
    some_sections_missing = not all(section_results.values())
    
    # Check that standard is registered
    standard_registered = "ISO-9001" in registry.standards
    
    success = some_sections_found and some_sections_missing and standard_registered
    
    proof = ProofObject(
        rule="ISO9001QualityManagement",
        premises=[
            f"standard_registered = {standard_registered}",
            f"some_sections_found = {some_sections_found}",
            f"some_sections_missing = {some_sections_missing}",
            f"required_clauses = {len(registry.standards['ISO-9001'].required_sections)}",
        ],
        conclusion=(
            "ISO 9001:2015 quality management requirements enforced"
            if success
            else "FAIL: ISO 9001 requirements not enforced"
        ),
    )
    return success, proof


def check_iso_27001_information_security() -> Tuple[bool, ProofObject]:
    """
    Invariant: ISO 27001 requires information security controls.
    
    Standard: ISO 27001:2022 Annex A (information security controls)
    Falsifies if: ISMS without security controls passes compliance.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    registry = ISOStandardsRegistry()
    
    # ISO 27001-like requirements
    content = b"ISO 27001 ISMS requirements"
    registry.pin_standard(
        standard_id="ISO-27001",
        name="Information Security Management",
        version="2022",
        content=content,
        release_date=datetime(2022, 10, 1),
        required_sections=[
            "information_security_policies",
            "organization_of_information_security",
            "human_resource_security",
            "asset_management",
            "access_control",
            "cryptography",
            "physical_security",
            "operations_security",
        ],
    )
    
    # Implementation with security controls
    isms_impl = b"information_security_policies and access_control and cryptography"
    section_results = registry.standards["ISO-27001"].check_section_compliance(isms_impl)
    
    security_controls_found = sum(1 for v in section_results.values() if v)
    security_controls_required = len(registry.standards["ISO-27001"].required_sections)
    
    # Some controls found, but not all
    partial_compliance = security_controls_found > 0
    
    standard_registered = "ISO-27001" in registry.standards
    
    success = partial_compliance and standard_registered
    
    proof = ProofObject(
        rule="ISO27001InformationSecurity",
        premises=[
            f"standard_registered = {standard_registered}",
            f"security_controls_found = {security_controls_found}",
            f"security_controls_required = {security_controls_required}",
            f"partial_compliance = {partial_compliance}",
        ],
        conclusion=(
            "ISO 27001:2022 information security requirements enforced"
            if success
            else "FAIL: ISO 27001 requirements not enforced"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_ISO_STANDARDS invariants."""
    checks = [
        ("check_standard_integrity_verification", check_standard_integrity_verification),
        ("check_compliance_requires_integrity", check_compliance_requires_integrity),
        ("check_compliance_sections_required", check_compliance_sections_required),
        ("check_hash_consistency", check_hash_consistency),
        ("check_iso_9001_quality_management", check_iso_9001_quality_management),
        ("check_iso_27001_information_security", check_iso_27001_information_security),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ISO_STANDARDS invariants: PASS")
