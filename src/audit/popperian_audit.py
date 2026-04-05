"""
Popperian Audit — src/audit/popperian_audit.py

Audits the repository for claims without falsification tests.
ZERO EXEMPTIONS: theological correspondences are treated identically to all other claims.
A POPPERIAN_EXEMPT classification is a FAIL, not a tolerated status.

Exit codes:
  0 — all claims have falsification tests (PASS)
  1 — one or more claims lack falsification tests (FAIL)

Usage:
  python src/audit/popperian_audit.py
  python src/audit/popperian_audit.py --report-path restoration/popperian_audit_report.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Root of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Paths
ONTOLOGY_PATH = REPO_ROOT / "ontology" / "ontology.json"
THEOLOGY_PATH = REPO_ROOT / "minimal_ai_ide" / "MATHEMATICAL_THEOLOGY_V60_SUMMARY.md"
TESTS_DIR = REPO_ROOT / "tests"
DEFAULT_REPORT_PATH = REPO_ROOT / "restoration" / "popperian_audit_report.json"

# Theological correspondence falsification test IDs (F_THEO_001-006)
THEOLOGICAL_FALSIFICATION_IDS = {
    "F_THEO_001",
    "F_THEO_002",
    "F_THEO_003",
    "F_THEO_004",
    "F_THEO_005",
    "F_THEO_006",
}


def _find_test_file_for_id(falsification_id: str) -> str | None:
    """Return path to test file implementing the given falsification ID, or None."""
    pattern = falsification_id.lower()
    # Search tests/ for any file containing the ID string
    for test_file in sorted(TESTS_DIR.glob("*.py")):
        try:
            content = test_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if falsification_id in content or pattern in test_file.stem:
            return str(test_file.relative_to(REPO_ROOT))
    return None


def _audit_ontology_domains() -> list[dict[str, Any]]:
    """Audit all domains in ontology.json for falsification test coverage."""
    if not ONTOLOGY_PATH.exists():
        return [{"error": f"ontology not found: {ONTOLOGY_PATH}"}]

    with ONTOLOGY_PATH.open(encoding="utf-8") as f:
        ontology = json.load(f)

    domains = ontology.get("domains", [])
    results = []

    for domain in domains:
        domain_id = domain.get("id", "UNKNOWN")
        f_test_id = domain.get("example_falsification_test", "")

        if not f_test_id:
            results.append({
                "domain_id": domain_id,
                "falsification_id": None,
                "test_file": None,
                "popperian_status": "FAIL",
                "reason": "No falsification test ID declared in ontology",
            })
            continue

        test_file = _find_test_file_for_id(f_test_id)
        if test_file:
            results.append({
                "domain_id": domain_id,
                "falsification_id": f_test_id,
                "test_file": test_file,
                "popperian_status": "PASS",
                "reason": "Falsification test found",
            })
        else:
            results.append({
                "domain_id": domain_id,
                "falsification_id": f_test_id,
                "test_file": None,
                "popperian_status": "FAIL",
                "reason": f"No test file found implementing {f_test_id}",
            })

    return results


def _audit_theological_correspondences() -> list[dict[str, Any]]:
    """
    Audit theological correspondences for falsification test coverage.

    CRITICAL: There are NO exemptions for theological claims.
    popperian_status: 'POPPERIAN_EXEMPT' is treated as 'FAIL'.
    Theological claims are claims. Claims require falsification tests.
    """
    results = []

    # The 6 required theological falsification tests
    correspondences = [
        {
            "id": "F_THEO_001",
            "math_concept": "H (fixed point)",
            "theological_concept": "Mediator (Christ)",
            "description": "Fixed-point operator H converges on all contractive mappings",
        },
        {
            "id": "F_THEO_002",
            "math_concept": "κ (salvation operator)",
            "theological_concept": "Grace (unearned)",
            "description": "κ is input-invariant: κ(x) == κ(y) for all x, y (not conditioned on merit)",
        },
        {
            "id": "F_THEO_003",
            "math_concept": "λ (logos / ordering principle)",
            "theological_concept": "Ordering principle",
            "description": "λ is idempotent: λ(λ(S)) == λ(S) for all sets S",
        },
        {
            "id": "F_THEO_004",
            "math_concept": "kenosis (self-limitation)",
            "theological_concept": "Self-limitation for others' benefit",
            "description": "Kenotic override logs the override event; silent failure is a violation",
        },
        {
            "id": "F_THEO_005",
            "math_concept": "agape (unconditional)",
            "theological_concept": "Unconditional constraint satisfaction",
            "description": "Agape constraint satisfied for all inputs, including adversarial ones",
        },
        {
            "id": "F_THEO_006",
            "math_concept": "chalcedon (dual-nature)",
            "theological_concept": "Dual-nature without contradiction",
            "description": "System holds two incompatible invariants simultaneously; neither overrides silently",
        },
    ]

    for corr in correspondences:
        f_id = corr["id"]
        test_file = _find_test_file_for_id(f_id)

        if test_file:
            status = "PASS"
            reason = "Falsification test found"
        else:
            # POPPERIAN_EXEMPT IS A FAIL — no theological exemptions
            status = "FAIL"
            reason = (
                f"No test file found implementing {f_id}. "
                "Theological claims are not exempt from Popperian standard. "
                "POPPERIAN_EXEMPT is a FAIL."
            )

        results.append({
            "falsification_id": f_id,
            "math_concept": corr["math_concept"],
            "theological_concept": corr["theological_concept"],
            "description": corr["description"],
            "test_file": test_file,
            "popperian_status": status,
            "reason": reason,
        })

    return results


def run_audit(report_path: Path | None = None) -> dict[str, Any]:
    """Run the full Popperian audit. Returns the report dict."""
    domain_results = _audit_ontology_domains()
    theo_results = _audit_theological_correspondences()

    domain_fails = [r for r in domain_results if r.get("popperian_status") == "FAIL"]
    theo_fails = [r for r in theo_results if r.get("popperian_status") == "FAIL"]
    total_fails = len(domain_fails) + len(theo_fails)

    report = {
        "audit_type": "POPPERIAN",
        "zero_exemptions": True,
        "theological_exemptions_allowed": False,
        "domain_audit": {
            "total": len(domain_results),
            "pass": len([r for r in domain_results if r.get("popperian_status") == "PASS"]),
            "fail": len(domain_fails),
            "results": domain_results,
        },
        "theological_audit": {
            "total": len(theo_results),
            "pass": len([r for r in theo_results if r.get("popperian_status") == "PASS"]),
            "fail": len(theo_fails),
            "note": "POPPERIAN_EXEMPT is FAIL. No theological exemptions.",
            "results": theo_results,
        },
        "summary": {
            "total_claims": len(domain_results) + len(theo_results),
            "total_pass": (
                len([r for r in domain_results if r.get("popperian_status") == "PASS"])
                + len([r for r in theo_results if r.get("popperian_status") == "PASS"])
            ),
            "total_fail": total_fails,
            "popperian_exempt_count": 0,  # always 0 — exempt is impossible
            "overall": "PASS" if total_fails == 0 else "FAIL",
        },
    }

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to: {report_path}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Popperian audit — zero exemptions")
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to write the JSON report (default: restoration/popperian_audit_report.json)",
    )
    args = parser.parse_args()

    report = run_audit(report_path=args.report_path)
    summary = report["summary"]

    print(f"\nPopperian Audit Summary:")
    print(f"  Total claims:   {summary['total_claims']}")
    print(f"  Passing:        {summary['total_pass']}")
    print(f"  Failing:        {summary['total_fail']}")
    print(f"  Exempt (allowed): 0 — no exemptions")
    print(f"  Overall: {summary['overall']}")

    if summary["overall"] == "FAIL":
        print("\nFailing claims:")
        for r in report["domain_audit"]["results"]:
            if r.get("popperian_status") == "FAIL":
                print(f"  [DOMAIN] {r.get('domain_id')}: {r.get('reason')}")
        for r in report["theological_audit"]["results"]:
            if r.get("popperian_status") == "FAIL":
                print(f"  [THEO]   {r.get('falsification_id')}: {r.get('reason')}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
