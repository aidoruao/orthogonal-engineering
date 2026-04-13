"""D_PUBLIC_HEALTH Invariants — Disease Control, Vaccination, Epidemiology

Verifies herd immunity thresholds, case fatality rates, 
public health program coverage, outbreak response.

Standards: Public Health Service Act, CDC guidelines, WHO IHR
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    DiseaseOutbreak,
    DiseaseSeverity,
    InterventionType,
    PublicHealthProgram,
    herd_immunity_threshold,
    max_acceptable_cfr,
)


def check_herd_immunity(outbreak: DiseaseOutbreak) -> Tuple[bool, ProofObject]:
    """
    Vaccination coverage should reach herd immunity threshold.
    
    CDC/WHO guidelines:
    - Measles: 95% coverage required
    - Polio: 80% coverage
    - Varies by disease transmissibility
    
    Falsifies if: coverage < 95% for high-transmissibility diseases
    falsifies_if: coverage < 95% for high-transmissibility diseases
    """
    threshold = herd_immunity_threshold()
    coverage = outbreak.get_vaccination_coverage()
    
    if outbreak.disease_name.lower() in ("measles", "pertussis") and coverage < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: Outbreak {outbreak.outbreak_id} {outbreak.disease_name} vaccination {coverage} below herd immunity {threshold}",
            premises=[
                f"Vaccinated: {outbreak.population_vaccinated}",
                f"At risk: {outbreak.population_at_risk}",
                f"Coverage: {coverage}",
                "CDC/WHO — Herd immunity thresholds"
            ],
            rule="herd_immunity"
        )
    
    return True, ProofObject(
        conclusion=f"Outbreak {outbreak.outbreak_id} vaccination coverage acceptable",
        premises=[f"Coverage: {coverage}"],
        rule="herd_immunity"
    )


def check_case_fatality_rate(outbreak: DiseaseOutbreak) -> Tuple[bool, ProofObject]:
    """
    Case fatality rate indicates disease severity and care quality.
    
    Epidemiological standards:
    - CFR monitored for severity trends
    - High CFR triggers intervention
    - Comparative analysis across outbreaks
    
    Falsifies if: CFR > 10% without identified cause
    falsifies_if: CFR > 10% without identified cause
    """
    max_cfr = max_acceptable_cfr()
    cfr = outbreak.get_case_fatality_rate()
    
    total_cases = outbreak.cases_confirmed + outbreak.cases_probable
    if total_cases > 10 and cfr > max_cfr:
        return False, ProofObject(
            conclusion=f"VIOLATION: Outbreak {outbreak.outbreak_id} CFR {cfr} exceeds {max_cfr}",
            premises=[
                f"Deaths: {outbreak.deaths}",
                f"Cases: {total_cases}",
                f"CFR: {cfr}",
                "Public health — Case fatality monitoring"
            ],
            rule="case_fatality_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Outbreak {outbreak.outbreak_id} CFR acceptable",
        premises=[f"CFR: {cfr}"],
        rule="case_fatality_rate"
    )


def check_public_health_coverage(program: PublicHealthProgram) -> Tuple[bool, ProofObject]:
    """
    Public health programs should meet coverage targets.
    
    Program effectiveness:
    - Coverage indicates reach
    - Target achievement required
    - Equity considerations
    
    Falsifies if: coverage < 80% of target
    falsifies_if: coverage < 80% of target
    """
    min_coverage = Fraction(8, 10)  # 80%
    rate = program.get_coverage_rate()
    
    if rate < min_coverage:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} coverage {rate} below {min_coverage}",
            premises=[
                f"Reached: {program.people_reached}",
                f"Target: {program.target_population}",
                f"Rate: {rate}",
                "Public health program — Coverage standards"
            ],
            rule="public_health_coverage"
        )
    
    return True, ProofObject(
        conclusion=f"Program {program.program_id} coverage acceptable",
        premises=[f"Rate: {rate}"],
        rule="public_health_coverage"
    )


def check_r_naught_containment(outbreak: DiseaseOutbreak) -> Tuple[bool, ProofObject]:
    """
    R0 (reproduction number) indicates outbreak controllability.
    
    Epidemiological threshold:
    - R0 < 1: outbreak declining
    - R0 > 1: outbreak growing
    - R0 > 3: requires aggressive intervention
    
    Falsifies if: R0 > 3 without intervention
    falsifies_if: R0 > 3 without intervention
    """
    critical_r0 = Fraction(3)
    
    if outbreak.r_naught_estimate > critical_r0 and len(outbreak.intervention_deployed) == 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: Outbreak {outbreak.outbreak_id} R0 {outbreak.r_naught_estimate} > {critical_r0} without intervention",
            premises=[
                f"R0: {outbreak.r_naught_estimate}",
                f"Interventions: {len(outbreak.intervention_deployed)}",
                "Epidemiology — R0 containment required"
            ],
            rule="r_naught_containment"
        )
    
    return True, ProofObject(
        conclusion=f"Outbreak {outbreak.outbreak_id} R0 status acceptable",
        premises=[f"R0: {outbreak.r_naught_estimate}", f"Interventions: {len(outbreak.intervention_deployed)}"],
        rule="r_naught_containment"
    )


def check_program_budget_utilization(program: PublicHealthProgram) -> Tuple[bool, ProofObject]:
    """
    Public health funds should be utilized appropriately.
    
    Fiscal management:
    - Under-utilization indicates implementation issues
    - Over-utilization indicates budget problems
    - Target: 80-100% utilization
    
    Falsifies if: utilization < 50% or > 110%
    falsifies_if: utilization < 50% or > 110%
    """
    utilization = program.get_budget_utilization()
    min_util = Fraction(1, 2)  # 50%
    max_util = Fraction(11, 10)  # 110%
    
    if utilization < min_util:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} budget utilization {utilization} below {min_util}",
            premises=[
                f"Spent: {program.budget_spent}",
                f"Allocated: {program.budget_allocated}",
                f"Utilization: {utilization}",
                "Public health fiscal management"
            ],
            rule="budget_utilization"
        )
    
    if utilization > max_util:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} budget over-utilization {utilization}",
            premises=[
                f"Spent: {program.budget_spent}",
                f"Allocated: {program.budget_allocated}",
                f"Utilization: {utilization}",
                "Public health fiscal management"
            ],
            rule="budget_utilization"
        )
    
    return True, ProofObject(
        conclusion=f"Program {program.program_id} budget utilization appropriate",
        premises=[f"Utilization: {utilization}"],
        rule="budget_utilization"
    )


def run_all_invariants() -> dict:
    """Run all D_PUBLIC_HEALTH invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    disease_outbreak = DiseaseOutbreak(
        outbreak_id=None,
        disease_name=None,
        severity=DiseaseSeverity.MILD,
        cases_confirmed=None,
        cases_probable=None,
        deaths=None,
        recoveries=None,
        population_at_risk=Fraction(1),
        population_vaccinated=Fraction(1),
        r_naught_estimate=Fraction(1),
        intervention_deployed=None,
    )
    public_health_program = PublicHealthProgram(
        program_id=None,
        intervention_type=InterventionType.VACCINATION,
        target_population=Fraction(1),
        people_reached=Fraction(1),
        interventions_delivered=None,
        coverage_target=Fraction(100),
        effectiveness_estimate=Fraction(1),
        budget_allocated=Fraction(1000),
        budget_spent=Fraction(1000),
    )

    checks = [
        ("check_case_fatality_rate", lambda: check_case_fatality_rate(disease_outbreak)),
        ("check_herd_immunity", lambda: check_herd_immunity(disease_outbreak)),
        ("check_program_budget_utilization", lambda: check_program_budget_utilization(public_health_program)),
        ("check_public_health_coverage", lambda: check_public_health_coverage(public_health_program)),
        ("check_r_naught_containment", lambda: check_r_naught_containment(disease_outbreak)),
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
    print("All D_PUBLIC_HEALTH invariants: PASS")
