"""D_BILL_OF_RIGHTS invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Amendments 1-10 (Bill of Rights)
- First Amendment: Congress shall make no law abridging freedom of speech
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ConstitutionalRight


def check_first_amendment_prior_restraint(right: ConstitutionalRight) -> Tuple[bool, ProofObject]:
    """
    Rule: Prior restraint on speech carries a heavy presumption of unconstitutionality (Near v. Minnesota, 1931).

    Standard: U.S. Constitution Amendment I
    falsifies_if: prior_restraint is True AND government_actor is True.
    """
    violation = right.prior_restraint and right.government_actor
    success = not violation

    premises = [
        f"right_id={right.right_id}",
        f"amendment_number={right.amendment_number}",
        f"government_actor={right.government_actor}",
        f"prior_restraint={right.prior_restraint}",
    ]

    if not success:
        return False, ProofObject(
            rule="FirstAmendmentPriorRestraint",
            premises=premises,
            conclusion="VIOLATION: First Amendment prior restraint prohibition violated — government imposed prior restraint on speech",
        )

    return True, ProofObject(
        rule="FirstAmendmentPriorRestraint",
        premises=premises,
        conclusion="First Amendment prior restraint prohibition satisfied — no unconstitutional prior restraint",
    )


def check_strict_scrutiny_applied(right: ConstitutionalRight) -> Tuple[bool, ProofObject]:
    """
    Rule: When government restricts fundamental rights, strict scrutiny requires compelling interest + narrow tailoring.

    Standard: U.S. Constitution Amendments I, XIV; strict scrutiny doctrine
    falsifies_if: restriction_applies is True AND government_actor is True AND (compelling_interest is False OR narrowly_tailored is False).
    """
    if right.restriction_applies and right.government_actor:
        success = right.compelling_interest and right.narrowly_tailored
    else:
        success = True

    premises = [
        f"right_id={right.right_id}",
        f"amendment_number={right.amendment_number}",
        f"government_actor={right.government_actor}",
        f"restriction_applies={right.restriction_applies}",
        f"compelling_interest={right.compelling_interest}",
        f"narrowly_tailored={right.narrowly_tailored}",
    ]

    if not success:
        return False, ProofObject(
            rule="StrictScrutinyApplied",
            premises=premises,
            conclusion="VIOLATION: Strict scrutiny not met — government restriction lacks compelling interest or narrow tailoring",
        )

    return True, ProofObject(
        rule="StrictScrutinyApplied",
        premises=premises,
        conclusion="Strict scrutiny satisfied — compelling interest and narrow tailoring confirmed",
    )


def check_bill_of_rights_state_action(right: ConstitutionalRight) -> Tuple[bool, ProofObject]:
    """
    Rule: Bill of Rights protections apply only to government actors, not purely private conduct (state action doctrine).

    Standard: U.S. Constitution Amendments I-X; Civil Rights Cases (1883)
    falsifies_if: right is claimed against non-government actor without incorporation theory.
    """
    invalid_claim = right.restriction_applies and not right.government_actor
    success = not invalid_claim

    premises = [
        f"right_id={right.right_id}",
        f"amendment_number={right.amendment_number}",
        f"government_actor={right.government_actor}",
        f"restriction_applies={right.restriction_applies}",
    ]

    if not success:
        return False, ProofObject(
            rule="BillOfRightsStateAction",
            premises=premises,
            conclusion="VIOLATION: State action doctrine — Bill of Rights restriction claimed against private actor",
        )

    return True, ProofObject(
        rule="BillOfRightsStateAction",
        premises=premises,
        conclusion="State action doctrine satisfied — restriction properly attributed to government actor",
    )


def run_all_invariants() -> dict:
    """Run all D_BILL_OF_RIGHTS invariants with nominal sample data.

    falsifies_if: any Bill of Rights invariant check fails or raises an exception.
    """
    right = ConstitutionalRight(
        right_id="RIGHT-001",
        amendment_number=1,
        right_description="Freedom of speech",
        government_actor=True,
        restriction_applies=True,
        compelling_interest=True,
        narrowly_tailored=True,
        prior_restraint=False,
    )

    checks = [
        ("check_first_amendment_prior_restraint", lambda: check_first_amendment_prior_restraint(right)),
        ("check_strict_scrutiny_applied", lambda: check_strict_scrutiny_applied(right)),
        ("check_bill_of_rights_state_action", lambda: check_bill_of_rights_state_action(right)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
