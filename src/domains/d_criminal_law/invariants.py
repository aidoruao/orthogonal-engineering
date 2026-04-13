"""D_CRIMINAL_LAW invariants — Fraction only. 0 floats.

Standards:
- U.S. Constitution Amendment IV (Search and Seizure)
- U.S. Constitution Amendment V (Double Jeopardy, Due Process)
- U.S. Constitution Amendment VI (Speedy Trial)
- Speedy Trial Act, 18 U.S.C. §3161
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CriminalSearch, CriminalCharge


def check_fourth_amendment_search(search: CriminalSearch) -> Tuple[bool, ProofObject]:
    """
    Rule: A search is constitutional if a warrant was obtained, OR if an exception applies (probable cause + exigent circumstances, consent, or plain view).

    Standard: U.S. Constitution Amendment IV; Katz v. United States (1967)
    falsifies_if: warrant_obtained is False AND no recognized exception applies.
    """
    has_exception = (
        (search.probable_cause_documented and search.exigent_circumstances)
        or search.consent_given
        or search.plain_view
    )
    success = search.warrant_obtained or has_exception

    premises = [
        f"search_id={search.search_id}",
        f"warrant_obtained={search.warrant_obtained}",
        f"probable_cause_documented={search.probable_cause_documented}",
        f"exigent_circumstances={search.exigent_circumstances}",
        f"consent_given={search.consent_given}",
        f"plain_view={search.plain_view}",
        f"has_exception={has_exception}",
    ]

    if not success:
        return False, ProofObject(
            rule="FourthAmendmentSearch",
            premises=premises,
            conclusion="VIOLATION: Fourth Amendment — warrantless search without recognized exception",
        )

    return True, ProofObject(
        rule="FourthAmendmentSearch",
        premises=premises,
        conclusion="Fourth Amendment search requirements satisfied — warrant or valid exception present",
    )


def check_due_process_charge(charge: CriminalCharge) -> Tuple[bool, ProofObject]:
    """
    Rule: Criminal prosecution requires proof beyond a reasonable doubt, no double jeopardy bar, and trial within speedy trial limits.

    Standard: U.S. Constitution Amendments V, VI; In re Winship (1970); Speedy Trial Act 18 U.S.C. §3161
    falsifies_if: beyond_reasonable_doubt is False OR double_jeopardy_bar is True OR speedy_trial_days > max_speedy_trial_days.
    """
    speedy_trial_met = charge.speedy_trial_days <= charge.max_speedy_trial_days
    success = (
        charge.beyond_reasonable_doubt
        and not charge.double_jeopardy_bar
        and speedy_trial_met
    )

    premises = [
        f"charge_id={charge.charge_id}",
        f"beyond_reasonable_doubt={charge.beyond_reasonable_doubt}",
        f"double_jeopardy_bar={charge.double_jeopardy_bar}",
        f"speedy_trial_days={charge.speedy_trial_days}",
        f"max_speedy_trial_days={charge.max_speedy_trial_days}",
        f"speedy_trial_met={speedy_trial_met}",
    ]

    if not success:
        return False, ProofObject(
            rule="DueProcessCharge",
            premises=premises,
            conclusion="VIOLATION: Due process — prosecution fails reasonable doubt standard, double jeopardy bar, or speedy trial limit",
        )

    return True, ProofObject(
        rule="DueProcessCharge",
        premises=premises,
        conclusion="Fifth and Sixth Amendment due process requirements satisfied",
    )


def check_double_jeopardy_bar(charge: CriminalCharge) -> Tuple[bool, ProofObject]:
    """
    Rule: No person shall be subject to double jeopardy — tried twice for the same offense.

    Standard: U.S. Constitution Amendment V; Blockburger v. United States (1932)
    falsifies_if: double_jeopardy_bar is True (prosecution barred by prior acquittal/conviction).
    """
    success = not charge.double_jeopardy_bar

    premises = [
        f"charge_id={charge.charge_id}",
        f"double_jeopardy_bar={charge.double_jeopardy_bar}",
    ]

    if not success:
        return False, ProofObject(
            rule="DoubleJeopardyBar",
            premises=premises,
            conclusion="VIOLATION: Fifth Amendment double jeopardy — prosecution barred by prior jeopardy",
        )

    return True, ProofObject(
        rule="DoubleJeopardyBar",
        premises=premises,
        conclusion="Fifth Amendment double jeopardy check passed — no prior jeopardy bar",
    )


def run_all_invariants() -> dict:
    """Run all D_CRIMINAL_LAW invariants with nominal sample data.

    falsifies_if: any criminal law invariant check fails or raises an exception.
    """
    search = CriminalSearch(
        search_id="SEARCH-001",
        warrant_obtained=True,
        probable_cause_documented=True,
        exigent_circumstances=False,
        consent_given=False,
        plain_view=False,
    )
    charge = CriminalCharge(
        charge_id="CHARGE-001",
        elements_proven=Fraction(1),
        beyond_reasonable_doubt=True,
        double_jeopardy_bar=False,
        speedy_trial_days=Fraction(60),
        max_speedy_trial_days=Fraction(70),
    )

    checks = [
        ("check_fourth_amendment_search", lambda: check_fourth_amendment_search(search)),
        ("check_due_process_charge", lambda: check_due_process_charge(charge)),
        ("check_double_jeopardy_bar", lambda: check_double_jeopardy_bar(charge)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
