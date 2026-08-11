"""TSS v10 diagnostics engine.

The diagnostics engine validates the entire build and computes a quality
score out of 100.  It is intentionally self-contained (standard library
only) so it can validate every other component without depending on them.

Checks performed:
    structure    required files/directories exist
    syntax       every .py file compiles
    docstrings   every class and method has a docstring
    imports      standard library only (no third-party dependencies)
    bias         no hidden bias variables in any source file
    data         embedded JSON databases parse and meet coverage targets
    database     SQLite verification log exists with required tables
    sizes        per-module < 100 KB, project total < 1 MB
    tests        unit test suite present with 50+ test methods
    runnability  every module is independently runnable

Score: 100.0 means every check passed with zero critical issues.
"""

from __future__ import annotations

import ast
import datetime
import html
import json
import pathlib
import re
import sqlite3
import sys
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# targets
# ---------------------------------------------------------------------------

TARGETS: Dict[str, int] = {
    "whistleblowers.json": 15,
    "corporations.json": 12,
    "statutes.json": 15,
    "cases.json": 11,
    "sources.json": 25,
}

REQUIRED_MODULES: List[str] = [
    "tss_core/tss_whistleblower.py",
    "tss_core/tss_corporate.py",
    "tss_core/tss_regulatory.py",
    "tss_core/tss_verification.py",
    "tss_core/tss_ingestion.py",
    "tss_core/tss_projection.py",
    "tss_core/tss_filing.py",
    "tss_core/tss_security.py",
    "tss_core/tss_aggregation.py",
    "tss_core/tss_blockchain.py",
    "tss_core/tss_diagnostics.py",
]

REQUIRED_DELIVERABLES: List[str] = [
    "tss_web/tss_server.py",
    "tss_tests/tss_tests.py",
    "tss_cicd/tss_cicd.py",
    "tss_rdf/tss_rdf.py",
    "tss_updater/tss_updater.py",
    "tss_leaks/tss_leaks.py",
    "tss_monument/TSS_v10_MONUMENT.txt",
]

REQUIRED_DATABASES: List[str] = [
    "data/whistleblowers.json",
    "data/corporations.json",
    "data/statutes.json",
    "data/cases.json",
    "data/sources.json",
]

REQUIRED_TABLES: List[str] = [
    "evidence_manifest",
    "atomic_claims",
    "source_rot",
]

MAX_MODULE_BYTES = 100_000
MAX_PROJECT_BYTES = 1_000_000

STDLIB = set(getattr(sys, "stdlib_module_names", ()))
PROJECT_MODULES = {
    "tss_core", "tss_web", "tss_tests", "tss_cicd", "tss_rdf",
    "tss_updater", "tss_leaks",
}

# Hidden bias variables the CI pipeline must never find.  Built by
# concatenation so this file itself does not contain the literal names.
BIAS_TERMS = [
    "actual" + "Alpha",
    "effective" + "Grant",
    "steer" + "ing" + "Vector",
    "hidden" + "Theta",
    "opac" + "ity" + "Factor",
]


def _project_files(suffix: str = ".py") -> List[pathlib.Path]:
    """Return all project files with the given suffix, excluding VCS/build dirs."""
    skip = {".git", "__pycache__", "docs", ".github"}
    out: List[pathlib.Path] = []
    for path in PROJECT_ROOT.rglob("*" + suffix):
        rel = path.relative_to(PROJECT_ROOT)
        if any(part in skip for part in rel.parts):
            continue
        out.append(path)
    return sorted(out)


def _iter_classes_functions(tree: ast.AST):
    """Yield every class and function definition node in an AST."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def _has_docstring(node: ast.AST) -> bool:
    """Return True if the node's first statement is a string literal."""
    body = getattr(node, "body", None)
    if not body:
        return False
    first = body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
        return isinstance(first.value.value, str)
    return False


def _stdlib_only(tree: ast.AST) -> List[str]:
    """Return a list of non-standard-library top-level imports."""
    violations: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in STDLIB and top not in PROJECT_MODULES:
                    violations.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top not in STDLIB and top not in PROJECT_MODULES:
                violations.append(node.module)
    return sorted(set(violations))


def _bias_hits(source: str) -> List[str]:
    """Return forbidden bias-variable names found in the source text."""
    hits: List[str] = []
    for term in BIAS_TERMS:
        if re.search(re.escape(term), source):
            hits.append(term)
    return hits


