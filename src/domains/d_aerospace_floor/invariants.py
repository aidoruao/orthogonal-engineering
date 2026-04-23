"""Invariant checks for Aerospace Floor meta-standard domain."""

from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject
from .implementation import (
    MAX_MISHAP_PROBABILITY,
    MAX_RECURSION_DEPTH,
    MIN_AF_SCAN_COVERAGE,
    MIN_DETERMINISM_SCORE,
    MIN_INDEPENDENCE_REVIEW_SCORE,
    MIN_MCDC_COVERAGE,
    MIN_NASA_COMPLIANCE,
    MIN_SIL_LEVEL,
    AerospaceFloorClaim,
    create_nominal_claim,
)


def check_determinism_score(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: DO-178C determinism score meets floor.

    Standard: DO-178C Software Considerations in Airborne Systems.
    Falsifies if: determinism_score < MIN_DETERMINISM_SCORE.
    falsifies_if: determinism_score < MIN_DETERMINISM_SCORE.
    """
    success = data.determinism_score >= MIN_DETERMINISM_SCORE
    proof = ProofObject(
        rule="check_determinism_score",
        premises=[
            f"determinism_score={data.determinism_score}",
            f"floor={MIN_DETERMINISM_SCORE}",
        ],
        conclusion=(
            f"PASS: determinism score {data.determinism_score} >= {MIN_DETERMINISM_SCORE}"
            if success
            else f"FAIL: determinism score {data.determinism_score} < {MIN_DETERMINISM_SCORE}"
        ),
    )
    return success, proof


def check_mcdc_coverage_fraction(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MC/DC coverage fraction meets requirement.

    Standard: DO-178C Level A modified condition/decision coverage.
    Falsifies if: mcdc_coverage_fraction < MIN_MCDC_COVERAGE.
    falsifies_if: mcdc_coverage_fraction < MIN_MCDC_COVERAGE.
    """
    success = data.mcdc_coverage_fraction >= MIN_MCDC_COVERAGE
    proof = ProofObject(
        rule="check_mcdc_coverage_fraction",
        premises=[
            f"mcdc_coverage_fraction={data.mcdc_coverage_fraction}",
            f"floor={MIN_MCDC_COVERAGE}",
        ],
        conclusion=(
            f"PASS: MC/DC coverage {data.mcdc_coverage_fraction} >= {MIN_MCDC_COVERAGE}"
            if success
            else f"FAIL: MC/DC coverage {data.mcdc_coverage_fraction} < {MIN_MCDC_COVERAGE}"
        ),
    )
    return success, proof


def check_recursion_depth_bound(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MISRA recursion depth is within bound.

    Standard: MISRA-C:2012 Rule 17.2.
    Falsifies if: recursion_depth_bound > MAX_RECURSION_DEPTH.
    falsifies_if: recursion_depth_bound > MAX_RECURSION_DEPTH.
    """
    success = data.recursion_depth_bound <= MAX_RECURSION_DEPTH
    proof = ProofObject(
        rule="check_recursion_depth_bound",
        premises=[
            f"recursion_depth_bound={data.recursion_depth_bound}",
            f"max={MAX_RECURSION_DEPTH}",
        ],
        conclusion=(
            f"PASS: recursion depth {data.recursion_depth_bound} <= {MAX_RECURSION_DEPTH}"
            if success
            else f"FAIL: recursion depth {data.recursion_depth_bound} > {MAX_RECURSION_DEPTH}"
        ),
    )
    return success, proof


def check_mishap_probability_risk(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: MIL-STD-882E mishap probability is below risk threshold.

    Standard: MIL-STD-882E System Safety.
    Falsifies if: mishap_probability >= MAX_MISHAP_PROBABILITY.
    falsifies_if: mishap_probability >= MAX_MISHAP_PROBABILITY.
    """
    success = data.mishap_probability < MAX_MISHAP_PROBABILITY
    proof = ProofObject(
        rule="check_mishap_probability_risk",
        premises=[
            f"mishap_probability={data.mishap_probability}",
            f"max={MAX_MISHAP_PROBABILITY}",
        ],
        conclusion=(
            f"PASS: mishap probability {data.mishap_probability} < {MAX_MISHAP_PROBABILITY}"
            if success
            else f"FAIL: mishap probability {data.mishap_probability} >= {MAX_MISHAP_PROBABILITY}"
        ),
    )
    return success, proof


def check_independence_review_score(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Independence review score meets floor.

    Standard: DO-178C independence of verification.
    Falsifies if: independence_review_score < MIN_INDEPENDENCE_REVIEW_SCORE.
    falsifies_if: independence_review_score < MIN_INDEPENDENCE_REVIEW_SCORE.
    """
    success = data.independence_review_score >= MIN_INDEPENDENCE_REVIEW_SCORE
    proof = ProofObject(
        rule="check_independence_review_score",
        premises=[
            f"independence_review_score={data.independence_review_score}",
            f"floor={MIN_INDEPENDENCE_REVIEW_SCORE}",
        ],
        conclusion=(
            f"PASS: independence score {data.independence_review_score} >= {MIN_INDEPENDENCE_REVIEW_SCORE}"
            if success
            else f"FAIL: independence score {data.independence_review_score} < {MIN_INDEPENDENCE_REVIEW_SCORE}"
        ),
    )
    return success, proof


def check_sil_integrity_level(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: IEC 61508 SIL integrity level meets requirement.

    Standard: IEC 61508 Functional Safety SIL-4.
    Falsifies if: sil_integrity_level < MIN_SIL_LEVEL.
    falsifies_if: sil_integrity_level < MIN_SIL_LEVEL.
    """
    success = data.sil_integrity_level >= MIN_SIL_LEVEL
    proof = ProofObject(
        rule="check_sil_integrity_level",
        premises=[
            f"sil_integrity_level={data.sil_integrity_level}",
            f"floor={MIN_SIL_LEVEL}",
        ],
        conclusion=(
            f"PASS: SIL level {data.sil_integrity_level} >= {MIN_SIL_LEVEL}"
            if success
            else f"FAIL: SIL level {data.sil_integrity_level} < {MIN_SIL_LEVEL}"
        ),
    )
    return success, proof


def check_nasa_compliance_score(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: NASA NPR 7150.2 compliance score meets floor.

    Standard: NASA NPR 7150.2 Software Engineering Requirements Class A.
    Falsifies if: nasa_compliance_score < MIN_NASA_COMPLIANCE.
    falsifies_if: nasa_compliance_score < MIN_NASA_COMPLIANCE.
    """
    success = data.nasa_compliance_score >= MIN_NASA_COMPLIANCE
    proof = ProofObject(
        rule="check_nasa_compliance_score",
        premises=[
            f"nasa_compliance_score={data.nasa_compliance_score}",
            f"floor={MIN_NASA_COMPLIANCE}",
        ],
        conclusion=(
            f"PASS: NASA compliance {data.nasa_compliance_score} >= {MIN_NASA_COMPLIANCE}"
            if success
            else f"FAIL: NASA compliance {data.nasa_compliance_score} < {MIN_NASA_COMPLIANCE}"
        ),
    )
    return success, proof


def check_af_scan_coverage(data: AerospaceFloorClaim) -> Tuple[bool, ProofObject]:
    """Invariant: Aerospace floor compliance scan coverage meets requirement.

    Standard: AF-001/AF-002/AF-007 meta-standard compliance.
    Falsifies if: af_scan_coverage < MIN_AF_SCAN_COVERAGE.
    falsifies_if: af_scan_coverage < MIN_AF_SCAN_COVERAGE.
    """
    success = data.af_scan_coverage >= MIN_AF_SCAN_COVERAGE
    proof = ProofObject(
        rule="check_af_scan_coverage",
        premises=[
            f"af_scan_coverage={data.af_scan_coverage}",
            f"floor={MIN_AF_SCAN_COVERAGE}",
        ],
        conclusion=(
            f"PASS: AF scan coverage {data.af_scan_coverage} >= {MIN_AF_SCAN_COVERAGE}"
            if success
            else f"FAIL: AF scan coverage {data.af_scan_coverage} < {MIN_AF_SCAN_COVERAGE}"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain.

    Standard: Aerospace Floor meta-standard nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.
    """
    data = create_nominal_claim()
    checks = [
        ("check_determinism_score", check_determinism_score),
        ("check_mcdc_coverage_fraction", check_mcdc_coverage_fraction),
        ("check_recursion_depth_bound", check_recursion_depth_bound),
        ("check_mishap_probability_risk", check_mishap_probability_risk),
        ("check_independence_review_score", check_independence_review_score),
        ("check_sil_integrity_level", check_sil_integrity_level),
        ("check_nasa_compliance_score", check_nasa_compliance_score),
        ("check_af_scan_coverage", check_af_scan_coverage),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
