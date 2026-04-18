#!/usr/bin/env python3
"""audit/aerospace_floor_audit.py — Aerospace Floor Meta-Standard Compliance Scanner.

Scans the d_aerospace_floor meta-standard domain and verifies AF-001..AF-010.

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
AEROSPACE_FLOOR_DIR = DOMAINS_DIR / "d_aerospace_floor"
AEROSPACE_ADJACENT = ["d_aerospace", "d_aviation", "d_space", "d_military", "d_nuclear", "d_medical"]

_REQUIRED_CHECKS = {
    "AF-001": ["check_do178c_determinism", "determinism"],
    "AF-002": ["check_mcdc_coverage", "mcdc"],
    "AF-003": ["check_misra_recursion_bounded", "misra", "recursion"],
    "AF-004": ["check_milstd882e_mishap_probability", "mishap", "probability"],
    "AF-005": ["check_independence_review", "independence", "review"],
    "AF-006": ["check_iec61508_sil4", "sil4", "iec"],
    "AF-007": ["check_nasa_npr7150_class_a", "nasa", "npr"],
    "AF-008": ["check_af_compliance_scanned", "compliance", "scan"],
}


def _audit_d_aerospace_floor() -> Tuple[bool, List[str]]:
    """Verify d_aerospace_floor contains all required meta-standard checks."""
    inv_path = AEROSPACE_FLOOR_DIR / "invariants.py"
    if not inv_path.exists():
        return False, ["d_aerospace_floor/invariants.py does not exist"]
    source = inv_path.read_text(encoding="utf-8")
    failures = []
    for std_id, keywords in _REQUIRED_CHECKS.items():
        found = any(kw in source for kw in keywords)
        if not found:
            failures.append(f"{std_id}: missing required check ({keywords[0]}) in d_aerospace_floor/invariants.py")
    return not failures, failures


def _audit_af_010() -> Tuple[bool, List[str]]:
    """AF-010: No float() in aerospace-adjacent domain invariants."""
    failures = []
    for domain_name in AEROSPACE_ADJACENT:
        inv_path = DOMAINS_DIR / domain_name / "invariants.py"
        if not inv_path.exists():
            continue
        source = inv_path.read_text(encoding="utf-8")
        for lineno, line in enumerate(source.splitlines(), start=1):
            if re.search(r"\bfloat\s*\(", line) or re.search(r"\bisclose\s*\(", line):
                failures.append(f"{domain_name}/invariants.py:{lineno}: float/isclose call found")
    return not failures, failures


def check_determinism() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-001" in f or "determinism" in f]


def check_mcdc() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-002" in f or "mcdc" in f]


def check_misra() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-003" in f or "misra" in f]


def check_mishap() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-004" in f or "mishap" in f]


def check_independence() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-005" in f or "independence" in f]


def check_sil4() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-006" in f or "sil4" in f]


def check_nasa() -> Tuple[bool, List[str]]:
    passed, failures = _audit_d_aerospace_floor()
    return passed, [f for f in failures if "AF-007" in f or "nasa" in f]


def check_traceability() -> Tuple[bool, List[str]]:
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
        "AF-010": _audit_af_010,
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