class IssueTracker:
    """Classifies problems by severity and records recommendations."""

    def __init__(self) -> None:
        """Initialize the tracker with an empty issue list."""
        self.issues: List[Dict[str, str]] = []

    def add(self, severity: str, check: str, detail: str) -> None:
        """Record one issue with severity critical/high/medium/info."""
        self.issues.append({
            "severity": severity,
            "check": check,
            "detail": detail,
        })

    def critical_count(self) -> int:
        """Return the number of critical issues."""
        return sum(1 for i in self.issues if i["severity"] == "critical")

    def list_all(self) -> List[Dict[str, str]]:
        """Return all recorded issues."""
        return self.issues


class CoverageMetrics:
    """Computes per-database coverage percentages against targets."""

    def compute_coverage(self) -> Dict[str, Any]:
        """Return {database: {actual, target, coverage_pct}} for every target."""
        result: Dict[str, Any] = {}
        for filename, target in TARGETS.items():
            path = PROJECT_ROOT / "data" / filename
            actual = 0
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    actual = len(data) if isinstance(data, list) else len(data.keys())
                except (json.JSONDecodeError, OSError):
                    actual = 0
            pct = round(min(100.0, actual * 100.0 / target), 1) if target else 0.0
            result[filename] = {
                "actual": actual,
                "target": target,
                "coverage_pct": pct,
            }
        return result


