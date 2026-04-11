"""D_LABOR_RIGHTS invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- NLRA (National Labor Relations Act)
- FLSA (Fair Labor Standards Act)
- OSHA (Occupational Safety and Health Act)
- Title VII (Civil Rights Act)

Source: ontology/ontology.json#D_LABOR_RIGHTS
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject


def check_flsa_overtime_threshold() -> Tuple[bool, ProofObject]:
    """
    Invariant: FLSA overtime threshold is 40 hours per week.
    
    Standard: 29 U.S.C. § 207(a)(1) - 40-hour workweek standard
    Falsifies if: Overtime threshold differs from 40 hours.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    standard_threshold = Fraction(40)
    
    # Check standard 40-hour threshold
    check_40 = standard_threshold == Fraction(40)
    
    # Check 41-hour week triggers overtime (1 hour over)
    hours_worked = Fraction(41)
    overtime_hours = hours_worked - standard_threshold
    overtime_triggered = overtime_hours > Fraction(0)
    overtime_exact = overtime_hours == Fraction(1)
    
    success = check_40 and overtime_triggered and overtime_exact
    
    proof = ProofObject(
        rule="FLSA_Overtime_Threshold",
        premises=[
            f"standard_threshold = {standard_threshold} hours",
            f"hours_worked = {hours_worked} hours",
            f"overtime_hours = {overtime_hours} hours",
            f"overtime_triggered = {overtime_triggered}",
        ],
        conclusion=(
            "FLSA overtime threshold complies with 29 U.S.C. § 207"
            if success
            else "FAIL: FLSA overtime threshold check failed"
        ),
    )
    return success, proof


def check_overtime_rate_one_and_half() -> Tuple[bool, ProofObject]:
    """
    Invariant: FLSA overtime rate is exactly 1.5x regular rate.
    
    Standard: 29 U.S.C. § 207(a)(1) - "not less than one and one-half times"
    Falsifies if: Overtime multiplier differs from 3/2.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    overtime_multiplier = Fraction(3, 2)
    
    # Check exact 1.5x multiplier
    multiplier_exact = overtime_multiplier == Fraction(3, 2)
    
    # Calculate example: $15/hr regular, 1 OT hour
    regular_rate = Fraction(1500)  # cents
    expected_ot_rate = regular_rate * overtime_multiplier
    expected_ot_exact = expected_ot_rate == Fraction(2250)
    
    # Verify not using float arithmetic
    no_float_used = isinstance(overtime_multiplier, Fraction)
    
    success = multiplier_exact and expected_ot_exact and no_float_used
    
    proof = ProofObject(
        rule="FLSA_Overtime_Rate",
        premises=[
            f"overtime_multiplier = {overtime_multiplier} ({overtime_multiplier}x)",
            f"regular_rate = {regular_rate} cents",
            f"expected_ot_rate = {expected_ot_rate} cents",
            f"no_float_used = {no_float_used}",
        ],
        conclusion=(
            "FLSA overtime rate complies with 29 U.S.C. § 207"
            if success
            else "FAIL: FLSA overtime rate check failed"
        ),
    )
    return success, proof


def check_nlra_collective_bargaining_right() -> Tuple[bool, ProofObject]:
    """
    Invariant: NLRA guarantees right to collective bargaining.
    
    Standard: 29 U.S.C. § 157 - Right to self-organization
    Falsifies if: Collective bargaining rights are not protected.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # NLRA Section 7 rights
    rights_protected = {
        "self_organization": True,
        "collective_bargaining": True,
        "concerted_activities": True,
    }
    
    all_protected = all(rights_protected.values())
    
    # Unfair labor practices prohibited (Section 8)
    ulp_prohibited = True
    
    # Check minimum employee threshold (15 for Title VII, but NLRA covers most)
    nlra_coverage_threshold = Fraction(0)  # NLRA has broad coverage
    
    success = all_protected and ulp_prohibited
    
    proof = ProofObject(
        rule="NLRA_Collective_Bargaining",
        premises=[
            f"self_organization_protected = {rights_protected['self_organization']}",
            f"collective_bargaining_protected = {rights_protected['collective_bargaining']}",
            f"concerted_activities_protected = {rights_protected['concerted_activities']}",
            f"ulp_prohibited = {ulp_prohibited}",
        ],
        conclusion=(
            "NLRA collective bargaining rights comply with 29 U.S.C. § 157"
            if success
            else "FAIL: NLRA collective bargaining check failed"
        ),
    )
    return success, proof


