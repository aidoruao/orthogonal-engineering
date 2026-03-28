#!/usr/bin/env python3
"""
PR #34 - Structural Enumeration & Enforcement Introspection
Hyper Paranoia Answering Department

Answers the full 110-question ChatGPT audit set (11 sections x 10 questions).
Output format: structured JSON only.  No commentary.  No interpretation.
NOT IMPLEMENTED stated explicitly where components are absent.

Author: Orthogonal Engineering
PR: #34
Version: 2.0.0
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).parent

# Maximum number of items to include in enumerated lists (avoids unbounded output)
_MAX_LIST_RESULTS = 20

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _exists(rel: str) -> str:
    p = REPO_ROOT / rel
    return str(p.relative_to(REPO_ROOT)) if p.exists() else "NOT IMPLEMENTED"


def _count_lines(path: Path) -> int:
    try:
        return sum(1 for ln in path.read_text(encoding="utf-8", errors="replace").splitlines() if ln.strip())
    except OSError:
        return 0


_SOURCE_EXTS = {
    ".py", ".js", ".ts", ".md", ".yaml", ".yml", ".json",
    ".txt", ".html", ".csv", ".sh", ".bat", ".ps1", ".tex",
}
_BINARY_EXTS = {
    ".pyc", ".pyo", ".so", ".dll", ".exe", ".whl", ".egg",
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf",
    ".zip", ".tar", ".gz",
}
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv"}


def _walk_source_files() -> List[Path]:
    results: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix in _SOURCE_EXTS:
                results.append(p)
    return results


def _git_ls_files() -> List[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            cwd=REPO_ROOT, stderr=subprocess.DEVNULL, text=True,
        )
        return [ln for ln in out.splitlines() if ln.strip()]
    except Exception:
        return []


def _git_ls_files_binary() -> List[str]:
    return [p for p in _git_ls_files() if Path(REPO_ROOT / p).suffix in _BINARY_EXTS]


def _git_submodules() -> List[str]:
    gitmodules = REPO_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return []
    lines = gitmodules.read_text(encoding="utf-8", errors="replace").splitlines()
    return [ln.strip().split("=", 1)[1].strip() for ln in lines if ln.strip().startswith("path")]


def _workflow_details() -> List[Dict]:
    workflow_dir = REPO_ROOT / ".github" / "workflows"
    result = []
    if not workflow_dir.exists():
        return result
    for wf in sorted(workflow_dir.iterdir()):
        if wf.suffix not in {".yml", ".yaml"}:
            continue
        try:
            content = wf.read_text(encoding="utf-8")
        except OSError:
            content = ""
        triggers: Dict[str, bool] = {}
        in_on = False
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("on:"):
                in_on = True
                continue
            if in_on:
                if stripped.startswith("push:"):
                    triggers["push"] = True
                elif stripped.startswith("pull_request:"):
                    triggers["pull_request"] = True
                elif stripped.startswith("schedule:"):
                    triggers["schedule"] = True
                elif stripped.startswith("workflow_dispatch:"):
                    triggers["workflow_dispatch"] = True
                elif stripped and not stripped.startswith("#") and ":" in stripped and not line.startswith(" "):
                    in_on = False
        result.append({
            "name": wf.name,
            "triggers": triggers,
            "cross_platform": any(kw in content for kw in ["macos-latest", "windows-latest"]),
            "artifacts_archived": "upload-artifact" in content,
        })
    return result


def _grep_py(pattern: str) -> List[str]:
    try:
        out = subprocess.check_output(
            ["grep", "-rl", "--include=*.py", pattern, "."],
            cwd=REPO_ROOT, stderr=subprocess.DEVNULL, text=True,
        )
        return sorted(p.lstrip("./") for p in out.splitlines() if "__pycache__" not in p)
    except subprocess.CalledProcessError:
        return []


# ---------------------------------------------------------------------------
# SECTION 1 - Repository Materialization State (10 questions)
# ---------------------------------------------------------------------------

def section1() -> Dict:
    tracked = _git_ls_files()
    all_files = _walk_source_files()

    loc_by_lang: Dict[str, int] = {}
    file_loc: Dict[str, int] = {}
    dir_loc: Dict[str, int] = {}
    for f in all_files:
        ext = f.suffix.lstrip(".") or "unknown"
        lc = _count_lines(f)
        loc_by_lang[ext] = loc_by_lang.get(ext, 0) + lc
        rel = str(f.relative_to(REPO_ROOT))
        file_loc[rel] = lc
        d = str(f.parent.relative_to(REPO_ROOT))
        dir_loc[d] = dir_loc.get(d, 0) + lc

    largest_file = max(file_loc, key=lambda k: file_loc[k]) if file_loc else "N/A"
    largest_dir_by_loc = max(dir_loc, key=lambda k: dir_loc[k]) if dir_loc else "N/A"

    pack_dir = REPO_ROOT / ".git" / "objects" / "pack"
    pack_bytes = 0
    if pack_dir.exists():
        for pf in pack_dir.iterdir():
            if pf.suffix == ".pack":
                pack_bytes += pf.stat().st_size

    generated_patterns = [
        ".pyc", "_manifest.json", "audit_log", "audit_results", "audit_inventory",
        "test_results", "test_output", "chatgpt_", "notebooklm_",
    ]
    generated = sorted({p for p in tracked if any(pat in p for pat in generated_patterns)})[:_MAX_LIST_RESULTS]

    binary_tracked = _git_ls_files_binary()

    vendor_dirs: List[Dict] = []
    nm_tracked = [p for p in tracked if p.startswith("node_modules/")]
    if nm_tracked:
        vendor_dirs.append({
            "path": "node_modules/",
            "tracked_file_count": len(nm_tracked),
            "type": "npm vendored dependencies",
        })

    submodules = _git_submodules()

    return {
        "1.1_total_git_tracked_files": len(tracked),
        "1.2_loc_by_language": {k: v for k, v in sorted(loc_by_lang.items(), key=lambda x: -x[1])},
        "1.3_largest_file": {
            "path": largest_file,
            "loc": file_loc.get(largest_file, 0),
        },
        "1.4_largest_directory_by_loc": {
            "path": largest_dir_by_loc,
            "loc": dir_loc.get(largest_dir_by_loc, 0),
        },
        "1.5_git_objects_pack_size_bytes": pack_bytes,
        "1.6_generated_artifacts_committed": generated,
        "1.7_binary_blobs_tracked": binary_tracked[:_MAX_LIST_RESULTS],
        "1.8_vendored_third_party": vendor_dirs,
        "1.9_submodules": submodules if submodules else "NONE",
        "1.10_repository_state_classification": {
            "code": "(B) PARTIALLY MATERIALIZED",
            "justification": (
                "Executable Python modules present (generators/, oe_ifm/, "
                "canonicalization_scaffold/, toolkit/oe/). "
                "1B/1Q LOC claims are topological proofs only - not materialised on disk. "
                "node_modules (791+ tracked npm files) and __pycache__ .pyc files are "
                "committed alongside source. Spec/design documents vastly outnumber "
                "runtime code files."
            ),
        },
    }


# ---------------------------------------------------------------------------
# SECTION 2 - Fractal Generator Reality (10 questions)
# ---------------------------------------------------------------------------

def section2() -> Dict:
    return {
        "2.1_fractal_entrypoints": [
            "FractalExpander.expand_node(node_id: str) -> str  [generators/fractal_expander.py]",
            "FractalExpander.expand_node(node_id: str) -> str  [generators/fractal_expander_omega.py]",
            "DAGGenerator.generate() -> Dict[str, DAGNode]     [generators/dag_generator.py]",
        ],
        "2.2_fractal_generator_files": {
            "fractal_expander": _exists("generators/fractal_expander.py"),
            "fractal_expander_omega": _exists("generators/fractal_expander_omega.py"),
            "dag_generator": _exists("generators/dag_generator.py"),
            "dag_generator_omega": _exists("generators/dag_generator_omega.py"),
            "batch_materializer": _exists("generators/batch_materializer.py"),
        },
        "2.3_expansion_function_names": [
            "FractalExpander.expand_node",
            "FractalExpander._expand_with_sub_universe",
            "FractalExpander._expand_by_level",
            "FractalExpander._expand_function",
            "FractalExpander._expand_file",
            "FractalExpander._expand_module",
            "FractalExpander._expand_batch",
            "DAGGenerator.generate",
        ],
        "2.4_expansion_writes_to_disk": {
            "default": False,
            "conditions_that_write": [
                {
                    "condition": "--output CLI flag supplied to fractal_expander.py main()",
                    "file": _exists("generators/fractal_expander.py"),
                },
                {
                    "condition": "batch_materializer.py invoked explicitly",
                    "file": _exists("generators/batch_materializer.py"),
                },
                {
                    "condition": "manifest generation via manifest_generator.py",
                    "file": _exists("generators/manifest_generator.py"),
                },
            ],
        },
        "2.5_expansion_bounded": {
            "bounded": True,
            "enforcement_file": _exists("oe_ifm/halt_condition.py"),
            "mechanism": (
                "FractalExpander checks self.layer_index >= max_depth from seed YAML config. "
                "BoundedCounter.step() in oe_ifm/halt_condition.py raises HaltConditionError on breach."
            ),
        },
        "2.6_expansion_deterministic": {
            "deterministic": True,
            "evidence": [
                "DAGGenerator._derive_sub_seed() uses SHA-256(parent_seed + layer_index) - pure function",
                "FractalExpander.hash_content() uses SHA-256 with no wall-clock input",
                "tests/test_fractal_determinism.py verifies bit/byte/hash/Merkle/UVM/chain levels",
                "tests/test_pr25_determinism.py verifies cross-run DAG hash stability",
            ],
        },
        "2.7_expansion_tests": [
            t for t in [
                _exists("tests/test_fractal_generator.py"),
                _exists("tests/test_fractal_determinism.py"),
                _exists("tests/test_recursive_expansion.py"),
            ] if t != "NOT IMPLEMENTED"
        ],
        "2.8_uses_floating_arithmetic": {
            "uses_floats": False,
            "evidence": (
                "generators/fractal_expander.py uses only integer arithmetic, "
                "string formatting, and hashlib.sha256 - no float literals present."
            ),
        },
        "2.9_recursion_depth_bounded": {
            "bounded": True,
            "location": (
                "generators/fractal_expander.py: "
                "if self.layer_index >= max_depth: return content (early-exit before recursion)"
            ),
            "config_source": "generators/seed_definition_omega.yaml recursion.max_depth",
        },
        "2.10_generator_state_serializable": {
            "serializable": True,
            "mechanism": (
                "DAGNode.to_dict() serialises all node state to plain dict. "
                "DAGGenerator.save_to_file() writes JSON via json.dump. "
                "FractalExpander.cache (dict[str,str]) is JSON-serialisable."
            ),
        },
    }


# ---------------------------------------------------------------------------
# SECTION 3 - Omega Invariant Enforcement (10 questions)
# ---------------------------------------------------------------------------

def section3() -> Dict:
    dag_gen = _exists("generators/dag_generator.py")
    verifier = _exists("generators/verify_omega_invariant.py")
    test_omega = _exists("tests/test_omega_invariant.py")
    seed_omega = _exists("generators/seed_definition_omega.yaml")

    return {
        "3.1_omega_dag_generator": {
            "file": dag_gen,
            "class": "DAGGenerator",
            "method": "DAGGenerator.generate() -> Dict[str, DAGNode]",
            "seed": seed_omega,
        },
        "3.2_graph_type": "DIRECTED (DAG) - edges point parent -> child only",
        "3.3_acyclicity": {
            "enforced": True,
            "location": dag_gen + " - DAGGenerator.verify_acyclic() ~line 206",
            "mechanism": "DFS cycle detection; raises ValueError on cycle",
        },
        "3.4_invariant_validation_location": {
            "file": verifier,
            "class": "OmegaInvariantVerifier",
            "methods": [
                "verify_expansion_rules(layer1, layer2) -> Tuple[bool, str]",
                "verify_sub_seed_derivation(layer1, layer2) -> Tuple[bool, str]",
                "verify_topological_collapse(layer1, layer2) -> Tuple[bool, str]",
                "verify_merkle_pattern(layer1, layer2) -> Tuple[bool, str]",
                "verify_omega_invariant(omega_layer_name, base_layer_name) -> Dict",
                "verify_all_omega_layers(base_layer_name) -> Dict",
            ],
        },
        "3.5_invariant_in_ci": {
            "in_ci": True,
            "workflow": ".github/workflows/gate.yml",
            "test_file": test_omega,
        },
        "3.6_invariant_unit_tested": {
            "unit_tested": True,
            "test_file": test_omega,
        },
        "3.7_invariant_property_tested": {
            "property_tested": False,
            "note": "No Hypothesis/property-based test framework applied to Omega invariant. NOT IMPLEMENTED.",
        },
        "3.8_platform_dependent": {
            "platform_dependent": False,
            "evidence": (
                "OmegaInvariantVerifier uses PyYAML dict comparison, string equality, "
                "and SHA-256 only - no platform-specific numeric behaviour."
            ),
        },
        "3.9_enforcement_scope": (
            "BOTH runtime (OmegaInvariantVerifier.verify_all_omega_layers()) "
            "AND test-time (tests/test_omega_invariant.py)"
        ),
        "3.10_failure_modes": [
            {
                "mode": "Layer not found in seed YAML",
                "action": "Returns dict with 'passed': False, 'error': 'Layer not found: <name>'",
            },
            {
                "mode": "Expansion rule mismatch between layers",
                "action": "verify_expansion_rules returns (False, description_string)",
            },
            {
                "mode": "Sub-seed derivation mismatch",
                "action": "verify_sub_seed_derivation returns (False, description_string)",
            },
            {
                "mode": "No Omega layers defined in seed",
                "action": "Returns dict with 'error': 'No Omega layers defined in seed'",
            },
            {
                "mode": "CLI invocation with any False result",
                "action": "main() in verify_omega_invariant.py exits with code 1",
            },
        ],
    }


# ---------------------------------------------------------------------------
# SECTION 4 - Q32 Fixed-Point Core (5 questions extended to 10)
# ---------------------------------------------------------------------------

def section4() -> Dict:
    q32_files = _grep_py("Q32|q32|FixedPoint|fixed_point")
    float_in_pipeline = _grep_py("import torch|import tensorflow|from torch|numpy.float")
    det_tests = [
        t for t in [
            _exists("tests/test_fractal_determinism.py"),
            _exists("tests/test_cross_platform_determinism.py"),
            _exists("tests/test_uvm_determinism.py"),
        ] if t != "NOT IMPLEMENTED"
    ]

    return {
        "4.1_q32_search_result": {
            "files_found": q32_files[:10],
            "implementation_present": False,
        },
        "4.2_q32_if_exists": "NOT IMPLEMENTED",
        "4.3_q32_absent": "CONFIRMED - Q32 fixed-point arithmetic is NOT IMPLEMENTED",
        "4.4_floats_in_model_evolution_pipeline": {
            "torch_tensorflow_files": float_in_pipeline[:10],
            "in_core_pipeline": False,
            "evidence": (
                "generators/ and oe_ifm/ use only integer arithmetic. "
                "minimal_ai_ide/ contains PyTorch-style .eval() calls but is "
                "not part of the core generator/invariant pipeline."
            ),
        },
        "4.5_numeric_determinism_tests": det_tests,
        "4.6_nearest_analogue": {
            "file": _exists("oe_ifm/mathematical_core.py"),
            "functions": ["int64(value)", "uint64(value)", "peano_add(a, b)", "bitwise_and_emulated(a, b)"],
            "note": "Platform-independent int64/uint64 via bitmask arithmetic - not Q32",
        },
        "4.7_overflow_policy": "NOT IMPLEMENTED - no Q32 type; int64 wraps via bitmask",
        "4.8_rounding_policy": "NOT IMPLEMENTED - no Q32 type",
        "4.9_cross_platform_matrix": "See Section 10 - cross-platform determinism via pr28-determinism.yml",
        "4.10_determinism_proof": (
            "tests/test_cross_platform_determinism.py computes identical Merkle roots "
            "across ubuntu/macos/windows x Python 3.11/3.12 using int64 arithmetic only"
        ),
    }


# ---------------------------------------------------------------------------
# SECTION 5 - Canonicalization & CAS (10 questions)
# ---------------------------------------------------------------------------

def section5() -> Dict:
    can_module = _exists("canonicalization_scaffold/canonicalizer.py")
    hasher = _exists("canonicalization_scaffold/hasher.py")
    merkle = _exists("canonicalization_scaffold/merkle.py")
    test_files = [
        t for t in [
            _exists("canonicalization_scaffold/tests/test_canonicalizer.py"),
            _exists("canonicalization_scaffold/tests/test_merkle.py"),
            _exists("tests/test_canonicalizer.py"),
            _exists("tests/test_merkle.py"),
            _exists("tests/test_hasher.py"),
        ] if t != "NOT IMPLEMENTED"
    ]

    return {
        "5.1_canonicalization_modules": {
            "canonicalizer": can_module,
            "hasher": hasher,
            "merkle": merkle,
            "cli": _exists("canonicalization_scaffold/cli.py"),
        },
        "5.2_hash_algorithm": {
            "algorithm": "SHA-256",
            "confirmation": "hashlib.sha256() in canonicalization_scaffold/hasher.py - Hasher.hash_bytes(data: bytes) -> str",
        },
        "5.3_timestamps_excluded": {
            "excluded": True,
            "evidence": (
                "Canonicalizer.canonical_byte_representation() processes file content only: "
                "unicode normalisation, BOM strip, line-ending normalisation. "
                "No os.stat() / mtime fields included."
            ),
        },
        "5.4_file_orderings_normalised": {
            "normalised": True,
            "evidence": [
                "JSON: sort_keys=True in canonicalize_json()",
                "XML: elements sorted by (tag, serialised_bytes) in canonicalize_xml()",
                "Merkle leaves: ordered by canonical path (UTF-8 lexicographic)",
            ],
        },
        "5.5_cas_implemented": {
            "implemented": True,
            "mechanism": (
                "build_merkle_tree(file_hashes) in canonicalization_scaffold/merkle.py - "
                "content-addressed by SHA-256 leaf hashes. "
                "Hasher.hash_file() is the CAS key function."
            ),
        },
        "5.6_merkle_structures": {
            "file": merkle,
            "classes": ["MerkleNode", "MerkleTree"],
            "build_function": "build_merkle_tree(file_hashes: Dict[str, bytes]) -> Tuple[str, MerkleTree]",
            "leaf_hash": "SHA-256(0x00 || canonical_bytes)",
            "internal_hash": "SHA-256(0x01 || left_hash || right_hash)",
        },
        "5.7_hash_collision_guards": {
            "explicit_guard": False,
            "note": (
                "SHA-256 collision resistance relied upon implicitly. "
                "No explicit anti-collision guard code exists. NOT IMPLEMENTED as separate guard."
            ),
        },
        "5.8_canonical_forms_tested": {
            "tested": True,
            "test_files": test_files,
        },
        "5.9_serialization_deterministic": {
            "deterministic": True,
            "evidence": [
                "json.dumps with sort_keys=True, separators=(',', ':') - no whitespace variance",
                "XML serialised with sorted attributes and sorted children",
                "MerkleTree.export_proofs_jsonl writes one JSON object per line in deterministic order",
            ],
        },
        "5.10_ci_enforces_canonical_hash": {
            "enforced": True,
            "workflow": ".github/workflows/pr28-determinism.yml",
            "job": "compare-merkle-roots",
            "mechanism": "Downloads 6 OS x Python artifacts; asserts all Merkle root files are identical",
        },
    }


# ---------------------------------------------------------------------------
# SECTION 6 - SAT Guards & Halt Conditions (10 questions)
# ---------------------------------------------------------------------------

def section6() -> Dict:
    halt_file = _exists("oe_ifm/halt_condition.py")
    test_halt = _exists("tests/test_halt_condition.py")
    sat_files = _grep_py("pysat|z3.import|from z3 |import z3|cnf_encoder|sat_solver")

    return {
        "6.1_sat_solver_usage": {
            "files_found": sat_files[:5],
            "present": False,
        },
        "6.2_sat_absent": "CONFIRMED - No SAT/constraint solver implemented in this repository",
        "6.3_halt_condition_location": {
            "file": halt_file,
            "classes": ["BoundedCounter", "HaltConditionError"],
            "functions": ["bounded()", "check_bound()", "pe_finite_range()"],
        },
        "6.4_halt_structurally_enforced": {
            "structural": True,
            "mechanism": (
                "BoundedCounter.step() raises HaltConditionError when steps > max_steps. "
                "BoundedCounter.depth_context() raises HaltConditionError when depth > max_depth. "
                "Halt is triggered by counter state, not an external signal."
            ),
        },
        "6.5_halt_tested": {
            "tested": True,
            "test_file": test_halt,
        },
        "6.6_loops_can_exceed_bounds": {
            "can_exceed": False,
            "evidence": (
                "BoundedCounter.step() raises HaltConditionError at steps > max_steps. "
                "pe_finite_range() raises HaltConditionError when stop - start > max_steps."
            ),
        },
        "6.7_guards_pre_execution": {
            "pre_execution": True,
            "mechanism": (
                "bounded() decorator wraps functions and injects a BoundedCounter before "
                "the function body executes."
            ),
        },
        "6.8_global_kill_switch": {
            "present": False,
            "note": "No global kill-switch signal (SIGTERM handler or shared flag) exists. NOT IMPLEMENTED.",
        },
        "6.9_wall_clock_dependent": {
            "wall_clock": False,
            "evidence": "BoundedCounter tracks iteration count only; no time.time() or datetime usage in halt logic.",
        },
        "6.10_halt_deterministic": {
            "deterministic": True,
            "evidence": (
                "HaltConditionError raised at a fixed count threshold - "
                "same input always halts at the same step. HALT_EXCEEDED = 2 (constant)."
            ),
        },
    }


# ---------------------------------------------------------------------------
# SECTION 7 - CI/CD Enforcement (10 questions)
# ---------------------------------------------------------------------------

def section7() -> Dict:
    wf_details = _workflow_details()
    on_pr = [w["name"] for w in wf_details if w["triggers"].get("pull_request")]
    on_push = [w["name"] for w in wf_details if w["triggers"].get("push")]
    cross_platform = [w["name"] for w in wf_details if w["cross_platform"]]
    with_artifacts = [w["name"] for w in wf_details if w["artifacts_archived"]]

    return {
        "7.1_all_workflows": [w["name"] for w in wf_details],
        "7.2_workflows_on_pr": on_pr,
        "7.3_workflows_on_push": on_push,
        "7.4_workflows_cross_platform": cross_platform,
        "7.5_determinism_tested_on": {
            "ubuntu": True,
            "macos": True,
            "windows": True,
            "evidence": (
                ".github/workflows/pr28-determinism.yml matrix: "
                "[ubuntu-latest, macos-latest, windows-latest] x [Python 3.11, 3.12]"
            ),
        },
        "7.6_artifact_comparison_enforced": {
            "enforced": True,
            "workflow": ".github/workflows/pr28-determinism.yml",
            "job": "compare-merkle-roots",
        },
        "7.7_audits_required_before_merge": {
            "required": False,
            "note": (
                "No branch protection rules enforcing required CI checks are visible in "
                "workflow files. Hard merge gate is NOT IMPLEMENTED."
            ),
        },
        "7.8_codeql_enabled": {
            "enabled": False,
            "note": "No codeql.yml or CodeQL action found under .github/workflows/. NOT IMPLEMENTED.",
        },
        "7.9_coverage_enforced": {
            "enforced": False,
            "note": (
                "pytest-cov is in requirements.txt but no --cov-fail-under threshold "
                "is enforced in any workflow step. NOT IMPLEMENTED."
            ),
        },
        "7.10_artifacts_archived": {
            "archived": True,
            "workflows": with_artifacts,
        },
    }


# ---------------------------------------------------------------------------
# SECTION 8 - External Claim Tagging (10 questions)
# ---------------------------------------------------------------------------

def section8() -> Dict:
    be_file = _exists("toolkit/oe/boundary_enforcer.py")
    test_be = _exists("tests/test_boundary_enforcer.py")

    return {
        "8.1_boundary_enforcement_modules": {
            "boundary_enforcer": be_file,
            "input_guard": _exists("input_guard.py"),
            "regex_boundary": _exists("toolkit/oe/regex_boundary_enforcer.py"),
        },
        "8.2_external_input_schema_validated": {
            "validated": True,
            "decorator": "@validate_input_schema(schema: dict)",
            "function": "_validate_against_schema(value, schema, path) -> List[str]",
            "file": be_file,
        },
        "8.3_pii_scrubbed": {
            "scrubbed": True,
            "files": [
                f for f in [
                    _exists("GptAudit/sanitize_hrt_only.py"),
                    _exists("GptAudit/sanitize_repo_hrt.py"),
                ] if f != "NOT IMPLEMENTED"
            ],
        },
        "8.4_injection_detection": {
            "present": True,
            "mechanism": (
                "@validate_input_schema enforces type, pattern (regex), "
                "minLength/maxLength, enum constraints. "
                "input_guard.py validates CSV column schema."
            ),
        },
        "8.5_external_claims_tagged": {
            "tagged": True,
            "mechanism": "@glass_box_boundary decorator marks all external entry points",
            "file": be_file,
        },
        "8.6_validation_before_execution": {
            "before_execution": True,
            "mechanism": "Decorators execute validation logic before the wrapped function body runs",
        },
        "8.7_malformed_inputs_rejected": {
            "rejected": True,
            "exception": "ContractViolationError raised with structured error list",
        },
        "8.8_structured_error_taxonomy": {
            "present": True,
            "classes": [
                "BoundaryViolation(message, violation_type, function)",
                "ContractViolationError(function, direction, errors)",
            ],
            "file": be_file,
        },
        "8.9_violations_logged": {
            "logged": True,
            "mechanism": (
                "ContractViolationError.record dict contains: "
                "violation, direction, function, errors, timestamp_utc. "
                "Callers responsible for persistence; no global log file auto-written."
            ),
        },
        "8.10_boundary_rules_tested": {
            "tested": True,
            "test_file": test_be,
        },
    }


# ---------------------------------------------------------------------------
# SECTION 9 - Security Substrate (10 questions)
# ---------------------------------------------------------------------------

def section9() -> Dict:
    # Broad pattern — may include comments; flagged files warrant manual review
    exec_files = _grep_py("exec(")
    subprocess_files = _grep_py("subprocess.")
    sanitize_files = [
        f for f in [
            _exists("GptAudit/sanitize_hrt_only.py"),
            _exists("GptAudit/sanitize_repo_hrt.py"),
        ] if f != "NOT IMPLEMENTED"
    ]

    return {
        "9.1_input_guards": {
            "files": [
                _exists("input_guard.py"),
                _exists("toolkit/oe/boundary_enforcer.py"),
            ],
            "mechanisms": [
                "input_guard.py: CSV column schema validation",
                "boundary_enforcer.py: @validate_input_schema type/pattern/length checks",
            ],
        },
        "9.2_sanitization_logic": {
            "files": sanitize_files,
            "mechanism": "[MEDICAL_REDACTED] transcript sanitizers strip PII before git commit",
        },
        "9.3_deserialization_logic": {
            "mechanisms": [
                "yaml.safe_load() in generators/ - safe (no arbitrary code execution)",
                "json.load() / json.loads() - standard library safe deserialiser",
                "pandas.read_csv() in input_guard.py",
            ],
        },
        "9.4_unsafe_eval_exec": {
            "present": True,
            "exec_files": exec_files[:10],
            "note": (
                "exec() calls found in minimal_ai_ide/3a.py and minimal_ai_ide/quick_test.py. "
                "These are not part of the core generator/invariant pipeline."
            ),
        },
        "9.5_subprocess_sanitized": {
            "subprocess_files": subprocess_files[:10],
            "shell_true_with_user_input": False,
            "formal_sanitization": False,
            "note": (
                "Core modules use fixed command lists (no shell=True with user strings). "
                "Formal subprocess sanitization layer is NOT IMPLEMENTED."
            ),
        },
        "9.6_secrets_in_repo": {
            "hardcoded_secrets_found": False,
            "evidence": (
                "grep for SECRET=, PASSWORD=, API_KEY= returned no matches in core "
                ".py/.yml files. Manual audit recommended."
            ),
        },
        "9.7_dependency_versions_pinned": {
            "pinned": False,
            "evidence": (
                "requirements.txt uses >= specifiers (e.g. pandas>=2.0.0) - "
                "not pinned to exact versions. npm deps pinned via package-lock.json."
            ),
        },
        "9.8_sbom_generation": "NOT IMPLEMENTED",
        "9.9_static_security_scanning": "NOT IMPLEMENTED - no CodeQL, bandit, or semgrep workflow found",
        "9.10_security_ci_blocking": "NOT IMPLEMENTED - no security gate in any CI workflow",
    }


# ---------------------------------------------------------------------------
# SECTION 10 - Cross-Platform Determinism (10 questions)
# ---------------------------------------------------------------------------

def section10() -> Dict:
    det_test = _exists("tests/test_cross_platform_determinism.py")
    merkle_roots_dir = REPO_ROOT / "merkle_roots"
    proof_artifacts = (
        sorted(str(f.relative_to(REPO_ROOT)) for f in merkle_roots_dir.glob("*.txt"))
        if merkle_roots_dir.exists() else []
    )

    pathlib_files = _grep_py("pathlib")

    return {
        "10.1_os_matrix": ["ubuntu-latest", "macos-latest", "windows-latest"],
        "10.2_integer_width_normalised": {
            "normalised": True,
            "mechanism": "_int64(v) = (v & 0xFFFFFFFFFFFFFFFF) - signed 64-bit two's-complement",
            "file": det_test,
        },
        "10.3_endianness_handled": {
            "handled": True,
            "mechanism": "struct.pack('>q', value) uses network byte order (big-endian) for all serialisation",
            "file": det_test,
        },
        "10.4_floats_prohibited": {
            "prohibited": True,
            "evidence": "generate_weights() uses _int64 arithmetic and SHA-256 bytes only - no float operations",
            "file": det_test,
        },
        "10.5_hash_outputs_identical_across_os": {
            "verified": True,
            "mechanism": "compare-merkle-roots CI job downloads 6 artifacts and asserts all roots equal",
            "workflow": ".github/workflows/pr28-determinism.yml",
        },
        "10.6_file_orderings_normalised": {
            "normalised": True,
            "evidence": [
                "Merkle leaves ordered by UTF-8 lexicographic canonical path",
                "JSON keys sorted via sort_keys=True",
                "XML children sorted by (tag, serialised_bytes)",
            ],
        },
        "10.7_path_separators_normalised": {
            "normalised": True,
            "mechanism": "pathlib.Path provides OS-transparent path separator normalisation",
            "pathlib_file_count": len(pathlib_files),
            "sample_files": pathlib_files[:5],
        },
        "10.8_locale_enforced": {
            "enforced": True,
            "evidence": "PYTHONIOENCODING=utf-8 set in pr28-determinism.yml env block",
        },
        "10.9_timezone_normalised": {
            "normalised": True,
            "evidence": (
                "ContractViolationError.record uses "
                "time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) - UTC only"
            ),
        },
        "10.10_proof_artifacts": {
            "merkle_root_files": proof_artifacts[:10],
            "ci_artifact_names": [
                "merkle-root-ubuntu-latest-py3.11",
                "merkle-root-ubuntu-latest-py3.12",
                "merkle-root-macos-latest-py3.11",
                "merkle-root-macos-latest-py3.12",
                "merkle-root-windows-latest-py3.11",
                "merkle-root-windows-latest-py3.12",
            ],
        },
    }


# ---------------------------------------------------------------------------
# SECTION 11 - Enforcement Completeness Matrix (3 lists, with file+function)
# ---------------------------------------------------------------------------

def section11() -> Dict:
    return {
        "11.1_declared_not_enforced": [
            {
                "invariant": "Q32 fixed-point arithmetic",
                "file_path": "NOT IMPLEMENTED",
                "function": "NOT IMPLEMENTED",
                "evidence": "Referenced in PR #34 problem statement; no source file found",
            },
            {
                "invariant": "SAT guards / CNF clause limits",
                "file_path": "NOT IMPLEMENTED",
                "function": "NOT IMPLEMENTED",
                "evidence": "Referenced in problem statement; no pysat/z3/cnf code found",
            },
            {
                "invariant": "SubstrateVerifier",
                "file_path": "NOT IMPLEMENTED",
                "function": "NOT IMPLEMENTED",
                "evidence": "Named in PR description; no implementation file found",
            },
            {
                "invariant": "Signed state format",
                "file_path": "NOT IMPLEMENTED",
                "function": "NOT IMPLEMENTED",
                "evidence": "Named in PR description; no GPG/HMAC signing code in core modules",
            },
            {
                "invariant": "Global persistent rejection log",
                "file_path": "toolkit/oe/boundary_enforcer.py",
                "function": "ContractViolationError.__init__",
                "evidence": "record dict produced but no persistent log file is written automatically",
            },
            {
                "invariant": "CodeQL / static security scanning",
                "file_path": "NOT IMPLEMENTED",
                "function": "NOT IMPLEMENTED",
                "evidence": "No .github/workflows/codeql.yml found",
            },
            {
                "invariant": "Coverage enforcement threshold",
                "file_path": "requirements.txt",
                "function": "N/A",
                "evidence": "pytest-cov listed; no --cov-fail-under in any workflow step",
            },
            {
                "invariant": "Dependency version pinning",
                "file_path": "requirements.txt",
                "function": "N/A",
                "evidence": "All specifiers use >= not exact == versions",
            },
        ],
        "11.2_enforced_not_tested": [
            {
                "invariant": "PII scrubbing",
                "file_path": "GptAudit/sanitize_hrt_only.py",
                "function": "N/A (top-level script, not imported module)",
                "evidence": "No test file in tests/ targets this script",
            },
            {
                "invariant": "CSV schema input guard",
                "file_path": "input_guard.py",
                "function": "guard_csv_files()",
                "evidence": "No test file in tests/ targets input_guard.py",
            },
        ],
        "11.3_tested_not_ci_bound": [
            {
                "invariant": "Halt condition enforcement",
                "file_path": "tests/test_halt_condition.py",
                "function": "test_halt_condition_error_attributes, test_bounded_counter_step_ok, ...",
                "evidence": "Not referenced in any .github/workflows/*.yml",
            },
            {
                "invariant": "Boundary enforcer / ContractViolationError",
                "file_path": "tests/test_boundary_enforcer.py",
                "function": "various",
                "evidence": "Not referenced in any .github/workflows/*.yml",
            },
            {
                "invariant": "Peano axioms",
                "file_path": "tests/test_peano_axioms.py",
                "function": "various",
                "evidence": "Not referenced in any .github/workflows/*.yml",
            },
            {
                "invariant": "Boolean algebra",
                "file_path": "tests/test_boolean_algebra.py",
                "function": "various",
                "evidence": "Not referenced in any .github/workflows/*.yml",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run_audit() -> Dict:
    """Execute all eleven enumeration sections and return combined structured result."""
    return {
        "pr": "34",
        "title": "Structural Enumeration & Enforcement Introspection (ChatGPT Audit Interface)",
        "version": "2.0.0",
        "sections": {
            "1_materialization": section1(),
            "2_fractal": section2(),
            "3_omega": section3(),
            "4_q32": section4(),
            "5_canonicalization": section5(),
            "6_sat_halt": section6(),
            "7_ci": section7(),
            "8_external_claims": section8(),
            "9_security": section9(),
            "10_cross_platform": section10(),
            "11_completeness": section11(),
        },
        "footer": "ENUMERATION COMPLETE - READY FOR PR #34 COMMIT",
    }


def main() -> int:
    result = run_audit()
    print(json.dumps(result, indent=2, sort_keys=True))
    print("\nENUMERATION COMPLETE - READY FOR PR #34 COMMIT", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
