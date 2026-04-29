"""audit/depth_measurement.py — Per-Domain Depth Scorer.

Measures per-domain depth scores using exact Fraction arithmetic.
Depth indicates implementation richness: LOC, check count, dataclass count,
fraction field count, computational check count, and invariant coverage.

Per domain, computes:
  depth_score = Fraction(
    loc_implementation * 2 +
    loc_invariants * 2 +
    check_count * 30 +
    dataclass_count * 20 +
    fraction_field_count * 10 +
    computational_check_count * 50 +
    has_run_all * 100 +
    has_failing_test * 100,
    1000
  )

Run as:
    python3 audit/depth_measurement.py [--output <path>]

Returns exit code 0 if polymathic_check passes (all domains >= 200/1000),
1 otherwise. Persists JSON report to audit/DEPTH_REPORT.json by default.

Standard: DEPTH-001
Falsifies if: depth_score is computed using float instead of Fraction,
              or polymathic_check returns True when any domain is below threshold.
falsifies_if: depth_score is computed using float instead of Fraction,
              or polymathic_check returns True when any domain is below threshold.
"""

from __future__ import annotations

import ast
import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

DOMAINS_DIR = REPO_ROOT / "src" / "domains"
DEFAULT_REPORT_PATH = Path(__file__).parent / "DEPTH_REPORT.json"
THRESHOLD = Fraction(200, 1000)


def _count_non_blank_non_comment_lines(source: str) -> int:
    """Count lines that are not blank and not pure comments."""
    count = 0
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


def _count_check_functions(tree: ast.AST) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("check_")
    )


