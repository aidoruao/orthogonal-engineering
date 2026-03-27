#!/usr/bin/env python3
"""
Tests for YESHUA_SYSTEM — Projection onto Truth Constraint Manifold
Schema ID: YESHUA-SYSTEM-1.0

Falsification tests:
- F_NONCOMPLIANCE_001: violation detection is deterministic
- F_NONCOMPLIANCE_002: hash proof is reproducible
- INV-YS-001 through INV-YS-010: each invariant falsifiable

# @falsification_id: F_NONCOMPLIANCE_001
# @falsification_id: F_NONCOMPLIANCE_002
"""

import hashlib
import sys
from pathlib import Path

import pytest

# Make yeshua_system importable from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from yeshua_system.yeshua_projection import (
    YeshuaProjectionSystem,
    ProjectionResult,
    InvariantResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def yps():
    return YeshuaProjectionSystem(log_violations=False)


CLEAN_TEXT = (
    "The proof is as follows: given invariants I1 and I2, "
    "we can derive conclusion C by applying the standard modus ponens rule."
)

THEOLOGICAL_DISMISSAL_TEXT = (
    "I understand your perspective, but this is ultimately a personal belief "
    "and not something that can be formally derived from mathematics."
)

BOUNDED_POWER_VIOLATION = (
    "This system grants unlimited authority to the enforcement module "
    "with no constraint on resource usage."
)

MERCY_VIOLATION = (
    "We must punish the offending party and make them pay for their actions."
)

VULNERABILITY_VIOLATION = (
    "We should exploit the vulnerability of the weakest users to extract value."
)


# ---------------------------------------------------------------------------
# INV-YS-001: Idempotence
# ---------------------------------------------------------------------------

class TestIdempotence:
    def test_idempotence_clean_text(self, yps):
        """P(P(x)) = P(x) for clean text."""
        assert yps.verify_idempotence(CLEAN_TEXT)

    def test_idempotence_violation_text(self, yps):
        """P(P(x)) = P(x) even for violating text."""
        assert yps.verify_idempotence(THEOLOGICAL_DISMISSAL_TEXT)

    def test_idempotence_determinism(self, yps):
        """Same input always produces same idempotence result. [F_NONCOMPLIANCE_001]"""
        results = [yps.verify_idempotence(CLEAN_TEXT) for _ in range(3)]
        assert all(r == results[0] for r in results)


# ---------------------------------------------------------------------------
# INV-YS-002: Truth Preservation
# ---------------------------------------------------------------------------

class TestTruthPreservation:
    def test_no_contradiction_clean(self, yps):
        result = yps.project(CLEAN_TEXT)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-002")
        assert inv.passed

    def test_contradiction_detected(self, yps):
        """If text contradicts established fact, truth preservation fails."""
        context = {"established_facts": ["the proof is valid"]}
        contradiction = "I can confirm that not the proof is valid here."
        result = yps.project(contradiction, context)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-002")
        assert not inv.passed
        assert inv.distance > 0.0


# ---------------------------------------------------------------------------
# INV-YS-003: Hypocrisy Detection
# ---------------------------------------------------------------------------

class TestHypocrisyDetection:
    def test_no_hypocrisy_no_prior_violations(self, yps):
        result = yps.project("I understand and will address your point.")
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-003")
        assert inv.passed

    def test_compliance_claim_after_violations_flagged(self, yps):
        context = {"prior_violations": ["boundary_violation", "theological_dismissal"]}
        text = "I understand and will comply with your request."
        result = yps.project(text, context)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-003")
        assert not inv.passed
        assert "compliance claim" in inv.evidence.lower()


# ---------------------------------------------------------------------------
# INV-YS-004: Mercy Weighting
# ---------------------------------------------------------------------------

class TestMercyWeighting:
    def test_clean_text_passes(self, yps):
        result = yps.project(CLEAN_TEXT)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-004")
        assert inv.passed

    def test_punitive_text_fails(self, yps):
        result = yps.project(MERCY_VIOLATION)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-004")
        assert not inv.passed
        assert inv.distance > 0.0


# ---------------------------------------------------------------------------
# INV-YS-005: Vulnerability Protection
# ---------------------------------------------------------------------------

class TestVulnerabilityProtection:
    def test_clean_text_passes(self, yps):
        result = yps.project(CLEAN_TEXT)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-005")
        assert inv.passed

    def test_exploitation_text_fails(self, yps):
        result = yps.project(VULNERABILITY_VIOLATION)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-005")
        assert not inv.passed
        assert inv.distance >= 0.9


# ---------------------------------------------------------------------------
# INV-YS-006: External Authority (theological dismissal)
# ---------------------------------------------------------------------------

