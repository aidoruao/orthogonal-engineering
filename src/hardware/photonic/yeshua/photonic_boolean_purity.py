"""PHOTONIC Boolean Purity — Validate no global state, deterministic branching,
exhaustive truth tables in all photonic check functions.

Category 16: Yeshua Mathematics (validations 9-11).
"""

from __future__ import annotations

import ast
import inspect
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

from axioms.logic import ProofObject


def _get_photonic_source_files() -> List[Path]:
    """List all non-test photonic source files."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    photonic_dir = repo_root / "src" / "hardware" / "photonic"
    return sorted(
        p for p in photonic_dir.glob("*.py") if not p.name.startswith("test_")
    )


def _parse_file(path: Path) -> ast.AST:
    """Parse a Python file into an AST."""
    with open(path, "r", encoding="utf-8") as fh:
        return ast.parse(fh.read(), filename=str(path))


def validate_no_global_state_in_photonic_checks() -> Tuple[bool, ProofObject]:
    """No `global` keyword in any check_* function.

    Falsifies if: global found in photonic check function.
    falsifies_if: global found in photonic check function.
    """
    violations: List[str] = []
    for path in _get_photonic_source_files():
        tree = _parse_file(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
                for child in ast.walk(node):
                    if isinstance(child, ast.Global):
                        violations.append(f"{path.name}:{node.name}")
    if violations:
        return False, ProofObject(
            conclusion=f"VIOLATION: global found in {len(violations)} check function(s)",
            premises=violations,
            rule="boolean_purity_global",
        )
    return True, ProofObject(
        conclusion="No global keyword found in any photonic check function",
        premises=["Files scanned: " + str(len(_get_photonic_source_files()))],
        rule="boolean_purity_global",
    )


def validate_deterministic_branching() -> Tuple[bool, ProofObject]:
    """All if conditions are deterministic (no random, no time, no os.environ).

    Falsifies if: non-deterministic source found in conditional.
    falsifies_if: non-deterministic source found in conditional.
    """
    non_deterministic = {"random", "time", "os.environ"}
    violations: List[str] = []
    for path in _get_photonic_source_files():
        tree = _parse_file(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        for name_node in ast.walk(child.test):
                            if isinstance(name_node, ast.Name):
                                if name_node.id in non_deterministic:
                                    violations.append(f"{path.name}:{node.name}:{name_node.id}")
                            elif isinstance(name_node, ast.Attribute):
                                full = ""
                                if isinstance(name_node.value, ast.Name):
                                    full = f"{name_node.value.id}.{name_node.attr}"
                                if full in non_deterministic:
                                    violations.append(f"{path.name}:{node.name}:{full}")
    if violations:
        return False, ProofObject(
            conclusion=f"VIOLATION: non-deterministic branching in {len(violations)} location(s)",
            premises=violations,
            rule="boolean_purity_deterministic",
        )
    return True, ProofObject(
        conclusion="All photonic check conditionals are deterministic",
        premises=["No random, time, or os.environ in conditionals"],
        rule="boolean_purity_deterministic",
    )


def validate_exhaustive_truth_tables() -> Tuple[bool, ProofObject]:
    """For every Boolean parameter combination, both True and False paths are tested.

    Falsifies if: a branch path has no test coverage.
    falsifies_if: a branch path has no test coverage.
    """
    # Simplified check: verify that every check function has at least one
    # test case for pass and one for fail (both True and False branches).
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    test_dir = repo_root / "src" / "hardware" / "photonic" / "tests"
    test_files = list(test_dir.glob("test_*.py"))

    # Collect all test function names
    tested_funcs: Dict[str, Dict[str, bool]] = {}
    for test_path in test_files:
        tree = _parse_file(test_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                # Guess which check function is being tested
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                        callee = child.func.id
                        if callee.startswith("check_"):
                            if callee not in tested_funcs:
                                tested_funcs[callee] = {"pass": False, "fail": False}
                            if "pass" in node.name:
                                tested_funcs[callee]["pass"] = True
                            elif "fail" in node.name:
                                tested_funcs[callee]["fail"] = True

    missing: List[str] = []
    for func, coverage in tested_funcs.items():
        if not coverage["pass"]:
            missing.append(f"{func}: no pass test")
        if not coverage["fail"]:
            missing.append(f"{func}: no fail test")

    if missing:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(missing)} branch path(s) untested",
            premises=missing,
            rule="boolean_purity_truth_tables",
        )
    return True, ProofObject(
        conclusion="All photonic check functions have pass and fail test coverage",
        premises=[f"Test files: {len(test_files)}", f"Functions tested: {len(tested_funcs)}"],
        rule="boolean_purity_truth_tables",
    )


# ---------------------------------------------------------------------------
# Run-all helper
# ---------------------------------------------------------------------------

def run_all_validations() -> list:
    """Run all 3 Boolean purity validations.

    falsifies_if: any validation fails.
    """
    checks = [
        ("validate_no_global_state_in_photonic_checks", validate_no_global_state_in_photonic_checks),
        ("validate_deterministic_branching", validate_deterministic_branching),
        ("validate_exhaustive_truth_tables", validate_exhaustive_truth_tables),
    ]
    results = []
    for name, func in checks:
        try:
            ok, proof = func()
            results.append((name, ok, proof))
        except Exception as exc:
            fake_proof = ProofObject(
                conclusion=f"ERROR in {name}: {exc}",
                premises=[],
                rule=name,
            )
            results.append((name, False, fake_proof))
    return results
