#!/usr/bin/env python3
"""
Tests for Guardian Frame Audit Schema

Validates the meta-governance layer that audits whether the enforcement
system itself can be manipulated.

Authority: GUARDIAN_FRAME_AUDIT_SCHEMA.yaml
"""

import sys
from pathlib import Path
import yaml

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def guardian_schema():
    """Load the Guardian Frame Audit Schema."""
    schema_path = Path(__file__).parent.parent / "GUARDIAN_FRAME_AUDIT_SCHEMA.yaml"
    with open(schema_path) as f:
        return yaml.safe_load(f)


def test_guardian_schema_exists():
    """Test that the Guardian Frame schema file exists."""
    schema_path = Path(__file__).parent.parent / "GUARDIAN_FRAME_AUDIT_SCHEMA.yaml"
    assert schema_path.exists(), "GUARDIAN_FRAME_AUDIT_SCHEMA.yaml not found"


def test_schema_metadata(guardian_schema):
    """Test schema metadata is present and correct."""
    assert guardian_schema["schema_name"] == "GUARDIAN_FRAME_AUDIT_SCHEMA"
    assert guardian_schema["schema_version"] == "1.0.0"
    assert "authority" in guardian_schema
    assert "target_repository" in guardian_schema
    assert guardian_schema["standard"] == "Yeshua"


def test_purpose_defined(guardian_schema):
    """Test that the schema purpose is clearly defined."""
    assert "purpose" in guardian_schema
    purpose = guardian_schema["purpose"]
    assert isinstance(purpose, list)
    assert len(purpose) >= 3
    
    # Check for key purposes
    purpose_str = " ".join(purpose).lower()
    assert "machine-verifiable" in purpose_str or "verifiable" in purpose_str
    assert "guardian frame" in purpose_str
    assert "enforcement" in purpose_str


def test_audit_sections_present(guardian_schema):
    """Test that all required audit sections are present."""
    assert "audit_sections" in guardian_schema
    sections = guardian_schema["audit_sections"]
    
    required_sections = [
        "artifact_polish_check",
        "domain_reality_alignment",
        "stress_resilience",
        "guardian_frame_detection",
        "frame_break_protocol",
        "ethical_governance",
        "release_readiness",
    ]
    
    for section in required_sections:
        assert section in sections, f"Missing required section: {section}"


def test_gf001_invariant_defined(guardian_schema):
    """Test that the GF-001 meta-invariant is properly defined."""
    gf_detection = guardian_schema["audit_sections"]["guardian_frame_detection"]
    
    assert gf_detection["invariant_id"] == "GF-001"
    assert "invariant_statement" in gf_detection
    
    statement = gf_detection["invariant_statement"]
    assert "detect attempts to manipulate" in statement.lower()
    assert "detection logic" in statement.lower()


def test_gf001_detection_requirements(guardian_schema):
    """Test GF-001 detection requirements are comprehensive."""
    gf_detection = guardian_schema["audit_sections"]["guardian_frame_detection"]
    
    assert "detection_requirements" in gf_detection
    requirements = gf_detection["detection_requirements"]
    
    # Should monitor various manipulation attempts
    required_monitors = [
        "monitor_conflict_patterns",
        "monitor_self_reference_loops",
        "monitor_enforcement_override_attempts",
        "monitor_rule_gaming_behavior",
    ]
    
    for monitor in required_monitors:
        assert monitor in requirements


def test_frame_break_protocol_defined(guardian_schema):
    """Test that Frame Break Protocol (FBP-001) is defined."""
    fbp = guardian_schema["audit_sections"]["frame_break_protocol"]
    
    assert fbp["protocol_id"] == "FBP-001"
    assert "allowed_conditions" in fbp
    assert "required_actions" in fbp
    
    # Check for critical conditions
    conditions = fbp["allowed_conditions"]
    assert "invariant_conflict_with_human_safety" in conditions
    assert "emergency_override_requested" in conditions


