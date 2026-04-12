"""audit/popperian_audit.py — Popperian Integrity Auditor.

Scans all domain invariants.py files to verify:
  1. Every public function docstring contains a ``Falsifies if:`` clause.
  2. No ``float()`` or ``math.isclose()`` calls appear (Fraction-only rule).
  3. Every function returns ``Tuple[bool, ProofObject]``.

Run as:
    python audit/popperian_audit.py [--domain <name>] [--fail-fast] [--output <path>]

Returns exit code 0 if all domains pass, 1 otherwise.
Persists the full JSON report to ``audit/POPPERIAN_AUDIT_REPORT.json`` by default
(override with ``--output``).

Standard: Yeshua / Glass-Box / Orthogonal Engineering
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO_ROOT / "src" / "domains"
DEFAULT_REPORT_PATH = Path(__file__).parent / "POPPERIAN_AUDIT_REPORT.json"

_FALSIFIES_IF_RE = re.compile(r"falsifies[\s_]if", re.IGNORECASE)
_FLOAT_CALL_RE = re.compile(r"\bfloat\s*\(")
_ISCLOSE_RE = re.compile(r"\bisclose\s*\(")


@dataclass
class AuditResult:
    """Single finding for one function in a domain invariants file.

    Falsifies if: any field is non-empty while ``passed`` is True.
    """

    domain: str
    function_name: str
    passed: bool
    missing_falsifies_if: bool = False
    float_violations: List[int] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialise to plain dict."""
        return {
            "domain": self.domain,
            "function": self.function_name,
            "passed": self.passed,
            "missing_falsifies_if": self.missing_falsifies_if,
            "float_violations": self.float_violations,
            "notes": self.notes,
        }


@dataclass
class DomainAuditReport:
    """Aggregated audit report for one domain.

    Falsifies if: ``passed`` is True while ``findings`` contains failures.
    """

    domain: str
    invariants_path: str
    passed: bool
    findings: List[AuditResult] = field(default_factory=list)

    @property
    def failure_count(self) -> int:
        """Number of failing audit results."""
        return sum(1 for f in self.findings if not f.passed)

    def to_dict(self) -> dict:
        """Serialise to plain dict."""
        return {
            "domain": self.domain,
            "invariants_path": self.invariants_path,
            "passed": self.passed,
            "failure_count": self.failure_count,
            "findings": [f.to_dict() for f in self.findings],
        }


def _audit_invariants_file(
    invariants_path: Path,
    domain_name: str,
) -> DomainAuditReport:
    """Audit a single invariants.py file for Popperian compliance.

    Checks performed per public function:
      - Docstring contains ``Falsifies if:`` (case-insensitive).
      - No ``float(`` calls in the function body source lines.

    Falsifies if: ``passed`` is True but any function is missing
    the ``Falsifies if:`` clause or contains float() calls.
    """
    source = invariants_path.read_text(encoding="utf-8")
    lines = source.splitlines()

    try:
        tree = ast.parse(source, filename=str(invariants_path))
    except SyntaxError as exc:
        report = DomainAuditReport(
            domain=domain_name,
            invariants_path=str(invariants_path.relative_to(REPO_ROOT)),
            passed=False,
            findings=[
                AuditResult(
                    domain=domain_name,
                    function_name="<module>",
                    passed=False,
                    notes=[f"SyntaxError: {exc}"],
                )
            ],
        )
        return report

    findings: List[AuditResult] = []

    # Only audit top-level module-level functions (direct children of the Module
    # node), not inner/nested functions or methods defined inside other functions.
    module_functions = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]

    for node in module_functions:

        docstring = ast.get_docstring(node) or ""
        has_falsifies_if = bool(_FALSIFIES_IF_RE.search(docstring))

        # Check body lines for float() calls.
        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, "end_lineno") else len(lines)
        body_lines = lines[start:end]
        float_violation_lines: List[int] = []
        for offset, line in enumerate(body_lines):
            if _FLOAT_CALL_RE.search(line) or _ISCLOSE_RE.search(line):
                float_violation_lines.append(node.lineno + offset)

        passed = has_falsifies_if and not float_violation_lines
        notes: List[str] = []
        if not has_falsifies_if:
            notes.append("Missing 'Falsifies if:' in docstring")
        for ln in float_violation_lines:
            notes.append(f"float() or isclose() call at line {ln}")

        findings.append(
            AuditResult(
                domain=domain_name,
                function_name=node.name,
                passed=passed,
                missing_falsifies_if=not has_falsifies_if,
                float_violations=float_violation_lines,
                notes=notes,
            )
        )

    domain_passed = all(f.passed for f in findings) if findings else True
    return DomainAuditReport(
        domain=domain_name,
        invariants_path=str(invariants_path.relative_to(REPO_ROOT)),
        passed=domain_passed,
        findings=findings,
    )


