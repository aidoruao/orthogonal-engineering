"""TSS v10 CI/CD pipeline.

Runs the full hermetic build gate with nothing but the standard library:

    1.  syntax check every .py file (py_compile)
    2.  run the unit test suite (tss_tests/tss_tests.py)
    3.  run the diagnostics engine, require score >= 95.0
    4.  run every module end-to-end (standalone execution, JSON outputs)
    5.  check file sizes (each module < 100 KB, total < 1 MB)
    6.  scan for hidden bias variables
    7.  verify every source link has an archive mirror
    8.  generate the CI report
    9.  tag BUILD_PASSED and write the manifest on success
    10. tag BUILD_FAILED and write an error report on failure

Output: tss_cicd/cicd_report.json
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT_PATH = pathlib.Path(__file__).resolve().parent / "cicd_report.json"
TAG_PASSED = pathlib.Path(__file__).resolve().parent / "BUILD_PASSED"
TAG_FAILED = pathlib.Path(__file__).resolve().parent / "BUILD_FAILED"

# Built by concatenation so this file itself never contains the literals.
BIAS_TERMS = ["actual" + "Alpha", "effective" + "Grant",
              "steer" + "ing" + "Vector", "hidden" + "Theta"]


class Pipeline:
    """Runs the ten CI/CD steps and records results."""

    def __init__(self) -> None:
        """Initialize the pipeline with an empty results ledger."""
        self.steps: List[Dict[str, Any]] = []

    def record(self, step: str, passed: bool, detail: str) -> None:
        """Append one step result to the ledger."""
        self.steps.append({
            "step": step,
            "passed": bool(passed),
            "detail": detail,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        })

    def project_files(self, suffix: str) -> List[pathlib.Path]:
        """Return all project files with the suffix, skipping VCS/build dirs."""
        skip = {".git", "__pycache__", "docs", ".github"}
        out = []
        for path in PROJECT_ROOT.rglob("*" + suffix):
            rel = path.relative_to(PROJECT_ROOT)
            if not any(part in skip for part in rel.parts):
                out.append(path)
        return sorted(out)

    # -- steps -------------------------------------------------------------

    def step1_syntax(self) -> bool:
        """Compile every .py file; record failures."""
        bad: List[str] = []
        for path in self.project_files(".py"):
            proc = subprocess.run(
                [sys.executable, "-m", "py_compile", str(path)],
                capture_output=True, text=True,
            )
            if proc.returncode != 0:
                bad.append(str(path.relative_to(PROJECT_ROOT)))
        ok = not bad
        self.record("syntax", ok, "ok" if ok else "; ".join(bad))
        return ok

    def step2_tests(self) -> bool:
        """Run the unit test suite; require a passing run."""
        test_file = PROJECT_ROOT / "tss_tests" / "tss_tests.py"
        if not test_file.exists():
            self.record("unit_tests", False, "tss_tests/tss_tests.py missing")
            return False
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", str(test_file)],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        ok = proc.returncode == 0
        tail = (proc.stdout + proc.stderr).strip().splitlines()[-4:]
        self.record("unit_tests", ok, "\n".join(tail))
        return ok

    def step3_diagnostics(self) -> bool:
        """Run diagnostics; require score >= 95.0."""
        script = PROJECT_ROOT / "tss_core" / "tss_diagnostics.py"
        proc = subprocess.run(
            [sys.executable, str(script), "--json"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        if proc.returncode != 0:
            self.record("diagnostics", False, proc.stderr.strip()[-400:])
            return False
        try:
            report = json.loads(proc.stdout)
        except json.JSONDecodeError:
            self.record("diagnostics", False, "unparseable diagnostics output")
            return False
        score = float(report.get("score", 0))
        ok = score >= 95.0
        self.record("diagnostics", ok,
                    f"score {score}/100 (gate >= 95.0)")
        return ok

    def step4_end_to_end(self) -> bool:
        """Run every module standalone and verify JSON-producing deliverables."""
        failures: List[str] = []
        modules = [p for p in self.project_files(".py")
                   if p.name != "tss_cicd.py"]
        for path in modules:
            command = [sys.executable, str(path)]
            if path.name == "tss_server.py":
                command.append("--once")  # self-test mode; serves forever otherwise
            proc = subprocess.run(
                command,
                capture_output=True, text=True, cwd=str(PROJECT_ROOT),
                timeout=120,
            )
            if proc.returncode != 0:
                tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
                failures.append(f"{path.relative_to(PROJECT_ROOT)}: {' | '.join(tail)}")
        # JSON deliverables that must exist after the run above.
        required_outputs = [
            PROJECT_ROOT / "tss_rdf" / "tss_ontology.ttl",
            PROJECT_ROOT / "data" / "update_log.json",
            PROJECT_ROOT / "tss_leaks" / "leak_verification_report.json",
            PROJECT_ROOT / "tss_cicd" / "cicd_report.json",  # written later; skip
        ]
        for path in required_outputs:
            if path.name == "cicd_report.json":
                continue
            if not path.exists():
                failures.append(f"missing output {path.relative_to(PROJECT_ROOT)}")
            elif path.suffix == ".json":
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    failures.append(f"invalid JSON {path.name}: {exc}")
        ok = not failures
        self.record("end_to_end", ok, "ok" if ok else "; ".join(failures[:5]))
        return ok

    def step5_sizes(self) -> bool:
        """Verify per-module < 100 KB and project source total < 1 MB."""
        oversized: List[str] = []
        total = 0
        for path in self.project_files(".py"):
            size = path.stat().st_size
            total += size
            if size > 100_000:
                oversized.append(str(path.relative_to(PROJECT_ROOT)))
        for path in self.project_files(".json"):
            total += path.stat().st_size
        for extra in ("tss_monument/TSS_v10_MONUMENT.txt", "README.md"):
            path = PROJECT_ROOT / extra
            if path.exists():
                total += path.stat().st_size
        ok = not oversized and total <= 1_000_000
        self.record("sizes", ok,
                    f"total {total} bytes; oversized: {oversized or 'none'}")
        return ok

    def step6_bias_scan(self) -> bool:
        """Scan all sources for hidden bias variable names."""
        hits: List[str] = []
        for path in self.project_files(".py"):
            source = path.read_text(encoding="utf-8", errors="replace")
            for term in BIAS_TERMS:
                if re.search(re.escape(term), source):
                    hits.append(f"{term} in {path.relative_to(PROJECT_ROOT)}")
        ok = not hits
        self.record("bias_scan", ok, "ok" if ok else "; ".join(hits))
        return ok

    def step7_archive_mirrors(self) -> bool:
        """Verify every source entry in sources.json has an archive mirror."""
        path = PROJECT_ROOT / "data" / "sources.json"
        if not path.exists():
            self.record("archive_mirrors", False, "data/sources.json missing")
            return False
        try:
            sources = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            self.record("archive_mirrors", False, str(exc))
            return False
        missing = [s.get("url") for s in sources if not s.get("archive_url")]
        ok = not missing
        self.record("archive_mirrors", ok,
                    f"{len(sources)} sources, {len(missing)} without archive")
        return ok

    # -- orchestration -----------------------------------------------------

    def run(self) -> Dict[str, Any]:
        """Execute all steps and produce the CI report."""
        results = [
            ("syntax", self.step1_syntax),
            ("unit_tests", self.step2_tests),
            ("diagnostics", self.step3_diagnostics),
            ("end_to_end", self.step4_end_to_end),
            ("sizes", self.step5_sizes),
            ("bias_scan", self.step6_bias_scan),
            ("archive_mirrors", self.step7_archive_mirrors),
        ]
        for name, fn in results:
            try:
                fn()
            except Exception as exc:  # noqa: BLE001 - pipeline must not die
                self.record(name, False, f"pipeline error: {exc}")
        all_ok = all(s["passed"] for s in self.steps)
        report: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "pipeline": "tss_cicd v10",
            "overall_status": "BUILD_PASSED" if all_ok else "BUILD_FAILED",
            "steps": self.steps,
        }
        REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        if all_ok:
            TAG_PASSED.write_text(
                json.dumps(report, indent=2), encoding="utf-8")
            if TAG_FAILED.exists():
                TAG_FAILED.unlink()
        else:
            TAG_FAILED.write_text(
                json.dumps(report, indent=2), encoding="utf-8")
            if TAG_PASSED.exists():
                TAG_PASSED.unlink()
        return report


def main(argv: List[str]) -> int:
    """Run the pipeline, print the summary, exit non-zero on failure."""
    report = Pipeline().run()
    print(f"TSS v10 CI/CD: {report['overall_status']}")
    print(f"CI RESULT: {report['overall_status']}")
    for step in report["steps"]:
        print(f"  {step['step']:16s} "
              f"{'PASS' if step['passed'] else 'FAIL'} — {step['detail']}")
    print(f"report: {REPORT_PATH}")
    return 0 if report["overall_status"] == "BUILD_PASSED" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
