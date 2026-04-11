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
    ratio = school.spending_equity_ratio()
    if ratio < Fraction(8, 10):
        return False, ProofObject(
            conclusion=f"VIOLATION: Spending {ratio}x below state average",
            premises=[f"School: {school.school_id}"],
            rule":"essa_equitable_spending"
        )
    return True, ProofObject(
        conclusion="Spending equitable",
        premises=[f"Ratio: {ratio}"],
        rule="spending_compliant"
    )


def check_disparate_impact(discipline: DisciplineRecord, threshold: Fraction) -> Tuple[bool, ProofObject]:
    races = list(discipline.enrollment_by_race.keys())
    for r1 in races:
        for r2 in races:
            if r1 != r2:
                ratio = discipline.disparate_impact_ratio(r1, r2)
                if ratio > threshold:
                    return False, ProofObject(
                        conclusion=f"VIOLATION: Disparate impact {ratio}x between {r1} and {r2}",
                        premises=[],
                        rule":"civil_rights_title_vi"
                    )
    return True, ProofObject(
        conclusion="No disparate impact detected",
        premises=[],
        rule="disparate_impact_compliant"
    )


def check_title_i_allocation(school: School) -> Tuple[bool, ProofObject]:
    if school.title_i_eligible and school.title_i_funding == 0:
        return False, ProofObject(
            conclusion="VIOLATION: Title I eligible but no funding",
            premises=[f"School: {school.school_id}"],
            rule":"essa_title_i_funding"
        )
    return True, ProofObject(
        conclusion="Title I funding appropriate",
        premises=[],
        rule="title_i_compliant"
    )


def check_suspension_rate_reasonable(discipline: DisciplineRecord) -> Tuple[bool, ProofObject]:
    total_rate = Fraction(discipline.suspensions_total, sum(discipline.enrollment_by_race.values()))
    if total_rate > Fraction(1, 10):  # > 10%
        return False, ProofObject(
            conclusion=f"VIOLATION: Suspension rate {total_rate} excessive",
            premises=[],
            rule":"school_discipline_reform"
        )
    return True, ProofObject(
        conclusion="Suspension rate acceptable",
        premises=[f"Rate: {total_rate}"],
        rule="suspension_compliant"
    )


def check_racial_compliance(discipline: DisciplineRecord) -> Tuple[bool, ProofObject]:
    """All racial groups must have enrollment data.
    
    falsifies_if: condition_evaluated_to_false"""
    if not discipline.enrollment_by_race:
        return False, ProofObject(
            conclusion="VIOLATION: No enrollment data by race",
            premises=[],
            rule":"civil_rights_data_collection"
        )
    return True, ProofObject(
        conclusion="Racial data collected",
        premises=[],
        rule="data_compliant"
    )
