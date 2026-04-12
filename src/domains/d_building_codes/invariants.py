"""D_BUILDING_CODES invariants — Fraction only. 0 floats.

Each function returns Tuple[bool, ProofObject] and encodes IBC, NFPA 101,
and ADA building code requirements.

Standards:
- International Building Code (IBC) 2021
- NFPA 101 Life Safety Code
- ADA Standards for Accessible Design (28 CFR 36)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple

from axioms.logic import ProofObject
from .implementation import BuildingPermit


def check_fire_egress(permit: BuildingPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Minimum fire exits must be provided per IBC §1006 and NFPA 101.

    falsifies_if: fire_exits_count < min_fire_exits.
    """
    success = permit.fire_exits_count >= permit.min_fire_exits

    if not success:
        return False, ProofObject(
            rule="FireEgressRequirement",
            premises=[
                f"permit_id={permit.permit_id}",
                f"fire_exits_count={permit.fire_exits_count}",
                f"min_fire_exits={permit.min_fire_exits}",
            ],
            conclusion="VIOLATION: IBC §1006/NFPA 101 — insufficient fire exits",
        )

    return True, ProofObject(
        rule="FireEgressRequirement",
        premises=[
            f"permit_id={permit.permit_id}",
            f"fire_exits_count={permit.fire_exits_count}",
            f"min_fire_exits={permit.min_fire_exits}",
        ],
        conclusion="IBC §1006 fire egress requirement satisfied",
    )


def check_occupant_load(permit: BuildingPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Actual occupant load must not exceed permitted maximum per IBC §1004.

    falsifies_if: occupant_load > max_occupant_load.
    """
    success = permit.occupant_load <= permit.max_occupant_load

    if not success:
        return False, ProofObject(
            rule="OccupantLoadLimit",
            premises=[
                f"permit_id={permit.permit_id}",
                f"occupant_load={permit.occupant_load}",
                f"max_occupant_load={permit.max_occupant_load}",
            ],
            conclusion="VIOLATION: IBC §1004 — occupant load exceeds permitted maximum",
        )

    return True, ProofObject(
        rule="OccupantLoadLimit",
        premises=[
            f"permit_id={permit.permit_id}",
            f"occupant_load={permit.occupant_load}",
            f"max_occupant_load={permit.max_occupant_load}",
        ],
        conclusion="IBC §1004 occupant load limit satisfied",
    )


def check_mechanical_compliance(permit: BuildingPermit) -> Tuple[bool, ProofObject]:
    """
    Rule: Electrical and plumbing systems must comply with adopted codes per IBC §2701 and §2901.

    falsifies_if: electrical_code_compliant is False OR plumbing_code_compliant is False.
    """
    success = permit.electrical_code_compliant and permit.plumbing_code_compliant

    if not success:
        return False, ProofObject(
            rule="MechanicalSystemsCompliance",
            premises=[
                f"permit_id={permit.permit_id}",
                f"electrical_code_compliant={permit.electrical_code_compliant}",
                f"plumbing_code_compliant={permit.plumbing_code_compliant}",
            ],
            conclusion="VIOLATION: IBC §2701/§2901 — electrical or plumbing code non-compliance",
        )

    return True, ProofObject(
        rule="MechanicalSystemsCompliance",
        premises=[
            f"permit_id={permit.permit_id}",
            f"electrical_code_compliant={permit.electrical_code_compliant}",
            f"plumbing_code_compliant={permit.plumbing_code_compliant}",
        ],
        conclusion="IBC §2701/§2901 mechanical systems compliance satisfied",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all D_BUILDING_CODES invariants with nominal passing data.

    falsifies_if: any building code invariant check fails or raises an exception.
    """
    permit = BuildingPermit(
        permit_id="BP-001",
        permit_obtained=True,
        occupancy_type="commercial",
        fire_exits_count=4,
        min_fire_exits=2,
        sprinkler_installed=True,
        electrical_code_compliant=True,
        plumbing_code_compliant=True,
        occupant_load=Fraction(200),
        max_occupant_load=Fraction(300),
        seismic_zone=2,
    )

    checks = [
        ("check_fire_egress", lambda: check_fire_egress(permit)),
        ("check_occupant_load", lambda: check_occupant_load(permit)),
        ("check_mechanical_compliance", lambda: check_mechanical_compliance(permit)),
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
    print("All D_BUILDING_CODES invariants: PASS")
