"""D_ENVIRONMENTAL_LAW invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes Clean Air Act,
Clean Water Act, NEPA, and RCRA requirements.

Standards:
- Clean Air Act (42 U.S.C. §7401)
- Clean Water Act (33 U.S.C. §1251)
- NEPA (42 U.S.C. §4321)
- RCRA (42 U.S.C. §6901)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import EnvironmentalPermit


def check_clean_air_act(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Emissions must not exceed NAAQS limits (Clean Air Act 42 U.S.C. §7409).

    falsifies_if: emission_tons_per_year > naaqs_limit_tons.
    """
    success = permit.emission_tons_per_year <= permit.naaqs_limit_tons

    if not success:
        return False, ProofObject(
            rule="CleanAirActNAAQS",
            premises=[
                f"permit_id={permit.permit_id}",
                f"emission_tons_per_year={permit.emission_tons_per_year}",
                f"naaqs_limit_tons={permit.naaqs_limit_tons}",
            ],
            conclusion="VIOLATION: CAA §7409 — emissions exceed NAAQS limit",
        )

    return True, ProofObject(
        rule="CleanAirActNAAQS",
        premises=[
            f"permit_id={permit.permit_id}",
            f"emission_tons_per_year={permit.emission_tons_per_year}",
            f"naaqs_limit_tons={permit.naaqs_limit_tons}",
        ],
        conclusion="CAA §7409 NAAQS emission limit satisfied",
    )


def check_clean_water_npdes(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Discharges into navigable waters require an NPDES permit (CWA 33 U.S.C. §1342).

    falsifies_if: npdes_permit is False.
    """
    success = permit.npdes_permit

    if not success:
        return False, ProofObject(
            rule="CleanWaterNPDES",
            premises=[
                f"permit_id={permit.permit_id}",
                f"npdes_permit={permit.npdes_permit}",
                f"epa_permit_valid={permit.epa_permit_valid}",
            ],
            conclusion="VIOLATION: CWA §1342 — discharge without NPDES permit",
        )

    return True, ProofObject(
        rule="CleanWaterNPDES",
        premises=[
            f"permit_id={permit.permit_id}",
            f"npdes_permit={permit.npdes_permit}",
        ],
        conclusion="CWA §1342 NPDES permit requirement satisfied",
    )


def check_nepa_eis(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Major federal actions with significant environmental impacts require an EIS (NEPA 42 U.S.C. §4332).

    falsifies_if: eis_completed is False.
    """
    success = permit.eis_completed

    if not success:
        return False, ProofObject(
            rule="NEPAEnvironmentalImpactStatement",
            premises=[
                f"permit_id={permit.permit_id}",
                f"eis_completed={permit.eis_completed}",
            ],
            conclusion="VIOLATION: NEPA §4332 — EIS not completed for major federal action",
        )

    return True, ProofObject(
        rule="NEPAEnvironmentalImpactStatement",
        premises=[
            f"permit_id={permit.permit_id}",
            f"eis_completed={permit.eis_completed}",
        ],
        conclusion="NEPA §4332 EIS requirement satisfied",
    )


def check_rcra_manifest(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Hazardous waste transportation requires a manifest (RCRA 42 U.S.C. §6922).

    falsifies_if: hazardous_waste_manifest is False.
    """
    success = permit.hazardous_waste_manifest

    if not success:
        return False, ProofObject(
            rule="RCRAHazardousWasteManifest",
            premises=[
                f"permit_id={permit.permit_id}",
                f"hazardous_waste_manifest={permit.hazardous_waste_manifest}",
            ],
            conclusion="VIOLATION: RCRA §6922 — hazardous waste without required manifest",
        )

    return True, ProofObject(
        rule="RCRAHazardousWasteManifest",
        premises=[
            f"permit_id={permit.permit_id}",
            f"hazardous_waste_manifest={permit.hazardous_waste_manifest}",
        ],
        conclusion="RCRA §6922 hazardous waste manifest satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_ENVIRONMENTAL_LAW invariants with nominal passing data.

    falsifies_if: any environmental law invariant check fails or raises an exception.
    """
    permit = EnvironmentalPermit(
        permit_id="EP-001",
        epa_permit_valid=True,
        npdes_permit=True,
        emission_tons_per_year=Fraction(80),
        naaqs_limit_tons=Fraction(100),
        wetlands_impacted=False,
        section_404_permit=False,
        eis_completed=True,
        hazardous_waste_manifest=True,
    )

    checks = [
        ("check_clean_air_act", lambda: check_clean_air_act(permit)),
        ("check_clean_water_npdes", lambda: check_clean_water_npdes(permit)),
        ("check_nepa_eis", lambda: check_nepa_eis(permit)),
        ("check_rcra_manifest", lambda: check_rcra_manifest(permit)),
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
    print("All D_ENVIRONMENTAL_LAW invariants: PASS")
