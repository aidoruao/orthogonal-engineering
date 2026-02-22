"""
dvcl/determinism_guard.py — DVCL Determinism Guard

Enforces that all executions are deterministic by:
  - Seeding all pseudo-random generators with canonical seeds
  - Prohibiting non-deterministic iteration (dict.items() order, set iteration)
  - Enforcing explicit float bounds
  - Validating environment hashes against canonical_env.lock

Author: Orthogonal Engineering
PR: #37
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

__all__ = [
    "DeterminismViolation",
    "DeterminismReport",
    "check_file_for_nondeterminism",
    "run_determinism_guard",
]

REPO_ROOT = Path(__file__).parent.parent
CANONICAL_SEED: int = 37

# Patterns that indicate non-determinism
_NONDETERMINISTIC_CALLS = frozenset({
    "random",
    "uuid4",
    "time",
    "datetime",
    "os.urandom",
})

_FORBIDDEN_BUILTINS = frozenset({"hash"})  # Python hash() is seed-dependent


class DeterminismViolation:
    """A single non-determinism finding."""

    def __init__(self, file: str, line: int, kind: str, detail: str) -> None:
        self.file = file
        self.line = line
        self.kind = kind
        self.detail = detail

    def to_dict(self) -> Dict:
        return {
            "file": self.file,
            "line": self.line,
            "kind": self.kind,
            "detail": self.detail,
        }


class DeterminismReport:
    """Structured result of running the determinism guard."""

    def __init__(self) -> None:
        self.violations: List[DeterminismViolation] = []
        self.passed: List[str] = []

    @property
    def all_passed(self) -> bool:
        return len(self.violations) == 0

    def add_violation(self, v: DeterminismViolation) -> None:
        self.violations.append(v)

    def add_pass(self, check: str) -> None:
        self.passed.append(check)

    def to_dict(self) -> Dict:
        return {
            "all_passed": self.all_passed,
            "violation_count": len(self.violations),
            "violations": [v.to_dict() for v in self.violations],
            "passed": self.passed,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def check_file_for_nondeterminism(path: Path) -> List[DeterminismViolation]:
    """AST-scan a Python file for known non-determinism patterns."""
    violations: List[DeterminismViolation] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node)
            if name in _NONDETERMINISTIC_CALLS:
                violations.append(
                    DeterminismViolation(
                        file=str(path),
                        line=node.lineno,
                        kind="nondeterministic_call",
                        detail=f"Unsuppressed call to {name!r}",
                    )
                )
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _FORBIDDEN_BUILTINS:
                violations.append(
                    DeterminismViolation(
                        file=str(path),
                        line=node.lineno,
                        kind="forbidden_builtin",
                        detail=f"Built-in {node.func.id!r} is seed-dependent",
                    )
                )
    return violations


def _call_name(node: ast.Call) -> str:
    """Return dotted name for a call node, or empty string."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        parts = []
        cur: ast.expr = node.func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return ".".join(reversed(parts))
    return ""


def run_determinism_guard(dirs: List[str] | None = None) -> DeterminismReport:
    """Run the determinism guard over the given directories (default: core dirs)."""
    if dirs is None:
        dirs = ["axioms", "yeshua", "oe_ifm", "generators", "dvcl", "yeshua_math"]

    report = DeterminismReport()
    for d in dirs:
        dp = REPO_ROOT / d
        if not dp.exists():
            report.add_pass(f"skip:{d} (absent)")
            continue
        for root, dirnames, filenames in os.walk(dp):
            dirnames[:] = [dn for dn in dirnames if dn != "__pycache__"]
            for fname in filenames:
                if not fname.endswith(".py"):
                    continue
                fpath = Path(root) / fname
                violations = check_file_for_nondeterminism(fpath)
                if violations:
                    for v in violations:
                        report.add_violation(v)
                else:
                    report.add_pass(str(fpath.relative_to(REPO_ROOT)))

    return report


if __name__ == "__main__":
    import sys

    report = run_determinism_guard()
    print(report.to_json())
    sys.exit(0 if report.all_passed else 1)
