"""D_CITIZENSHIP invariants — Fraction only. 0 floats.

Standards:
- Immigration and Nationality Act (INA) 8 U.S.C. §1401
- U.S. Constitution 14th Amendment (Birthright Citizenship)
- INA 8 U.S.C. §1423 (Naturalization Requirements)
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CitizenshipApplication


def check_naturalization_requirements(app: CitizenshipApplication) -> Tuple[bool, ProofObject]:
    """
    Rule: Naturalization requires continuous residence >= required years, good moral character, English proficiency, civics knowledge, and no criminal bars.

    Standard: INA 8 U.S.C. §1423, §1427
    falsifies_if: years_continuous_residence < required_years OR criminal_bars is True OR good_moral_character is False.
    """
    residence_met = app.years_continuous_residence >= app.required_years
    no_criminal_bars = not app.criminal_bars
    all_criteria = app.good_moral_character and app.english_proficiency and app.civics_knowledge

    success = residence_met and no_criminal_bars and all_criteria

    premises = [
        f"applicant_id={app.applicant_id}",
        f"years_continuous_residence={app.years_continuous_residence}",
        f"required_years={app.required_years}",
        f"residence_met={residence_met}",
        f"good_moral_character={app.good_moral_character}",
        f"english_proficiency={app.english_proficiency}",
        f"civics_knowledge={app.civics_knowledge}",
        f"criminal_bars={app.criminal_bars}",
    ]

    if not success:
        return False, ProofObject(
            rule="NaturalizationRequirements",
            premises=premises,
            conclusion="VIOLATION: INA §1427 naturalization requirements not met — residence, character, or proficiency criteria failed",
        )

    return True, ProofObject(
        rule="NaturalizationRequirements",
        premises=premises,
        conclusion="INA §1427 naturalization requirements satisfied",
    )


def check_no_criminal_disqualification(app: CitizenshipApplication) -> Tuple[bool, ProofObject]:
    """
    Rule: Applicants with disqualifying criminal history are barred from naturalization.

    Standard: INA 8 U.S.C. §1101(f), §1182(a)
    falsifies_if: criminal_bars is True.
    """
    success = not app.criminal_bars

    premises = [
        f"applicant_id={app.applicant_id}",
        f"criminal_bars={app.criminal_bars}",
        f"good_moral_character={app.good_moral_character}",
    ]

    if not success:
        return False, ProofObject(
            rule="NoCriminalDisqualification",
            premises=premises,
            conclusion="VIOLATION: INA §1101(f) — applicant has disqualifying criminal history",
        )

    return True, ProofObject(
        rule="NoCriminalDisqualification",
        premises=premises,
        conclusion="INA §1101(f) criminal bar check passed — no disqualifying criminal history",
    )


def check_residency_duration(app: CitizenshipApplication) -> Tuple[bool, ProofObject]:
    """
    Rule: Continuous residence period must meet the statutory minimum.

    Standard: INA 8 U.S.C. §1427(a) (5 years) or §1430(a) (3 years for spouse of citizen)
    falsifies_if: years_continuous_residence < required_years.
    """
    success = app.years_continuous_residence >= app.required_years

    premises = [
        f"applicant_id={app.applicant_id}",
        f"years_continuous_residence={app.years_continuous_residence}",
        f"required_years={app.required_years}",
    ]

    if not success:
        return False, ProofObject(
            rule="ResidencyDuration",
            premises=premises,
            conclusion=f"VIOLATION: INA §1427(a) residency requirement not met — {app.years_continuous_residence} years < {app.required_years} required",
        )

    return True, ProofObject(
        rule="ResidencyDuration",
        premises=premises,
        conclusion="INA §1427(a) residency duration requirement satisfied",
    )


def run_all_invariants() -> dict:
    """Run all D_CITIZENSHIP invariants with nominal sample data.

    falsifies_if: any citizenship invariant check fails or raises an exception.
    """
    app = CitizenshipApplication(
        applicant_id="APP-001",
        years_continuous_residence=Fraction(5),
        required_years=Fraction(5),
        good_moral_character=True,
        english_proficiency=True,
        civics_knowledge=True,
        age_at_application=Fraction(30),
        renounced_prior_citizenship=True,
        criminal_bars=False,
    )

    checks = [
        ("check_naturalization_requirements", lambda: check_naturalization_requirements(app)),
        ("check_no_criminal_disqualification", lambda: check_no_criminal_disqualification(app)),
        ("check_residency_duration", lambda: check_residency_duration(app)),
    ]

    results = {}
    for name, func in checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as exc:
            results[name] = f"ERROR: {exc}"

    return results
