"""D_SEPARATION_OF_POWERS invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Articles I, II, III (Separation of Powers)
- INS v. Chadha (1983) — legislative veto unconstitutional
- Youngstown Sheet & Tube Co. v. Sawyer (1952) — executive power limits
- Clinton v. City of New York (1998) — presentment clause
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ExecutiveAction, LegislativeAction


def check_executive_action_authority(action: ExecutiveAction) -> Tuple[bool, ProofObject]:
    """
    Rule: Executive action must rest on statutory authorization or constitutional commander-in-chief power, must not use legislative veto, and must preserve judicial review.

    Standard: U.S. Constitution Article II; Youngstown Sheet & Tube Co. v. Sawyer (1952)
    falsifies_if: statutory_authorization is False AND commander_in_chief_power is False, OR legislative_veto_used is True, OR judicial_review_available is False.
    """
    has_authority = action.statutory_authorization or action.commander_in_chief_power
    no_legislative_veto = not action.legislative_veto_used
    success = has_authority and no_legislative_veto and action.judicial_review_available

    premises = [
        f"action_id={action.action_id}",
        f"statutory_authorization={action.statutory_authorization}",
        f"commander_in_chief_power={action.commander_in_chief_power}",
        f"has_authority={has_authority}",
        f"legislative_veto_used={action.legislative_veto_used}",
        f"congress_acquiescence={action.congress_acquiescence}",
        f"judicial_review_available={action.judicial_review_available}",
    ]

    if not success:
        return False, ProofObject(
            rule="ExecutiveActionAuthority",
            premises=premises,
            conclusion="VIOLATION: Separation of powers — executive action lacks authority, uses legislative veto, or bars judicial review",
        )

    return True, ProofObject(
        rule="ExecutiveActionAuthority",
        premises=premises,
        conclusion="Article II executive action authority satisfied — authorization, no legislative veto, judicial review available",
    )


def check_presentment_clause(legislation: LegislativeAction) -> Tuple[bool, ProofObject]:
    """
    Rule: All legislation must pass both chambers (bicameralism) and be presented to the President for signature or veto (presentment).

    Standard: U.S. Constitution Article I §7; INS v. Chadha (1983); Clinton v. City of New York (1998)
    falsifies_if: presentment_followed is False OR bicameralism_followed is False.
    """
    success = legislation.presentment_followed and legislation.bicameralism_followed

    premises = [
        f"action_id={legislation.action_id}",
        f"enumerated_power_basis={legislation.enumerated_power_basis}",
        f"presentment_followed={legislation.presentment_followed}",
        f"bicameralism_followed={legislation.bicameralism_followed}",
    ]

    if not success:
        return False, ProofObject(
            rule="PresentmentClause",
            premises=premises,
            conclusion="VIOLATION: Article I §7 presentment clause — legislation bypassed bicameralism or presentment requirement",
        )

    return True, ProofObject(
        rule="PresentmentClause",
        premises=premises,
        conclusion="Article I §7 presentment and bicameralism requirements satisfied",
    )


def check_nondelegation_doctrine(legislation: LegislativeAction) -> Tuple[bool, ProofObject]:
    """
    Rule: Congress may delegate legislative power only if it provides an intelligible principle to guide the agency.

    Standard: U.S. Constitution Article I §1; J.W. Hampton Jr. & Co. v. United States (1928)
    falsifies_if: nondelegation_intelligible_principle is False.
    """
    success = legislation.nondelegation_intelligible_principle

    premises = [
        f"action_id={legislation.action_id}",
        f"enumerated_power_basis={legislation.enumerated_power_basis}",
        f"nondelegation_intelligible_principle={legislation.nondelegation_intelligible_principle}",
    ]

    if not success:
        return False, ProofObject(
            rule="NondelegationDoctrine",
            premises=premises,
            conclusion="VIOLATION: Nondelegation doctrine — congressional delegation lacks intelligible principle",
        )

    return True, ProofObject(
        rule="NondelegationDoctrine",
        premises=premises,
        conclusion="Nondelegation doctrine satisfied — intelligible principle present in delegation",
    )


def run_all_invariants() -> dict:
    """Run all D_SEPARATION_OF_POWERS invariants with nominal sample data.

    falsifies_if: any separation of powers invariant check fails or raises an exception.
    """
    exec_action = ExecutiveAction(
        action_id="EXEC-001",
        statutory_authorization=True,
        commander_in_chief_power=False,
        legislative_veto_used=False,
        congress_acquiescence=True,
        judicial_review_available=True,
    )
    legislation = LegislativeAction(
        action_id="LEG-001",
        enumerated_power_basis="commerce_clause",
        presentment_followed=True,
        bicameralism_followed=True,
        nondelegation_intelligible_principle=True,
    )

    checks = [
        ("check_executive_action_authority", lambda: check_executive_action_authority(exec_action)),
        ("check_presentment_clause", lambda: check_presentment_clause(legislation)),
        ("check_nondelegation_doctrine", lambda: check_nondelegation_doctrine(legislation)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
