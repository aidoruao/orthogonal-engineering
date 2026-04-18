"""Invariant checks for d_arxiv_decidable_construction."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import DecidableConstructionClaim, create_nominal_claim


def check_decidability(data: DecidableConstructionClaim) -> Tuple[bool, ProofObject]:
    """System property must be decidable.

    Standard: arXiv 2603.25414v1 (cs.LO) claim operationalization.
    Falsifies if: not property_is_decidable.
    falsifies_if: not property_is_decidable.

    Returns:
        Tuple of (success, proof).
    """
    success = data.property_is_decidable
    proof = ProofObject(
        rule="check_decidability",
        premises=["paper_id=2603.25414v1", f"property_is_decidable={data.property_is_decidable}"],
        conclusion=(
            "PASS: property is decidable"
            if success
            else "FAIL: property is not decidable"
        ),
    )
    return success, proof


def check_design_time_verification(data: DecidableConstructionClaim) -> Tuple[bool, ProofObject]:
    """Verification must be performed at design time.

    Standard: arXiv 2603.25414v1 (cs.LO) claim operationalization.
    Falsifies if: not verified_at_design_time.
    falsifies_if: not verified_at_design_time.

    Returns:
        Tuple of (success, proof).
    """
    success = data.verified_at_design_time
    proof = ProofObject(
        rule="check_design_time_verification",
        premises=["paper_id=2603.25414v1", f"verified_at_design_time={data.verified_at_design_time}"],
        conclusion=(
            "PASS: design-time verification holds"
            if success
            else "FAIL: design-time verification not performed"
        ),
    )
    return success, proof


def check_soundness(data: DecidableConstructionClaim) -> Tuple[bool, ProofObject]:
    """Verification procedure soundness must be guaranteed.

    Standard: arXiv 2603.25414v1 (cs.LO) claim operationalization.
    Falsifies if: not soundness_guaranteed.
    falsifies_if: not soundness_guaranteed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.soundness_guaranteed
    proof = ProofObject(
        rule="check_soundness",
        premises=["paper_id=2603.25414v1", f"soundness_guaranteed={data.soundness_guaranteed}"],
        conclusion=(
            "PASS: soundness is guaranteed"
            if success
            else "FAIL: soundness not guaranteed"
        ),
    )
    return success, proof


def check_completeness(data: DecidableConstructionClaim) -> Tuple[bool, ProofObject]:
    """Verification procedure completeness must be guaranteed.

    Standard: arXiv 2603.25414v1 (cs.LO) claim operationalization.
    Falsifies if: not completeness_guaranteed.
    falsifies_if: not completeness_guaranteed.

    Returns:
        Tuple of (success, proof).
    """
    success = data.completeness_guaranteed
    proof = ProofObject(
        rule="check_completeness",
        premises=["paper_id=2603.25414v1", f"completeness_guaranteed={data.completeness_guaranteed}"],
        conclusion=(
            "PASS: completeness is guaranteed"
            if success
            else "FAIL: completeness not guaranteed"
        ),
    )
    return success, proof


def check_verification_steps_positive(data: DecidableConstructionClaim) -> Tuple[bool, ProofObject]:
    """At least one verification step must be performed.

    Standard: arXiv 2603.25414v1 (cs.LO) claim operationalization.
    Falsifies if: verification_steps < 1.
    falsifies_if: verification_steps < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.verification_steps >= Fraction(1)
    proof = ProofObject(
        rule="check_verification_steps_positive",
        premises=["paper_id=2603.25414v1", f"verification_steps={data.verification_steps}"],
        conclusion=(
            "PASS: verification steps are positive"
            if success
            else "FAIL: verification steps are zero or negative"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2603.25414v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_decidability", check_decidability),
        ("check_design_time_verification", check_design_time_verification),
        ("check_soundness", check_soundness),
        ("check_completeness", check_completeness),
        ("check_verification_steps_positive", check_verification_steps_positive),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
