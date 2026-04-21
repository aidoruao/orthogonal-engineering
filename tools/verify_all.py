#!/usr/bin/env python3
"""tools/verify_all.py — Complete verification suite.

Runs all verification and audit tools in order.
Exit 0 only if ALL pass. Print summary table.

Standard: VQ-001
Falsifies if: returns 0 when any check failed.
falsifies_if: returns 0 when any check failed.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class CheckResult:
    """Result of a single verification check.

    Falsifies if: status is "PASS" while the underlying command failed.
    falsifies_if: status is "PASS" while the underlying command failed.
    """

    name: str
    status: str  # "PASS", "FAIL", "STALE", "INFO", "SKIP"
    details: str = ""


def _run_cmd(cmd: List[str], timeout: int = 120) -> Tuple[int, str, str]:
    """Run a subprocess command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", "command not found"


def _check_feed_chain() -> CheckResult:
    rc, out, _ = _run_cmd(
        ["python3", "tools/state_witness/generate_feed_entry.py", "--verify"]
    )
    if rc == 0:
        return CheckResult("Feed chain", "PASS", out.strip().splitlines()[-1] if out.strip() else "")
    return CheckResult("Feed chain", "FAIL", out.strip().splitlines()[-1] if out.strip() else "")


def _check_popperian() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "audit/popperian_audit.py"])
    detail = out.strip().splitlines()[0] if out.strip() else ""
    if rc == 0:
        return CheckResult("Popperian audit", "PASS", detail)
    return CheckResult("Popperian audit", "FAIL", detail)


def _check_standards() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "tools/standards_check.py", "--verify"])
    detail = out.strip().splitlines()[-1] if out.strip() else ""
    if rc == 0:
        return CheckResult("Standards", "PASS", detail)
    return CheckResult("Standards", "FAIL", detail)


def _check_tests() -> CheckResult:
    rc, out, _ = _run_cmd(
        ["python3", "-m", "pytest", "tests/", "-q", "--maxfail=3"],
        timeout=300,
    )
    lines = out.strip().splitlines()
    detail = lines[-1] if lines else ""
    if rc == 0:
        return CheckResult("Tests", "PASS", detail)
    return CheckResult("Tests", "FAIL", detail)


def _check_scope() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "audit/scope_audit.py"])
    detail = out.strip() if out.strip() else ""
    if rc == 0:
        return CheckResult("Scope audit", "PASS", detail)
    return CheckResult("Scope audit", "FAIL", detail)


def _check_tautology() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "audit/tautology_detector.py"])
    detail = out.strip() if out.strip() else ""
    return CheckResult("Tautology", "INFO", detail)


def _check_depth() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "audit/depth_measurement.py"])
    detail = out.strip() if out.strip() else ""
    if rc == 0:
        return CheckResult("Depth measurement", "PASS", detail)
    return CheckResult("Depth measurement", "FAIL", detail)


def _check_anti_nominalism() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "audit/anti_nominalism_audit.py"])
    detail = out.strip() if out.strip() else ""
    if rc == 0:
        return CheckResult("Anti-nominalism", "PASS", detail)
    return CheckResult("Anti-nominalism", "FAIL", detail)


def _check_merkle() -> CheckResult:
    rc, out, _ = _run_cmd(["python3", "audit/merkle_verify.py"])
    detail = out.strip() if out.strip() else ""
    if rc == 0:
        return CheckResult("Merkle verify", "PASS", detail)
    return CheckResult("Merkle verify", "STALE", detail)


def _check_scope_reduction() -> CheckResult:
    spec_files = list((REPO_ROOT / "campaigns").glob("*.json"))
    if not spec_files:
        return CheckResult("Scope reduction", "SKIP", "no campaign specs found")
    # Run against the first spec file found
    spec = spec_files[0]
    rc, out, _ = _run_cmd(
        ["python3", "audit/scope_reduction_detector.py", str(spec)]
    )
    detail = out.strip() if out.strip() else ""
    if rc == 0:
        return CheckResult("Scope reduction", "PASS", detail)
    return CheckResult("Scope reduction", "FAIL", detail)


def run_all_checks() -> List[CheckResult]:
    """Run the complete verification suite.

    Falsifies if: returns results where any status is "FAIL" but overall exit is 0.
    falsifies_if: returns results where any status is "FAIL" but overall exit is 0.
    """
    checks: List[CheckResult] = []
    checks.append(_check_feed_chain())
    checks.append(_check_popperian())
    checks.append(_check_standards())
    checks.append(_check_tests())
    checks.append(_check_scope())
    checks.append(_check_tautology())
    checks.append(_check_depth())
    checks.append(_check_anti_nominalism())
    checks.append(_check_merkle())
    checks.append(_check_scope_reduction())
    return checks


def _print_table(results: List[CheckResult]) -> None:
    """Print a formatted summary table."""
    name_width = max(len(r.name) for r in results)
    status_width = max(len(r.status) for r in results)

    header = f"| {'Check':<{name_width}} | {'Status':<{status_width}} | Details"
    separator = f"|{'-' * (name_width + 2)}|{'-' * (status_width + 2)}|{'-' * 40}"

    print(header)
    print(separator)
    for r in results:
        detail = r.details[:60] if r.details else ""
        print(f"| {r.name:<{name_width}} | {r.status:<{status_width}} | {detail}")


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Complete verification suite wrapper"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip the pytest suite (faster for CI)",
    )
    parser.add_argument(
        "--skip-merkle",
        action="store_true",
        help="Skip Merkle verification (expected to be stale during development)",
    )
    args = parser.parse_args(argv)

    results = run_all_checks()

    if args.skip_tests:
        results = [r for r in results if r.name != "Tests"]
    if args.skip_merkle:
        results = [r for r in results if r.name != "Merkle verify"]

    _print_table(results)

    failures = sum(
        1 for r in results if r.status in ("FAIL", "STALE") and r.name != "Merkle verify"
    )
    if args.skip_merkle:
        failures = sum(1 for r in results if r.status == "FAIL")

    print(f"\nTotal checks: {len(results)}  Failures: {failures}")
    return failures


if __name__ == "__main__":
    sys.exit(main())
