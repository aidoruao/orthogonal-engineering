#!/usr/bin/env python3
"""Employment Law Invariants — FLSA, Title VII."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import WageCalculator, DisparateImpactAnalyzer


def check_minimum_wage(calculator: WageCalculator) -> Tuple[bool, ProofObject]:
    """FLSA: Hourly rate must meet federal minimum wage."""
    if not calculator.meets_minimum_wage():
        return False, ProofObject(
            conclusion=f"VIOLATION: Rate {calculator.employee.hourly_rate} < minimum {calculator.employee.FEDERAL_MINIMUM_WAGE}",
            premises=[],
            rule="flsa_minimum_wage"
        )
    
    return True, ProofObject(
        conclusion=f"Minimum wage satisfied ({calculator.employee.hourly_rate} >= {calculator.employee.FEDERAL_MINIMUM_WAGE})",
        premises=[],
        rule="flsa_minimum_wage"
    )


def check_overtime_calculation(employee) -> Tuple[bool, ProofObject]:
    """FLSA: Overtime must be 1.5x regular rate."""
    if employee.hours_worked <= employee.OVERTIME_THRESHOLD:
        return True, ProofObject(
            conclusion="No overtime hours",
            premises=[],
            rule="flsa_overtime"
        )
    
    expected_overtime = employee.overtime_hours() * employee.hourly_rate * employee.OVERTIME_MULTIPLIER
    actual_overtime = employee.overtime_pay()
    
    if actual_overtime < expected_overtime:
        return False, ProofObject(
            conclusion="VIOLATION: Overtime pay insufficient",
            premises=[],
            rule="flsa_overtime"
        )
    
    return True, ProofObject(
        conclusion=f"Overtime pay correct ({employee.overtime_hours()} hours)",
        premises=[],
        rule="flsa_overtime"
    )


def check_disparate_impact(analyzer: DisparateImpactAnalyzer) -> Tuple[bool, ProofObject]:
    """Title VII: 4/5ths rule for disparate impact detection."""
    violations = analyzer.four_fifths_rule()
    
    if violations:
        return False, ProofObject(
            conclusion=f"VIOLATION: Disparate impact detected ({len(violations)} groups)",
            premises=[v[0] for v in violations],
            rule="title_vii_disparate_impact"
        )
    
    return True, ProofObject(
        conclusion="No disparate impact detected",
        premises=[],
        rule="title_vii_disparate_impact"
    )
