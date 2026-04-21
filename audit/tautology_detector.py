"""audit/tautology_detector.py — Boolean Echo Pattern Detector.

AST-scans every check_* function in every domain invariants.py to classify
functions as TAUTOLOGICAL (boolean echo) or COMPUTATIONAL (real derivation).

Definitions:
  TAUTOLOGICAL: every assignment to ``success`` is exactly ``data.<field>``.
  COMPUTATIONAL: at least one assignment to ``success`` involves arithmetic,
  comparison, function calls, or conditional logic.

Run as:
    python3 audit/tautology_detector.py [--output <path>]

Exit code is always 0 (informational). Prints summary to stdout.
Persists JSON report to audit/TAUTOLOGY_REPORT.json by default.

Standard: TAUT-001
Falsifies if: classifies a function with arithmetic as tautological,
              or a pure boolean echo as computational.
falsifies_if: classifies a function with arithmetic as tautological,
              or a pure boolean echo as computational.
"""

from __future__ import annotations

import ast
import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO_ROOT / "src" / "domains"
DEFAULT_REPORT_PATH = Path(__file__).parent / "TAUTOLOGY_REPORT.json"


@dataclass
class CheckClassification:
    """Classification result for a single check_* function.

    Falsifies if: type is "tautological" while the function body contains
    arithmetic or function calls affecting success.
    falsifies_if: type is "tautological" while the function body contains
    arithmetic or function calls affecting success.
    """

    name: str
    check_type: str  # "tautological" or "computational"

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "type": self.check_type}


@dataclass
class DomainClassification:
    """Aggregated classification for one domain.

    Falsifies if: domain_type is "tautological" while any check is computational.
    falsifies_if: domain_type is "tautological" while any check is computational.
    """

    domain: str
    checks: List[CheckClassification] = field(default_factory=list)

    @property
    def domain_type(self) -> str:
        types = {c.check_type for c in self.checks}
        if types == {"tautological"}:
            return "tautological"
        elif types == {"computational"}:
            return "computational"
        else:
            return "mixed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "checks": [c.to_dict() for c in self.checks],
            "domain_type": self.domain_type,
        }


def _is_data_attribute(node: ast.expr) -> bool:
    """Return True if node is ``data.<Name>``."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "data"
    )


def _is_computational_expr(node: ast.expr) -> bool:
    """Return True if the expression involves computation beyond a raw data field."""
    if _is_data_attribute(node):
        return False

    # Any binary operation is computational
    if isinstance(node, ast.BinOp):
        return True

    # Any comparison is computational
    if isinstance(node, ast.Compare):
        return True

    # Any call is computational
    if isinstance(node, ast.Call):
        return True

    # Unary op (e.g., not) is computational
    if isinstance(node, ast.UnaryOp):
        return True

    # IfExp (conditional expression) is computational
    if isinstance(node, ast.IfExp):
        return True

    # BoolOp (and/or) is computational
    if isinstance(node, ast.BoolOp):
        return True

    # Tuple/List/Dict with more than one element is computational (multiple fields)
    if isinstance(node, (ast.Tuple, ast.List)):
        if len(node.elts) > 1:
            return True
        if len(node.elts) == 1:
            return _is_computational_expr(node.elts[0])
        return False

    # Subscript is computational
    if isinstance(node, ast.Subscript):
        return True

    # Name that is not 'data' could be a computed variable
    if isinstance(node, ast.Name):
        return node.id != "data"

    # Default: treat as computational to be safe
    return True


def _classify_function(func: ast.FunctionDef) -> str:
    """Classify a single check_* function as tautological or computational."""
    success_assignments: List[ast.expr] = []

    for stmt in ast.walk(func):
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "success":
                    success_assignments.append(stmt.value)
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name) and stmt.target.id == "success" and stmt.value is not None:
                success_assignments.append(stmt.value)

    if not success_assignments:
        # No success assignment found — treat as computational (not a pure echo)
        return "computational"

    # If ANY success assignment is computational, the whole function is computational
    for val in success_assignments:
        if _is_computational_expr(val):
            return "computational"

    # All assignments are raw data.<field>
    return "tautological"


def classify_domain_invariants(inv_path: Path, domain: str) -> DomainClassification:
    """Classify all check_* functions in a domain's invariants.py.

    Falsifies if: a computational function is labeled tautological.
    falsifies_if: a computational function is labeled tautological.
    """
    result = DomainClassification(domain=domain)

    try:
        source = inv_path.read_text(encoding="utf-8")
    except OSError:
        return result

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):
            check_type = _classify_function(node)
            result.checks.append(
                CheckClassification(name=node.name, check_type=check_type)
            )

    return result


def run_tautology_audit(
    output_path: Path = DEFAULT_REPORT_PATH,
) -> Tuple[bool, Dict[str, Any]]:
    """Run the tautology detector across all domains.

    Falsifies if: a computational function is labeled tautological.
    falsifies_if: a computational function is labeled tautological.
    """
    if not DOMAINS_DIR.exists():
        result = {
            "total_checks": 0,
            "tautological_checks": 0,
            "computational_checks": 0,
            "tautological_ratio": "0/1",
            "domains": {},
            "error": "src/domains/ does not exist",
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
        return False, result

    domain_results: List[DomainClassification] = []
    total_checks = 0
    tautological_checks = 0
    computational_checks = 0

    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        inv_path = domain_dir / "invariants.py"
        if not inv_path.exists():
            continue
        dc = classify_domain_invariants(inv_path, domain_dir.name)
        domain_results.append(dc)
        for c in dc.checks:
            total_checks += 1
            if c.check_type == "tautological":
                tautological_checks += 1
            else:
                computational_checks += 1

    from fractions import Fraction
    ratio = Fraction(tautological_checks, max(total_checks, 1))

    result = {
        "total_checks": total_checks,
        "tautological_checks": tautological_checks,
        "computational_checks": computational_checks,
        "tautological_ratio": f"{ratio.numerator}/{ratio.denominator}",
        "domains": {dc.domain: dc.to_dict() for dc in domain_results},
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    return True, result


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Tautology detector for domain invariants"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON report",
    )
    args = parser.parse_args(argv)

    ok, result = run_tautology_audit(output_path=args.output)
    print(
        f"Tautology audit: {result['tautological_checks']}/{result['total_checks']} "
        f"tautological ({result['tautological_ratio']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
