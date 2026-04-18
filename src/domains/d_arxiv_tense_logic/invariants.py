"""Invariant checks for d_arxiv_tense_logic."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import TenseLogicClaim, create_nominal_claim


def check_intuitionistic_base(data: TenseLogicClaim) -> Tuple[bool, ProofObject]:
    """Logic must be intuitionistic (not classical).

    Standard: arXiv 2603.29424v1 (cs.LO) claim operationalization.
    Falsifies if: not is_intuitionistic.
    falsifies_if: not is_intuitionistic.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_intuitionistic
    proof = ProofObject(
        rule="check_intuitionistic_base",
        premises=["paper_id=2603.29424v1", f"is_intuitionistic={data.is_intuitionistic}"],
        conclusion=(
            "PASS: logic is intuitionistic"
            if success
            else "FAIL: logic is not intuitionistic"
        ),
    )
    return success, proof


def check_loop_termination(data: TenseLogicClaim) -> Tuple[bool, ProofObject]:
    """Loop-checking procedure must terminate.

    Standard: arXiv 2603.29424v1 (cs.LO) claim operationalization.
    Falsifies if: not loop_check_terminates.
    falsifies_if: not loop_check_terminates.

    Returns:
        Tuple of (success, proof).
    """
    success = data.loop_check_terminates
    proof = ProofObject(
        rule="check_loop_termination",
        premises=["paper_id=2603.29424v1", f"loop_check_terminates={data.loop_check_terminates}"],
        conclusion=(
            "PASS: loop check terminates"
            if success
            else "FAIL: loop check does not terminate"
        ),
    )
    return success, proof


def check_counter_model_extraction(data: TenseLogicClaim) -> Tuple[bool, ProofObject]:
    """Either formula is provable or counter-model can be extracted.

    Standard: arXiv 2603.29424v1 (cs.LO) claim operationalization.
    Falsifies if: not formula_provable and not counter_model_extracted.
    falsifies_if: not formula_provable and not counter_model_extracted.

    Returns:
        Tuple of (success, proof).
    """
    success = data.formula_provable or data.counter_model_extracted
    proof = ProofObject(
        rule="check_counter_model_extraction",
        premises=[
            "paper_id=2603.29424v1",
            f"formula_provable={data.formula_provable}",
            f"counter_model_extracted={data.counter_model_extracted}",
        ],
        conclusion=(
            "PASS: proof or counter-model available"
            if success
            else "FAIL: neither proof nor counter-model available"
        ),
    )
    return success, proof


def check_sequent_depth_positive(data: TenseLogicClaim) -> Tuple[bool, ProofObject]:
    """Nested sequent depth must be at least 1.

    Standard: arXiv 2603.29424v1 (cs.LO) claim operationalization.
    Falsifies if: sequent_depth < 1.
    falsifies_if: sequent_depth < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.sequent_depth >= Fraction(1)
    proof = ProofObject(
        rule="check_sequent_depth_positive",
        premises=["paper_id=2603.29424v1", f"sequent_depth={data.sequent_depth}"],
        conclusion=(
            "PASS: sequent depth is positive"
            if success
            else "FAIL: sequent depth is zero or negative"
        ),
    )
    return success, proof


def check_decidability_via_loop_check(data: TenseLogicClaim) -> Tuple[bool, ProofObject]:
    """Decidability is ensured by terminating loop check.

    Standard: arXiv 2603.29424v1 (cs.LO) claim operationalization.
    Falsifies if: not loop_check_terminates.
    falsifies_if: not loop_check_terminates.

    Returns:
        Tuple of (success, proof).
    """
    success = data.loop_check_terminates
    proof = ProofObject(
        rule="check_decidability_via_loop_check",
        premises=["paper_id=2603.29424v1", f"loop_check_terminates={data.loop_check_terminates}"],
        conclusion=(
            "PASS: decidability via loop check holds"
            if success
            else "FAIL: decidability not ensured"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2603.29424v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_intuitionistic_base", check_intuitionistic_base),
        ("check_loop_termination", check_loop_termination),
        ("check_counter_model_extraction", check_counter_model_extraction),
        ("check_sequent_depth_positive", check_sequent_depth_positive),
        ("check_decidability_via_loop_check", check_decidability_via_loop_check),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
