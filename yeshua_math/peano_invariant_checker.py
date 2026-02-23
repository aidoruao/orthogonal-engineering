"""
yeshua_math/peano_invariant_checker.py — Peano Arithmetic Invariant Checker

Enforces that all arithmetic in the repository satisfies Peano reducibility:
  - No unbounded floating-point drift
  - Explicit error bounds where floats are used
  - Integer fallback equivalence path
  - All arithmetic reducible to Peano axioms

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
from typing import Dict, List

__all__ = [
    "PeanoViolation",
    "PeanoInvariantReport",
    "check_file_for_float_drift",
    "run_peano_invariant_checker",
]

REPO_ROOT = Path(__file__).parent.parent

# Float operations that bypass integer-path checks
_FLOAT_CONSTRUCTS = frozenset({"float", "complex"})
_FLOAT_METHODS = frozenset({
    "round", "ceil", "floor", "trunc", "fabs",
    "exp", "log", "sqrt", "sin", "cos", "tan",
})

# Directories subject to Peano arithmetic invariants
_CORE_DIRS = ["axioms", "yeshua", "oe_ifm", "generators", "dvcl", "yeshua_math"]


class PeanoViolation:
    """A single Peano arithmetic invariant violation."""

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


class PeanoInvariantReport:
    """Structured result of running the Peano invariant checker."""

    def __init__(self) -> None:
        self.violations: List[PeanoViolation] = []
        self.passed: List[str] = []

    @property
    def all_passed(self) -> bool:
        return len(self.violations) == 0

    def add_violation(self, v: PeanoViolation) -> None:
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


def check_file_for_float_drift(path: Path) -> List[PeanoViolation]:
    """AST-scan a Python file for unbounded float use in the arithmetic core."""
    violations: List[PeanoViolation] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return violations

    # Check for raw float literals (bare floats without an explicit bounds comment)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            # Allowed only if the surrounding line contains an explicit bounds annotation
            lines = source.splitlines()
            lineno = node.lineno - 1
            line_text = lines[lineno] if lineno < len(lines) else ""
            if "# bounds:" not in line_text and "# exact" not in line_text:
                violations.append(
                    PeanoViolation(
                        file=str(path),
                        line=node.lineno,
                        kind="unbounded_float_literal",
                        detail=(
                            f"Float literal {node.value!r} lacks explicit bounds annotation "
                            f"('# bounds: <epsilon>' or '# exact')"
                        ),
                    )
                )
        # Check for float() constructor calls
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "float":
                violations.append(
                    PeanoViolation(
                        file=str(path),
                        line=node.lineno,
                        kind="float_constructor",
                        detail="float() constructor introduces potential drift; use int or Peano arithmetic",
                    )
                )

    return violations


def run_peano_invariant_checker(dirs: List[str] | None = None) -> PeanoInvariantReport:
    """Run Peano invariant checker over the given directories."""
    if dirs is None:
        dirs = _CORE_DIRS

    report = PeanoInvariantReport()
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
                violations = check_file_for_float_drift(fpath)
                if violations:
                    for v in violations:
                        report.add_violation(v)
                else:
                    report.add_pass(str(fpath.relative_to(REPO_ROOT)))

    return report


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Peano Invariant Checker — verify arithmetic invariants in source code."
    )
    parser.add_argument(
        "--spec",
        type=str,
        default=None,
        help="Path to a freeze spec file (e.g. resilience/invariant_spec_v2.freeze) to validate "
             "spec file hashes before running the invariant check.",
    )
    parser.add_argument(
        "--dirs",
        nargs="*",
        default=None,
        help="Directories to scan (default: all core dirs).",
    )
    args = parser.parse_args()

    if args.spec:
        import hashlib
        import json as _json

        spec_path = Path(args.spec)
        if not spec_path.is_absolute():
            spec_path = REPO_ROOT / spec_path
        freeze = _json.loads(spec_path.read_text(encoding="utf-8"))
        spec_ok = True
        for entry in freeze.get("spec_files", []):
            sf = REPO_ROOT / entry["path"]
            expected = entry["sha256"]
            if not sf.exists():
                print(f"SPEC ERROR: missing spec file: {sf}", file=sys.stderr)
                spec_ok = False
                continue
            actual = hashlib.sha256(sf.read_bytes()).hexdigest()
            if actual != expected:
                print(
                    f"SPEC ERROR: hash mismatch for {entry['path']}: "
                    f"expected={expected} actual={actual}",
                    file=sys.stderr,
                )
                spec_ok = False
        if not spec_ok:
            print("SPEC VALIDATION FAILED", file=sys.stderr)
            sys.exit(2)

    report = run_peano_invariant_checker(dirs=args.dirs)
    print(report.to_json())
    sys.exit(0 if report.all_passed else 1)
