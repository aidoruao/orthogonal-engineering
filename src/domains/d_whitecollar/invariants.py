"""D_WHITECOLLAR Invariants — White Collar Crime, FCPA, Sarbanes-Oxley

Verifies SEC compliance, FCPA anti-bribery, antitrust, compliance programs,
penalty proportionality, self-reporting incentives.

Standards: 15 U.S.C. § 78j (Securities Exchange Act), 15 U.S.C. § 78dd-1 (FCPA), 18 U.S.C. § 3571
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import WhiteCollarCase, ComplianceProgram, ViolationType, InvestigationStatus, min_cooperation_threshold, max_penalty_multiplier


def check_penalty_proportionality(case: WhiteCollarCase) -> Tuple[bool, ProofObject]:
    """
    Penalties should be proportional to offense (not excessive).
    
    US Sentencing Guidelines:
    - Penalties based on gain/loss amounts
    - Multipliers applied
    - Cooperation can reduce
    
    Falsifies if: penalty > 3x gain (unusual)
    falsifies_if: penalty > 3x gain (unusual)
    """
    max_multiplier = max_penalty_multiplier()
    ratio = case.penalty_to_gain_ratio()
    
    if case.alleged_gain > 0 and ratio > max_multiplier:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} penalty ratio {ratio} exceeds maximum {max_multiplier}",
            premises=[
                f"Penalty: {case.get_total_penalty()}",
                f"Gain: {case.alleged_gain}",
                f"Ratio: {ratio}",
                "USSG — Penalty proportionality"
            ],
            rule="penalty_proportionality"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} penalty proportionality acceptable",
        premises=[f"Ratio: {ratio}"],
        rule="penalty_proportionality"
    )


def check_compliance_program_effectiveness(program: ComplianceProgram) -> Tuple[bool, ProofObject]:
    """
    DOJ evaluates compliance program effectiveness.
    
    DOJ Compliance Program Evaluation:
    - Risk-based approach
    - Training coverage
    - Confidential reporting
    - Independent investigations
    
    Falsifies if: <90% training coverage
    falsifies_if: <90% training coverage
    """
    min_coverage = Fraction(9, 10)
    coverage = program.get_training_coverage()
    
    if coverage < min_coverage:
        return False, ProofObject(
            conclusion=f"VIOLATION: Compliance program {program.program_id} training coverage {coverage} below {min_coverage}",
            premises=[
                f"Trained: {program.employees_trained_annual}",
                f"Total: {program.total_employees}",
                f"Coverage: {coverage}",
                "DOJ Compliance Program Evaluation — Training"
            ],
            rule="compliance_program_effectiveness"
        )
    
    if not program.confidential_reporting_available:
        return False, ProofObject(
            conclusion=f"VIOLATION: Compliance program {program.program_id} lacks confidential reporting",
            premises=[
                f"Confidential reporting: {program.confidential_reporting_available}",
                "DOJ — Confidential reporting required"
            ],
            rule="compliance_program_effectiveness"
        )
    
    return True, ProofObject(
        conclusion=f"Compliance program {program.program_id} effectiveness verified",
        premises=[f"Training: {coverage}"],
        rule="compliance_program_effectiveness"
    )


def check_self_reporting_incentive(case: WhiteCollarCase) -> Tuple[bool, ProofObject]:
    """
    Self-reporting should receive penalty reduction.
    
    DOJ/SEC policies:
    - Self-reporting is mitigating factor
    - Cooperation credit
    - Remediation considered
    
    Falsifies if: self-reported but no cooperation credit
    falsifies_if: self-reported but no cooperation credit
    """
    if case.self_reported and case.cooperation_level < min_cooperation_threshold():
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} self-reported but cooperation {case.cooperation_level} below threshold",
            premises=[
                f"Self-reported: {case.self_reported}",
                f"Cooperation: {case.cooperation_level}",
                "DOJ/SEC — Self-reporting incentives"
            ],
            rule="self_reporting_incentive"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} self-reporting/cooperation appropriate",
        premises=[
            f"Self-reported: {case.self_reported}",
            f"Cooperation: {case.cooperation_level}"
        ],
        rule="self_reporting_incentive"
    )


def check_monitor_independence(case: WhiteCollarCase) -> Tuple[bool, ProofObject]:
    """
    Compliance monitors should be independent.
    
    Monitorship requirements:
    - Independent from company
    - Defined scope and duration
    - Regular reporting
    
    Falsifies if: monitor duration excessive without cause
    falsifies_if: monitor duration excessive without cause
    """
    if not case.compliance_monitor_appointed:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} no compliance monitor appointed",
            premises=["Monitor: not appointed"],
            rule="monitor_independence"
        )
    
    max_duration = Fraction(3)  # 3 years typical
    
    if case.monitor_duration_years > max_duration:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} monitor duration {case.monitor_duration_years} years exceeds typical {max_duration}",
            premises=[
                f"Duration: {case.monitor_duration_years} years",
                f"Typical max: {max_duration} years",
                "Monitorship standards — Duration"
            ],
            rule="monitor_independence"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} monitor duration acceptable",
        premises=[f"Duration: {case.monitor_duration_years} years"],
        rule="monitor_independence"
    )


def check_fcpa_anti_bribery(case: WhiteCollarCase) -> Tuple[bool, ProofObject]:
    """
    FCPA prohibits bribery of foreign officials.
    
    15 U.S.C. § 78dd-1:
    - Prohibits corrupt payments to foreign officials
    - Accounting transparency required
    - Facilitating payments exception (limited)
    
    Falsifies if: bribery confirmed without remediation
    falsifies_if: bribery confirmed without remediation
    """
    if case.violation_type != ViolationType.BRIBERY:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} not FCPA bribery case",
            premises=[f"Type: {case.violation_type.name}"],
            rule="fcpa_exemption"
        )
    
    if case.investigation_status == InvestigationStatus.CONVICTED and not case.remediation_completed:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} FCPA violation without remediation",
            premises=[
                f"Status: {case.investigation_status.name}",
                f"Remediation: {case.remediation_completed}",
                "FCPA — Remediation required"
            ],
            rule="fcpa_anti_bribery"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} FCPA compliance status",
        premises=[f"Status: {case.investigation_status.name}", f"Remediation: {case.remediation_completed}"],
        rule="fcpa_anti_bribery"
    )


def run_all_invariants() -> dict:
    """Run all D_WHITECOLLAR invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    compliance_program = ComplianceProgram(
        program_id=None,
        company_id=None,
        risk_assessment_current=None,
        policies_procedures_documented=None,
        training_provided=None,
        confidential_reporting_available=None,
        investigations_independent=None,
        continuous_improvement=None,
        employees_trained_annual=None,
        total_employees=None,
        hotline_reports_annual=None,
        investigations_completed=None,
    )
    white_collar_case = WhiteCollarCase(
        case_id=None,
        defendant_id=None,
        violation_type=ViolationType.SECURITIES_FRAUD,
        alleged_gain=Fraction(1),
        victim_losses=Fraction(1),
        disgorgement_ordered=Fraction(1),
        fines_ordered=Fraction(1),
        investigation_status=InvestigationStatus.PENDING,
        compliance_monitor_appointed=None,
        monitor_duration_years=Fraction(1),
        self_reported=None,
        cooperation_level=Fraction(1, 2),
        remediation_completed=None,
    )

    checks = [
        ("check_compliance_program_effectiveness", lambda: check_compliance_program_effectiveness(compliance_program)),
        ("check_fcpa_anti_bribery", lambda: check_fcpa_anti_bribery(white_collar_case)),
        ("check_monitor_independence", lambda: check_monitor_independence(white_collar_case)),
        ("check_penalty_proportionality", lambda: check_penalty_proportionality(white_collar_case)),
        ("check_self_reporting_incentive", lambda: check_self_reporting_incentive(white_collar_case)),
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
    print("All D_WHITECOLLAR invariants: PASS")
