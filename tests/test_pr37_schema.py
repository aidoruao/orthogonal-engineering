"""
tests/test_pr37_schema.py — Tests for PR #37 DVCL + YML Schema

Validates that pr37_schema.build_schema() returns the expected structured
schema covering the Distributed Verifiable Compute Layer and Yeshua
Mathematics Layer.

Author: Orthogonal Engineering
PR: #37
Version: 1.0.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import pr37_schema
from dvcl.determinism_guard import run_determinism_guard
from dvcl.benchmark_harness import run_benchmark
from yeshua_math.peano_invariant_checker import run_peano_invariant_checker
from yeshua_math.boolean_purity_validator import run_boolean_purity_validator, validate_truth_table
from yeshua_math.pure_reference_runtime.cross_validator import run_cross_validation


# ---------------------------------------------------------------------------
# Smoke tests — build_schema
# ---------------------------------------------------------------------------


def test_build_schema_returns_dict():
    schema = pr37_schema.build_schema()
    assert isinstance(schema, dict)


def test_pr_number_is_37():
    schema = pr37_schema.build_schema()
    assert schema["pr_number"] == 37


def test_build_schema_has_required_top_level_keys():
    schema = pr37_schema.build_schema()
    for key in ("pr_number", "title", "standard", "version", "module_list", "sections", "footer"):
        assert key in schema, f"Missing top-level key: {key!r}"


def test_footer_contains_complete():
    schema = pr37_schema.build_schema()
    assert "COMPLETE" in schema["footer"]


def test_schema_is_json_serialisable():
    schema = pr37_schema.build_schema()
    serialised = json.dumps(schema)
    parsed = json.loads(serialised)
    assert parsed["pr_number"] == 37


def test_schema_to_json_returns_string():
    j = pr37_schema.schema_to_json()
    assert isinstance(j, str)
    parsed = json.loads(j)
    assert parsed["pr_number"] == 37


def test_module_list_contains_dvcl_and_yml():
    schema = pr37_schema.build_schema()
    assert "dvcl" in schema["module_list"]
    assert "yeshua_math" in schema["module_list"]
    assert "ci" in schema["module_list"]


def test_sections_has_all_ten_steps():
    schema = pr37_schema.build_schema()
    expected = {
        "1_initialization",
        "2_deterministic_execution_spec",
        "3_proof_carrying_execution",
        "4_cross_node_verification",
        "5_dual_path_execution",
        "6_yeshua_mathematics_layer",
        "7_benchmark_harness",
        "8_tensor_identity_enforcement",
        "9_zero_trust_merge_gate",
        "10_halting_condition",
    }
    assert expected == set(schema["sections"].keys())


# ---------------------------------------------------------------------------
# Section 1 — Initialization
# ---------------------------------------------------------------------------


def test_s1_returns_dict():
    s = pr37_schema.section1_initialization()
    assert isinstance(s, dict)


def test_s1_step_label():
    s = pr37_schema.section1_initialization()
    assert s["step"] == "initialization"


def test_s1_depends_on_pr36():
    s = pr37_schema.section1_initialization()
    assert "pr_36" in s["pr_37_depends_on"]


def test_s1_architectural_layers_count():
    s = pr37_schema.section1_initialization()
    assert len(s["architectural_layers"]) == 6


def test_s1_each_layer_has_required_fields():
    s = pr37_schema.section1_initialization()
    for layer in s["architectural_layers"]:
        assert "layer" in layer
        assert "name" in layer
        assert "pr" in layer


# ---------------------------------------------------------------------------
# Section 2 — Deterministic Execution Spec
# ---------------------------------------------------------------------------


def test_s2_returns_dict():
    s = pr37_schema.section2_deterministic_execution_spec()
    assert isinstance(s, dict)


def test_s2_step_label():
    s = pr37_schema.section2_deterministic_execution_spec()
    assert s["step"] == "deterministic_execution_spec"


def test_s2_ci_rejects_without_spec():
    s = pr37_schema.section2_deterministic_execution_spec()
    assert s["ci_rejects_without_spec"] is True


def test_s2_artifacts_is_dict():
    s = pr37_schema.section2_deterministic_execution_spec()
    assert isinstance(s["artifacts"], dict)
    assert len(s["artifacts"]) >= 1


def test_s2_execution_spec_yaml_exists():
    s = pr37_schema.section2_deterministic_execution_spec()
    assert s["canonical_runtime_version_lock"] != "NOT IMPLEMENTED"


def test_s2_determinism_guard_exists():
    s = pr37_schema.section2_deterministic_execution_spec()
    assert s["determinism_guard"] != "NOT IMPLEMENTED"


# ---------------------------------------------------------------------------
# Section 3 — Proof-Carrying Execution
# ---------------------------------------------------------------------------


def test_s3_returns_dict():
    s = pr37_schema.section3_proof_carrying_execution()
    assert isinstance(s, dict)


def test_s3_step_label():
    s = pr37_schema.section3_proof_carrying_execution()
    assert s["step"] == "proof_carrying_execution"


def test_s3_bundle_required_files():
    s = pr37_schema.section3_proof_carrying_execution()
    required = {"input.hash", "env.hash", "trace.hash", "output.hash", "merkle_root.hash", "verification.json"}
    assert required == set(s["bundle_required_files"])


def test_s3_verification_json_has_four_fields():
    s = pr37_schema.section3_proof_carrying_execution()
    assert len(s["verification_json_required_fields"]) == 4


def test_s3_no_output_valid_without_bundle():
    s = pr37_schema.section3_proof_carrying_execution()
    assert s["no_output_valid_without_bundle"] is True


# ---------------------------------------------------------------------------
# Section 4 — Cross-Node Verification
# ---------------------------------------------------------------------------


def test_s4_returns_dict():
    s = pr37_schema.section4_cross_node_verification()
    assert isinstance(s, dict)


def test_s4_step_label():
    s = pr37_schema.section4_cross_node_verification()
    assert s["step"] == "cross_node_verification_protocol"


def test_s4_minimum_nodes():
    s = pr37_schema.section4_cross_node_verification()
    assert s["minimum_nodes"] == 2


def test_s4_protocol_steps_count():
    s = pr37_schema.section4_cross_node_verification()
    assert len(s["protocol_steps"]) == 6


def test_s4_merge_blocked_until_verified():
    s = pr37_schema.section4_cross_node_verification()
    assert s["merge_blocked_until_verified"] is True


# ---------------------------------------------------------------------------
# Section 5 — Dual-Path Execution
# ---------------------------------------------------------------------------


def test_s5_returns_dict():
    s = pr37_schema.section5_dual_path_execution()
    assert isinstance(s, dict)


def test_s5_step_label():
    s = pr37_schema.section5_dual_path_execution()
    assert s["step"] == "dual_path_execution"


def test_s5_fast_path_not_authoritative():
    s = pr37_schema.section5_dual_path_execution()
    assert s["fast_path"]["authoritative"] is False


def test_s5_pure_path_authoritative():
    s = pr37_schema.section5_dual_path_execution()
    assert s["pure_path"]["authoritative"] is True


def test_s5_agreement_bitwise():
    s = pr37_schema.section5_dual_path_execution()
    assert s["agreement_requirement"] == "bitwise_identical"


def test_s5_speed_not_authoritative():
    s = pr37_schema.section5_dual_path_execution()
    assert s["speed_not_authoritative"] is True


# ---------------------------------------------------------------------------
# Section 6 — Yeshua Mathematics Layer
# ---------------------------------------------------------------------------


def test_s6_returns_dict():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert isinstance(s, dict)


def test_s6_step_label():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["step"] == "yeshua_mathematics_layer"


def test_s6_is_enforcement_layer():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["yml_is_enforcement_layer"] is True


def test_s6_peano_checker_exists():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["peano_arithmetic_invariants"]["checker"] != "NOT IMPLEMENTED"


def test_s6_boolean_validator_exists():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["boolean_logic_purity"]["validator"] != "NOT IMPLEMENTED"


def test_s6_arithmetic_core_c_exists():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["peano_arithmetic_invariants"]["arithmetic_core"] != "NOT IMPLEMENTED"


def test_s6_logic_engine_c_exists():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["boolean_logic_purity"]["logic_engine"] != "NOT IMPLEMENTED"


def test_s6_cross_validator_exists():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["pure_reference_runtime"]["cross_validator"] != "NOT IMPLEMENTED"


def test_s6_yeshua_standards_document_exists():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert s["yeshua_standards"]["document"] != "NOT IMPLEMENTED"


def test_s6_yeshua_standards_count():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    assert len(s["yeshua_standards"]["standards"]) == 7


def test_s6_pure_path_target_platforms():
    s = pr37_schema.section6_yeshua_mathematics_layer()
    platforms = s["pure_reference_runtime"]["target_platforms"]
    assert "x86" in platforms
    assert "ARM" in platforms


# ---------------------------------------------------------------------------
# Section 7 — Benchmark Harness
# ---------------------------------------------------------------------------


def test_s7_returns_dict():
    s = pr37_schema.section7_benchmark_harness()
    assert isinstance(s, dict)


def test_s7_step_label():
    s = pr37_schema.section7_benchmark_harness()
    assert s["step"] == "canonical_benchmark_harness"


def test_s7_harness_exists():
    s = pr37_schema.section7_benchmark_harness()
    assert s["harness"] != "NOT IMPLEMENTED"


# ---------------------------------------------------------------------------
# Section 9 — Zero-Trust Merge Gate
# ---------------------------------------------------------------------------


def test_s9_returns_dict():
    s = pr37_schema.section9_zero_trust_merge_gate()
    assert isinstance(s, dict)


def test_s9_step_label():
    s = pr37_schema.section9_zero_trust_merge_gate()
    assert s["step"] == "zero_trust_merge_gate"


def test_s9_pipeline_order_has_eight_steps():
    s = pr37_schema.section9_zero_trust_merge_gate()
    assert len(s["pipeline_order"]) == 8


def test_s9_merge_blocked_on_any_failure():
    s = pr37_schema.section9_zero_trust_merge_gate()
    assert s["merge_blocked_on_any_failure"] is True


# ---------------------------------------------------------------------------
# Section 10 — Halting Condition
# ---------------------------------------------------------------------------


def test_s10_returns_dict():
    s = pr37_schema.section10_halting_condition()
    assert isinstance(s, dict)


def test_s10_all_criteria_met():
    s = pr37_schema.section10_halting_condition()
    assert s["all_criteria_met"] is True


def test_s10_status_contains_complete():
    s = pr37_schema.section10_halting_condition()
    assert "COMPLETE" in s["status"]


def test_s10_criteria_is_dict():
    s = pr37_schema.section10_halting_condition()
    assert isinstance(s["criteria"], dict)
    assert len(s["criteria"]) == 10


def test_s10_all_individual_criteria_true():
    s = pr37_schema.section10_halting_condition()
    for k, v in s["criteria"].items():
        assert v is True, f"Halting criterion not met: {k!r}"


# ---------------------------------------------------------------------------
# write_schema_file — integration test
# ---------------------------------------------------------------------------


def test_write_schema_file_creates_file(tmp_path):
    out = tmp_path / "pr_37_schema_test.json"
    result_path = pr37_schema.write_schema_file(output_path=out)
    assert result_path == out
    assert out.exists()
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert parsed["pr_number"] == 37


def test_write_schema_file_is_valid_json(tmp_path):
    out = tmp_path / "pr_37_schema_test.json"
    pr37_schema.write_schema_file(output_path=out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# DVCL — Determinism Guard
# ---------------------------------------------------------------------------


def test_determinism_guard_returns_report():
    report = run_determinism_guard()
    assert report is not None
    assert hasattr(report, "all_passed")


def test_determinism_guard_to_dict():
    report = run_determinism_guard()
    d = report.to_dict()
    assert "all_passed" in d
    assert "violation_count" in d
    assert isinstance(d["violations"], list)
    assert isinstance(d["passed"], list)


def test_determinism_guard_to_json():
    report = run_determinism_guard()
    j = report.to_json()
    parsed = json.loads(j)
    assert "all_passed" in parsed


# ---------------------------------------------------------------------------
# DVCL — Benchmark Harness
# ---------------------------------------------------------------------------


def test_benchmark_harness_reproducible():
    def deterministic_eval(data: bytes) -> float:
        return float(len(data))  # exact; deterministic # exact

    result = run_benchmark(
        name="test_benchmark",
        dataset=b"canonical_test_dataset_v1",
        eval_fn=deterministic_eval,
    )
    assert result.reproducible is True
    assert result.valid is True


def test_benchmark_harness_to_dict():
    def eval_fn(data: bytes) -> float:
        return 1.0  # exact # exact

    result = run_benchmark(name="test", dataset=b"data", eval_fn=eval_fn)
    d = result.to_dict()
    assert "name" in d
    assert "dataset_hash" in d
    assert "reproducible" in d
    assert "valid" in d


# ---------------------------------------------------------------------------
# YML — Peano Invariant Checker
# ---------------------------------------------------------------------------


def test_peano_checker_returns_report():
    report = run_peano_invariant_checker()
    assert report is not None
    assert hasattr(report, "all_passed")


def test_peano_checker_to_dict():
    report = run_peano_invariant_checker()
    d = report.to_dict()
    assert "all_passed" in d
    assert "violation_count" in d


# ---------------------------------------------------------------------------
# YML — Boolean Purity Validator
# ---------------------------------------------------------------------------


def test_boolean_purity_returns_report():
    report = run_boolean_purity_validator()
    assert report is not None
    assert hasattr(report, "all_passed")


def test_boolean_purity_to_dict():
    report = run_boolean_purity_validator()
    d = report.to_dict()
    assert "all_passed" in d
    assert "violation_count" in d


def test_validate_truth_table_deterministic():
    def bool_and(a: bool, b: bool) -> bool:
        return a and b

    domain = [(False, False), (False, True), (True, False), (True, True)]
    passed, failures = validate_truth_table(bool_and, domain)
    assert passed is True
    assert failures == []


# ---------------------------------------------------------------------------
# YML — Pure Reference Runtime Cross-Validator
# ---------------------------------------------------------------------------


def test_cross_validation_returns_result():
    result = run_cross_validation()
    assert result is not None
    assert hasattr(result, "all_passed")


def test_cross_validation_all_passed():
    result = run_cross_validation()
    assert result.all_passed, f"Cross-validation failures: {result.failures}"


def test_cross_validation_to_dict():
    result = run_cross_validation()
    d = result.to_dict()
    assert "all_passed" in d
    assert "check_count" in d
    assert isinstance(d["checks"], list)


def test_cross_validation_runtime_files_exist():
    result = run_cross_validation()
    file_checks = [c for c in result.checks if c["name"].startswith("runtime_file_exists:")]
    assert len(file_checks) == 2
    for check in file_checks:
        assert check["passed"] is True, f"Runtime file missing: {check['name']}"


if __name__ == "__main__":
    import pytest as _pytest

    sys.exit(_pytest.main([__file__, "-v"]))