class DiagnosticsEngine:
    """Runs all quality checks and computes the overall score."""

    def __init__(self) -> None:
        """Initialize the engine with empty results."""
        self.results: Dict[str, Dict[str, Any]] = {}
        self.issues = IssueTracker()
        self.coverage = CoverageMetrics()

    # -- individual checks -------------------------------------------------

    def _check_structure(self) -> bool:
        """Verify every required module and deliverable file exists."""
        missing = [rel for rel in REQUIRED_MODULES + REQUIRED_DELIVERABLES
                   if not (PROJECT_ROOT / rel).exists()]
        missing += [rel for rel in REQUIRED_DATABASES
                    if not (PROJECT_ROOT / rel).exists()]
        if missing:
            self.issues.add("high", "structure", "missing: " + ", ".join(missing))
            return False
        return True

    def _check_syntax(self) -> bool:
        """Compile every .py file in the project."""
        bad: List[str] = []
        for path in _project_files(".py"):
            try:
                compile(path.read_text(encoding="utf-8"), str(path), "exec")
            except SyntaxError as exc:
                bad.append(f"{path.relative_to(PROJECT_ROOT)}:{exc.lineno}")
        if bad:
            self.issues.add("critical", "syntax", "syntax errors in: " + ", ".join(bad))
            return False
        return True

    def _check_docstrings(self) -> bool:
        """Verify every class and method in every module has a docstring."""
        missing: List[str] = []
        for path in _project_files(".py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            rel = path.relative_to(PROJECT_ROOT)
            for node in _iter_classes_functions(tree):
                if not _has_docstring(node):
                    missing.append(f"{rel}:{getattr(node, 'lineno', '?')} {node.name}")
        if missing:
            self.issues.add(
                "medium", "docstrings",
                f"{len(missing)} definitions missing docstrings (first: {missing[0]})",
            )
            return False
        return True

    def _check_imports(self) -> bool:
        """Verify only standard library and project modules are imported."""
        violations: List[str] = []
        for path in _project_files(".py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            rel = str(path.relative_to(PROJECT_ROOT))
            for module in _stdlib_only(tree):
                violations.append(f"{module} (in {rel})")
        if violations:
            self.issues.add("critical", "imports",
                            "non-stdlib imports: " + ", ".join(violations))
            return False
        return True

    def _check_bias(self) -> bool:
        """Verify no hidden bias variable names appear in source files."""
        hits: List[str] = []
        for path in _project_files(".py"):
            found = _bias_hits(path.read_text(encoding="utf-8", errors="replace"))
            for term in found:
                hits.append(f"{term} in {path.relative_to(PROJECT_ROOT)}")
        if hits:
            self.issues.add("critical", "bias", "found: " + ", ".join(hits))
            return False
        return True

    def _check_data(self) -> bool:
        """Verify JSON databases parse and meet coverage targets."""
        ok = True
        for filename, target in TARGETS.items():
            path = PROJECT_ROOT / "data" / filename
            if not path.exists():
                self.issues.add("high", "data", f"{filename} missing")
                ok = False
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                self.issues.add("critical", "data", f"{filename} invalid JSON: {exc}")
                ok = False
                continue
            actual = len(data) if isinstance(data, list) else len(data.keys())
            if actual < target:
                self.issues.add("high", "data",
                                f"{filename}: {actual}/{target} records")
                ok = False
        return ok

    def _check_database(self) -> bool:
        """Verify the SQLite verification log exists with required tables."""
        db_path = PROJECT_ROOT / "data" / "verification_log.db"
        if not db_path.exists():
            self.issues.add("high", "database",
                            "data/verification_log.db not created yet")
            return False
        try:
            con = sqlite3.connect(str(db_path))
            rows = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            con.close()
        except sqlite3.Error as exc:
            self.issues.add("high", "database", f"sqlite error: {exc}")
            return False
        tables = {row[0] for row in rows}
        missing = [t for t in REQUIRED_TABLES if t not in tables]
        if missing:
            self.issues.add("high", "database", "missing tables: " + ", ".join(missing))
            return False
        return True

    def _check_sizes(self) -> bool:
        """Verify per-module < 100 KB and project total < 1 MB."""
        oversized: List[str] = []
        total = 0
        for path in _project_files(".py"):
            size = path.stat().st_size
            total += size
            if size > MAX_MODULE_BYTES:
                oversized.append(str(path.relative_to(PROJECT_ROOT)))
        for path in _project_files(".json"):
            total += path.stat().st_size
        for extra in ("tss_monument/TSS_v10_MONUMENT.txt",
                      "README.md"):
            path = PROJECT_ROOT / extra
            if path.exists():
                total += path.stat().st_size
        if oversized:
            self.issues.add("medium", "sizes",
                            "oversized modules: " + ", ".join(oversized))
            return False
        if total > MAX_PROJECT_BYTES:
            self.issues.add("medium", "sizes",
                            f"project total {total} bytes exceeds 1 MB")
            return False
        return True

    def _check_tests(self) -> bool:
        """Verify the test suite exists with at least 50 test methods."""
        path = PROJECT_ROOT / "tss_tests" / "tss_tests.py"
        if not path.exists():
            self.issues.add("high", "tests", "tss_tests/tss_tests.py missing")
            return False
        source = path.read_text(encoding="utf-8", errors="replace")
        count = len(re.findall(r"^\s*def\s+test_", source, re.MULTILINE))
        if count < 50:
            self.issues.add("high", "tests", f"{count}/50 test methods")
            return False
        return True

    def _check_runnability(self) -> bool:
        """Verify every module has an independent __main__ entry point."""
        missing: List[str] = []
        for path in _project_files(".py"):
            if path.name == "__init__.py":
                continue  # package marker, not a standalone module
            source = path.read_text(encoding="utf-8", errors="replace")
            if "__main__" not in source:
                missing.append(str(path.relative_to(PROJECT_ROOT)))
        if missing:
            self.issues.add("medium", "runnability",
                            "no __main__ block in: " + ", ".join(missing))
            return False
        return True

    # -- orchestration -----------------------------------------------------

    def run_all_checks(self) -> Dict[str, Any]:
        """Run every check, classify issues, and compute the overall score."""
        weights = {
            "structure": 8, "syntax": 10, "docstrings": 12, "imports": 10,
            "bias": 10, "data": 15, "database": 5, "sizes": 10,
            "tests": 10, "runnability": 10,
        }
        checks = {
            "structure": self._check_structure,
            "syntax": self._check_syntax,
            "docstrings": self._check_docstrings,
            "imports": self._check_imports,
            "bias": self._check_bias,
            "data": self._check_data,
            "database": self._check_database,
            "sizes": self._check_sizes,
            "tests": self._check_tests,
            "runnability": self._check_runnability,
        }
        score = 0.0
        per_check: Dict[str, Dict[str, Any]] = {}
        for name, fn in checks.items():
            passed = fn()
            weight = weights[name]
            if passed:
                score += weight
            per_check[name] = {"passed": passed, "weight": weight,
                               "earned": weight if passed else 0.0}
        coverage = self.coverage.compute_coverage()
        all_covered = all(
            entry["coverage_pct"] >= 100.0 for entry in coverage.values()
        )
        if not all_covered and not any(
            i["check"] == "data" for i in self.issues.list_all()
        ):
            self.issues.add("info", "coverage",
                            "some databases below 100% target coverage")
        report = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "engine": "tss_diagnostics v10",
            "project_root": str(PROJECT_ROOT),
            "score": round(score, 1),
            "overall": round(score, 1),  # v11 harness alias for the same score
            "target_score": 100.0,
            "pass": score >= 95.0,
            "critical_issues": self.issues.critical_count(),
            "checks": per_check,
            "coverage": coverage,
            "issues": self.issues.list_all(),
            "recommendations": [
                i["detail"] for i in self.issues.list_all()
                if i["severity"] in ("critical", "high")
            ],
        }
        self.results = report
        return report

    def export_json(self) -> Dict[str, Any]:
        """Return the machine-readable report dict (runs checks if needed)."""
        if not self.results:
            self.run_all_checks()
        return self.results

    def generate_html_report(self) -> str:
        """Return a self-contained dark-theme HTML diagnostics report."""
        report = self.export_json()
        score = report["score"]
        color = "#00ff66" if score >= 95 else "#ff4444"
        bars = []
        for name, entry in report["coverage"].items():
            pct = entry["coverage_pct"]
            bars.append(
                f'<div class="bar-row"><span class="bar-label">{name}</span>'
                f'<div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>'
                f'<span class="bar-value">{pct}% ({entry["actual"]}/{entry["target"]})</span></div>'
            )
        issues = "".join(
            f'<li class="{i["severity"]}">[{i["severity"]}] {html.escape(i["check"])}: '
            f'{html.escape(i["detail"])}</li>'
            for i in report["issues"]
        ) or "<li>none</li>"
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>TSS v10 Diagnostics</title>
<style>
body {{ background:#010102; color:#e0e0e0; font-family:monospace; padding:2em; }}
h1 {{ color:#00ccff; }} h2 {{ color:#00ccff; }}
.score {{ font-size:3em; color:{color}; }}
.bar-row {{ margin:.4em 0; }} .bar {{ display:inline-block; width:60%; height:1em;
  background:#1a1a1a; border:1px solid #333; vertical-align:middle; }}
.bar-fill {{ height:100%; background:#00ff66; }}
.bar-label {{ display:inline-block; width:22em; }} .bar-value {{ margin-left:.6em; }}
li.critical {{ color:#ff4444; }} li.high {{ color:#ff8844; }}
li.medium {{ color:#ffcc00; }} li.info {{ color:#00ccff; }}
</style></head><body>
<h1>TSS v10 — Diagnostics Report</h1>
<p>Timestamp: {html.escape(report["timestamp"])} &mdash; engine {html.escape(report["engine"])}</p>
<p class="score">Score: {score}/100</p>
<p>Critical issues: {report["critical_issues"]} &mdash; Status: {"PASS" if report["pass"] else "FAIL"}</p>
<h2>Database coverage</h2>{''.join(bars)}
<h2>Issues</h2><ul>{issues}</ul>
<h2>Recommendations</h2><ul>{''.join('<li>' + html.escape(r) + '</li>' for r in report["recommendations"]) or '<li>none</li>'}</ul>
</body></html>"""


def main(argv: List[str]) -> int:
    """Run diagnostics, print a summary, and optionally write artifacts."""
    engine = DiagnosticsEngine()
    report = engine.run_all_checks()
    if "--json" in argv:
        # Compact single-line JSON so `... | tail -1` yields the whole report.
        print(json.dumps(report))
    else:
        print(f"TSS v10 diagnostics: score {report['score']}/100 "
              f"({'PASS' if report['pass'] else 'FAIL'})")
        print(f"critical issues: {report['critical_issues']}")
        for name, entry in report["checks"].items():
            print(f"  {name:12s} {'PASS' if entry['passed'] else 'FAIL'}")
        for i in report["issues"]:
            print(f"  [{i['severity']}] {i['check']}: {i['detail']}")
    html_path = PROJECT_ROOT / "data" / "diagnostics_report.html"
    html_path.write_text(engine.generate_html_report(), encoding="utf-8")
    # Keep stdout pure JSON in --json mode for machine consumers.
    print(f"html report written: {html_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
