"""audit/scope_audit.py — Domain Completeness Auditor.

Scans all domain directories under src/domains/ to verify:
  1. Required files exist (__init__.py, invariants.py, implementation.py).
  2. invariants.py contains run_all_invariants() (AST).
  3. invariants.py contains at least one check_* function (AST).
  4. implementation.py contains at least one @dataclass (AST).
  5. No float() calls in implementation.py or invariants.py (regex).
  6. No pass-only bodies in check_* functions (AST).

Run as:
    python3 audit/scope_audit.py [--output <path>]

Returns exit code 0 if all domains are complete, 1 otherwise.
Persists the JSON report to audit/SCOPE_AUDIT_REPORT.json by default.

Standard: SCOPE-001
Falsifies if: returns 0 when any domain is missing required files or functions.
falsifies_if: returns 0 when any domain is missing required files or functions.
"""

from __future__ import annotations

import ast
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

DOMAINS_DIR = REPO_ROOT / "src" / "domains"
DEFAULT_REPORT_PATH = Path(__file__).parent / "SCOPE_AUDIT_REPORT.json"

_FLOAT_RE = re.compile(r"\bfloat\s*\(")


@dataclass
class DomainScopeReport:
    """Per-domain scope audit results.

    Falsifies if: passed is True while any required artifact is missing.
    falsifies_if: passed is True while any required artifact is missing.
    """

    domain: str
    passed: bool = True
    missing_files: List[str] = field(default_factory=list)
    missing_functions: List[str] = field(default_factory=list)
    stub_functions: List[str] = field(default_factory=list)
    float_violations: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "passed": self.passed,
            "missing_files": self.missing_files,
            "missing_functions": self.missing_functions,
            "stub_functions": self.stub_functions,
            "float_violations": self.float_violations,
            "notes": self.notes,
        }


def _has_float_calls(source: str) -> bool:
    # TODO: Expand _has_float_calls() - stub detected by Yeshua Agent
    return bool(_FLOAT_RE.search(source))


def _check_ast_requirements(
    # TODO: Expand _check_ast_requirements() - stub detected by Yeshua Agent
    source: str, domain: str
) -> Tuple[List[str], List[str], List[str]]:
    """Parse invariants.py source and check for required functions.

    Returns (missing_functions, stub_functions, notes).
    """
    missing: List[str] = []
    stubs: List[str] = []
    notes: List[str] = []

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        notes.append(f"Syntax error in {domain}/invariants.py: {exc}")
        return missing, stubs, notes

    has_run_all = False
    check_functions: List[ast.FunctionDef] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "run_all_invariants":
                has_run_all = True
            elif node.name.startswith("check_"):
                check_functions.append(node)

    if not has_run_all:
        missing.append("run_all_invariants")

    if not check_functions:
        missing.append("check_* function")

    for func in check_functions:
        # Detect pass-only body: single statement that is Pass, or empty body
        body = func.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            stubs.append(func.name)
        elif len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            # Docstring-only function is also a stub
            stubs.append(func.name)

    return missing, stubs, notes


def _check_implementation_ast(source: str, domain: str) -> Tuple[bool, List[str]]:
    """Parse implementation.py source and check for @dataclass.

    Returns (has_dataclass, notes).
    """
    notes: List[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        notes.append(f"Syntax error in {domain}/implementation.py: {exc}")
        return False, notes

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                    return True, notes
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                        return True, notes
    return False, notes


def audit_domain(domain_dir: Path) -> DomainScopeReport:
    """Audit a single domain directory.

    Falsifies if: any required file or function is missing.
    falsifies_if: any required file or function is missing.
    """
    domain = domain_dir.name
    report = DomainScopeReport(domain=domain)

    required_files = ["__init__.py", "invariants.py", "implementation.py"]
    for fname in required_files:
        fpath = domain_dir / fname
        if not fpath.exists():
            report.missing_files.append(fname)
            report.passed = False

    inv_path = domain_dir / "invariants.py"
    impl_path = domain_dir / "implementation.py"

    if inv_path.exists():
        try:
            inv_source = inv_path.read_text(encoding="utf-8")
        except OSError as exc:
            report.notes.append(f"Cannot read invariants.py: {exc}")
            inv_source = ""
        else:
            if _has_float_calls(inv_source):
                report.float_violations.append("invariants.py")
                report.passed = False

            missing_funcs, stubs, ast_notes = _check_ast_requirements(inv_source, domain)
            report.missing_functions.extend(missing_funcs)
            report.stub_functions.extend(stubs)
            report.notes.extend(ast_notes)
            if missing_funcs or stubs:
                report.passed = False

    if impl_path.exists():
        try:
            impl_source = impl_path.read_text(encoding="utf-8")
        except OSError as exc:
            report.notes.append(f"Cannot read implementation.py: {exc}")
            impl_source = ""
        else:
            if _has_float_calls(impl_source):
                report.float_violations.append("implementation.py")
                report.passed = False

            has_dataclass, impl_notes = _check_implementation_ast(impl_source, domain)
            report.notes.extend(impl_notes)
            if not has_dataclass:
                report.missing_functions.append("@dataclass in implementation.py")
                report.passed = False

    return report


def run_scope_audit(output_path: Path = DEFAULT_REPORT_PATH) -> Tuple[bool, ProofObject]:
    """Run the scope audit across all domains.

    Falsifies if: returns True while any domain is incomplete.
    falsifies_if: returns True while any domain is incomplete.
    """
    if not DOMAINS_DIR.exists():
        proof = ProofObject(
            rule="run_scope_audit",
            premises=["domains_dir missing"],
            conclusion="FAIL: src/domains/ does not exist",
        )
        return False, proof

    domain_reports: List[DomainScopeReport] = []
    incomplete_domains: List[str] = []
    missing_files_map: Dict[str, List[str]] = {}
    missing_functions_map: Dict[str, List[str]] = {}
    stub_bodies_map: Dict[str, List[str]] = {}

    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        report = audit_domain(domain_dir)
        domain_reports.append(report)
        if not report.passed:
            incomplete_domains.append(report.domain)
        if report.missing_files:
            missing_files_map[report.domain] = report.missing_files
        if report.missing_functions:
            missing_functions_map[report.domain] = report.missing_functions
        if report.stub_functions:
            stub_bodies_map[report.domain] = report.stub_functions

    total = len(domain_reports)
    complete = sum(1 for r in domain_reports if r.passed)
    all_pass = complete == total and total > 0

    result = {
        "total_domains": total,
        "complete_domains": complete,
        "incomplete_domains": incomplete_domains,
        "missing_files": missing_files_map,
        "missing_functions": missing_functions_map,
        "stub_bodies": stub_bodies_map,
        "domain_reports": [r.to_dict() for r in domain_reports],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    conclusion = (
        f"PASS: {complete}/{total} domains complete"
        if all_pass
        else f"FAIL: {total - complete}/{total} domains incomplete"
    )
    proof = ProofObject(
        rule="run_scope_audit",
        premises=[
            f"total_domains={total}",
            f"complete_domains={complete}",
        ],
        conclusion=conclusion,
    )
    return all_pass, proof


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Domain completeness scope audit"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON report",
    )
    args = parser.parse_args(argv)

    passed, proof = run_scope_audit(output_path=args.output)
    print(proof.conclusion)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