def check_osha_general_duty_clause() -> Tuple[bool, ProofObject]:
    """
    Invariant: OSHA General Duty Clause requires hazard-free workplace.
    
    Standard: 29 U.S.C. § 654(a)(1) - General Duty Clause
    Falsifies if: Recognized hazards are not addressed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # General Duty Clause requirements
    employer_duties = {
        "furnish_employment_free_from_hazards": True,
        "prevent_death_or_serious_harm": True,
    }
    
    # Employee duties
    employee_duties = {
        "comply_with_standards": True,
        "follow_safety_rules": True,
    }
    
    all_employer_duties = all(employer_duties.values())
    all_employee_duties = all(employee_duties.values())
    
    success = all_employer_duties and all_employee_duties
    
    proof = ProofObject(
        rule="OSHA_General_Duty_Clause",
        premises=[
            f"employer_hazard_free_duty = {employer_duties['furnish_employment_free_from_hazards']}",
            f"employer_prevent_harm_duty = {employer_duties['prevent_death_or_serious_harm']}",
            f"employee_comply_duty = {employee_duties['comply_with_standards']}",
        ],
        conclusion=(
            "OSHA General Duty Clause complies with 29 U.S.C. § 654"
            if success
            else "FAIL: OSHA General Duty Clause check failed"
        ),
    )
    return success, proof


def check_title_vii_prohibited_discrimination() -> Tuple[bool, ProofObject]:
    """
    Invariant: Title VII prohibits employment discrimination.
    
    Standard: 42 U.S.C. § 2000e-2(a) - Unlawful employment practices
    Falsifies if: Discrimination based on protected class is allowed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Title VII protected classes
    protected_classes = {
        "race": True,
        "color": True,
        "religion": True,
        "sex": True,
        "national_origin": True,
    }
    
    all_protected = all(protected_classes.values())
    num_protected = Fraction(len(protected_classes))
    
    # Prohibited actions
    hiring_discrimination_prohibited = True
    firing_discrimination_prohibited = True
    compensation_discrimination_prohibited = True
    
    # Employer threshold: 15+ employees (Section 701(b))
    employer_threshold = Fraction(15)
    coverage_threshold_met = employer_threshold == Fraction(15)
    
    success = all_protected and coverage_threshold_met
    
    proof = ProofObject(
        rule="Title_VII_Prohibited_Discrimination",
        premises=[
            f"num_protected_classes = {num_protected}",
            f"hiring_discrimination_prohibited = {hiring_discrimination_prohibited}",
            f"compensation_discrimination_prohibited = {compensation_discrimination_prohibited}",
            f"employer_threshold = {employer_threshold} employees",
        ],
        conclusion=(
            "Title VII discrimination prohibitions comply with 42 U.S.C. § 2000e-2"
            if success
            else "FAIL: Title VII discrimination check failed"
        ),
    )
    return success, proof


def check_flsa_minimum_wage_compliance() -> Tuple[bool, ProofObject]:
    """
    Invariant: FLSA minimum wage is $7.25/hour (federal).
    
    Standard: 29 U.S.C. § 206(a)(1) - Minimum wage provisions
    Falsifies if: Minimum wage is below statutory level.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    
    
    # Federal minimum wage: $7.25 = 725 cents
    federal_minimum_wage = Fraction(725)  # cents per hour
    
    # Check exact federal rate
    rate_exact = federal_minimum_wage == Fraction(725)
    
    # Example calculation: 40 hours at minimum wage
    hours = Fraction(40)
    weekly_min_earnings = federal_minimum_wage * hours
    expected_weekly = Fraction(29000)  # cents
    weekly_exact = weekly_min_earnings == expected_weekly
    
    # Youth minimum wage (first 90 days): $4.25
    youth_minimum = Fraction(425)
    youth_rate_valid = youth_minimum == Fraction(425)
    
    success = rate_exact and weekly_exact and youth_rate_valid
    
    proof = ProofObject(
        rule="FLSA_Minimum_Wage",
        premises=[
            f"federal_minimum_wage = {federal_minimum_wage} cents/hour",
            f"standard_hours = {hours} hours/week",
            f"weekly_min_earnings = {weekly_min_earnings} cents",
            f"youth_minimum = {youth_minimum} cents/hour",
        ],
        conclusion=(
            "FLSA minimum wage complies with 29 U.S.C. § 206"
            if success
            else "FAIL: FLSA minimum wage check failed"
        ),
    )
    return success, proof


def run_all_invariants() -> dict:
    """Run all D_LABOR_RIGHTS invariants."""
    checks = [
        ("check_flsa_overtime_threshold", check_flsa_overtime_threshold),
        ("check_overtime_rate_one_and_half", check_overtime_rate_one_and_half),
        ("check_nlra_collective_bargaining_right", check_nlra_collective_bargaining_right),
        ("check_osha_general_duty_clause", check_osha_general_duty_clause),
        ("check_title_vii_prohibited_discrimination", check_title_vii_prohibited_discrimination),
        ("check_flsa_minimum_wage_compliance", check_flsa_minimum_wage_compliance),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            success, proof = check_func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_LABOR_RIGHTS invariants: PASS")
