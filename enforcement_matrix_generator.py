"""
enforcement_matrix_generator.py — Generates enforcement_matrix.json

Produces a machine-readable snapshot of:
  - All declared invariants / hypotheses
  - All proof objects (from axioms layer)
  - All CI bindings (workflow files)
  - All test files
  - All falsification attempts + results
  - All content hashes

Run as: python enforcement_matrix_generator.py

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).parent
OUTPUT_FILE = REPO_ROOT / "enforcement_matrix.json"

sys.path.insert(0, str(REPO_ROOT))

from falsification.property_tests import *  # noqa: F401,F403 — registers hypotheses
from falsification.counterexample_engine import run_all_hypotheses
from falsification.hypothesis import HYPOTHESIS_REGISTRY
from merkle.global_merkle import build_global_merkle
from yeshua.enforcement import run_yeshua_enforcement


def _hash_file(fpath: Path) -> str:
    try:
        return hashlib.sha256(fpath.read_bytes()).hexdigest()
    except OSError:
        return "ERROR"


def ci_workflows() -> List[Dict[str, str]]:
    """
    Enumerate all workflow definitions in the repository.

    Includes GitHub Actions workflows (.github/workflows) and auxiliary
    workflow specs kept under workflows/. Each record includes:
      - path: repo-relative path to the workflow file
      - name: filename only (retained for backward compatibility)
      - hash: SHA-256 of the workflow file contents
    """
    workflow_dirs = [
        REPO_ROOT / ".github" / "workflows",
        REPO_ROOT / "workflows",
    ]

    result: List[Dict[str, str]] = []
    for wf_dir in workflow_dirs:
        if not wf_dir.exists():
            continue

        workflow_files = sorted(
            set(wf_dir.rglob("*.yml")) | set(wf_dir.rglob("*.yaml"))
        )

        for wf in workflow_files:
            result.append({
                "path": wf.relative_to(REPO_ROOT).as_posix(),
                "name": wf.name,
                "hash": _hash_file(wf),
            })

    return result


def _ci_workflows() -> List[Dict[str, str]]:
    warnings.warn(
        "_ci_workflows is deprecated; use ci_workflows instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return ci_workflows()


def _test_files() -> List[Dict]:
    tests_dir = REPO_ROOT / "tests"
    result = []
    if tests_dir.exists():
        for tf in sorted(tests_dir.glob("test_*.py")):
            result.append({
                "name": tf.name,
                "hash": _hash_file(tf),
            })
    return result


def generate_enforcement_matrix() -> Dict[str, Any]:
    # Hypotheses
    hypotheses = [h.to_dict() for h in HYPOTHESIS_REGISTRY]

    # Falsification results
    fals_results = [r.to_dict() for r in run_all_hypotheses(HYPOTHESIS_REGISTRY)]

    # CI workflows
    ci_bindings = _ci_workflows()

    # Tests
    tests = _test_files()

    # Global Merkle root
    root_hash, file_count = build_global_merkle()

    # Yeshua enforcement
    yeshua_report = run_yeshua_enforcement().to_dict()

    matrix = {
        "version": "1.0.0",
        "invariants": hypotheses,
        "falsification_results": fals_results,
        "ci_bindings": ci_bindings,
        "tests": tests,
        "global_merkle_root": root_hash,
        "global_file_count": file_count,
        "yeshua_enforcement": yeshua_report,
    }

    # Hash the matrix itself for integrity
    matrix_json = json.dumps(matrix, sort_keys=True, separators=(",", ":"))
    matrix["matrix_hash"] = hashlib.sha256(matrix_json.encode("utf-8")).hexdigest()

    return matrix


if __name__ == "__main__":
    matrix = generate_enforcement_matrix()
    OUTPUT_FILE.write_text(
        json.dumps(matrix, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"enforcement_matrix.json written ({len(matrix['invariants'])} invariants)")
    sys.exit(0)
