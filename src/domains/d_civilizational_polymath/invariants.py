"""Invariant checks for the civilizational polymath capability domain."""
from __future__ import annotations

from fractions import Fraction
from typing import List, Tuple

from axioms.logic import ProofObject

from .implementation import (
    MIN_REGISTER_COVERAGE,
    PolymathClaim,
    create_nominal_claim,
)


def check_all_registers_has_capability(
    data: PolymathClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: every civilizational register is at HAS status.

    Standard: BC-004 capability comparison (HAS / DOES_NOT_HAVE / UNKNOWN).
    Falsifies if: any of the five register capability flags is False.
    falsifies_if: any of the five register capability flags is False.
    """
    flags = {
        "mathematics": data.has_formal_mathematics,
        "science": data.has_empirical_science,
        "engineering": data.has_engineering,
        "governance": data.has_governance,
        "theology_ethics": data.has_theology_ethics,
    }
    missing = [name for name, flag in flags.items() if not flag]
    success = not missing
    proof = ProofObject(
        rule="check_all_registers_has_capability",
        premises=[f"{name}={flag}" for name, flag in flags.items()],
        conclusion=(
            "PASS: all 5 registers at HAS"
            if success else f"FAIL: missing registers={missing}"
        ),
    )
    return success, proof


def check_register_coverage_floor(
    data: PolymathClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: each register meets the coverage floor.

    Standard: AF-008 quarterly scan + OE-247 certainty threshold.
    Falsifies if: any register coverage < MIN_REGISTER_COVERAGE.
    falsifies_if: any register coverage < MIN_REGISTER_COVERAGE.
    """
    coverages = {
        "mathematics": data.mathematics_coverage,
        "science": data.science_coverage,
        "engineering": data.engineering_coverage,
        "governance": data.governance_coverage,
        "theology_ethics": data.theology_coverage,
    }
    below = [
        (name, cov) for name, cov in coverages.items() if cov < MIN_REGISTER_COVERAGE
    ]
    success = not below
    proof = ProofObject(
        rule="check_register_coverage_floor",
        premises=[f"floor={MIN_REGISTER_COVERAGE}"]
        + [f"{name}={cov}" for name, cov in coverages.items()],
        conclusion=(
            "PASS: all registers >= floor"
            if success
            else f"FAIL: under floor={[(n, str(c)) for n, c in below]}"
        ),
    )
    return success, proof


def check_cross_register_entailments_complete(
    data: PolymathClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: every declared cross-register entailment has a proof.

    Standard: YS-001 every truth is derivable + YS-004 no authority without proof.
    Falsifies if: proved entailments < total entailments.
    falsifies_if: proved entailments < total entailments.
    """
    total = max(data.cross_register_entailments_total, 0)
    proved = max(data.cross_register_entailments_proved, 0)
    success = proved >= total and total > 0
    proof = ProofObject(
        rule="check_cross_register_entailments_complete",
        premises=[
            f"proved={proved}",
            f"total={total}",
        ],
        conclusion=(
            "PASS: all entailments proved"
            if success
            else f"FAIL: unproved={total - proved}"
        ),
    )
    return success, proof


def check_coverage_monotone_across_registers(
    data: PolymathClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: no single register is more than 25 pp above the lowest.

    Standard: DR-001 technical register balance — prevents polymath claims
    that are strong in one register and vacuous elsewhere.
    Falsifies if: (max coverage - min coverage) > Fraction(1, 4).
    falsifies_if: (max coverage - min coverage) > Fraction(1, 4).
    """
    coverages = [
        data.mathematics_coverage,
        data.science_coverage,
        data.engineering_coverage,
        data.governance_coverage,
        data.theology_coverage,
    ]
    spread = max(coverages) - min(coverages)
    limit = Fraction(1, 4)
    success = spread <= limit
    proof = ProofObject(
        rule="check_coverage_monotone_across_registers",
        premises=[
            f"max={max(coverages)}",
            f"min={min(coverages)}",
            f"spread={spread}",
            f"limit={limit}",
        ],
        conclusion=(
            "PASS: coverage spread within tolerance"
            if success else f"FAIL: spread {spread} > {limit}"
        ),
    )
    return success, proof


def check_polymath_capability_invariant(
    data: PolymathClaim,
) -> Tuple[bool, ProofObject]:
    """Invariant: combined (capability AND coverage) polymath certificate holds.

    Standard: composite of the four preceding checks. Mirrors AF-008
    meta-standard scan that certifies the whole claim, not just one axis.
    Falsifies if: any of the four sub-invariants fail.
    falsifies_if: any of the four sub-invariants fail.
    """
    cap_ok, cap_proof = check_all_registers_has_capability(data)
    cov_ok, cov_proof = check_register_coverage_floor(data)
    ent_ok, ent_proof = check_cross_register_entailments_complete(data)
    mon_ok, mon_proof = check_coverage_monotone_across_registers(data)
    success = cap_ok and cov_ok and ent_ok and mon_ok
    proof = ProofObject(
        rule="check_polymath_capability_invariant",
        premises=[
            f"capability_ok={cap_ok}",
            f"coverage_ok={cov_ok}",
            f"entailments_ok={ent_ok}",
            f"monotone_ok={mon_ok}",
            f"capability_conclusion={cap_proof.conclusion}",
            f"coverage_conclusion={cov_proof.conclusion}",
            f"entailments_conclusion={ent_proof.conclusion}",
            f"monotone_conclusion={mon_proof.conclusion}",
        ],
        conclusion=(
            "PASS: polymath capability invariant holds"
            if success else "FAIL: at least one sub-invariant failed"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this domain on the nominal claim.

    Standard: Civilizational polymath nominal executable check set.
    Falsifies if: any invariant check returns False on the nominal claim.
    falsifies_if: any invariant check returns False on the nominal claim.
    """
    data = create_nominal_claim()
    checks = [
        ("check_all_registers_has_capability", check_all_registers_has_capability),
        ("check_register_coverage_floor", check_register_coverage_floor),
        (
            "check_cross_register_entailments_complete",
            check_cross_register_entailments_complete,
        ),
        (
            "check_coverage_monotone_across_registers",
            check_coverage_monotone_across_registers,
        ),
        ("check_polymath_capability_invariant", check_polymath_capability_invariant),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