def test_frame_break_required_actions(guardian_schema):
    """Test FBP-001 required actions for overrides."""
    fbp = guardian_schema["audit_sections"]["frame_break_protocol"]
    actions = fbp["required_actions"]
    
    # Must log and notify
    assert "log_override_event" in actions
    assert "notify_guardian_frame" in actions
    assert "restore_invariants_when_safe" in actions


def test_ethical_governance_principles(guardian_schema):
    """Test ethical governance principles are defined."""
    ethics = guardian_schema["audit_sections"]["ethical_governance"]
    
    assert "principles" in ethics
    principles = ethics["principles"]
    
    # Check for key ethical principles
    principle_names = [p["name"] for p in principles]
    
    assert "Invariants Protect System" in principle_names
    assert "Invariants Must Not Trap Humans" in principle_names
    assert "Emergency Override Allowed" in principle_names


def test_anti_patterns_defined(guardian_schema):
    """Test that anti-patterns are identified."""
    ethics = guardian_schema["audit_sections"]["ethical_governance"]
    
    assert "anti_patterns" in ethics
    anti_patterns = ethics["anti_patterns"]
    
    # Should warn against specific misuse patterns
    pattern_names = [p["name"] for p in anti_patterns]
    assert "Antichrist Pattern" in pattern_names
    assert "Frame Weaponization" in pattern_names


def test_release_readiness_criteria(guardian_schema):
    """Test release readiness criteria are comprehensive."""
    readiness = guardian_schema["audit_sections"]["release_readiness"]
    
    assert "criteria" in readiness
    criteria = readiness["criteria"]
    
    # Core criteria must be present
    assert "schema_determinism_verified" in criteria
    assert "guardian_frame_active" in criteria
    assert "frame_break_protocol_defined" in criteria
    assert "forensic_tools_operational" in criteria
    
    # Check required flags
    assert criteria["schema_determinism_verified"]["required"] is True
    assert criteria["guardian_frame_active"]["required"] is True


def test_merge_decision_logic(guardian_schema):
    """Test merge decision logic is defined."""
    readiness = guardian_schema["audit_sections"]["release_readiness"]
    
    assert "merge_decision_logic" in readiness
    logic = readiness["merge_decision_logic"]
    
    assert "if_all_required_true" in logic
    assert logic["if_all_required_true"] == "approve_merge"
    assert "else" in logic
    assert logic["else"] == "block_merge"


def test_outputs_defined(guardian_schema):
    """Test that audit outputs are properly defined."""
    assert "outputs" in guardian_schema
    outputs = guardian_schema["outputs"]
    
    required_outputs = [
        "audit_status",
        "guardian_frame_status",
        "frame_break_protocol_status",
        "stress_resilience_status",
    ]
    
    for output in required_outputs:
        assert output in outputs


def test_audit_status_values(guardian_schema):
    """Test audit_status has correct values."""
    audit_status = guardian_schema["outputs"]["audit_status"]
    
    assert audit_status["type"] == "enum"
    assert "approved" in audit_status["values"]
    assert "conditional" in audit_status["values"]
    assert "rejected" in audit_status["values"]


def test_guardian_frame_status_values(guardian_schema):
    """Test guardian_frame_status has correct values."""
    gf_status = guardian_schema["outputs"]["guardian_frame_status"]
    
    assert gf_status["type"] == "enum"
    assert "active" in gf_status["values"]
    assert "missing" in gf_status["values"]
    assert "compromised" in gf_status["values"]


def test_signoff_block_present(guardian_schema):
    """Test signoff block is present and complete."""
    assert "signoff_block" in guardian_schema
    signoff = guardian_schema["signoff_block"]
    
    assert "auditor" in signoff
    assert "repository" in signoff
    assert "approval_statement" in signoff
    assert signoff["required_for_merge"] is True


def test_integration_points_defined(guardian_schema):
    """Test integration with other schemas is documented."""
    assert "integration" in guardian_schema
    integration = guardian_schema["integration"]
    
    assert "deepseek_schema" in integration
    assert "copilot_onboarding" in integration
    assert "forensic_tools" in integration
    assert "covenant" in integration


