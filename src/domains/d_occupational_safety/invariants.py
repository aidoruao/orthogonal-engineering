#!/usr/bin/env python3
"""Occupational Safety Invariants — OSHA compliance."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    FallProtection,
    Hazard,
    OSHAInspection,
    Workplace,
    ViolationType,
)

def check_pel(hazard: Hazard) -> Tuple[bool, ProofObject]:
    """OSHA Permissible Exposure Limit compliance.

    Falsifies if: chemical exposure exceeds the permissible exposure limit.
    falsifies_if: chemical exposure exceeds the permissible exposure limit.
    """
    if not hazard.exceeds_pel():
        return True, ProofObject(
            conclusion=f"PEL compliant ({hazard.chemical_exposure_ppm} <= {hazard.permissible_exposure_limit})",
            premises=[],
            rule="osha_pel"
        )
    return False, ProofObject(
        conclusion="VIOLATION: PEL exceeded",
        premises=[f"Actual: {hazard.chemical_exposure_ppm}", f"Limit: {hazard.permissible_exposure_limit}"],
        rule="osha_pel"
    )

def check_fall_protection(fp: FallProtection) -> Tuple[bool, ProofObject]:
    """OSHA 1926.501: Fall protection at 6+ feet.

    Falsifies if: fall protection is required but not provided.
    falsifies_if: fall protection is required but not provided.
    """
    if not fp.protection_required():
        return True, ProofObject(
            conclusion=f"Fall protection not required ({fp.work_height_feet} < {fp.FALL_PROTECTION_THRESHOLD} ft)",
            premises=[],
            rule="osha_fall_protection"
        )
    
    if fp.is_compliant():
        return True, ProofObject(
            conclusion="Fall protection adequate",
            premises=[],
            rule="osha_fall_protection"
        )
    
    return False, ProofObject(
        conclusion="VIOLATION: Fall protection required but not provided",
        premises=[f"Height: {fp.work_height_feet} feet"],
        rule="osha_fall_protection"
    )

def check_general_duty(inspection: OSHAInspection) -> Tuple[bool, ProofObject]:
    """OSH Act § 5(a)(1): General duty clause.

    Falsifies if: recognized hazard is not abated under the general duty clause.
    falsifies_if: recognized hazard is not abated under the general duty clause.
    """
    if inspection.has_general_duty_violation():
        return False, ProofObject(
            conclusion="VIOLATION: General duty clause — recognized hazard not abated",
            premises=[],
            rule="osha_general_duty"
        )
    return True, ProofObject(
        conclusion="General duty clause satisfied",
        premises=[],
        rule="osha_general_duty"
    )


def run_all_invariants() -> dict:
    """Run all D_OCCUPATIONAL_SAFETY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    fall_protection = FallProtection(
        work_height_feet=Fraction(1),
    )
    osha_inspection = OSHAInspection(
        workplace=Workplace(
        employer="SAMPLE",
        location="Sample Location",
        industry="SAMPLE",
        employees_count=1,
    ),
        inspection_date="SAMPLE",
        hazards_found=[Hazard(
        description="Sample description",
        location="Sample Location",
    )],
        citations_issued=[ViolationType.SERIOUS],
    )
    hazard = Hazard(
        description="Sample description",
        location="Sample Location",
    )

    checks = [
        ("check_fall_protection", lambda: check_fall_protection(fall_protection)),
        ("check_general_duty", lambda: check_general_duty(osha_inspection)),
        ("check_pel", lambda: check_pel(hazard)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_OCCUPATIONAL_SAFETY invariants: PASS")
