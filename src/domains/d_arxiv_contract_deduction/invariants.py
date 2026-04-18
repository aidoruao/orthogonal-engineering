"""Invariant checks for d_arxiv_contract_deduction."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import ContractDeductionClaim, create_nominal_claim


def check_contract_soundness(data: ContractDeductionClaim) -> Tuple[bool, ProofObject]:
    """Deductive system must be sound.

    Standard: arXiv 2604.09165v1 (cs.LO) claim operationalization.
    Falsifies if: not is_sound.
    falsifies_if: not is_sound.

    Returns:
        Tuple of (success, proof).
    """
    success = data.is_sound
    proof = ProofObject(
        rule="check_contract_soundness",
        premises=["paper_id=2604.09165v1", f"is_sound={data.is_sound}"],
        conclusion=(
            "PASS: deductive system is sound"
            if success
            else "FAIL: deductive system is not sound"
        ),
    )
    return success, proof


def check_precondition_required(data: ContractDeductionClaim) -> Tuple[bool, ProofObject]:
    """Postcondition cannot be derived without precondition.

    Standard: arXiv 2604.09165v1 (cs.LO) claim operationalization.
    Falsifies if: postcondition_derived and not precondition_satisfied.
    falsifies_if: postcondition_derived and not precondition_satisfied.

    Returns:
        Tuple of (success, proof).
    """
    success = not data.postcondition_derived or data.precondition_satisfied
    proof = ProofObject(
        rule="check_precondition_required",
        premises=[
            "paper_id=2604.09165v1",
            f"precondition_satisfied={data.precondition_satisfied}",
            f"postcondition_derived={data.postcondition_derived}",
        ],
        conclusion=(
            "PASS: precondition requirement satisfied"
            if success
            else "FAIL: postcondition derived without precondition"
        ),
    )
    return success, proof


def check_axiom_count_positive(data: ContractDeductionClaim) -> Tuple[bool, ProofObject]:
    """At least one axiom must be applied.

    Standard: arXiv 2604.09165v1 (cs.LO) claim operationalization.
    Falsifies if: contract_axioms_used < 1.
    falsifies_if: contract_axioms_used < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.contract_axioms_used >= Fraction(1)
    proof = ProofObject(
        rule="check_axiom_count_positive",
        premises=["paper_id=2604.09165v1", f"contract_axioms_used={data.contract_axioms_used}"],
        conclusion=(
            "PASS: axiom count is positive"
            if success
            else "FAIL: axiom count is zero or negative"
        ),
    )
    return success, proof


def check_inference_steps_positive(data: ContractDeductionClaim) -> Tuple[bool, ProofObject]:
    """At least one inference step must be performed.

    Standard: arXiv 2604.09165v1 (cs.LO) claim operationalization.
    Falsifies if: inference_steps < 1.
    falsifies_if: inference_steps < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.inference_steps >= Fraction(1)
    proof = ProofObject(
        rule="check_inference_steps_positive",
        premises=["paper_id=2604.09165v1", f"inference_steps={data.inference_steps}"],
        conclusion=(
            "PASS: inference steps are positive"
            if success
            else "FAIL: inference steps are zero or negative"
        ),
    )
    return success, proof


def check_derivation_bound(data: ContractDeductionClaim) -> Tuple[bool, ProofObject]:
    """Inference steps must not exceed 10x axiom count.

    Standard: arXiv 2604.09165v1 (cs.LO) claim operationalization.
    Falsifies if: inference_steps > contract_axioms_used * 10.
    falsifies_if: inference_steps > contract_axioms_used * 10.

    Returns:
        Tuple of (success, proof).
    """
    bound = data.contract_axioms_used * Fraction(10)
    success = data.inference_steps <= bound
    proof = ProofObject(
        rule="check_derivation_bound",
        premises=[
            "paper_id=2604.09165v1",
            f"inference_steps={data.inference_steps}",
            f"bound={bound}",
        ],
        conclusion=(
            "PASS: derivation bound satisfied"
            if success
            else "FAIL: derivation bound exceeded"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.09165v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_contract_soundness", check_contract_soundness),
        ("check_precondition_required", check_precondition_required),
        ("check_axiom_count_positive", check_axiom_count_positive),
        ("check_inference_steps_positive", check_inference_steps_positive),
        ("check_derivation_bound", check_derivation_bound),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
