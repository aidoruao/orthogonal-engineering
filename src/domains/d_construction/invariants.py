#!/usr/bin/env python3
"""D_CONSTRUCTION Invariants — FEM analysis, BIM clash detection, OSHA compliance

Structural engineering per ASCE 7, ACI 318, and OSHA 1926 requirements.
All invariants use Fraction arithmetic for exact safety factors and tolerances.
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    StructuralMember, FEMAnalysis, BIMClashDetection, OSHACompliance,
    LoadType, structural_safety_factor_min, fem_tolerance,
    bim_false_negative_max, osha_fall_protection_height
)


def check_structural_safety_factor(member: StructuralMember) -> Tuple[bool, ProofObject]:
    """
    Structural members require safety factor >= 3.0 per building codes.

    Falsifies if: capacity_kn / applied_load_kn < 3.0
    falsifies_if: capacity_kn / applied_load_kn < 3.0
    """
    min_sf = structural_safety_factor_min()
    actual_sf = member.capacity_kn / member.applied_load_kn

    if actual_sf < min_sf:
        return False, ProofObject(
            conclusion=f"VIOLATION: Member {member.member_id} safety factor {actual_sf} < {min_sf}",
            premises=[
                f"Capacity: {member.capacity_kn} kN",
                f"Load: {member.applied_load_kn} kN",
                f"SF: {actual_sf}"
            ],
            rule="structural_safety_factor"
        )

    return True, ProofObject(
        conclusion=f"Member {member.member_id} safety factor {actual_sf} adequate",
        premises=[f"SF: {actual_sf} >= {min_sf}"],
        rule="structural_safety_factor"
    )


def check_fem_accuracy(analysis: FEMAnalysis) -> Tuple[bool, ProofObject]:
    """
    FEM results must match analytical solutions within 1% for validation.

    Falsifies if: |computed - analytical| / analytical > 0.01
    falsifies_if: |computed - analytical| / analytical > 0.01
    """
    tolerance = fem_tolerance()
    error = abs(analysis.computed_stress_mpa - analysis.analytical_stress_mpa) / analysis.analytical_stress_mpa

    if error > tolerance:
        return False, ProofObject(
            conclusion=f"VIOLATION: FEM analysis {analysis.analysis_id} error {error * 100}% > {tolerance * 100}%",
            premises=[
                f"Computed: {analysis.computed_stress_mpa} MPa",
                f"Analytical: {analysis.analytical_stress_mpa} MPa",
                f"Error: {error * 100}%"
            ],
            rule="fem_validation_tolerance"
        )

    return True, ProofObject(
        conclusion=f"FEM analysis {analysis.analysis_id} within tolerance",
        premises=[f"Error: {error * 100}% <= {tolerance * 100}%"],
        rule="fem_validation_tolerance"
    )


def check_bim_clash_detection(bim: BIMClashDetection) -> Tuple[bool, ProofObject]:
    """
    BIM clash detection must achieve <0.1% false negative rate.

    Falsifies if: false_negative_rate >= 0.001
    falsifies_if: false_negative_rate >= 0.001
    """
    max_fn = bim_false_negative_max()

    if bim.false_negative_rate >= max_fn:
        return False, ProofObject(
            conclusion=f"VIOLATION: BIM {bim.model_id} false negative rate {bim.false_negative_rate * 100}% >= {max_fn * 100}%",
            premises=[
                f"FN rate: {bim.false_negative_rate * 100}%",
                f"Max: {max_fn * 100}%"
            ],
            rule="bim_clash_detection_accuracy"
        )

    return True, ProofObject(
        conclusion=f"BIM {bim.model_id} clash detection adequate",
        premises=[f"FN rate: {bim.false_negative_rate * 100}% < {max_fn * 100}%"],
        rule="bim_clash_detection_accuracy"
    )


def check_osha_fall_protection(osha: OSHACompliance) -> Tuple[bool, ProofObject]:
    """
    OSHA 1926 requires fall protection at heights >6 ft.

    Falsifies if: height_ft > 6 AND NOT has_fall_protection
    falsifies_if: height_ft > 6 AND NOT has_fall_protection
    """
    threshold = osha_fall_protection_height()

    if osha.height_ft > threshold and not osha.has_fall_protection:
        return False, ProofObject(
            conclusion=f"VIOLATION: Site {osha.site_id} height {osha.height_ft} ft > {threshold} ft without fall protection",
            premises=[
                f"Height: {osha.height_ft} ft",
                f"Fall protection: {osha.has_fall_protection}",
                f"Threshold: {threshold} ft"
            ],
            rule="osha_1926_fall_protection"
        )

    return True, ProofObject(
        conclusion=f"Site {osha.site_id} fall protection compliant",
        premises=[f"Height: {osha.height_ft} ft", f"Protected: {osha.has_fall_protection}"],
        rule="osha_1926_fall_protection"
    )


def run_all_invariants() -> dict:
    """Run all D_CONSTRUCTION invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    bim_clash_detection = BIMClashDetection(
        model_id=None,
        clashes_detected=None,
        false_negative_rate=Fraction(1),
    )
    fem_analysis = FEMAnalysis(
        analysis_id=None,
        computed_stress_mpa=Fraction(1),
        analytical_stress_mpa=Fraction(1),
        mesh_convergence_percent=Fraction(1),
    )
    osha_compliance = OSHACompliance(
        site_id=None,
        height_ft=Fraction(1),
        has_fall_protection=None,
    )
    structural_member = StructuralMember(
        member_id=None,
        applied_load_kn=Fraction(1),
        capacity_kn=Fraction(1000),
        safety_factor=Fraction(1),
    )

    checks = [
        ("check_bim_clash_detection", lambda: check_bim_clash_detection(bim_clash_detection)),
        ("check_fem_accuracy", lambda: check_fem_accuracy(fem_analysis)),
        ("check_osha_fall_protection", lambda: check_osha_fall_protection(osha_compliance)),
        ("check_structural_safety_factor", lambda: check_structural_safety_factor(structural_member)),
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
    print("All D_CONSTRUCTION invariants: PASS")
