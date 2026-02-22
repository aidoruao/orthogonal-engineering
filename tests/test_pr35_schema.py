"""
tests/test_pr35_schema.py — Tests for PR #35 Schema Integration

Validates that pr35_schema.build_schema() returns the expected structured
schema covering all 7 steps of the Yeshua Standard Integration Continuity.

Author: Orthogonal Engineering
PR: #35
Version: 1.0.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import pr35_schema


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

def test_build_schema_returns_dict():
    schema = pr35_schema.build_schema()
    assert isinstance(schema, dict)


def test_build_schema_has_required_top_level_keys():
    schema = pr35_schema.build_schema()
    for key in ("pr_number", "module_list", "invariants_applied",
                "verification_hooks", "delta_mapping", "agent_enforcement",
                "sections", "footer"):
        assert key in schema, f"Missing top-level key: {key!r}"


def test_pr_number_is_35():
    schema = pr35_schema.build_schema()
    assert schema["pr_number"] == 35


def test_footer_contains_complete():
    schema = pr35_schema.build_schema()
    assert "COMPLETE" in schema["footer"]


def test_schema_is_json_serialisable():
    schema = pr35_schema.build_schema()
    serialised = json.dumps(schema)
    parsed = json.loads(serialised)
    assert parsed["pr_number"] == 35


def test_schema_to_json_returns_string():
    j = pr35_schema.schema_to_json()
    assert isinstance(j, str)
    parsed = json.loads(j)
    assert parsed["pr_number"] == 35


# ---------------------------------------------------------------------------
# Section 1 — Initialization
# ---------------------------------------------------------------------------

def test_s1_returns_dict():
    s = pr35_schema.section1_initialization()
    assert isinstance(s, dict)


def test_s1_step_label():
    s = pr35_schema.section1_initialization()
    assert s["step"] == "initialization"


def test_s1_depends_on_required_prs():
    s = pr35_schema.section1_initialization()
    deps = s["pr_35_depends_on"]
    for pr_key in ("pr_16", "pr_22", "pr_23", "pr_24", "pr_26", "pr_32", "pr_34"):
        assert pr_key in deps, f"Missing dependency: {pr_key}"


def test_s1_each_dependency_has_required_fields():
    s = pr35_schema.section1_initialization()
    for pr_key, dep in s["pr_35_depends_on"].items():
        assert "description" in dep, f"{pr_key} missing description"
        assert "evidence_files" in dep, f"{pr_key} missing evidence_files"
        assert "status" in dep, f"{pr_key} missing status"
        assert isinstance(dep["evidence_files"], list)


# ---------------------------------------------------------------------------
# Section 2 — Delta Mapping
# ---------------------------------------------------------------------------

def test_s2_returns_dict():
    s = pr35_schema.section2_delta_mapping()
    assert isinstance(s, dict)


def test_s2_step_label():
    s = pr35_schema.section2_delta_mapping()
    assert s["step"] == "delta_extraction"


def test_s2_new_modules_is_list():
    s = pr35_schema.section2_delta_mapping()
    assert isinstance(s["new_modules"], list)
    assert len(s["new_modules"]) >= 1


def test_s2_each_module_has_required_fields():
    s = pr35_schema.section2_delta_mapping()
    for mod in s["new_modules"]:
        assert "module" in mod
        assert "purpose" in mod
        assert "predecessor" in mod


def test_s2_delta_from_34_is_list():
    s = pr35_schema.section2_delta_mapping()
    assert isinstance(s["delta_from_pr34"], list)
    assert len(s["delta_from_pr34"]) >= 1


def test_s2_delta_count_matches_new_modules():
    s = pr35_schema.section2_delta_mapping()
    assert s["delta_count"] == len(s["new_modules"])


# ---------------------------------------------------------------------------
# Section 3 — Constraint Integration
# ---------------------------------------------------------------------------

def test_s3_returns_dict():
    s = pr35_schema.section3_constraint_integration()
    assert isinstance(s, dict)


def test_s3_step_label():
    s = pr35_schema.section3_constraint_integration()
    assert s["step"] == "constraint_integration"


def test_s3_all_eight_axioms_present():
    s = pr35_schema.section3_constraint_integration()
    axiom_numbers = {c["axiom"] for c in s["constraints"]}
    assert axiom_numbers == {1, 2, 3, 4, 5, 6, 7, 8}


def test_s3_constraints_applied_count():
    s = pr35_schema.section3_constraint_integration()
    assert s["constraints_applied"] == 8


def test_s3_each_constraint_has_required_fields():
    s = pr35_schema.section3_constraint_integration()
    for c in s["constraints"]:
        for field in ("axiom", "text", "scope", "verification_hook", "fail_safe"):
            assert field in c, f"Constraint missing field: {field!r}"


def test_s3_enforcement_module_present():
    s = pr35_schema.section3_constraint_integration()
    assert s["enforcement_module"] != "NOT IMPLEMENTED"


def test_s3_axioms_module_present():
    s = pr35_schema.section3_constraint_integration()
    assert s["axioms_module"] != "NOT IMPLEMENTED"


# ---------------------------------------------------------------------------
# Section 4 — Verification / Fractal Mapping
# ---------------------------------------------------------------------------

def test_s4_returns_dict():
    s = pr35_schema.section4_verification_hooks()
    assert isinstance(s, dict)


def test_s4_step_label():
    s = pr35_schema.section4_verification_hooks()
    assert s["step"] == "verification_and_fractal_mapping"


def test_s4_hash_validation_sha256():
    s = pr35_schema.section4_verification_hooks()
    hv = s["cross_platform_hash_validation"]
    assert hv["algorithm"] == "SHA-256"
    assert hv["deterministic"] is True
    assert hv["cross_platform"] is True


def test_s4_no_float_arithmetic():
    s = pr35_schema.section4_verification_hooks()
    assert s["floating_arithmetic_elimination"]["uses_floats"] is False


def test_s4_recursive_integrity_bounded():
    s = pr35_schema.section4_verification_hooks()
    ri = s["recursive_integrity_validation"]
    assert ri["bounded"] is True
    assert ri["deterministic"] is True


def test_s4_nondeterminism_patterns_listed():
    s = pr35_schema.section4_verification_hooks()
    patterns = s["nondeterminism_check"]["patterns_forbidden"]
    assert isinstance(patterns, list)
    assert len(patterns) >= 2


# ---------------------------------------------------------------------------
# Section 5 — Agent Enforcement
# ---------------------------------------------------------------------------

def test_s5_returns_dict():
    s = pr35_schema.section5_agent_enforcement()
    assert isinstance(s, dict)


def test_s5_step_label():
    s = pr35_schema.section5_agent_enforcement()
    assert s["step"] == "copilot_agent_onboarding_and_enforcement"


def test_s5_enforcement_directives_is_list():
    s = pr35_schema.section5_agent_enforcement()
    directives = s["enforcement_directives"]
    assert isinstance(directives, list)
    assert len(directives) >= 3


def test_s5_each_directive_has_source():
    s = pr35_schema.section5_agent_enforcement()
    for d in s["enforcement_directives"]:
        assert "directive" in d
        assert "source" in d


def test_s5_verification_hooks_active():
    s = pr35_schema.section5_agent_enforcement()
    assert s["verification_hooks_active"] is True


# ---------------------------------------------------------------------------
# Section 6 — Serialization
# ---------------------------------------------------------------------------

def test_s6_returns_dict():
    s = pr35_schema.section6_serialization()
    assert isinstance(s, dict)


def test_s6_step_label():
    s = pr35_schema.section6_serialization()
    assert s["step"] == "schema_serialization"


def test_s6_output_file_is_json():
    s = pr35_schema.section6_serialization()
    assert s["output_file"].endswith(".json")


def test_s6_required_fields_listed():
    s = pr35_schema.section6_serialization()
    required = {"pr_number", "module_list", "invariants_applied",
                "verification_hooks", "delta_mapping", "agent_enforcement"}
    assert required == set(s["fields"])


def test_s6_hash_anchored():
    s = pr35_schema.section6_serialization()
    assert s["hash_anchored"] is True


# ---------------------------------------------------------------------------
# Section 7 — Audit and Execution
# ---------------------------------------------------------------------------

def test_s7_returns_dict():
    s = pr35_schema.section7_audit_and_execution()
    assert isinstance(s, dict)


def test_s7_step_label():
    s = pr35_schema.section7_audit_and_execution()
    assert s["step"] == "audit_and_execution"


def test_s7_all_halting_criteria_pass():
    s = pr35_schema.section7_audit_and_execution()
    criteria = s["halting_criteria"]
    for k, v in criteria.items():
        assert v is True, f"Halting criterion not met: {k!r}"


def test_s7_status_contains_complete():
    s = pr35_schema.section7_audit_and_execution()
    assert "COMPLETE" in s["status"]


def test_s7_cross_pr_check_covers_all_deps():
    s = pr35_schema.section7_audit_and_execution()
    check = s["cross_pr_check"]
    for pr_key in ("pr_16", "pr_22_23", "pr_24", "pr_26", "pr_32", "pr_34"):
        assert pr_key in check, f"Missing cross-PR check: {pr_key!r}"


# ---------------------------------------------------------------------------
# Top-level schema structure
# ---------------------------------------------------------------------------

def test_schema_module_list_is_list():
    schema = pr35_schema.build_schema()
    assert isinstance(schema["module_list"], list)
    assert len(schema["module_list"]) >= 1


def test_schema_invariants_applied_has_eight_items():
    schema = pr35_schema.build_schema()
    assert len(schema["invariants_applied"]) == 8


def test_schema_invariants_have_required_fields():
    schema = pr35_schema.build_schema()
    for inv in schema["invariants_applied"]:
        for f in ("axiom", "text", "verification_hook"):
            assert f in inv, f"invariant missing field: {f!r}"


def test_schema_sections_has_all_seven_steps():
    schema = pr35_schema.build_schema()
    expected = {
        "1_initialization", "2_delta_mapping", "3_constraint_integration",
        "4_verification_hooks", "5_agent_enforcement", "6_serialization",
        "7_audit_and_execution",
    }
    assert expected == set(schema["sections"].keys())


# ---------------------------------------------------------------------------
# write_schema_file — integration test
# ---------------------------------------------------------------------------

def test_write_schema_file_creates_file(tmp_path):
    out = tmp_path / "pr_35_schema_test.json"
    result_path = pr35_schema.write_schema_file(output_path=out)
    assert result_path == out
    assert out.exists()
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["pr_number"] == 35


def test_write_schema_file_is_valid_json(tmp_path):
    out = tmp_path / "pr_35_schema_test.json"
    pr35_schema.write_schema_file(output_path=out)
    # Must not raise
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, dict)


if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v"]))
