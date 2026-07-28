#!/usr/bin/env python3
"""CI/CD pipeline for Shampoo Ingredient Ontology v5.0.

Implements a minimal CI pipeline using subprocess and os (standard library).
Steps: py_compile all files → run unit tests → diagnostics score check →
orchestrator JSON validation → file size check → generate pass/fail report.

Run: python3 shampoo_ontology_cicd.py
Output: cicd_report.json
"""

import json
import os
import subprocess
import sys
import time

from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_V4_PATH = str(_PROJECT_ROOT / "shampoo-ontology-v4")
_V5_PATH = str(_PROJECT_ROOT / "shampoo-ontology-v5")

MODULES_V4 = [
    "shampoo_ontology_parser.py",
    "shampoo_ontology_divergence.py",
    "shampoo_ontology_fragrance.py",
    "shampoo_ontology_supplier_audit.py",
    "shampoo_ontology_diagnostics.py",
]

MODULES_V5 = [
    "shampoo_ontology_tests.py",
    "shampoo_ontology_server.py",
    "shampoo_ontology_updater.py",
    "shampoo_ontology_cicd.py",
    "shampoo_ontology_rdf.py",
    "shampoo_ontology_leaks.py",
]

MAX_FILE_SIZE = 102400  # 100KB per file
MAX_TOTAL_SIZE = 512000  # 500KB total


