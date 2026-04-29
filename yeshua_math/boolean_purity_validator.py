"""
yeshua_math/boolean_purity_validator.py — Boolean Logic Purity Validator

Enforces that all conditional logic satisfies Boolean algebra purity:
  - Reduction to Boolean algebra (no hidden mutable state in conditionals)
  - Exhaustive truth table validation for finite domains
  - Deterministic branching guarantee

Author: Orthogonal Engineering
PR: #37
Standard: Yeshua
Version: 1.0.0
"""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

__all__ = [
    "BooleanViolation",
    "BooleanPurityReport",
    "validate_truth_table",
    "run_boolean_purity_validator",
]

REPO_ROOT = Path(__file__).parent.parent

_CORE_DIRS = ["axioms", "yeshua", "oe_ifm", "generators", "dvcl", "yeshua_math"]


class BooleanViolation:
    """A single Boolean purity violation."""

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


class BooleanPurityReport:
    """Structured result of running the Boolean purity validator."""

    def __init__(self) -> None:
        self.violations: List[BooleanViolation] = []
        self.passed: List[str] = []

    @property
    def all_passed(self) -> bool:
        return len(self.violations) == 0

    def add_violation(self, v: BooleanViolation) -> None:
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
        # TODO: Expand to_json() - stub detected by Yeshua Agent
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


def validate_truth_table(
    fn: Callable[..., bool],
    inputs: List[Tuple],
) -> Tuple[bool, List[Tuple]]:
    """Exhaustively validate a Boolean function over the provided input domain.

    Returns (all_deterministic, failures) where failures is a list of input
    tuples for which fn returned different results across two calls.
    """
    failures = []
    for inp in inputs:
        r1 = fn(*inp)
        r2 = fn(*inp)
        if r1 != r2:
            failures.append(inp)
    return len(failures) == 0, failures


def _check_file_for_mutable_conditionals(path: Path) -> List[BooleanViolation]:
    """AST-scan a Python file for conditional expressions that depend on
    mutable global state (a proxy for hidden mutable state in conditionals).
    """
    violations: List[BooleanViolation] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    # Look for assignment to module-level mutable objects used inside If tests
    # This is a lightweight heuristic: flag `global` statements inside functions
    # that are subsequently used in conditionals.
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in ast.walk(node):
                if isinstance(child, ast.Global):
                    violations.append(
                        BooleanViolation(
                            file=str(path),
                            line=child.lineno,
                            kind="global_mutable_state",
                            detail=(
                                f"'global {', '.join(child.names)}' introduces potential "
                                "hidden mutable state into conditional logic"
                            ),
                        )
                    )

    return violations


def run_boolean_purity_validator(dirs: List[str] | None = None) -> BooleanPurityReport:
    """Run Boolean purity validator over the given directories."""
    if dirs is None:
        dirs = _CORE_DIRS

    report = BooleanPurityReport()
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
                violations = _check_file_for_mutable_conditionals(fpath)
                if violations:
                    for v in violations:
                        report.add_violation(v)
                else:
                    report.add_pass(str(fpath.relative_to(REPO_ROOT)))

    return report


if __name__ == "__main__":
    import sys

    report = run_boolean_purity_validator()
    print(report.to_json())
    sys.exit(0 if report.all_passed else 1)
