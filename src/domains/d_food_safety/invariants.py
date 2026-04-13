"""D_FOOD_SAFETY invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes FDA food safety
regulatory requirements including FSMA, HACCP, and recall classification.

Standards:
- FSMA (21 U.S.C. §350g)
- FD&C Act (21 U.S.C. §301 et seq.)
- HACCP Principles (21 CFR Part 117)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import FoodFacility


def check_fda_registration(facility: FoodFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Food facilities must register with FDA under FSMA (21 U.S.C. §350d).

    falsifies_if: fda_registered is False.
    """
    success = facility.fda_registered

    if not success:
        return False, ProofObject(
            rule="FDAFacilityRegistration",
            premises=[
                f"facility_id={facility.facility_id}",
                f"fda_registered={facility.fda_registered}",
            ],
            conclusion="VIOLATION: FSMA §350d — food facility operating without FDA registration",
        )

    return True, ProofObject(
        rule="FDAFacilityRegistration",
        premises=[
            f"facility_id={facility.facility_id}",
            f"fda_registered={facility.fda_registered}",
        ],
        conclusion="FSMA §350d FDA facility registration satisfied",
    )


def check_haccp_plan(facility: FoodFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: HACCP plan must be current and all CCPs must be documented (21 CFR 117.126).

    falsifies_if: haccp_plan_current is False OR documented_ccps < critical_control_points.
    """
    plan_current = facility.haccp_plan_current
    ccps_documented = facility.documented_ccps >= facility.critical_control_points
    success = plan_current and ccps_documented

    if not success:
        return False, ProofObject(
            rule="HACCPPlanCompliance",
            premises=[
                f"facility_id={facility.facility_id}",
                f"haccp_plan_current={facility.haccp_plan_current}",
                f"documented_ccps={facility.documented_ccps}",
                f"critical_control_points={facility.critical_control_points}",
            ],
            conclusion="VIOLATION: 21 CFR 117.126 — HACCP plan not current or CCPs under-documented",
        )

    return True, ProofObject(
        rule="HACCPPlanCompliance",
        premises=[
            f"facility_id={facility.facility_id}",
            f"haccp_plan_current={facility.haccp_plan_current}",
            f"documented_ccps={facility.documented_ccps}",
            f"critical_control_points={facility.critical_control_points}",
        ],
        conclusion="21 CFR 117.126 HACCP plan and CCP documentation satisfied",
    )


def check_recall_classification(facility: FoodFacility) -> Tuple[bool, ProofObject]:
    """
    Rule: Recall class must be a valid FDA recall classification (21 CFR 7.3).

    falsifies_if: recall_class not in {"I","II","III","none"}.
    """
    valid_classes = {"I", "II", "III", "none"}
    success = facility.recall_class in valid_classes

    if not success:
        return False, ProofObject(
            rule="RecallClassification",
            premises=[
                f"facility_id={facility.facility_id}",
                f"recall_class={facility.recall_class}",
                f"valid_classes={sorted(valid_classes)}",
            ],
            conclusion=f"VIOLATION: 21 CFR 7.3 — invalid recall classification '{facility.recall_class}'",
        )

    return True, ProofObject(
        rule="RecallClassification",
        premises=[
            f"facility_id={facility.facility_id}",
            f"recall_class={facility.recall_class}",
        ],
        conclusion="21 CFR 7.3 recall classification valid",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_FOOD_SAFETY invariants with nominal passing data.

    falsifies_if: any food safety invariant check fails or raises an exception.
    """
    facility = FoodFacility(
        facility_id="FF-001",
        fda_registered=True,
        fsma_preventive_controls=True,
        haccp_plan_current=True,
        temperature_log_compliant=True,
        critical_control_points=3,
        documented_ccps=3,
        recall_class="none",
        foreign_supplier_verification=True,
    )

    checks = [
        ("check_fda_registration", lambda: check_fda_registration(facility)),
        ("check_haccp_plan", lambda: check_haccp_plan(facility)),
        ("check_recall_classification", lambda: check_recall_classification(facility)),
    ]

    results: Dict[str, str] = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_FOOD_SAFETY invariants: PASS")
