#!/usr/bin/env python3
"""School Equity Domain Invariants — ESSA, IDEA, disparate impact.

Standards:
- Title I ESSA
- IDEA
- Civil Rights Act Title VI
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import School, DisciplineRecord


def check_spending_equity(school: School) -> Tuple[bool, ProofObject]:
    """Spending ratio must be at least 0.8 of state average.

    Falsifies if: school.spending_equity_ratio() < 0.8.
    falsifies_if: school.spending_equity_ratio() < 0.8.
    """
    ratio = school.spending_equity_ratio()
    if ratio < Fraction(8, 10):
        return False, ProofObject(
            conclusion=f"VIOLATION: Spending {ratio}x below state average",
            premises=[f"School: {school.school_id}"],
            rule="essa_equitable_spending"
        )
    return True, ProofObject(
        conclusion="Spending equitable",
        premises=[f"Ratio: {ratio}"],
        rule="spending_compliant"
    )


def check_disparate_impact(discipline: DisciplineRecord, threshold: Fraction) -> Tuple[bool, ProofObject]:
    """Disparate impact ratio must stay within threshold.

    Falsifies if: discipline.disparate_impact_ratio(r1, r2) > threshold for any races.
    falsifies_if: discipline.disparate_impact_ratio(r1, r2) > threshold for any races.
    """
    races = list(discipline.enrollment_by_race.keys())
    for r1 in races:
        for r2 in races:
            if r1 != r2:
                ratio = discipline.disparate_impact_ratio(r1, r2)
                if ratio > threshold:
                    return False, ProofObject(
                        conclusion=f"VIOLATION: Disparate impact {ratio}x between {r1} and {r2}",
                        premises=[],
                        rule="civil_rights_title_vi"
                    )
    return True, ProofObject(
        conclusion="No disparate impact detected",
        premises=[],
        rule="disparate_impact_compliant"
    )


def check_title_i_allocation(school: School) -> Tuple[bool, ProofObject]:
    """Title I eligible schools must receive funding.

    Falsifies if: school.title_i_eligible is True and title_i_funding == 0.
    falsifies_if: school.title_i_eligible is True and title_i_funding == 0.
    """
    if school.title_i_eligible and school.title_i_funding == 0:
        return False, ProofObject(
            conclusion="VIOLATION: Title I eligible but no funding",
            premises=[f"School: {school.school_id}"],
            rule="essa_title_i_funding"
        )
    return True, ProofObject(
        conclusion="Title I funding appropriate",
        premises=[],
        rule="title_i_compliant"
    )


def check_suspension_rate_reasonable(discipline: DisciplineRecord) -> Tuple[bool, ProofObject]:
    """Suspension rate must not exceed 10%.

    Falsifies if: total suspension rate > 0.1.
    falsifies_if: total suspension rate > 0.1.
    """
    total_rate = Fraction(discipline.suspensions_total, sum(discipline.enrollment_by_race.values()))
    if total_rate > Fraction(1, 10):  # > 10%
        return False, ProofObject(
            conclusion=f"VIOLATION: Suspension rate {total_rate} excessive",
            premises=[],
            rule="school_discipline_reform"
        )
    return True, ProofObject(
        conclusion="Suspension rate acceptable",
        premises=[f"Rate: {total_rate}"],
        rule="suspension_compliant"
    )


def check_racial_compliance(discipline: DisciplineRecord) -> Tuple[bool, ProofObject]:
    """All racial groups must have enrollment data.

    Falsifies if: discipline.enrollment_by_race is empty.
    falsifies_if: discipline.enrollment_by_race is empty.
    """
    if not discipline.enrollment_by_race:
        return False, ProofObject(
            conclusion="VIOLATION: No enrollment data by race",
            premises=[],
            rule="civil_rights_data_collection"
        )
    return True, ProofObject(
        conclusion="Racial data collected",
        premises=[],
        rule="data_compliant"
    )


def run_all_invariants() -> dict:
    """Run all D_SCHOOL_EQUITY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    discipline_record = DisciplineRecord(
        school_id=None,
        year=None,
        suspensions_total=None,
        suspensions_by_race=None,
        enrollment_by_race=None,
    )
    school = School(
        school_id=None,
        name=None,
        district=None,
        enrollment_total=None,
        enrollment_by_race=None,
        title_i_eligible=None,
        title_i_funding=Fraction(1),
        per_pupil_spending=Fraction(1),
        state_avg_spending=Fraction(1),
    )

    checks = [
        ("check_disparate_impact", lambda: check_disparate_impact(discipline_record, Fraction(1000))),
        ("check_racial_compliance", lambda: check_racial_compliance(discipline_record)),
        ("check_spending_equity", lambda: check_spending_equity(school)),
        ("check_suspension_rate_reasonable", lambda: check_suspension_rate_reasonable(discipline_record)),
        ("check_title_i_allocation", lambda: check_title_i_allocation(school)),
    ]

    results: dict = {}
    for name, func in checks:
        try:
            result = func()
            if isinstance(result, tuple) and len(result) == 2:
                success, proof = result
                results[name] = "PASS" if success else "FAIL: " + str(proof.conclusion)
            else:
                passed = getattr(result, "passed", True)
                results[name] = "PASS" if passed else "FAIL: " + str(getattr(result, "evidence", result))
        except Exception as exc:  # pragma: no cover - safety net
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_SCHOOL_EQUITY invariants: PASS")
