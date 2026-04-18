"""Invariant checks for Aerospace Floor meta-standard domain."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import AerospaceFloorClaim, create_nominal_claim


def check_do178c_determinism(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: DO-178C §6.4.2.2 determinism is verified.

    Standard: DO-178C Software Considerations in Airborne Systems.
    Falsifies if: not do178c_determinism_verified.
    falsifies_if: not do178c_determinism_verified.

    Returns:
        Tuple of (success, proof).
    """
    success = data.do178c_determinism_verified
    proof = ProofObject(
        rule="check_do178c_determinism",
        premises=[
            "standard=DO-178C-6.4.2.2",
            f"do178c_determinism_verified={data.do178c_determinism_verified}",
        ],
        conclusion=(
            "PASS: DO-178C determinism verified"
            if success else "FAIL: DO-178C determinism not verified"
        ),
    )
    return success, proof


def check_mcdc_coverage(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MC/DC coverage is achieved.

    Standard: DO-178C Level A modified condition/decision coverage.
    Falsifies if: not mcdc_coverage_achieved.
    falsifies_if: not mcdc_coverage_achieved.

    Returns:
        Tuple of (success, proof).
    """
    success = data.mcdc_coverage_achieved
    proof = ProofObject(
        rule="check_mcdc_coverage",
        premises=[
            "standard=DO-178C-MC/DC",
            f"mcdc_coverage_achieved={data.mcdc_coverage_achieved}",
        ],
        conclusion=(
            "PASS: MC/DC coverage achieved"
            if success else "FAIL: MC/DC coverage not achieved"
        ),
    )
    return success, proof


def check_misra_recursion_bounded(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MISRA unbounded recursion is bounded.

    Standard: MISRA-C:2012 Rule 17.2.
    Falsifies if: not misra_recursion_bounded.
    falsifies_if: not misra_recursion_bounded.

    Returns:
        Tuple of (success, proof).
    """
    success = data.misra_recursion_bounded
    proof = ProofObject(
        rule="check_misra_recursion_bounded",
        premises=[
            "standard=MISRA-C-2012-17.2",
            f"misra_recursion_bounded={data.misra_recursion_bounded}",
        ],
        conclusion=(
            "PASS: MISRA recursion bounded"
            if success else "FAIL: MISRA recursion unbounded"
        ),
    )
    return success, proof


def check_milstd882e_mishap_probability(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MIL-STD-882E mishap probability is assessed.

    Standard: MIL-STD-882E System Safety.
    Falsifies if: not milstd882e_mishap_probability_assessed.
    falsifies_if: not milstd882e_mishap_probability_assessed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.milstd882e_mishap_probability_assessed
    proof = ProofObject(
        rule="check_milstd882e_mishap_probability",
        premises=[
            "standard=MIL-STD-882E",
            f"milstd882e_mishap_probability_assessed={data.milstd882e_mishap_probability_assessed}",
        ],
        conclusion=(
            "PASS: MIL-STD-882E mishap probability assessed"
            if success else "FAIL: MIL-STD-882E mishap probability not assessed"
        ),
    )
    return success, proof


def check_independence_review(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Independence review is conducted.

    Standard: DO-178C independence of verification.
    Falsifies if: not independence_review_conducted.
    falsifies_if: not independence_review_conducted.

    Returns:
        Tuple of (success, proof).
    """
    success = data.independence_review_conducted
    proof = ProofObject(
        rule="check_independence_review",
        premises=[
            "standard=DO-178C-Independence",
            f"independence_review_conducted={data.independence_review_conducted}",
        ],
        conclusion=(
            "PASS: Independence review conducted"
            if success else "FAIL: Independence review not conducted"
        ),
    )
    return success, proof


def check_iec61508_sil4(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: IEC 61508 SIL-4 is verified.

    Standard: IEC 61508 Functional Safety SIL-4.
    Falsifies if: not iec61508_sil4_verified.
    falsifies_if: not iec61508_sil4_verified.

    Returns:
        Tuple of (success, proof).
    """
    success = data.iec61508_sil4_verified
    proof = ProofObject(
        rule="check_iec61508_sil4",
        premises=[
            "standard=IEC-61508-SIL4",
            f"iec61508_sil4_verified={data.iec61508_sil4_verified}",
        ],
        conclusion=(
            "PASS: IEC 61508 SIL-4 verified"
            if success else "FAIL: IEC 61508 SIL-4 not verified"
        ),
    )
    return success, proof


def check_nasa_npr7150_class_a(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: NASA NPR 7150.2 Class A compliance.

    Standard: NASA NPR 7150.2 Software Engineering Requirements Class A.
    Falsifies if: not nasa_npr7150_class_a_compliant.
    falsifies_if: not nasa_npr7150_class_a_compliant.

    Returns:
        Tuple of (success, proof).
    """
    success = data.nasa_npr7150_class_a_compliant
    proof = ProofObject(
        rule="check_nasa_npr7150_class_a",
        premises=[
            "standard=NASA-NPR-7150.2-Class-A",
            f"nasa_npr7150_class_a_compliant={data.nasa_npr7150_class_a_compliant}",
        ],
        conclusion=(
            "PASS: NASA NPR 7150.2 Class A compliant"
            if success else "FAIL: NASA NPR 7150.2 Class A not compliant"
        ),
    )
    return success, proof


def check_af_compliance_scanned(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Aerospace floor compliance scan completed.

    Standard: AF-001/AF-002/AF-007 meta-standard compliance.
    Falsifies if: not af_compliance_scanned.
    falsifies_if: not af_compliance_scanned.

    Returns:
        Tuple of (success, proof).
    """
    success = data.af_compliance_scanned
    proof = ProofObject(
        rule="check_af_compliance_scanned",
        premises=[
            "standard=AF-001/AF-002/AF-007",
            f"af_compliance_scanned={data.af_compliance_scanned}",
        ],
        conclusion=(
            "PASS: Aerospace floor compliance scanned"
            if success else "FAIL: Aerospace floor compliance not scanned"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Aerospace Floor meta-standard nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_do178c_determinism", check_do178c_determinism),
        ("check_mcdc_coverage", check_mcdc_coverage),
        ("check_misra_recursion_bounded", check_misra_recursion_bounded),
        ("check_milstd882e_mishap_probability", check_milstd882e_mishap_probability),
        ("check_independence_review", check_independence_review),
        ("check_iec61508_sil4", check_iec61508_sil4),
        ("check_nasa_npr7150_class_a", check_nasa_npr7150_class_a),
        ("check_af_compliance_scanned", check_af_compliance_scanned),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