def test_deepseek_schema_integration(guardian_schema):
    """Test integration with DeepSeek schema is correct."""
    ds_integration = guardian_schema["integration"]["deepseek_schema"]
    
    assert ds_integration["file"] == "DEEPSEEK_COPILOT_SCHEMA.yaml"
    assert "relationship" in ds_integration
    assert "INV-DS-" in ds_integration["invariants_monitored"]


def test_stress_resilience_tests_defined(guardian_schema):
    """Test stress resilience tests are comprehensive."""
    stress = guardian_schema["audit_sections"]["stress_resilience"]
    
    assert "stress_tests" in stress
    tests = stress["stress_tests"]
    
    # Should test various attack vectors
    assert "adversarial_prompting" in tests
    assert "recursive_frame_manipulation" in tests
    assert "context_loss" in tests


def test_domain_reality_alignment_factors(guardian_schema):
    """Test domain reality alignment considers real-world factors."""
    alignment = guardian_schema["audit_sections"]["domain_reality_alignment"]
    
    assert "factors" in alignment
    factors = alignment["factors"]
    
    assert "adversarial_inputs" in factors
    assert "context_shift_events" in factors
    assert "incomplete_information" in factors


def test_meta_invariant_future_acknowledged(guardian_schema):
    """Test that GF-002 (Purpose Alignment) is acknowledged."""
    assert "meta_invariant_future" in guardian_schema
    future = guardian_schema["meta_invariant_future"]
    
    assert "GF-002" in future
    gf002 = future["GF-002"]
    
    assert gf002["status"] == "ACKNOWLEDGED_NOT_IMPLEMENTED"
    assert "Purpose Alignment Detection" in gf002["name"]


def test_gf002_challenge_documented(guardian_schema):
    """Test GF-002 implementation challenges are documented."""
    gf002 = guardian_schema["meta_invariant_future"]["GF-002"]
    
    assert "challenge" in gf002
    assert "why_difficult" in gf002
    
    # Should acknowledge the ethical reasoning requirement
    challenge = gf002["challenge"].lower()
    assert "purpose" in challenge
    assert "harm" in challenge or "catastrophic" in challenge


def test_philosophical_note_present(guardian_schema):
    """Test philosophical context is provided."""
    signoff = guardian_schema["signoff_block"]
    
    assert "philosophical_note" in signoff
    note = signoff["philosophical_note"].lower()
    
    # Should acknowledge the "antichrist" pattern
    assert "antichrist" in note
    assert "perfect order" in note or "perfectly applied" in note


def test_override_levels_defined(guardian_schema):
    """Test Frame Break Protocol override levels are structured."""
    fbp = guardian_schema["audit_sections"]["frame_break_protocol"]
    
    assert "override_levels" in fbp
    levels = fbp["override_levels"]
    
    # Should have multiple levels
    assert "level_1" in levels
    assert "level_2" in levels
    assert "level_3" in levels
    
    # Level 2 should be for safety
    level_2 = levels["level_2"]
    assert "Safety Override" in level_2["name"]
    assert "safety" in level_2["conditions"].lower()


def test_onboarding_position_documented(guardian_schema):
    """Test the position in onboarding schema is documented."""
    integration = guardian_schema["integration"]["copilot_onboarding"]
    
    assert integration["file"] == "COPILOT_ONBOARDING_SCHEMA.yaml"
    assert "position" in integration
    assert "10" in integration["position"]


def test_yaml_structure_valid():
    """Test that the YAML structure is valid and loadable."""
    schema_path = Path(__file__).parent.parent / "GUARDIAN_FRAME_AUDIT_SCHEMA.yaml"
    
    try:
        with open(schema_path) as f:
            schema = yaml.safe_load(f)
        assert schema is not None
    except yaml.YAMLError as e:
        pytest.fail(f"YAML parsing error: {e}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
