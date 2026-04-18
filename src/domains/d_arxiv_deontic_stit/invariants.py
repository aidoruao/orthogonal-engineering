"""Invariant checks for d_arxiv_deontic_stit."""
from __future__ import annotations
from fractions import Fraction
from typing import List, Tuple
from axioms.logic import ProofObject
from .implementation import DeonticSTITClaim, create_nominal_claim


def check_ought_implies_can(data: DeonticSTITClaim) -> Tuple[bool, ProofObject]:
    """Obligation implies ability: OUGHT implies CAN.

    Standard: arXiv 2604.00967v1 (cs.LO) claim operationalization.
    Falsifies if: action_is_obligatory and not agent_can_perform_action.
    falsifies_if: action_is_obligatory and not agent_can_perform_action.

    Returns:
        Tuple of (success, proof).
    """
    success = not data.action_is_obligatory or data.agent_can_perform_action
    proof = ProofObject(
        rule="check_ought_implies_can",
        premises=[
            "paper_id=2604.00967v1",
            f"action_is_obligatory={data.action_is_obligatory}",
            f"agent_can_perform_action={data.agent_can_perform_action}",
        ],
        conclusion=(
            "PASS: ought-implies-can holds"
            if success
            else "FAIL: obligation without ability"
        ),
    )
    return success, proof


def check_stit_model_validity(data: DeonticSTITClaim) -> Tuple[bool, ProofObject]:
    """STIT model must be valid.

    Standard: arXiv 2604.00967v1 (cs.LO) claim operationalization.
    Falsifies if: not stit_model_valid.
    falsifies_if: not stit_model_valid.

    Returns:
        Tuple of (success, proof).
    """
    success = data.stit_model_valid
    proof = ProofObject(
        rule="check_stit_model_validity",
        premises=["paper_id=2604.00967v1", f"stit_model_valid={data.stit_model_valid}"],
        conclusion=(
            "PASS: STIT model is valid"
            if success
            else "FAIL: STIT model is invalid"
        ),
    )
    return success, proof


def check_oic_consistency(data: DeonticSTITClaim) -> Tuple[bool, ProofObject]:
    """Ought-implies-can flag must be consistent with agent ability and obligation.

    Standard: arXiv 2604.00967v1 (cs.LO) claim operationalization.
    Falsifies if: ought_implies_can != (not action_is_obligatory or agent_can_perform_action).
    falsifies_if: ought_implies_can != (not action_is_obligatory or agent_can_perform_action).

    Returns:
        Tuple of (success, proof).
    """
    expected = not data.action_is_obligatory or data.agent_can_perform_action
    success = data.ought_implies_can == expected
    proof = ProofObject(
        rule="check_oic_consistency",
        premises=[
            "paper_id=2604.00967v1",
            f"ought_implies_can={data.ought_implies_can}",
            f"expected={expected}",
        ],
        conclusion=(
            "PASS: OIC flag is consistent"
            if success
            else "FAIL: OIC flag is inconsistent"
        ),
    )
    return success, proof


def check_alternatives_positive(data: DeonticSTITClaim) -> Tuple[bool, ProofObject]:
    """Agent must have at least one alternative.

    Standard: arXiv 2604.00967v1 (cs.LO) claim operationalization.
    Falsifies if: alternative_count < 1.
    falsifies_if: alternative_count < 1.

    Returns:
        Tuple of (success, proof).
    """
    success = data.alternative_count >= Fraction(1)
    proof = ProofObject(
        rule="check_alternatives_positive",
        premises=["paper_id=2604.00967v1", f"alternative_count={data.alternative_count}"],
        conclusion=(
            "PASS: alternatives count is positive"
            if success
            else "FAIL: no alternatives available"
        ),
    )
    return success, proof


def check_agency_requirement(data: DeonticSTITClaim) -> Tuple[bool, ProofObject]:
    """Agent must have at least two alternatives for genuine agency.

    Standard: arXiv 2604.00967v1 (cs.LO) claim operationalization.
    Falsifies if: alternative_count < 2.
    falsifies_if: alternative_count < 2.

    Returns:
        Tuple of (success, proof).
    """
    success = data.alternative_count >= Fraction(2)
    proof = ProofObject(
        rule="check_agency_requirement",
        premises=["paper_id=2604.00967v1", f"alternative_count={data.alternative_count}"],
        conclusion=(
            "PASS: agency requirement satisfied"
            if success
            else "FAIL: insufficient alternatives for agency"
        ),
    )
    return success, proof


def run_all_invariants() -> List[Tuple[str, bool, ProofObject]]:
    """Run all invariants for this arXiv-derived domain.

    Standard: arXiv 2604.00967v1 (cs.LO) nominal executable check set.
    Falsifies if: any invariant check returns False.
    falsifies_if: any invariant check returns False.

    Returns:
        List of (name, success, proof) tuples.
    """
    data = create_nominal_claim()
    checks = [
        ("check_ought_implies_can", check_ought_implies_can),
        ("check_stit_model_validity", check_stit_model_validity),
        ("check_oic_consistency", check_oic_consistency),
        ("check_alternatives_positive", check_alternatives_positive),
        ("check_agency_requirement", check_agency_requirement),
    ]
    results: List[Tuple[str, bool, ProofObject]] = []
    for name, func in checks:
        success, proof = func(data)
        print(f"{name}: {'PASS' if success else 'FAIL'}")
        results.append((name, success, proof))
    return results