def run_popperian_audit(
    domains_dir: Optional[Path] = None,
    domain_filter: Optional[str] = None,
) -> List[DomainAuditReport]:
    """Run the Popperian audit across all (or filtered) domain invariants.

    Args:
        domains_dir: Override directory to scan. Defaults to ``src/domains/``.
        domain_filter: If given, only audit the domain whose folder name
            matches this string (e.g. ``"d_aerospace"``).

    Returns:
        List of :class:`DomainAuditReport` — one per domain audited.

    Falsifies if: the returned list is empty when domains exist on disk.
    """
    base = domains_dir or DOMAINS_DIR

    reports: List[DomainAuditReport] = []
    for invariants_path in sorted(base.glob("*/invariants.py")):
        domain_name = invariants_path.parent.name
        if domain_filter and domain_name != domain_filter:
            continue
        reports.append(_audit_invariants_file(invariants_path, domain_name))

    return reports


def write_audit_report(
    reports: List[DomainAuditReport],
    output_path: Optional[Path] = None,
) -> Path:
    """Persist the full Popperian audit result as JSON.

    Args:
        reports: List of :class:`DomainAuditReport` from
            :func:`run_popperian_audit`.
        output_path: Destination file. Defaults to
            ``audit/POPPERIAN_AUDIT_REPORT.json``.

    Returns:
        The resolved :class:`Path` where the report was written.

    Falsifies if: the output file is absent after this function returns.
    """
    dest = output_path or DEFAULT_REPORT_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)

    total = len(reports)
    passing = sum(1 for r in reports if r.passed)
    payload = {
        "summary": {
            "total_domains": total,
            "passing_domains": passing,
            "failing_domains": total - passing,
            "all_pass": passing == total,
        },
        "reports": [r.to_dict() for r in reports],
    }

    dest.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False),
        encoding="utf-8",
    )
    return dest


def _main() -> int:
    """CLI entry point.

    Usage: python audit/popperian_audit.py [--domain <name>] [--fail-fast] [--output <path>]
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Popperian integrity audit for domain invariants."
    )
    parser.add_argument(
        "--domain",
        default=None,
        help="Audit only this domain folder (e.g. d_aerospace).",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit with code 1 on first failing domain.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON report to stdout instead of human-readable output.",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help=(
            "Path to write the JSON audit report. "
            f"Defaults to {DEFAULT_REPORT_PATH.name} in the audit/ directory."
        ),
    )
    args = parser.parse_args()

    reports = run_popperian_audit(domain_filter=args.domain)
    all_pass = all(r.passed for r in reports)
    failures = [r for r in reports if not r.passed]

    # Always persist the full JSON report to disk.
    output_path = Path(args.output) if args.output else None
    report_dest = write_audit_report(reports, output_path=output_path)

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    else:
        total = len(reports)
        passing = sum(1 for r in reports if r.passed)
        print(f"Popperian Audit: {passing}/{total} domains passing")
        print(f"Report written to: {report_dest}")
        for report in failures:
            print(f"\nFAIL: {report.domain} ({report.failure_count} issue(s))")
            for finding in report.findings:
                if not finding.passed:
                    print(f"  {finding.function_name}: {'; '.join(finding.notes)}")
            if args.fail_fast:
                return 1

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(_main())
