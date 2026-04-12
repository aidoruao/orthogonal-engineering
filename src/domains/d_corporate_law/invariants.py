"""D_CORPORATE_LAW invariants — Yeshua Standard. 0 floats.

Standards:
- Delaware General Corporation Law (DGCL) §144 — interested director transactions
- Smith v. Van Gorkom, 488 A.2d 858 (Del. 1985) — business judgment rule
- ALI Principles of Corporate Governance §4.01
- Sarbanes-Oxley Act §302 — fiduciary certification
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import Director, CorporateTransaction


def check_self_dealing_requires_disclosure(tx: CorporateTransaction) -> Tuple[bool, ProofObject]:
    """Self-dealing transaction requires complete disclosure.

    Standard: DGCL §144(a)(1) — material facts fully disclosed
    falsifies_if: tx.involves_self_dealing is True and tx.disclosure_complete is False.
    """
    if tx.involves_self_dealing:
        ok = tx.disclosure_complete
    else:
        ok = True
    premises = [
        f"transaction_id={tx.transaction_id}",
        f"involves_self_dealing={tx.involves_self_dealing}",
        f"disclosure_complete={tx.disclosure_complete}",
    ]
    return ok, ProofObject(
        rule="SelfDealingRequiresDisclosure",
        premises=premises,
        conclusion="PASS: disclosure requirement satisfied" if ok else "VIOLATION: self-dealing without disclosure",
    )


def check_duty_of_loyalty_prevents_self_dealing(tx: CorporateTransaction) -> Tuple[bool, ProofObject]:
    """Duty of loyalty: self-dealing transactions must be approved by disinterested directors.

    Standard: DGCL §144(a)(1); ALI Principles §4.01
    falsifies_if: tx.involves_self_dealing is True and approved_by_disinterested is False.
    """
    if tx.involves_self_dealing:
        ok = tx.approved_by_disinterested
    else:
        ok = True
    premises = [
        f"transaction_id={tx.transaction_id}",
        f"involves_self_dealing={tx.involves_self_dealing}",
        f"approved_by_disinterested={tx.approved_by_disinterested}",
    ]
    return ok, ProofObject(
        rule="DutyOfLoyaltyPreventsUnreviewedSelfDealing",
        premises=premises,
        conclusion="PASS: duty of loyalty satisfied" if ok else "VIOLATION: self-dealing without disinterested review",
    )


def check_corporate_veil_piercing_factors_cumulative(tx: CorporateTransaction) -> Tuple[bool, ProofObject]:
    """Board-approved transactions with complete disclosure are veil-piercing resistant.

    Standard: Walkovszky v. Carlton (N.Y. 1966) — corporate veil factors
    falsifies_if: tx.approved_by_board is False and tx.disclosure_complete is False.
    """
    ok = tx.approved_by_board or tx.disclosure_complete
    premises = [
        f"transaction_id={tx.transaction_id}",
        f"approved_by_board={tx.approved_by_board}",
        f"disclosure_complete={tx.disclosure_complete}",
    ]
    return ok, ProofObject(
        rule="CorporateVeilPiercingFactors",
        premises=premises,
        conclusion="PASS: veil-piercing factors not met" if ok else "VIOLATION: unapproved undisclosed transaction",
    )


def check_transaction_board_approved(tx: CorporateTransaction) -> Tuple[bool, ProofObject]:
    """Major corporate transaction must be approved by the board.

    Standard: DGCL §141(a) — board authority; Smith v. Van Gorkom (1985)
    falsifies_if: tx.approved_by_board is False.
    """
    ok = tx.approved_by_board
    premises = [
        f"transaction_id={tx.transaction_id}",
        f"value={tx.value}",
        f"approved_by_board={tx.approved_by_board}",
    ]
    return ok, ProofObject(
        rule="TransactionBoardApproved",
        premises=premises,
        conclusion="PASS: board approved" if ok else "VIOLATION: transaction not board-approved",
    )


def check_transaction_value_nonneg(tx: CorporateTransaction) -> Tuple[bool, ProofObject]:
    """Transaction value must be >= 0.

    Standard: DGCL — transaction consideration must be documented
    falsifies_if: tx.value < 0.
    """
    ok = tx.value >= Fraction(0)
    premises = [
        f"transaction_id={tx.transaction_id}",
        f"value={tx.value}",
    ]
    return ok, ProofObject(
        rule="TransactionValueNonNeg",
        premises=premises,
        conclusion=f"PASS: value {tx.value} >= 0" if ok else "VIOLATION: negative transaction value",
    )


def check_director_id_nonempty(director: Director) -> Tuple[bool, ProofObject]:
    """Director must have a non-empty director_id.

    Standard: SEC Form DEF 14A — director identification requirement
    falsifies_if: director.director_id is empty.
    """
    ok = bool(director.director_id.strip())
    premises = [f"name={director.name}", f"director_id={director.director_id!r}"]
    return ok, ProofObject(
        rule="DirectorIdNonEmpty",
        premises=premises,
        conclusion="PASS: director_id set" if ok else "VIOLATION: director_id empty",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    director = Director(name="Alice Smith", director_id="DIR-001")
    tx = CorporateTransaction(
        transaction_id="TX-001",
        description="Acquisition of subsidiary",
        counterparty="SubCorp LLC",
        value=Fraction(50_000_000),
        approved_by_board=True,
        approved_by_disinterested=True,
        disclosure_complete=True,
        fairness_opinion_obtained=True,
    )
    results = {}
    for fn, args in [
        (check_self_dealing_requires_disclosure, (tx,)),
        (check_duty_of_loyalty_prevents_self_dealing, (tx,)),
        (check_corporate_veil_piercing_factors_cumulative, (tx,)),
        (check_transaction_board_approved, (tx,)),
        (check_transaction_value_nonneg, (tx,)),
        (check_director_id_nonempty, (director,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
