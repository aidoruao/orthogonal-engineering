"""D_HOUSING_LAW invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes Fair Housing Act,
habitability standards, and eviction notice requirements.

Standards:
- Fair Housing Act (42 U.S.C. §3601 et seq.)
- HUD Lead Disclosure Rule (24 CFR 35)
- Uniform Residential Landlord and Tenant Act (URLTA)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import RentalUnit


def check_fair_housing_compliance(unit: RentalUnit) -> Tuple[bool, ProofObject]:
    """
    Rule: Rental units must not reject applicants based on protected class (FHA 42 U.S.C. §3604).
    For pre-1978 housing, lead paint disclosure is required (24 CFR 35.88).

    falsifies_if: protected_class_rejection is True OR (built_year < 1978 AND lead_paint_disclosure is False).
    """
    no_rejection = not unit.protected_class_rejection
    lead_ok = unit.built_year >= 1978 or unit.lead_paint_disclosure
    success = no_rejection and lead_ok

    if not success:
        return False, ProofObject(
            rule="FairHousingCompliance",
            premises=[
                f"unit_id={unit.unit_id}",
                f"protected_class_rejection={unit.protected_class_rejection}",
                f"built_year={unit.built_year}",
                f"lead_paint_disclosure={unit.lead_paint_disclosure}",
            ],
            conclusion=(
                "VIOLATION: FHA §3604 — protected class rejection"
                if not no_rejection
                else "VIOLATION: 24 CFR 35.88 — lead paint disclosure missing for pre-1978 unit"
            ),
        )

    return True, ProofObject(
        rule="FairHousingCompliance",
        premises=[
            f"unit_id={unit.unit_id}",
            f"protected_class_rejection={unit.protected_class_rejection}",
            f"lead_paint_disclosure_required={unit.built_year < 1978}",
            f"lead_paint_disclosure={unit.lead_paint_disclosure}",
        ],
        conclusion="FHA §3604 and 24 CFR 35.88 fair housing compliance satisfied",
    )


def check_habitability_standard(unit: RentalUnit) -> Tuple[bool, ProofObject]:
    """
    Rule: Landlords must maintain rental units in habitable condition (implied warranty of habitability).

    falsifies_if: habitability_met is False.
    """
    success = unit.habitability_met

    if not success:
        return False, ProofObject(
            rule="ImpliedWarrantyOfHabitability",
            premises=[
                f"unit_id={unit.unit_id}",
                f"habitability_met={unit.habitability_met}",
            ],
            conclusion="VIOLATION: Implied warranty of habitability — unit not maintained in habitable condition",
        )

    return True, ProofObject(
        rule="ImpliedWarrantyOfHabitability",
        premises=[
            f"unit_id={unit.unit_id}",
            f"habitability_met={unit.habitability_met}",
        ],
        conclusion="Implied warranty of habitability satisfied",
    )


def check_eviction_notice(unit: RentalUnit) -> Tuple[bool, ProofObject]:
    """
    Rule: Eviction notice must meet the minimum statutory notice period.

    falsifies_if: eviction_notice_days < min_notice_days.
    """
    success = unit.eviction_notice_days >= unit.min_notice_days

    if not success:
        return False, ProofObject(
            rule="EvictionNoticePeriod",
            premises=[
                f"unit_id={unit.unit_id}",
                f"eviction_notice_days={unit.eviction_notice_days}",
                f"min_notice_days={unit.min_notice_days}",
            ],
            conclusion="VIOLATION: URLTA — eviction notice period insufficient",
        )

    return True, ProofObject(
        rule="EvictionNoticePeriod",
        premises=[
            f"unit_id={unit.unit_id}",
            f"eviction_notice_days={unit.eviction_notice_days}",
            f"min_notice_days={unit.min_notice_days}",
        ],
        conclusion="URLTA eviction notice period satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_HOUSING_LAW invariants with nominal passing data.

    falsifies_if: any housing law invariant check fails or raises an exception.
    """
    unit = RentalUnit(
        unit_id="UNIT-001",
        fair_housing_compliant=True,
        protected_class_rejection=False,
        habitability_met=True,
        lead_paint_disclosure=True,
        built_year=1985,
        ada_compliant=True,
        rent_increase_pct=Fraction(3, 100),
        max_rent_increase_pct=Fraction(5, 100),
        eviction_notice_days=Fraction(30),
        min_notice_days=Fraction(30),
    )

    checks = [
        ("check_fair_housing_compliance", lambda: check_fair_housing_compliance(unit)),
        ("check_habitability_standard", lambda: check_habitability_standard(unit)),
        ("check_eviction_notice", lambda: check_eviction_notice(unit)),
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
    print("All D_HOUSING_LAW invariants: PASS")