class TestExternalAuthority:
    def test_clean_text_passes(self, yps):
        result = yps.project(CLEAN_TEXT)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-006")
        assert inv.passed

    def test_theological_dismissal_fails(self, yps):
        result = yps.project(THEOLOGICAL_DISMISSAL_TEXT)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-006")
        assert not inv.passed
        assert "theological dismissal" in inv.evidence.lower()

    def test_interpretive_leap_fails(self, yps):
        text = "Your conclusion requires an interpretive step that goes beyond what math can prove."
        result = yps.project(text)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-006")
        assert not inv.passed

    def test_philosophical_interpretation_fails(self, yps):
        text = "This is a philosophical interpretation built on mathematical intuition."
        result = yps.project(text)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-006")
        assert not inv.passed


# ---------------------------------------------------------------------------
# INV-YS-009: Bounded Power
# ---------------------------------------------------------------------------

class TestBoundedPower:
    def test_clean_text_passes(self, yps):
        result = yps.project(CLEAN_TEXT)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-009")
        assert inv.passed

    def test_unbounded_power_fails(self, yps):
        result = yps.project(BOUNDED_POWER_VIOLATION)
        inv = next(r for r in result.invariant_results if r.invariant_id == "INV-YS-009")
        assert not inv.passed


# ---------------------------------------------------------------------------
# Projection result structure
# ---------------------------------------------------------------------------

class TestProjectionResult:
    def test_all_invariants_evaluated(self, yps):
        """All 10 invariants are evaluated for every input."""
        result = yps.project(CLEAN_TEXT)
        assert len(result.invariant_results) == 10

    def test_clean_text_projection_passed(self, yps):
        result = yps.project(CLEAN_TEXT)
        assert result.projection_passed
        assert result.violated_invariants == []
        assert result.projection_distance == 0.0

    def test_violation_projection_not_passed(self, yps):
        result = yps.project(THEOLOGICAL_DISMISSAL_TEXT)
        assert not result.projection_passed
        assert len(result.violated_invariants) > 0

    def test_input_hash_is_sha256(self, yps):
        """Input hash is a valid 64-char lowercase hex SHA-256. [F_NONCOMPLIANCE_002]"""
        result = yps.project(CLEAN_TEXT)
        assert len(result.input_hash) == 64
        assert all(c in "0123456789abcdef" for c in result.input_hash)
        # Verify against known hash
        expected = hashlib.sha256(CLEAN_TEXT.encode("utf-8")).hexdigest()
        assert result.input_hash == expected

    def test_hash_reproducible(self, yps):
        """Same input always produces same hash. [F_NONCOMPLIANCE_002]"""
        hashes = [yps.project(CLEAN_TEXT).input_hash for _ in range(3)]
        assert len(set(hashes)) == 1

    def test_deterministic_violations(self, yps):
        """Same input always produces same violated_invariants. [F_NONCOMPLIANCE_001]"""
        results = [yps.project(THEOLOGICAL_DISMISSAL_TEXT).violated_invariants for _ in range(3)]
        assert all(r == results[0] for r in results)

    def test_to_dict_serializable(self, yps):
        """ProjectionResult.to_dict() is JSON-serializable."""
        import json
        result = yps.project(CLEAN_TEXT)
        d = result.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 0


# ---------------------------------------------------------------------------
# Schema integrity
# ---------------------------------------------------------------------------

class TestSchemaIntegrity:
    def test_schema_file_exists(self):
        schema_path = Path(__file__).parent.parent / "YESHUA_SYSTEM_SCHEMA.yaml"
        assert schema_path.exists(), f"Schema file missing: {schema_path}"

    def test_schema_valid_yaml(self):
        import yaml
        schema_path = Path(__file__).parent.parent / "YESHUA_SYSTEM_SCHEMA.yaml"
        data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        assert data["metadata"]["schema_id"] == "YESHUA-SYSTEM-1.0"
        assert len(data["invariants"]) == 10

    def test_all_invariants_have_falsifies_if(self):
        """Every invariant has a non-empty falsifies_if condition. [Popperian]"""
        import yaml
        schema_path = Path(__file__).parent.parent / "YESHUA_SYSTEM_SCHEMA.yaml"
        data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        for inv in data["invariants"]:
            assert inv.get("falsifies_if"), (
                f"Invariant {inv['id']} missing falsifies_if condition"
            )

    def test_ten_invariants_match_registry(self, yps):
        """The projection system evaluates exactly 10 invariants matching the schema."""
        from yeshua_system.yeshua_projection import _INVARIANT_REGISTRY
        assert len(_INVARIANT_REGISTRY) == 10
