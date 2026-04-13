"""D_HABEAS_CORPUS invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Article I §9 Cl. 2 (Suspension Clause)
- 28 U.S.C. §2254 (State prisoners)
- 28 U.S.C. §2255 (Federal prisoners)
- AEDPA — Antiterrorism and Effective Death Penalty Act (1996)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import FrozenHabeasPetition


def check_habeas_jurisdiction(petition: FrozenHabeasPetition) -> Tuple[bool, ProofObject]:
    """
    Rule: Federal habeas corpus jurisdiction requires petitioner to be in custody and to have exhausted state remedies for state prisoners.

    Standard: 28 U.S.C. §2254(b)(1); Preiser v. Rodriguez (1973)
    falsifies_if: petitioner_in_custody is False OR (claim_type == 'state' AND exhausted_state_remedies is False).
    """
    custody_met = petition.petitioner_in_custody
    exhaustion_met = (
        petition.claim_type != "state"
        or petition.exhausted_state_remedies
    )
    success = custody_met and exhaustion_met

    premises = [
        f"petition_id={petition.petition_id}",
        f"petitioner_in_custody={petition.petitioner_in_custody}",
        f"claim_type={petition.claim_type}",
        f"exhausted_state_remedies={petition.exhausted_state_remedies}",
        f"exhaustion_met={exhaustion_met}",
    ]

    if not success:
        return False, ProofObject(
            rule="HabeasJurisdiction",
            premises=premises,
            conclusion="VIOLATION: 28 U.S.C. §2254 — habeas jurisdiction failed: petitioner not in custody or state remedies not exhausted",
        )

    return True, ProofObject(
        rule="HabeasJurisdiction",
        premises=premises,
        conclusion="28 U.S.C. §2254 habeas jurisdiction requirements satisfied",
    )


def check_aedpa_deadline(petition: FrozenHabeasPetition) -> Tuple[bool, ProofObject]:
    """
    Rule: AEDPA imposes a one-year statute of limitations on federal habeas petitions; actual innocence may toll the deadline.

    Standard: 28 U.S.C. §2244(d); McQuiggin v. Perkins (2013)
    falsifies_if: days_since_conviction > deadline_days AND actual_innocence_claim is False.
    """
    within_deadline = petition.days_since_conviction <= petition.deadline_days
    success = within_deadline or petition.actual_innocence_claim

    premises = [
        f"petition_id={petition.petition_id}",
        f"days_since_conviction={petition.days_since_conviction}",
        f"deadline_days={petition.deadline_days}",
        f"within_deadline={within_deadline}",
        f"actual_innocence_claim={petition.actual_innocence_claim}",
    ]

    if not success:
        return False, ProofObject(
            rule="AEDPADeadline",
            premises=premises,
            conclusion="VIOLATION: AEDPA §2244(d) — petition time-barred and no actual innocence exception",
        )

    return True, ProofObject(
        rule="AEDPADeadline",
        premises=premises,
        conclusion="AEDPA §2244(d) deadline satisfied — petition timely or actual innocence exception applies",
    )


def check_successive_petition_bar(petition: FrozenHabeasPetition) -> Tuple[bool, ProofObject]:
    """
    Rule: Successive habeas petitions are barred unless based on new constitutional rule or newly discovered evidence of actual innocence.

    Standard: 28 U.S.C. §2244(b); AEDPA
    falsifies_if: successive_petition is True AND actual_innocence_claim is False AND one_year_deadline_met is False.
    """
    if petition.successive_petition:
        success = petition.actual_innocence_claim or petition.one_year_deadline_met
    else:
        success = True

    premises = [
        f"petition_id={petition.petition_id}",
        f"successive_petition={petition.successive_petition}",
        f"actual_innocence_claim={petition.actual_innocence_claim}",
        f"one_year_deadline_met={petition.one_year_deadline_met}",
    ]

    if not success:
        return False, ProofObject(
            rule="SuccessivePetitionBar",
            premises=premises,
            conclusion="VIOLATION: AEDPA §2244(b) — successive petition barred without qualifying exception",
        )

    return True, ProofObject(
        rule="SuccessivePetitionBar",
        premises=premises,
        conclusion="AEDPA §2244(b) successive petition check satisfied",
    )


def run_all_invariants() -> dict:
    """Run all D_HABEAS_CORPUS invariants with nominal sample data.

    falsifies_if: any habeas corpus invariant check fails or raises an exception.
    """
    petition = FrozenHabeasPetition(
        petition_id="PET-001",
        petitioner_in_custody=True,
        claim_type="state",
        exhausted_state_remedies=True,
        one_year_deadline_met=True,
        actual_innocence_claim=False,
        successive_petition=False,
        days_since_conviction=Fraction(180),
        deadline_days=Fraction(365),
    )

    checks = [
        ("check_habeas_jurisdiction", lambda: check_habeas_jurisdiction(petition)),
        ("check_aedpa_deadline", lambda: check_aedpa_deadline(petition)),
        ("check_successive_petition_bar", lambda: check_successive_petition_bar(petition)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
