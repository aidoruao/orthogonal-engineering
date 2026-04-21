"""audit/scope_reduction_detector.py — Campaign Spec vs Reality Checker.

Given a campaign specification JSON file listing expected outputs,
checks which files and directories actually exist on disk.
For Python files, also verifies they are non-empty and do not contain
pass-only function bodies.

Run as:
    python3 audit/scope_reduction_detector.py <campaign_spec.json> [--output <path>]

Exit code: 0 if all delivered, 1 if any missing.
Persists JSON report to audit/SCOPE_REDUCTION_REPORT.json by default.

Standard: SCOPE-002
Falsifies if: reports all delivered when files are missing.
falsifies_if: reports all delivered when files are missing.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject

DEFAULT_REPORT_PATH = Path(__file__).parent / "SCOPE_REDUCTION_REPORT.json"


def _is_pass_only_py(path: Path) -> bool:
    """Check if a .py file contains only pass bodies in all top-level functions."""
    try:
        source = path.read_text(encoding="utf-8").strip()
    except OSError:
        return True

    if not source:
        return True

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False  # Can't parse, so not pass-only

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body = node.body
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                return True
    return False


def check_expected_output(item: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Check a single expected output. Returns (delivered, issues)."""
    path_str = item.get("path", "")
    item_type = item.get("type", "file")
    path = REPO_ROOT / path_str
    issues: List[str] = []

    if item_type == "file":
        if not path.exists():
            issues.append("file missing")
        elif not path.is_file():
            issues.append("exists but is not a file")
        else:
            try:
                content = path.read_text(encoding="utf-8")
                if not content.strip():
                    issues.append("file is empty")
            except OSError:
                issues.append("cannot read file")

            if path.suffix == ".py" and _is_pass_only_py(path):
                issues.append("file contains pass-only bodies")
    elif item_type == "directory":
        if not path.exists():
            issues.append("directory missing")
        elif not path.is_dir():
            issues.append("exists but is not a directory")
        else:
            try:
                if not any(path.iterdir()):
                    issues.append("directory is empty")
            except OSError:
                issues.append("cannot read directory")
    else:
        issues.append(f"unknown type: {item_type}")

    return len(issues) == 0, issues


def run_scope_reduction_detector(
    spec_path: Path,
    output_path: Path = DEFAULT_REPORT_PATH,
) -> Tuple[bool, ProofObject]:
    """Run scope reduction detection against a campaign spec.

    Falsifies if: reports all delivered when files are missing.
    falsifies_if: reports all delivered when files are missing.
    """
    if not spec_path.exists():
        result = {
            "campaign": "",
            "total_expected": 0,
            "total_delivered": 0,
            "delivery_ratio": "0/1",
            "missing": [],
            "delivered": [],
            "scope_reduction_detected": True,
            "error": f"Spec file not found: {spec_path}",
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
        proof = ProofObject(
            rule="run_scope_reduction_detector",
            premises=["spec_path missing"],
            conclusion=f"FAIL: Spec file not found: {spec_path}",
        )
        return False, proof

    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        result = {
            "campaign": "",
            "total_expected": 0,
            "total_delivered": 0,
            "delivery_ratio": "0/1",
            "missing": [],
            "delivered": [],
            "scope_reduction_detected": True,
            "error": f"Cannot parse spec: {exc}",
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
        proof = ProofObject(
            rule="run_scope_reduction_detector",
            premises=["spec parse error"],
            conclusion=f"FAIL: Cannot parse spec: {exc}",
        )
        return False, proof

    campaign = spec.get("campaign", "")
    expected = spec.get("expected_outputs", [])

    missing: List[Dict[str, Any]] = []
    delivered: List[Dict[str, Any]] = []

    for item in expected:
        ok, issues = check_expected_output(item)
        record = {"path": item.get("path"), "type": item.get("type"), "issues": issues}
        if ok:
            delivered.append(record)
        else:
            missing.append(record)

    total = len(expected)
    num_delivered = len(delivered)
    ratio = Fraction(num_delivered, max(total, 1))
    scope_reduction = num_delivered < total

    result = {
        "campaign": campaign,
        "total_expected": total,
        "total_delivered": num_delivered,
        "delivery_ratio": f"{ratio.numerator}/{ratio.denominator}",
        "missing": missing,
        "delivered": delivered,
        "scope_reduction_detected": scope_reduction,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    all_pass = not scope_reduction
    conclusion = (
        f"PASS: {num_delivered}/{total} expected outputs delivered for '{campaign}'"
        if all_pass
        else f"FAIL: {total - num_delivered}/{total} missing for '{campaign}'"
    )
    proof = ProofObject(
        rule="run_scope_reduction_detector",
        premises=[
            f"total_expected={total}",
            f"total_delivered={num_delivered}",
        ],
        conclusion=conclusion,
    )
    return all_pass, proof


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Campaign scope reduction detector"
    )
    parser.add_argument(
        "spec",
        type=Path,
        help="Path to campaign spec JSON file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON report",
    )
    args = parser.parse_args(argv)

    passed, proof = run_scope_reduction_detector(
        spec_path=args.spec, output_path=args.output
    )
    print(proof.conclusion)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
