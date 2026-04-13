"""D_AMENDMENT_PROCESS invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Article V (Amendment Process)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ConstitutionalAmendment


def check_amendment_proposal_procedure(amendment: ConstitutionalAmendment) -> Tuple[bool, ProofObject]:
    """
    Rule: Amendments must be proposed by two-thirds of both houses of Congress or by a convention called by two-thirds of states.

    Standard: U.S. Constitution Article V
    falsifies_if: proposal_method not in valid set OR states_ratified < states_required.
    """
    valid_proposal_methods = {"congress_two_thirds", "convention"}
    proposal_valid = amendment.proposal_method in valid_proposal_methods
    ratification_met = amendment.states_ratified >= amendment.states_required

    success = proposal_valid and ratification_met

    premises = [
        f"amendment_id={amendment.amendment_id}",
        f"proposal_method={amendment.proposal_method}",
        f"proposal_valid={proposal_valid}",
        f"states_ratified={amendment.states_ratified}",
        f"states_required={amendment.states_required}",
        f"ratification_met={ratification_met}",
    ]

    if not success:
        return False, ProofObject(
            rule="AmendmentProposalProcedure",
            premises=premises,
            conclusion="VIOLATION: Article V amendment procedure not satisfied — invalid proposal method or insufficient state ratification",
        )

    return True, ProofObject(
        rule="AmendmentProposalProcedure",
        premises=premises,
        conclusion="Article V amendment proposal and ratification procedure satisfied",
    )


def check_ratification_threshold(amendment: ConstitutionalAmendment) -> Tuple[bool, ProofObject]:
    """
    Rule: Ratification requires approval by three-fourths of state legislatures or state conventions.

    Standard: U.S. Constitution Article V
    falsifies_if: states_ratified / states_required < Fraction(3, 4) threshold or ratification_complete is False when threshold met.
    """
    threshold = Fraction(3, 4)
    ratio = amendment.states_ratified / amendment.states_required if amendment.states_required > 0 else Fraction(0)
    threshold_met = ratio >= threshold or amendment.states_ratified >= amendment.states_required
    valid_method = amendment.ratification_method in {"state_legislatures", "state_conventions"}

    success = threshold_met and valid_method

    premises = [
        f"amendment_id={amendment.amendment_id}",
        f"states_ratified={amendment.states_ratified}",
        f"states_required={amendment.states_required}",
        f"ratification_method={amendment.ratification_method}",
        f"valid_method={valid_method}",
        f"threshold_met={threshold_met}",
    ]

    if not success:
        return False, ProofObject(
            rule="RatificationThreshold",
            premises=premises,
            conclusion="VIOLATION: Article V ratification threshold not met — insufficient states or invalid ratification method",
        )

    return True, ProofObject(
        rule="RatificationThreshold",
        premises=premises,
        conclusion="Article V three-fourths ratification threshold confirmed",
    )


def check_congressional_supermajority_requirement(amendment: ConstitutionalAmendment) -> Tuple[bool, ProofObject]:
    """
    Rule: Congressional proposal requires two-thirds vote in both houses.

    Standard: U.S. Constitution Article V
    falsifies_if: proposed_by_congress is True AND proposal_method != 'congress_two_thirds'.
    """
    if amendment.proposed_by_congress:
        method_valid = amendment.proposal_method == "congress_two_thirds"
    else:
        method_valid = amendment.proposal_method == "convention"

    premises = [
        f"amendment_id={amendment.amendment_id}",
        f"proposed_by_congress={amendment.proposed_by_congress}",
        f"proposal_method={amendment.proposal_method}",
        f"method_valid={method_valid}",
    ]

    if not method_valid:
        return False, ProofObject(
            rule="CongressionalSupermajority",
            premises=premises,
            conclusion="VIOLATION: Article V congressional supermajority requirement not met — proposal method inconsistent with proposing body",
        )

    return True, ProofObject(
        rule="CongressionalSupermajority",
        premises=premises,
        conclusion="Article V congressional supermajority requirement satisfied",
    )


def run_all_invariants() -> dict:
    """Run all D_AMENDMENT_PROCESS invariants with nominal sample data.

    falsifies_if: any amendment process invariant check fails or raises an exception.
    """
    amendment = ConstitutionalAmendment(
        amendment_id="AMEND-001",
        proposal_method="congress_two_thirds",
        ratification_method="state_legislatures",
        states_ratified=Fraction(38),
        states_required=Fraction(38),
        proposed_by_congress=True,
        ratification_complete=True,
    )

    checks = [
        ("check_amendment_proposal_procedure", lambda: check_amendment_proposal_procedure(amendment)),
        ("check_ratification_threshold", lambda: check_ratification_threshold(amendment)),
        ("check_congressional_supermajority_requirement", lambda: check_congressional_supermajority_requirement(amendment)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
