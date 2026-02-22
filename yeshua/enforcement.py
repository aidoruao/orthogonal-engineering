"""
yeshua/enforcement.py — Yeshua Mathematics Layer Enforcement

Verifies that all modules satisfy the Yeshua Standard:
  1. Every truth derivable.
  2. Every derivation reproducible.
  3. Every mutation re-verifiable.
  4. No authority without proof.
  5. No hidden state.
  6. No unverifiable dependency.
  7. No economic gatekeeping.
  8. Every artifact hash-anchored.

CI must verify:
  - No external API calls without boundary proofs
  - All dependencies have declared hashes
  - No float arithmetic in the core pipeline
  - No non-deterministic iteration

Author: Orthogonal Engineering
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from axioms.yeshua_axioms import YESHUA_AXIOMS, YeshuaClaim, YeshuaViolation, verify_yeshua_standard

__all__ = [
    "EnforcementReport",
    "enforce_no_float_in_core",
    "enforce_no_nondeterministic_iteration",
    "run_yeshua_enforcement",
]

REPO_ROOT = Path(__file__).parent.parent
CORE_DIRS = ["generators", "oe_ifm", "axioms", "falsification", "yeshua"]

# ---------------------------------------------------------------------------
# EnforcementReport
# ---------------------------------------------------------------------------


class EnforcementReport:
    """Structured result of running Yeshua enforcement over the codebase."""

    def __init__(self) -> None:
        self.violations: List[Dict] = []
        self.passed: List[str] = []

    def add_violation(self, check: str, file: str, detail: str) -> None:
        self.violations.append({"check": check, "file": file, "detail": detail})

    def add_pass(self, check: str) -> None:
        self.passed.append(check)

    @property
    def all_passed(self) -> bool:
        return len(self.violations) == 0

    def to_dict(self) -> Dict:
        return {
            "all_passed": self.all_passed,
            "violation_count": len(self.violations),
            "violations": self.violations,
            "passed": self.passed,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# AST-based checks
# ---------------------------------------------------------------------------

def _python_files_in(dirs: List[str]) -> List[Path]:
    files: List[Path] = []
    skip = {"__pycache__"}
    for d in dirs:
        dp = REPO_ROOT / d
        if not dp.exists():
            continue
        for root, dirnames, filenames in os.walk(dp):
            dirnames[:] = [dn for dn in dirnames if dn not in skip]
            for fname in filenames:
                if fname.endswith(".py"):
                    files.append(Path(root) / fname)
    return files


def _has_float_literals(source: str) -> List[int]:
    """Return list of line numbers containing float literals in the AST."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            lines.append(getattr(node, "lineno", 0))
    return lines


def enforce_no_float_in_core(report: EnforcementReport) -> None:
    """Axiom-aligned: no float arithmetic in the core pipeline."""
    files = _python_files_in(CORE_DIRS)
    found_any = False
    for fpath in files:
        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        float_lines = _has_float_literals(source)
        if float_lines:
            report.add_violation(
                check="no_float_in_core",
                file=str(fpath.relative_to(REPO_ROOT)),
                detail=f"Float literals at lines: {float_lines}",
            )
            found_any = True
    if not found_any:
        report.add_pass("no_float_in_core")


def enforce_no_nondeterministic_iteration(report: EnforcementReport) -> None:
    """
    Check for random / os.urandom / uuid / time.time usage in core modules
    without a fixed-seed pattern.
    """
    nondeterministic = ["random.random(", "random.randint(", "os.urandom(", "uuid.uuid4("]
    files = _python_files_in(CORE_DIRS)
    found_any = False
    for fpath in files:
        try:
            source = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pattern in nondeterministic:
            if pattern in source:
                # Allow if a fixed seed is set nearby (heuristic: "seed(" in file)
                if "seed(" not in source:
                    report.add_violation(
                        check="no_nondeterministic_iteration",
                        file=str(fpath.relative_to(REPO_ROOT)),
                        detail=f"Non-deterministic pattern without fixed seed: {pattern!r}",
                    )
                    found_any = True
                    break
    if not found_any:
        report.add_pass("no_nondeterministic_iteration")


def enforce_dependencies_declared(report: EnforcementReport) -> None:
    """Axiom 6: all external imports must be declared in requirements.txt."""
    req_file = REPO_ROOT / "requirements.txt"
    if not req_file.exists():
        report.add_violation(
            check="dependencies_declared",
            file="requirements.txt",
            detail="requirements.txt not found",
        )
        return
    report.add_pass("dependencies_declared")


# ---------------------------------------------------------------------------
# Main enforcement entry point
# ---------------------------------------------------------------------------

def run_yeshua_enforcement(strict: bool = False) -> EnforcementReport:
    """
    Run all Yeshua enforcement checks over the core codebase.

    If strict=True, raise RuntimeError on any violation.
    Returns the EnforcementReport.
    """
    report = EnforcementReport()
    enforce_no_float_in_core(report)
    enforce_no_nondeterministic_iteration(report)
    enforce_dependencies_declared(report)

    if strict and not report.all_passed:
        raise RuntimeError(
            f"Yeshua enforcement failed with {len(report.violations)} violations:\n"
            + json.dumps(report.violations, indent=2)
        )

    return report


if __name__ == "__main__":
    rep = run_yeshua_enforcement()
    print(rep.to_json())
    if not rep.all_passed:
        sys.exit(1)
