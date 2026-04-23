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


def check_fall_protection_coverage(fp: FallProtection) -> Tuple[bool, ProofObject]:
    """OSHA 1926.501: Fall protection coverage at 6+ feet.

    Falsifies if: work height is 6+ feet and fall protection coverage is less than 3/4.
    falsifies_if: work height is 6+ feet and fall protection coverage is less than 3/4.
    """
    threshold = Fraction(6)
    coverage_ratio = fp.fall_protection_coverage
    if fp.work_height_feet < threshold:
        return True, ProofObject(
            conclusion=f"Fall protection not required ({fp.work_height_feet} < {threshold} ft)",
            premises=[],
            rule="osha_fall_protection_coverage"
        )
    if coverage_ratio >= Fraction(3, 4):
        return True, ProofObject(
            conclusion=f"Fall protection coverage adequate ({coverage_ratio})",
            premises=[],
            rule="osha_fall_protection_coverage"
        )
    return False, ProofObject(
        conclusion=f"VIOLATION: Fall protection coverage insufficient ({coverage_ratio} < 3/4)",
        premises=[f"Height: {fp.work_height_feet} feet", f"Coverage: {coverage_ratio}"],
        rule="osha_fall_protection_coverage"
    )


def check_abatement_completeness_score(inspection: OSHAInspection) -> Tuple[bool, ProofObject]:
    """OSH Act § 5(a)(1): Abatement completeness score.

    Falsifies if: average abatement completeness score across hazards is less than 1/2.
    falsifies_if: average abatement completeness score across hazards is less than 1/2.
    """
    if not inspection.hazards_found:
        return True, ProofObject(
            conclusion="No hazards found; abatement completeness satisfied",
            premises=[],
            rule="osha_abatement_completeness"
        )
    total = Fraction(0)
    for hazard in inspection.hazards_found:
        total += hazard.abatement_completeness_score
    average = total / len(inspection.hazards_found)
    if average >= Fraction(1, 2):
        return True, ProofObject(
            conclusion=f"Average abatement completeness adequate ({average})",
            premises=[f"Hazards: {len(inspection.hazards_found)}", f"Average: {average}"],
            rule="osha_abatement_completeness"
        )
    return False, ProofObject(
        conclusion=f"VIOLATION: Average abatement completeness insufficient ({average} < 1/2)",
        premises=[f"Hazards: {len(inspection.hazards_found)}", f"Average: {average}"],
        rule="osha_abatement_completeness"
    )


def run_all_invariants() -> dict:
    """Run all D_OCCUPATIONAL_SAFETY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    fall_protection = FallProtection(
        work_height_feet=Fraction(1),
        fall_protection_coverage=Fraction(1, 1),
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
            abatement_completeness_score=Fraction(1, 1),
        )],
        citations_issued=[ViolationType.SERIOUS],
    )
    hazard = Hazard(
        description="Sample description",
        location="Sample Location",
    )

    checks = [
        ("check_fall_protection_coverage", lambda: check_fall_protection_coverage(fall_protection)),
        ("check_abatement_completeness_score", lambda: check_abatement_completeness_score(osha_inspection)),
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
