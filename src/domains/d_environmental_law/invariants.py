"""D_ENVIRONMENTAL_LAW invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes Clean Air Act,
Clean Water Act, NEPA, and RCRA requirements.

Standards:
- Clean Air Act (42 U.S.C. 7401)
- Clean Water Act (33 U.S.C. 1251)
- NEPA (42 U.S.C. 4321)
- RCRA (42 U.S.C. 6901)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import EnvironmentalPermit


def check_clean_air_act(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """Rule: Emissions must not exceed NAAQS limits (Clean Air Act 42 U.S.C. 7409).

    falsifies_if: emission_tons_per_year > naaqs_limit_tons.
    """
    success = permit.emission_tons_per_year <= permit.naaqs_limit_tons
    margin = permit.naaqs_limit_tons - permit.emission_tons_per_year

    if not success:
        return False, ProofObject(
            rule="CleanAirActNAAQS",
            premises=[
                f"permit_id={permit.permit_id}",
                f"emission_tons_per_year={permit.emission_tons_per_year}",
                f"naaqs_limit_tons={permit.naaqs_limit_tons}",
                f"margin={margin}",
            ],
            conclusion="VIOLATION: CAA 7409 — emissions exceed NAAQS limit",
        )

    return True, ProofObject(
        rule="CleanAirActNAAQS",
        premises=[
            f"permit_id={permit.permit_id}",
            f"emission_tons_per_year={permit.emission_tons_per_year}",
            f"naaqs_limit_tons={permit.naaqs_limit_tons}",
            f"margin={margin}",
        ],
        conclusion="CAA 7409 NAAQS emission limit satisfied",
    )


def check_clean_water_npdes(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """Rule: Discharge compliance score must meet NPDES threshold (CWA 33 U.S.C. 1342).

    falsifies_if: discharge_compliance_score < Fraction(3, 4).
    """
    threshold = Fraction(3, 4)
    success = permit.discharge_compliance_score >= threshold

    if not success:
        return False, ProofObject(
            rule="CleanWaterNPDES",
            premises=[
                f"permit_id={permit.permit_id}",
                f"discharge_compliance_score={permit.discharge_compliance_score}",
                f"threshold={threshold}",
            ],
            conclusion="VIOLATION: CWA 1342 — discharge compliance score below NPDES threshold",
        )

    return True, ProofObject(
        rule="CleanWaterNPDES",
        premises=[
            f"permit_id={permit.permit_id}",
            f"discharge_compliance_score={permit.discharge_compliance_score}",
            f"threshold={threshold}",
        ],
        conclusion="CWA 1342 NPDES discharge compliance satisfied",
    )


def check_nepa_eis(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """Rule: EIS completeness score must meet NEPA threshold (NEPA 42 U.S.C. 4332).

    falsifies_if: eis_completeness_score < Fraction(3, 4).
    """
    threshold = Fraction(3, 4)
    success = permit.eis_completeness_score >= threshold

    if not success:
        return False, ProofObject(
            rule="NEPAEnvironmentalImpactStatement",
            premises=[
                f"permit_id={permit.permit_id}",
                f"eis_completeness_score={permit.eis_completeness_score}",
                f"threshold={threshold}",
            ],
            conclusion="VIOLATION: NEPA 4332 — EIS completeness score below threshold",
        )

    return True, ProofObject(
        rule="NEPAEnvironmentalImpactStatement",
        premises=[
            f"permit_id={permit.permit_id}",
            f"eis_completeness_score={permit.eis_completeness_score}",
            f"threshold={threshold}",
        ],
        conclusion="NEPA 4332 EIS completeness requirement satisfied",
    )


def check_rcra_manifest(permit: EnvironmentalPermit) -> Tuple[bool, ProofObject]:
    """Rule: Hazardous waste manifest coverage must meet RCRA threshold (RCRA 42 U.S.C. 6922).

    falsifies_if: manifest_coverage_fraction < Fraction(1, 2).
    """
    threshold = Fraction(1, 2)
    success = permit.manifest_coverage_fraction >= threshold

    if not success:
        return False, ProofObject(
            rule="RCRAHazardousWasteManifest",
            premises=[
                f"permit_id={permit.permit_id}",
                f"manifest_coverage_fraction={permit.manifest_coverage_fraction}",
                f"threshold={threshold}",
            ],
            conclusion="VIOLATION: RCRA 6922 — hazardous waste manifest coverage below threshold",
        )

    return True, ProofObject(
        rule="RCRAHazardousWasteManifest",
        premises=[
            f"permit_id={permit.permit_id}",
            f"manifest_coverage_fraction={permit.manifest_coverage_fraction}",
            f"threshold={threshold}",
        ],
        conclusion="RCRA 6922 hazardous waste manifest coverage satisfied",
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
        discharge_compliance_score=Fraction(1, 1),
        eis_completeness_score=Fraction(1, 1),
        manifest_coverage_fraction=Fraction(1, 1),
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
