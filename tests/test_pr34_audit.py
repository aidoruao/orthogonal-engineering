"""
Tests for PR #34 Audit Module v2 - tests/test_pr34_audit.py

Validates that pr34_audit.run_audit() returns the expected structured
enumeration covering all 11 sections x 10 questions each.

Author: Orthogonal Engineering
PR: #34
Version: 2.0.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import pr34_audit


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

def test_run_audit_returns_dict():
    result = pr34_audit.run_audit()
    assert isinstance(result, dict)


def test_run_audit_has_required_top_level_keys():
    result = pr34_audit.run_audit()
    assert "pr" in result
    assert "sections" in result
    assert "footer" in result
    assert result["footer"].startswith("ENUMERATION COMPLETE")


def test_run_audit_has_all_eleven_sections():
    result = pr34_audit.run_audit()
    sections = result["sections"]
    expected = {
        "1_materialization", "2_fractal", "3_omega", "4_q32",
        "5_canonicalization", "6_sat_halt", "7_ci", "8_external_claims",
        "9_security", "10_cross_platform", "11_completeness",
    }
    assert expected == set(sections.keys())


def test_all_sections_have_ten_keys():
    result = pr34_audit.run_audit()
    for key, sec in result["sections"].items():
        assert isinstance(sec, dict), f"Section {key} is not a dict"
        if key == "11_completeness":
            # Section 11 specifies exactly 3 lists (declared/enforced/tested)
            assert len(sec) == 3, f"Section {key} has {len(sec)} keys, expected 3"
        else:
            assert len(sec) == 10, f"Section {key} has {len(sec)} keys, expected 10"


def test_audit_is_json_serialisable():
    result = pr34_audit.run_audit()
    serialised = json.dumps(result)
    parsed = json.loads(serialised)
    assert parsed["pr"] == "34"


# ---------------------------------------------------------------------------
# Section 1 - Repository Materialization State
# ---------------------------------------------------------------------------

def test_s1_total_git_files_positive():
    s = pr34_audit.section1()
    assert s["1.1_total_git_tracked_files"] > 0


def test_s1_loc_by_language_is_dict():
    s = pr34_audit.section1()
    assert isinstance(s["1.2_loc_by_language"], dict)
    assert len(s["1.2_loc_by_language"]) > 0


def test_s1_largest_file_has_path_and_loc():
    s = pr34_audit.section1()
    lf = s["1.3_largest_file"]
    assert "path" in lf and "loc" in lf
    assert lf["loc"] >= 0


def test_s1_largest_dir_by_loc():
    s = pr34_audit.section1()
    ld = s["1.4_largest_directory_by_loc"]
    assert "path" in ld and "loc" in ld


def test_s1_pack_size_is_int():
    s = pr34_audit.section1()
    assert isinstance(s["1.5_git_objects_pack_size_bytes"], int)


def test_s1_generated_artifacts_is_list():
    s = pr34_audit.section1()
    assert isinstance(s["1.6_generated_artifacts_committed"], list)


def test_s1_binary_blobs_is_list():
    s = pr34_audit.section1()
    assert isinstance(s["1.7_binary_blobs_tracked"], list)
    # .pyc files are intentionally committed in this repo (confirmed by git ls-files)
    assert any(".pyc" in b for b in s["1.7_binary_blobs_tracked"])


def test_s1_vendored_lists_node_modules():
    s = pr34_audit.section1()
    vendors = s["1.8_vendored_third_party"]
    assert isinstance(vendors, list)
    assert any("node_modules" in v.get("path", "") for v in vendors)


def test_s1_submodules_field_present():
    s = pr34_audit.section1()
    assert "1.9_submodules" in s
    assert s["1.9_submodules"] == "NONE"  # No submodules in this repo


def test_s1_classification_is_partially_materialized():
    s = pr34_audit.section1()
    cls = s["1.10_repository_state_classification"]
    assert "PARTIALLY MATERIALIZED" in cls["code"]
    assert "justification" in cls


# ---------------------------------------------------------------------------
# Section 2 - Fractal Generator Reality
# ---------------------------------------------------------------------------

def test_s2_entrypoints_is_list():
    s = pr34_audit.section2()
    assert isinstance(s["2.1_fractal_entrypoints"], list)
    assert len(s["2.1_fractal_entrypoints"]) >= 3


def test_s2_generator_files_exist():
    s = pr34_audit.section2()
    files = s["2.2_fractal_generator_files"]
    assert files["fractal_expander"] != "NOT IMPLEMENTED"
    assert files["dag_generator"] != "NOT IMPLEMENTED"


def test_s2_function_names_is_list():
    s = pr34_audit.section2()
    assert isinstance(s["2.3_expansion_function_names"], list)
    assert len(s["2.3_expansion_function_names"]) >= 5


def test_s2_writes_to_disk_default_false():
    s = pr34_audit.section2()
    assert s["2.4_expansion_writes_to_disk"]["default"] is False


def test_s2_bounded_true():
    s = pr34_audit.section2()
    assert s["2.5_expansion_bounded"]["bounded"] is True


def test_s2_deterministic_true():
    s = pr34_audit.section2()
    assert s["2.6_expansion_deterministic"]["deterministic"] is True


def test_s2_tests_listed():
    s = pr34_audit.section2()
    assert len(s["2.7_expansion_tests"]) >= 2


def test_s2_no_floats():
    s = pr34_audit.section2()
    assert s["2.8_uses_floating_arithmetic"]["uses_floats"] is False


def test_s2_recursion_bounded():
    s = pr34_audit.section2()
    assert s["2.9_recursion_depth_bounded"]["bounded"] is True


def test_s2_state_serializable():
    s = pr34_audit.section2()
    assert s["2.10_generator_state_serializable"]["serializable"] is True


# ---------------------------------------------------------------------------
# Section 3 - Omega Invariant Enforcement
# ---------------------------------------------------------------------------

def test_s3_dag_generator_file_exists():
    s = pr34_audit.section3()
    assert "NOT IMPLEMENTED" not in s["3.1_omega_dag_generator"]["file"]


def test_s3_graph_type_directed():
    s = pr34_audit.section3()
    assert "DIRECTED" in s["3.2_graph_type"].upper()


def test_s3_acyclicity_enforced():
    s = pr34_audit.section3()
    assert s["3.3_acyclicity"]["enforced"] is True


def test_s3_validation_location_file_exists():
    s = pr34_audit.section3()
    assert "NOT IMPLEMENTED" not in s["3.4_invariant_validation_location"]["file"]


def test_s3_in_ci():
    s = pr34_audit.section3()
    assert s["3.5_invariant_in_ci"]["in_ci"] is True


def test_s3_unit_tested():
    s = pr34_audit.section3()
    assert s["3.6_invariant_unit_tested"]["unit_tested"] is True


def test_s3_property_tested_not_implemented():
    s = pr34_audit.section3()
    assert s["3.7_invariant_property_tested"]["property_tested"] is False


def test_s3_platform_independent():
    s = pr34_audit.section3()
    assert s["3.8_platform_dependent"]["platform_dependent"] is False


def test_s3_enforcement_scope_both():
    s = pr34_audit.section3()
    scope = s["3.9_enforcement_scope"].upper()
    assert "BOTH" in scope or ("RUNTIME" in scope and "TEST" in scope)


def test_s3_failure_modes_is_list():
    s = pr34_audit.section3()
    assert isinstance(s["3.10_failure_modes"], list)
    assert len(s["3.10_failure_modes"]) >= 3


# ---------------------------------------------------------------------------
# Section 4 - Q32 Fixed-Point Core
# ---------------------------------------------------------------------------

def test_s4_q32_not_implemented():
    s = pr34_audit.section4()
    assert s["4.2_q32_if_exists"] == "NOT IMPLEMENTED"
    assert s["4.3_q32_absent"] != ""


def test_s4_floats_not_in_core_pipeline():
    s = pr34_audit.section4()
    assert s["4.4_floats_in_model_evolution_pipeline"]["in_core_pipeline"] is False


def test_s4_numeric_determinism_tests_present():
    s = pr34_audit.section4()
    assert len(s["4.5_numeric_determinism_tests"]) >= 1


def test_s4_nearest_analogue_file_exists():
    s = pr34_audit.section4()
    assert "NOT IMPLEMENTED" not in s["4.6_nearest_analogue"]["file"]


# ---------------------------------------------------------------------------
# Section 5 - Canonicalization & CAS
# ---------------------------------------------------------------------------

def test_s5_hasher_file_exists():
    s = pr34_audit.section5()
    assert "NOT IMPLEMENTED" not in s["5.1_canonicalization_modules"]["hasher"]


def test_s5_hash_is_sha256():
    s = pr34_audit.section5()
    assert "SHA-256" in s["5.2_hash_algorithm"]["algorithm"]


def test_s5_timestamps_excluded():
    s = pr34_audit.section5()
    assert s["5.3_timestamps_excluded"]["excluded"] is True


def test_s5_orderings_normalised():
    s = pr34_audit.section5()
    assert s["5.4_file_orderings_normalised"]["normalised"] is True


def test_s5_cas_implemented():
    s = pr34_audit.section5()
    assert s["5.5_cas_implemented"]["implemented"] is True


def test_s5_merkle_file_exists():
    s = pr34_audit.section5()
    assert "NOT IMPLEMENTED" not in s["5.6_merkle_structures"]["file"]


def test_s5_collision_guards_not_implemented():
    s = pr34_audit.section5()
    assert s["5.7_hash_collision_guards"]["explicit_guard"] is False


def test_s5_forms_tested():
    s = pr34_audit.section5()
    assert s["5.8_canonical_forms_tested"]["tested"] is True
    assert len(s["5.8_canonical_forms_tested"]["test_files"]) >= 1


def test_s5_serialization_deterministic():
    s = pr34_audit.section5()
    assert s["5.9_serialization_deterministic"]["deterministic"] is True


def test_s5_ci_enforces_hash():
    s = pr34_audit.section5()
    assert s["5.10_ci_enforces_canonical_hash"]["enforced"] is True


# ---------------------------------------------------------------------------
# Section 6 - SAT Guards & Halt Conditions
# ---------------------------------------------------------------------------

def test_s6_sat_absent():
    s = pr34_audit.section6()
    assert "NOT IMPLEMENTED" in s["6.2_sat_absent"].upper() or "CONFIRMED" in s["6.2_sat_absent"].upper()


def test_s6_halt_file_exists():
    s = pr34_audit.section6()
    assert "NOT IMPLEMENTED" not in s["6.3_halt_condition_location"]["file"]


def test_s6_structurally_enforced():
    s = pr34_audit.section6()
    assert s["6.4_halt_structurally_enforced"]["structural"] is True


def test_s6_halt_tested():
    s = pr34_audit.section6()
    assert s["6.5_halt_tested"]["tested"] is True


def test_s6_loops_cannot_exceed():
    s = pr34_audit.section6()
    assert s["6.6_loops_can_exceed_bounds"]["can_exceed"] is False


def test_s6_no_wall_clock():
    s = pr34_audit.section6()
    assert s["6.9_wall_clock_dependent"]["wall_clock"] is False


def test_s6_halt_deterministic():
    s = pr34_audit.section6()
    assert s["6.10_halt_deterministic"]["deterministic"] is True


# ---------------------------------------------------------------------------
# Section 7 - CI/CD Enforcement
# ---------------------------------------------------------------------------

def test_s7_all_workflows_list():
    s = pr34_audit.section7()
    wf = s["7.1_all_workflows"]
    assert isinstance(wf, list) and len(wf) > 0


def test_s7_gate_in_workflows():
    s = pr34_audit.section7()
    assert any("gate" in w for w in s["7.1_all_workflows"])


def test_s7_on_pr_list():
    s = pr34_audit.section7()
    assert isinstance(s["7.2_workflows_on_pr"], list)


def test_s7_on_push_list():
    s = pr34_audit.section7()
    assert isinstance(s["7.3_workflows_on_push"], list)


def test_s7_cross_platform_list():
    s = pr34_audit.section7()
    cp = s["7.4_workflows_cross_platform"]
    assert isinstance(cp, list) and len(cp) >= 1


def test_s7_determinism_on_all_three_os():
    s = pr34_audit.section7()
    det = s["7.5_determinism_tested_on"]
    assert det["ubuntu"] is True
    assert det["macos"] is True
    assert det["windows"] is True


def test_s7_artifact_comparison_enforced():
    s = pr34_audit.section7()
    assert s["7.6_artifact_comparison_enforced"]["enforced"] is True


def test_s7_codeql_not_implemented():
    s = pr34_audit.section7()
    assert s["7.8_codeql_enabled"]["enabled"] is False


def test_s7_coverage_not_enforced():
    s = pr34_audit.section7()
    assert s["7.9_coverage_enforced"]["enforced"] is False


def test_s7_artifacts_archived():
    s = pr34_audit.section7()
    assert s["7.10_artifacts_archived"]["archived"] is True


# ---------------------------------------------------------------------------
# Section 8 - External Claim Tagging
# ---------------------------------------------------------------------------

def test_s8_boundary_enforcer_exists():
    s = pr34_audit.section8()
    assert "NOT IMPLEMENTED" not in s["8.1_boundary_enforcement_modules"]["boundary_enforcer"]


def test_s8_schema_validated():
    s = pr34_audit.section8()
    assert s["8.2_external_input_schema_validated"]["validated"] is True


def test_s8_pii_scrubbed():
    s = pr34_audit.section8()
    assert s["8.3_pii_scrubbed"]["scrubbed"] is True
    assert len(s["8.3_pii_scrubbed"]["files"]) >= 1


def test_s8_injection_detection_present():
    s = pr34_audit.section8()
    assert s["8.4_injection_detection"]["present"] is True


def test_s8_claims_tagged():
    s = pr34_audit.section8()
    assert s["8.5_external_claims_tagged"]["tagged"] is True


def test_s8_malformed_rejected():
    s = pr34_audit.section8()
    assert s["8.7_malformed_inputs_rejected"]["rejected"] is True


def test_s8_error_taxonomy_present():
    s = pr34_audit.section8()
    assert s["8.8_structured_error_taxonomy"]["present"] is True
    assert len(s["8.8_structured_error_taxonomy"]["classes"]) >= 2


def test_s8_violations_logged():
    s = pr34_audit.section8()
    assert s["8.9_violations_logged"]["logged"] is True


def test_s8_boundary_rules_tested():
    s = pr34_audit.section8()
    assert s["8.10_boundary_rules_tested"]["tested"] is True


# ---------------------------------------------------------------------------
# Section 9 - Security Substrate
# ---------------------------------------------------------------------------

def test_s9_input_guards_listed():
    s = pr34_audit.section9()
    guards = s["9.1_input_guards"]
    assert len(guards["files"]) >= 1
    assert len(guards["mechanisms"]) >= 1


def test_s9_sanitization_files():
    s = pr34_audit.section9()
    assert len(s["9.2_sanitization_logic"]["files"]) >= 1


def test_s9_safe_deserializers():
    s = pr34_audit.section9()
    mechs = s["9.3_deserialization_logic"]["mechanisms"]
    assert any("safe_load" in m for m in mechs)


def test_s9_unsafe_exec_detected():
    s = pr34_audit.section9()
    assert s["9.4_unsafe_eval_exec"]["present"] is True
    assert len(s["9.4_unsafe_eval_exec"]["exec_files"]) >= 1


def test_s9_no_hardcoded_secrets():
    s = pr34_audit.section9()
    assert s["9.6_secrets_in_repo"]["hardcoded_secrets_found"] is False


def test_s9_deps_not_pinned():
    s = pr34_audit.section9()
    assert s["9.7_dependency_versions_pinned"]["pinned"] is False


def test_s9_sbom_not_implemented():
    s = pr34_audit.section9()
    assert s["9.8_sbom_generation"] == "NOT IMPLEMENTED"


def test_s9_security_scanning_not_implemented():
    s = pr34_audit.section9()
    assert "NOT IMPLEMENTED" in s["9.9_static_security_scanning"]


def test_s9_security_ci_not_blocking():
    s = pr34_audit.section9()
    assert "NOT IMPLEMENTED" in s["9.10_security_ci_blocking"]


# ---------------------------------------------------------------------------
# Section 10 - Cross-Platform Determinism
# ---------------------------------------------------------------------------

def test_s10_os_matrix_all_three():
    s = pr34_audit.section10()
    matrix = s["10.1_os_matrix"]
    assert "ubuntu-latest" in matrix
    assert "macos-latest" in matrix
    assert "windows-latest" in matrix


def test_s10_integer_normalised():
    s = pr34_audit.section10()
    assert s["10.2_integer_width_normalised"]["normalised"] is True


def test_s10_endianness_handled():
    s = pr34_audit.section10()
    assert s["10.3_endianness_handled"]["handled"] is True


def test_s10_floats_prohibited():
    s = pr34_audit.section10()
    assert s["10.4_floats_prohibited"]["prohibited"] is True


def test_s10_hashes_identical_across_os():
    s = pr34_audit.section10()
    assert s["10.5_hash_outputs_identical_across_os"]["verified"] is True


def test_s10_orderings_normalised():
    s = pr34_audit.section10()
    assert s["10.6_file_orderings_normalised"]["normalised"] is True


def test_s10_path_separators():
    s = pr34_audit.section10()
    assert s["10.7_path_separators_normalised"]["normalised"] is True


def test_s10_locale_enforced():
    s = pr34_audit.section10()
    assert s["10.8_locale_enforced"]["enforced"] is True


def test_s10_timezone_normalised():
    s = pr34_audit.section10()
    assert s["10.9_timezone_normalised"]["normalised"] is True


def test_s10_proof_artifacts_listed():
    s = pr34_audit.section10()
    arts = s["10.10_proof_artifacts"]
    assert "ci_artifact_names" in arts
    # 3 OS x 2 Python versions = 6 CI artifact names
    assert len(arts["ci_artifact_names"]) == 3 * 2


# ---------------------------------------------------------------------------
# Section 11 - Enforcement Completeness Matrix
# ---------------------------------------------------------------------------

def test_s11_all_three_lists():
    s = pr34_audit.section11()
    assert isinstance(s["11.1_declared_not_enforced"], list)
    assert isinstance(s["11.2_enforced_not_tested"], list)
    assert isinstance(s["11.3_tested_not_ci_bound"], list)


def test_s11_declared_items_have_required_fields():
    s = pr34_audit.section11()
    for item in s["11.1_declared_not_enforced"]:
        assert "invariant" in item
        assert "file_path" in item
        assert "function" in item
        assert "evidence" in item


def test_s11_enforced_items_have_required_fields():
    s = pr34_audit.section11()
    for item in s["11.2_enforced_not_tested"]:
        assert "invariant" in item
        assert "file_path" in item
        assert "function" in item
        assert "evidence" in item


def test_s11_ci_bound_items_have_required_fields():
    s = pr34_audit.section11()
    for item in s["11.3_tested_not_ci_bound"]:
        assert "invariant" in item
        assert "file_path" in item
        assert "function" in item
        assert "evidence" in item


def test_s11_q32_in_declared_not_enforced():
    s = pr34_audit.section11()
    names = [i["invariant"] for i in s["11.1_declared_not_enforced"]]
    assert any("Q32" in n or "q32" in n.lower() for n in names)


def test_s11_halt_in_tested_not_ci_bound():
    s = pr34_audit.section11()
    names = [i["invariant"].lower() for i in s["11.3_tested_not_ci_bound"]]
    assert any("halt" in n for n in names)


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

def test_exists_real_file():
    p = pr34_audit._exists("pr34_audit.py")
    assert p != "NOT IMPLEMENTED"
    assert p.endswith("pr34_audit.py")


def test_exists_missing_file():
    p = pr34_audit._exists("_definitely_not_here_xyz.py")
    assert p == "NOT IMPLEMENTED"


def test_count_lines_positive():
    p = pr34_audit.REPO_ROOT / "pr34_audit.py"
    count = pr34_audit._count_lines(p)
    assert count > 100


def test_git_ls_files_returns_list():
    files = pr34_audit._git_ls_files()
    assert isinstance(files, list) and len(files) > 100


if __name__ == "__main__":
    import pytest as _pytest
    sys.exit(_pytest.main([__file__, "-v"]))
