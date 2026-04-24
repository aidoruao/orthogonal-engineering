#!/usr/bin/env python3
"""Campaign Auditor -- aggregate scope reduction across all campaign specs.

Discovers every *_spec.json under campaigns/, runs scope_reduction_detector
against each, and produces an aggregate CAMPAIGN_AUDIT_REPORT.json.

Standard: CAMPAIGN-AUDIT-001
Falsifies if: aggregate report claims all_pass when any campaign shows scope reduction.
falsifies_if: aggregate report claims all_pass when any campaign shows scope reduction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from axioms.logic import ProofObject
from audit.scope_reduction_detector import run_scope_reduction_detector

SPEC_GLOB = "campaigns/**/*_spec.json"
REPORT_PATH = Path("audit/CAMPAIGN_AUDIT_REPORT.json")


def discover_specs(repo_root: Path) -> List[Path]:
    """Find all campaign spec JSON files under campaigns/.

    Falsifies if: a spec file exists but is not discoverable by the glob.
    falsifies_if: a spec file exists but is not discoverable by the glob.
    """
    return sorted(repo_root.glob(SPEC_GLOB))


def _spec_name(spec_path: Path) -> str:
    """Derive a short campaign name from the spec path.

    falsifies_if: two distinct specs map to the same short name.
    """
    return spec_path.stem


def audit_all_campaigns(repo_root: Path) -> Tuple[bool, ProofObject]:
    """Run scope reduction detection against every discovered spec and aggregate.

    Falsifies if: any campaign shows scope_reduction_detected=True while
    the aggregate report claims all_pass=True.
    falsifies_if: any campaign shows scope_reduction_detected=True while
    the aggregate report claims all_pass=True.
    """
    specs = discover_specs(repo_root)
    if not specs:
        result = {
            "all_pass": False,
            "total_campaigns": 0,
            "campaigns_with_scope_reduction": 0,
            "campaigns": [],
            "error": "No campaign specs discovered",
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
        proof = ProofObject(
            rule="campaign_auditor",
            premises=["spec_count=0"],
            conclusion="FAIL: No campaign specs discovered under campaigns/",
        )
        return False, proof

    campaigns: List[Dict] = []
    any_reduction = False

    for spec_path in specs:
        name = _spec_name(spec_path)
        # Unique per-campaign report to avoid overwriting the global one
        per_campaign_report = repo_root / "audit" / f"SCOPE_REDUCTION_{name}.json"
        passed, _proof = run_scope_reduction_detector(spec_path, per_campaign_report)

        # Read back the structured report written by scope_reduction_detector
        try:
            report_data = json.loads(per_campaign_report.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            report_data = {
                "campaign": name,
                "delivery_ratio": "0/1",
                "scope_reduction_detected": True,
                "error": "Could not read per-campaign report",
            }

        campaign_entry = {
            "name": name,
            "spec_path": str(spec_path.relative_to(repo_root)),
            "passed": passed,
            "delivery_ratio": report_data.get("delivery_ratio", "?/?"),
            "total_expected": report_data.get("total_expected", 0),
            "total_delivered": report_data.get("total_delivered", 0),
            "scope_reduction_detected": report_data.get(
                "scope_reduction_detected", True
            ),
        }
        campaigns.append(campaign_entry)
        if not passed:
            any_reduction = True

    num_total = len(campaigns)
    num_reduction = sum(1 for c in campaigns if c["scope_reduction_detected"])

    result = {
        "all_pass": not any_reduction,
        "total_campaigns": num_total,
        "campaigns_with_scope_reduction": num_reduction,
        "campaigns": campaigns,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )

    if any_reduction:
        conclusion = (
            f"FAIL: {num_reduction}/{num_total} campaigns show scope reduction"
        )
        proof = ProofObject(
            rule="campaign_auditor",
            premises=[
                f"total_campaigns={num_total}",
                f"campaigns_with_scope_reduction={num_reduction}",
            ],
            conclusion=conclusion,
        )
        return False, proof

    conclusion = f"PASS: All {num_total} campaigns deliver zero scope reduction"
    proof = ProofObject(
        rule="campaign_auditor",
        premises=[f"total_campaigns={num_total}"],
        conclusion=conclusion,
    )
    return True, proof


def main() -> int:
    """CLI entry point. Exit 0 if all campaigns pass, 1 otherwise.

    falsifies_if: exit code 0 when scope reduction is present.
    """
    all_pass, proof = audit_all_campaigns(REPO_ROOT)
    print(proof.conclusion)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
