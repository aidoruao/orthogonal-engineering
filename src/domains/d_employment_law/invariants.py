#!/usr/bin/env python3
"""Employment Law Invariants — FLSA, Title VII."""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    DisparateImpactAnalyzer,
    Employee,
    WageCalculator,
    WorkforceDemographics,
    PayType,
)


def check_minimum_wage(calculator: WageCalculator) -> Tuple[bool, ProofObject]:
    """FLSA: Hourly rate must meet federal minimum wage.

    Falsifies if: calculator.meets_minimum_wage() is False.
    falsifies_if: calculator.meets_minimum_wage() is False.
    """
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
    """FLSA: Overtime must be 1.5x regular rate.

    Falsifies if: actual overtime pay < expected 1.5x rate when overtime hours exist.
    falsifies_if: actual overtime pay < expected 1.5x rate when overtime hours exist.
    """
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
    """Title VII: 4/5ths rule for disparate impact detection.

    Falsifies if: analyzer.four_fifths_rule() reports any violating groups.
    falsifies_if: analyzer.four_fifths_rule() reports any violating groups.
    """
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


def run_all_invariants() -> dict:
    """Run all D_EMPLOYMENT_LAW invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    disparate_impact_analyzer = DisparateImpactAnalyzer(
        groups=[WorkforceDemographics(
        group_id="EMPLOYME-001",
        total_employees=1,
        total_applicants=1,
        selected_count=1,
    )],
    )
    wage_calculator = WageCalculator(
        employee=Employee(
        employee_id="EMPLOYME-001",
        pay_type=PayType.HOURLY,
    ),
    )

    checks = [
        ("check_disparate_impact", lambda: check_disparate_impact(disparate_impact_analyzer)),
        ("check_minimum_wage", lambda: check_minimum_wage(wage_calculator)),
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
    print("All D_EMPLOYMENT_LAW invariants: PASS")