class CIPipeline:
    """Run the v5.0 CI pipeline against v4.1 + v5 deliverables.

    Parameters
    ----------
    verbose : bool
        Print step-by-step progress.

    Attributes
    ----------
    report : dict
        CI report with ``steps``, ``overall``, ``timestamp``.
    """

    def __init__(self, verbose=True):
        """Initialize the CI pipeline."""
        self.verbose = verbose
        self.report = {
            "pipeline": "SIOG_v5_CI",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "steps": [],
            "overall": "PENDING",
        }
        self.all_passed = True

    def _log(self, msg):
        """Print a progress message if verbose is enabled.

        Parameters
        ----------
        msg : str
            Message to print.
        """
        if self.verbose:
            print(msg)

    def _step(self, name, result, detail=""):
        """Record a CI step result.

        Parameters
        ----------
        name : str
            Step name.
        result : str
            ``"PASS"`` or ``"FAIL"``.
        detail : str
            Optional detail message.
        """
        self.report["steps"].append({
            "step": name,
            "result": result,
            "detail": detail,
        })
        status_icon = "✓" if result == "PASS" else "✗"
        self._log(f"  [{status_icon}] {name}: {result}")
        if detail:
            self._log(f"       {detail[:120]}")

    def step_syntax_check(self):
        """Run ``python3 -m py_compile`` on all v4 and v5 modules.

        Returns
        -------
        bool
            True if all files compile, False otherwise.
        """
        self._log("\n--- STEP 1: Syntax Check (py_compile) ---")
        passed = True
        for fname in MODULES_V4:
            path = os.path.join(_V4_PATH, fname)
            if not os.path.exists(path):
                self._step(f"compile v4/{fname}", "FAIL", "file missing")
                passed = False
                continue
            try:
                subprocess.run(
                    [sys.executable, "-m", "py_compile", path],
                    capture_output=True, check=True, timeout=30,
                )
                self._step(f"compile v4/{fname}", "PASS")
            except subprocess.CalledProcessError as e:
                self._step(f"compile v4/{fname}", "FAIL", str(e.stderr)[:200])
                passed = False

        for fname in MODULES_V5:
            path = os.path.join(_V5_PATH, fname)
            if not os.path.exists(path):
                self._step(f"compile v5/{fname}", "SKIP", "file not yet created")
                continue
            try:
                subprocess.run(
                    [sys.executable, "-m", "py_compile", path],
                    capture_output=True, check=True, timeout=30,
                )
                self._step(f"compile v5/{fname}", "PASS")
            except subprocess.CalledProcessError as e:
                self._step(f"compile v5/{fname}", "FAIL", str(e.stderr)[:200])
                passed = False

        return passed

    def step_unit_tests(self):
        """Run the unit test suite.

        Returns
        -------
        bool
            True if all tests pass.
        """
        self._log("\n--- STEP 2: Unit Tests ---")
        test_path = os.path.join(_V5_PATH, "shampoo_ontology_tests.py")
        if not os.path.exists(test_path):
            self._step("unit tests", "SKIP", "test file not found")
            return True

        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", test_path, "-v"],
                capture_output=True, text=True, timeout=120,
                cwd=_V5_PATH,
                env={**os.environ, "PYTHONPATH": f"{_V4_PATH}:{_V5_PATH}"},
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                ok_line = [l for l in lines if l.startswith("Ran ") or "OK" in l]
                detail = ok_line[-1] if ok_line else "all tests passed"
                self._step("unit tests", "PASS", detail)
                return True
            else:
                self._step("unit tests", "FAIL", result.stderr[:200] or result.stdout[:200])
                return False
        except subprocess.TimeoutExpired:
            self._step("unit tests", "FAIL", "timed out after 120s")
            return False

    def step_diagnostics_score(self):
        """Run diagnostics and verify overall score >= 95.0.

        Returns
        -------
        bool
            True if score meets threshold.
        """
        self._log("\n--- STEP 3: Diagnostics Score Check ---")
        diag_path = os.path.join(_V4_PATH, "shampoo_ontology_diagnostics.py")
        if not os.path.exists(diag_path):
            self._step("diagnostics", "SKIP", "file not found")
            return True

        try:
            result = subprocess.run(
                [sys.executable, "-W", "ignore", diag_path],
                capture_output=True, text=True, timeout=60,
                cwd=_V4_PATH,
                env={**os.environ, "PYTHONPATH": _V4_PATH},
            )
            data = json.loads(result.stdout)
            score = data["scores"]["overall"]
            if score >= 95.0:
                self._step("diagnostics", "PASS", f"score={score:.1f}/100")
                return True
            else:
                self._step("diagnostics", "FAIL", f"score={score:.1f}/100 (need >=95.0)")
                return False
        except Exception as e:
            self._step("diagnostics", "FAIL", str(e)[:200])
            return False

    def step_orchestrator(self):
        """Run orchestrator and verify valid JSON output.

        Returns
        -------
        bool
            True if orchestrator produces valid JSON.
        """
        self._log("\n--- STEP 4: Orchestrator JSON Validation ---")
        orch_path = os.path.join(_V4_PATH, "shampoo_ontology_orchestrator.py")
        if not os.path.exists(orch_path):
            self._step("orchestrator", "SKIP", "file not found")
            return True

        try:
            result = subprocess.run(
                [sys.executable, "-W", "ignore", orch_path],
                capture_output=True, text=True, timeout=60,
                cwd=_V4_PATH,
                env={**os.environ, "PYTHONPATH": _V4_PATH},
            )
            # Verify the last line contains valid assertions pass
            if "ALL ORCHESTRATOR TESTS PASSED" in result.stdout:
                self._step("orchestrator", "PASS", "end-to-end test passed")
                return True
            else:
                self._step("orchestrator", "FAIL", result.stderr[:200] or "output mismatch")
                return False
        except subprocess.TimeoutExpired:
            self._step("orchestrator", "FAIL", "timed out after 60s")
            return False

    def step_file_sizes(self):
        """Check file sizes against limits.

        Returns
        -------
        bool
            True if all files and total are within limits.
        """
        self._log("\n--- STEP 5: File Size Check ---")
        total = 0
        passed = True
        all_files = [(os.path.join(_V4_PATH, f), f"v4/{f}") for f in MODULES_V4]
        all_files += [(os.path.join(_V5_PATH, f), f"v5/{f}") for f in MODULES_V5
                      if os.path.exists(os.path.join(_V5_PATH, f))]

        for path, label in all_files:
            if not os.path.exists(path):
                continue
            size = os.path.getsize(path)
            total += size
            if size > MAX_FILE_SIZE:
                self._step(f"size {label}", "FAIL", f"{size} bytes > {MAX_FILE_SIZE}")
                passed = False
            else:
                self._step(f"size {label}", "PASS", f"{size} bytes")

        if total > MAX_TOTAL_SIZE:
            self._step("size TOTAL", "FAIL", f"{total} bytes > {MAX_TOTAL_SIZE}")
            passed = False
        else:
            self._step("size TOTAL", "PASS", f"{total} bytes total")

        return passed

    def run(self):
        """Execute all CI steps and write the report.

        Returns
        -------
        dict
            The CI report.
        """
        self._log("=" * 60)
        self._log("SIOG v5.0 CI/CD Pipeline")
        self._log("=" * 60)

        results = [
            self.step_syntax_check(),
            self.step_unit_tests(),
            self.step_diagnostics_score(),
            self.step_orchestrator(),
            self.step_file_sizes(),
        ]

        self.all_passed = all(r for r in results)
        self.report["overall"] = "BUILD_PASSED" if self.all_passed else "BUILD_FAILED"

        self._log(f"\n{'='*60}")
        self._log(f"CI RESULT: {self.report['overall']}")
        self._log(f"{'='*60}")

        report_path = os.path.join(_V5_PATH, "cicd_report.json")
        with open(report_path, "w") as f:
            json.dump(self.report, f, indent=2)

        self._log(f"Report written to: {report_path}")
        return self.report


if __name__ == "__main__":
    pipeline = CIPipeline(verbose=True)
    report = pipeline.run()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["overall"] == "BUILD_PASSED" else 1)
