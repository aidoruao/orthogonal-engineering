"""
Tests for PR #34 Audit Module — tests/test_pr34_audit.py

Validates that pr34_audit.run_audit() returns the expected structured
enumeration covering all 11 sections, with correct types and required keys.

Author: Orthogonal Engineering
PR: #34
Version: 1.0.0
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import pr34_audit


# ---------------------------------------------------------------------------
# Smoke test — full audit runs without exception
# ---------------------------------------------------------------------------

def test_run_audit_returns_dict():
    result = pr34_audit.run_audit()
    assert isinstance(result, dict)


def test_run_audit_has_sections():
    result = pr34_audit.run_audit()
    assert "sections" in result
    sections = result["sections"]
    expected_keys = {
        "1_materialization",
        "2_fractal",
        "3_omega",
        "4_q32",
        "5_canonicalization",
        "6_sat_halt",
        "7_ci",
        "8_external_claims",
        "9_security",
        "10_cross_platform",
        "11_completeness",
    }
    assert expected_keys == set(sections.keys())


# ---------------------------------------------------------------------------
# Section 1 — Repository Materialization State
# ---------------------------------------------------------------------------

def test_section1_materialization_keys():
    s = pr34_audit.section1_materialization()
    assert "1.1_total_files" in s
    assert "1.2_loc_by_language" in s
    assert "1.3_largest_file" in s
    assert "1.4_largest_directory" in s
    assert "1.5_git_pack_size_bytes" in s
    assert "1.6_claim_classification" in s


def test_section1_file_count_positive():
    s = pr34_audit.section1_materialization()
    assert s["1.1_total_files"] > 0


def test_section1_loc_by_language_is_dict():
    s = pr34_audit.section1_materialization()
    assert isinstance(s["1.2_loc_by_language"], dict)


def test_section1_largest_file_has_path_and_loc():
    s = pr34_audit.section1_materialization()
    lf = s["1.3_largest_file"]
    assert "path" in lf
    assert "loc" in lf
    assert lf["loc"] >= 0


def test_section1_claim_classification_mentions_topological():
    s = pr34_audit.section1_materialization()
    assert "TOPOLOGICAL" in s["1.6_claim_classification"].upper()


# ---------------------------------------------------------------------------
# Section 2 — Fractal Generator
# ---------------------------------------------------------------------------

def test_section2_fractal_keys():
    s = pr34_audit.section2_fractal()
    assert "2.1_location" in s
    assert "2.6_expansion_function_signature" in s


def test_section2_location_has_fractal_expander():
    s = pr34_audit.section2_fractal()
    loc = s["2.1_location"]
    assert "fractal_expander" in loc
    # The file should exist in this repo
    assert loc["fractal_expander"] != "NOT IMPLEMENTED"


def test_section2_expansion_type_not_empty():
    s = pr34_audit.section2_fractal()
    assert len(s["2.2_expansion_type"]) > 10


# ---------------------------------------------------------------------------
# Section 3 — Omega Invariant
# ---------------------------------------------------------------------------

def test_section3_omega_keys():
    s = pr34_audit.section3_omega()
    assert "3.1_graph_construction" in s
    assert "3.2_graph_type" in s
    assert "3.7_in_ci" in s


def test_section3_graph_construction_file_exists():
    s = pr34_audit.section3_omega()
    assert "NOT IMPLEMENTED" not in s["3.1_graph_construction"]["file"]


def test_section3_graph_is_directed():
    s = pr34_audit.section3_omega()
    assert "DIRECTED" in s["3.2_graph_type"].upper()


# ---------------------------------------------------------------------------
# Section 4 — Q32 Fixed-Point (NOT IMPLEMENTED)
# ---------------------------------------------------------------------------

def test_section4_q32_reports_not_implemented():
    s = pr34_audit.section4_q32()
    assert s["4.1_implementation_file"] == "NOT IMPLEMENTED"
    assert s["4.2_overflow_policy"] == "NOT IMPLEMENTED"


# ---------------------------------------------------------------------------
# Section 5 — Canonicalization & CAS
# ---------------------------------------------------------------------------

def test_section5_canonicalization_keys():
    s = pr34_audit.section5_canonicalization()
    assert "5.1_entrypoint" in s
    assert "5.2_hash_function" in s
    assert "5.4_merkle_construction" in s


def test_section5_hash_function_is_sha256():
    s = pr34_audit.section5_canonicalization()
    assert "SHA-256" in s["5.2_hash_function"].upper()


def test_section5_timestamps_excluded():
    s = pr34_audit.section5_canonicalization()
    assert "YES" in s["5.3_timestamps_excluded"].upper()


# ---------------------------------------------------------------------------
# Section 6 — SAT Guards & Halt Conditions
# ---------------------------------------------------------------------------

def test_section6_sat_solver_not_implemented():
    s = pr34_audit.section6_sat_halt()
    assert "NOT IMPLEMENTED" in s["6.1_sat_solver"]


def test_section6_loop_guard_file_exists():
    s = pr34_audit.section6_sat_halt()
    assert "NOT IMPLEMENTED" not in s["6.4_loop_guard"]["file"]


def test_section6_halt_recovery_is_terminal():
    s = pr34_audit.section6_sat_halt()
    assert "TERMINAL" in s["6.6_halt_recovery"].upper()


# ---------------------------------------------------------------------------
# Section 7 — CI/CD Enforcement
# ---------------------------------------------------------------------------

def test_section7_workflows_list():
    s = pr34_audit.section7_ci()
    assert isinstance(s["7.1_workflows"], list)
    assert len(s["7.1_workflows"]) > 0


def test_section7_workflows_include_gate():
    s = pr34_audit.section7_ci()
    assert any("gate" in wf for wf in s["7.1_workflows"])


def test_section7_ci_computes_omega():
    s = pr34_audit.section7_ci()
    assert "YES" in s["7.2_ci_computes_omega"].upper()


# ---------------------------------------------------------------------------
# Section 8 — External Claim Tagging
# ---------------------------------------------------------------------------

def test_section8_external_claims_keys():
    s = pr34_audit.section8_external_claims()
    assert "8.1_external_claim_definition" in s
    assert "8.2_contract_validation" in s
    assert "8.3_validation_type" in s
    assert "8.4_rejection_log" in s


def test_section8_contract_validation_file_exists():
    s = pr34_audit.section8_external_claims()
    assert "NOT IMPLEMENTED" not in s["8.2_contract_validation"]["file"]


# ---------------------------------------------------------------------------
# Section 9 — Security Substrate
# ---------------------------------------------------------------------------

def test_section9_security_keys():
    s = pr34_audit.section9_security()
    assert "9.1_deterministic_firewall" in s
    assert "9.4_substrate_verifier" in s


def test_section9_substrate_verifier_not_implemented():
    s = pr34_audit.section9_security()
    assert s["9.4_substrate_verifier"] == "NOT IMPLEMENTED"


# ---------------------------------------------------------------------------
# Section 10 — Cross-Platform Determinism
# ---------------------------------------------------------------------------

def test_section10_os_matrix():
    s = pr34_audit.section10_cross_platform()
    matrix = s["10.1_os_matrix"]
    assert isinstance(matrix, list)
    assert "ubuntu-latest" in matrix
    assert "windows-latest" in matrix
    assert "macos-latest" in matrix


def test_section10_endianness_normalized():
    s = pr34_audit.section10_cross_platform()
    assert "YES" in s["10.3_endianness_normalization"].upper()


def test_section10_floating_point_excluded():
    s = pr34_audit.section10_cross_platform()
    assert "YES" in s["10.4_floating_point_exclusion"].upper()


# ---------------------------------------------------------------------------
# Section 11 — Enforcement Completeness
# ---------------------------------------------------------------------------

def test_section11_completeness_keys():
    s = pr34_audit.section11_completeness()
    assert "11.1_declared_not_enforced" in s
    assert "11.2_enforced_not_tested" in s
    assert "11.3_tested_not_ci_bound" in s


def test_section11_lists_are_lists():
    s = pr34_audit.section11_completeness()
    assert isinstance(s["11.1_declared_not_enforced"], list)
    assert isinstance(s["11.2_enforced_not_tested"], list)
    assert isinstance(s["11.3_tested_not_ci_bound"], list)


def test_section11_declared_not_enforced_mentions_q32():
    s = pr34_audit.section11_completeness()
    combined = " ".join(s["11.1_declared_not_enforced"])
    assert "Q32" in combined or "q32" in combined.lower()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_exists_helper_real_file():
    path = pr34_audit._exists("pr34_audit.py")
    assert path != "NOT IMPLEMENTED"
    assert path.endswith("pr34_audit.py")


def test_exists_helper_missing_file():
    path = pr34_audit._exists("definitely_not_a_real_file_xyz.py")
    assert path == "NOT IMPLEMENTED"


def test_count_lines_positive():
    p = pr34_audit.REPO_ROOT / "pr34_audit.py"
    count = pr34_audit._count_lines(p)
    assert count > 50


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
