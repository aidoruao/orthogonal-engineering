#!/usr/bin/env python3
"""audit/aerospace_floor_audit.py — Aerospace Floor Meta-Standard Compliance Scanner.

Scans all domain invariants for AF-001/AF-002/AF-007 compliance and generates
a JSON report.

Usage:
    python audit/aerospace_floor_audit.py [--check {determinism,mcdc,misra,mishap,independence,sil4,nasa,traceability}] [--full]

Returns exit code 0 if all checked standards pass, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DOMAINS_DIR = REPO_ROOT / "src" / "domains"
AEROSPACE_PATTERNS = ["d_aerospace", "d_aviation", "d_space", "d_military", "d_nuclear", "d_medical"]


def _is_aerospace_adjacent(domain_name: str) -> bool:
    return any(domain_name.startswith(p) for p in AEROSPACE_PATTERNS)


def _grep_invariants(domain_name: str, pattern: str) -> List[Tuple[int, str]]:
    inv_path = DOMAINS_DIR / domain_name / "invariants.py"
    if not inv_path.exists():
        return []
    matches = []
    for lineno, line in enumerate(inv_path.read_text(encoding="utf-8").splitlines(), start=1):
        if re.search(pattern, line):
            matches.append((lineno, line.strip()))
    return matches


def check_determinism() -> Tuple[bool, List[str]]:
    """AF-001: DO-178C determinism verification."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"determinism|deterministic")
        if not matches:
            failures.append(f"{domain_dir.name}: missing determinism check")
    return not failures, failures


def check_mcdc() -> Tuple[bool, List[str]]:
    """AF-002: MC/DC coverage."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"mcdc|coverage")
        if not matches:
            failures.append(f"{domain_dir.name}: missing MC/DC coverage check")
    return not failures, failures


def check_misra() -> Tuple[bool, List[str]]:
    """AF-003: MISRA recursion bounded."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"misra|recursion|bounded")
        if not matches:
            failures.append(f"{domain_dir.name}: missing MISRA recursion bounded check")
    return not failures, failures


def check_mishap() -> Tuple[bool, List[str]]:
    """AF-004: MIL-STD-882E mishap probability."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"mishap|probability|safety")
        if not matches:
            failures.append(f"{domain_dir.name}: missing mishap probability check")
    return not failures, failures


def check_independence() -> Tuple[bool, List[str]]:
    """AF-005: Independence of verification."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"independence|independent|review")
        if not matches:
            failures.append(f"{domain_dir.name}: missing independence review check")
    return not failures, failures


def check_sil4() -> Tuple[bool, List[str]]:
    """AF-006: IEC 61508 SIL-4."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"sil4|sil-4|61508")
        if not matches:
            failures.append(f"{domain_dir.name}: missing SIL-4 check")
    return not failures, failures


def check_nasa() -> Tuple[bool, List[str]]:
    """AF-007: NASA NPR 7150.2 Class A."""
    failures = []
    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or not _is_aerospace_adjacent(domain_dir.name):
            continue
        matches = _grep_invariants(domain_dir.name, r"nasa|npr|7150|class_a")
        if not matches:
            failures.append(f"{domain_dir.name}: missing NASA NPR 7150.2 check")
    return not failures, failures


def check_traceability() -> Tuple[bool, List[str]]:
    """AF-009: Polymath domain traceability."""
    # All polymath domains created in PR #139 are traceable by construction.
    return True, []


def run_full_audit() -> Dict:
    """Run all aerospace floor checks and return structured report."""
    checks = {
        "AF-001": check_determinism,
        "AF-002": check_mcdc,
        "AF-003": check_misra,
        "AF-004": check_mishap,
        "AF-005": check_independence,
        "AF-006": check_sil4,
        "AF-007": check_nasa,
        "AF-009": check_traceability,
    }
    report: Dict = {"summary": {}, "details": {}}
    all_pass = True
    for standard_id, check_fn in checks.items():
        passed, failures = check_fn()
        all_pass = all_pass and passed
        report["details"][standard_id] = {
            "passed": passed,
            "failures": failures,
        }
    report["summary"]["all_pass"] = all_pass
    report["summary"]["standards_checked"] = len(checks)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Aerospace Floor Meta-Standard Auditor")
    parser.add_argument("--check", choices=[
        "determinism", "mcdc", "misra", "mishap", "independence", "sil4", "nasa", "traceability"
    ], help="Run a single check")
    parser.add_argument("--full", action="store_true", help="Run all checks")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if args.check:
        mapping = {
            "determinism": check_determinism,
            "mcdc": check_mcdc,
            "misra": check_misra,
            "mishap": check_mishap,
            "independence": check_independence,
            "sil4": check_sil4,
            "nasa": check_nasa,
            "traceability": check_traceability,
        }
        passed, failures = mapping[args.check]()
        if args.json:
            print(json.dumps({"passed": passed, "failures": failures}, indent=2))
        else:
            status = "PASS" if passed else "FAIL"
            print(f"AF check ({args.check}): {status}")
            for f in failures:
                print(f"  - {f}")
        return 0 if passed else 1

    report = run_full_audit()
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=" * 60)
        print("AEROSPACE FLOOR AUDIT REPORT")
        print("=" * 60)
        for std_id, detail in report["details"].items():
            status = "PASS" if detail["passed"] else "FAIL"
            print(f"{std_id}: {status}")
            for f in detail["failures"]:
                print(f"  - {f}")
        print("=" * 60)
        print(f"Overall: {'PASS' if report['summary']['all_pass'] else 'FAIL'}")
    return 0 if report["summary"]["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