def _count_dataclasses(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                    count += 1
                elif isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                        count += 1
    return count


def _count_fraction_fields(tree: ast.AST) -> int:
    """Count fields annotated with Fraction across all dataclasses."""
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            ann = node.annotation
            if isinstance(ann, ast.Name) and ann.id == "Fraction":
                count += 1
            elif isinstance(ann, ast.Attribute):
                # fractions.Fraction or similar
                if isinstance(ann.value, ast.Name) and ann.value.id == "fractions" and ann.attr == "Fraction":
                    count += 1
    return count


def _has_run_all_invariants(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_all_invariants":
            return True
    return False


def _has_failing_test_case(tree: ast.AST) -> bool:
    """Check if run_all_invariants contains a FAIL case (string literal with 'FAIL')."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_all_invariants":
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and "FAIL" in sub.value:
                    return True
    return False


def _load_computational_checks() -> Dict[str, int]:
    """Load tautology report and return per-domain computational check counts."""
    tautology_path = Path(__file__).parent / "TAUTOLOGY_REPORT.json"
    if not tautology_path.exists():
        return {}
    try:
        data = json.loads(tautology_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    result: Dict[str, int] = {}
    for domain, dinfo in data.get("domains", {}).items():
        computational = sum(
            1 for c in dinfo.get("checks", []) if c.get("type") == "computational"
        )
        result[domain] = computational
    return result


def measure_domain_depth(domain_dir: Path, computational_counts: Dict[str, int]) -> Dict[str, Any]:
    """Compute depth metrics for a single domain.

    Falsifies if: any metric is computed with float arithmetic.
    falsifies_if: any metric is computed with float arithmetic.
    """
    domain = domain_dir.name
    inv_path = domain_dir / "invariants.py"
    impl_path = domain_dir / "implementation.py"

    loc_implementation = 0
    loc_invariants = 0
    check_count = 0
    dataclass_count = 0
    fraction_field_count = 0
    has_run_all = False
    has_failing_test = False

    if inv_path.exists():
        try:
            inv_source = inv_path.read_text(encoding="utf-8")
            loc_invariants = _count_non_blank_non_comment_lines(inv_source)
            inv_tree = ast.parse(inv_source)
            check_count = _count_check_functions(inv_tree)
            has_run_all = _has_run_all_invariants(inv_tree)
            has_failing_test = _has_failing_test_case(inv_tree)
        except (OSError, SyntaxError):
            pass

    if impl_path.exists():
        try:
            impl_source = impl_path.read_text(encoding="utf-8")
            loc_implementation = _count_non_blank_non_comment_lines(impl_source)
            impl_tree = ast.parse(impl_source)
            dataclass_count = _count_dataclasses(impl_tree)
            fraction_field_count = _count_fraction_fields(impl_tree)
        except (OSError, SyntaxError):
            pass

    computational_check_count = computational_counts.get(domain, 0)

    has_run_all_val = 1 if has_run_all else 0
    has_failing_test_val = 1 if has_failing_test else 0

    numerator = (
        loc_implementation * 2
        + loc_invariants * 2
        + check_count * 30
        + dataclass_count * 20
        + fraction_field_count * 10
        + computational_check_count * 50
        + has_run_all_val * 100
        + has_failing_test_val * 100
    )

    depth_score = Fraction(numerator, 1000)

    return {
        "loc_implementation": loc_implementation,
        "loc_invariants": loc_invariants,
        "check_count": check_count,
        "dataclass_count": dataclass_count,
        "fraction_field_count": fraction_field_count,
        "computational_check_count": computational_check_count,
        "has_run_all": has_run_all,
        "has_failing_test": has_failing_test,
        "depth_score": f"{depth_score.numerator}/{depth_score.denominator}",
    }


def run_depth_measurement(
    # TODO: Expand run_depth_measurement() - stub detected by Yeshua Agent
    output_path: Path = DEFAULT_REPORT_PATH,
) -> Tuple[bool, Dict[str, Any]]:
    """Run depth measurement across all domains.

    Falsifies if: polymathic_check is True while any domain is below threshold.
    falsifies_if: polymathic_check is True while any domain is below threshold.
    """
    if not DOMAINS_DIR.exists():
        result = {
            "domains": {},
            "summary": {
                "mean_depth": "0/1",
                "min_depth": {"domain": "", "score": "0/1"},
                "max_depth": {"domain": "", "score": "0/1"},
                "below_threshold": [],
                "polymathic_check": False,
            },
            "error": "src/domains/ does not exist",
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
        return False, result

    computational_counts = _load_computational_checks()
    domains_data: Dict[str, Dict[str, Any]] = {}

    for domain_dir in sorted(DOMAINS_DIR.iterdir()):
        if not domain_dir.is_dir() or domain_dir.name.startswith("_"):
            continue
        domains_data[domain_dir.name] = measure_domain_depth(
            domain_dir, computational_counts
        )

    scores: List[Tuple[str, Fraction]] = []
    for domain, data in domains_data.items():
        score_str = data["depth_score"]
        num, den = score_str.split("/")
        scores.append((domain, Fraction(int(num), int(den))))

    if scores:
        mean_score = Fraction(
            sum(s.numerator * s.denominator for _, s in scores),
            sum(s.denominator for _, s in scores),
        )
        min_domain, min_score = min(scores, key=lambda x: x[1])
        max_domain, max_score = max(scores, key=lambda x: x[1])
    else:
        mean_score = Fraction(0, 1)
        min_domain, min_score = "", Fraction(0, 1)
        max_domain, max_score = "", Fraction(0, 1)

    below_threshold = [
        domain for domain, score in scores if score < THRESHOLD
    ]
    polymathic_check = len(below_threshold) == 0 and len(scores) > 0

    result = {
        "domains": domains_data,
        "summary": {
            "mean_depth": f"{mean_score.numerator}/{mean_score.denominator}",
            "min_depth": {
                "domain": min_domain,
                "score": f"{min_score.numerator}/{min_score.denominator}",
            },
            "max_depth": {
                "domain": max_domain,
                "score": f"{max_score.numerator}/{max_score.denominator}",
            },
            "below_threshold": below_threshold,
            "polymathic_check": polymathic_check,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    return polymathic_check, result


def main(argv: List[str] = sys.argv[1:]) -> int:
    parser = argparse.ArgumentParser(
        description="Per-domain depth measurement"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path for the JSON report",
    )
    args = parser.parse_args(argv)

    passed, result = run_depth_measurement(output_path=args.output)
    summary = result["summary"]
    print(
        f"Depth measurement: mean={summary['mean_depth']} "
        f"min={summary['min_depth']['domain']}={summary['min_depth']['score']} "
        f"max={summary['max_depth']['domain']}={summary['max_depth']['score']} "
        f"below_threshold={len(summary['below_threshold'])} "
        f"polymathic_check={summary['polymathic_check']}"
    )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
