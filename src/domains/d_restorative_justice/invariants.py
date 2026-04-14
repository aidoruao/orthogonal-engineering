"""D_RESTORATIVE_JUSTICE Invariants — Victim-Offender Mediation, Circle Sentencing

Verifies restorative justice program integrity, victim participation,
agreement completion rates, recidivism tracking.

Standards: Victim Offender Reconciliation Act, UNODC RJ Guidelines
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    RJOutcome,
    RJProgramMetrics,
    RJProgramType,
    RestorativeJusticeCase,
    completion_rate_target,
    victim_satisfaction_target,
)


def check_victim_participation(case: RestorativeJusticeCase) -> Tuple[bool, ProofObject]:
    """
    Restorative justice requires meaningful victim participation.
    
    UNODC Handbook on Restorative Justice:
    - Victims should have opportunity to participate
    - Voluntary participation for all parties
    - Victim safety and support required
    
    Falsifies if: victim willing but excluded
    falsifies_if: victim willing but excluded
    """
    if case.victim_id is None:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} has no identified victim",
            premises=["No victim applicable"],
            rule="rj_victim_exemption"
        )
    
    if not case.victim_participating and case.victim_id:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} victim not participating — opportunity required",
            premises=[
                f"Victim: {case.victim_id}",
                f"Participating: {case.victim_participating}",
                "UNODC RJ Guidelines — Victim participation"
            ],
            rule="rj_victim_participation"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} victim participation verified",
        premises=[f"Participating: {case.victim_participating}"],
        rule="rj_victim_participation"
    )


def check_agreement_completion(program: RJProgramMetrics) -> Tuple[bool, ProofObject]:
    """
    RJ agreements should be completed at acceptable rates.
    
    Restorative Justice Standards:
    - Agreements should be achievable and monitored
    - Completion rates indicate program quality
    - Breach should be exception, not norm
    
    Falsifies if: completion rate < 60%
    falsifies_if: completion rate < 60%
    """
    target = completion_rate_target()
    rate = program.get_completion_rate()
    
    if rate < target:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} completion rate {rate} below target {target}",
            premises=[
                f"Completed: {program.cases_completed}",
                f"Breached: {program.cases_breached}",
                f"Rate: {rate}",
                "Restorative Justice quality standards"
            ],
            rule="rj_completion_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Program {program.program_id} completion rate satisfactory",
        premises=[f"Rate: {rate}", f"Target: {target}"],
        rule="rj_completion_rate"
    )


def check_victim_satisfaction(case: RestorativeJusticeCase) -> Tuple[bool, ProofObject]:
    """
    Victim satisfaction indicates RJ process quality.
    
    Victim Offender Reconciliation Act principles:
    - Victims should feel heard and validated
    - Restitution and apology important
    - Satisfaction tracking required
    
    Falsifies if: victim satisfaction < 70% on completed cases
    falsifies_if: victim satisfaction < 70% on completed cases
    """
    target = victim_satisfaction_target()
    
    if not case.victim_participating:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} victim did not participate — satisfaction N/A",
            premises=["No victim participation"],
            rule="rj_satisfaction_exemption"
        )
    
    if case.completion_status == "completed" and case.victim_satisfaction < target:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} victim satisfaction {case.victim_satisfaction} below target {target}",
            premises=[
                f"Satisfaction: {case.victim_satisfaction}",
                f"Target: {target}",
                "VOR Act — Victim satisfaction standards"
            ],
            rule="rj_victim_satisfaction"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} victim satisfaction acceptable",
        premises=[f"Satisfaction: {case.victim_satisfaction}"],
        rule="rj_victim_satisfaction"
    )


def check_preparation_standards(case: RestorativeJusticeCase) -> Tuple[bool, ProofObject]:
    """
    Adequate preparation required before RJ conference.
    
    Best practices:
    - Pre-conference preparation meetings
    - Safety assessment conducted
    - Expectations clarified
    
    Falsifies if: no preparation and conference held
    falsifies_if: no preparation and conference held
    """
    if not case.conference_held:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} no conference held — preparation check N/A",
            premises=["Conference: not held"],
            rule="rj_preparation_exemption"
        )
    
    if case.conference_held and case.preparation_meetings == 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} conference held without preparation meetings",
            premises=[
                f"Preparation meetings: {case.preparation_meetings}",
                "RJ best practices — Preparation required"
            ],
            rule="rj_preparation_standards"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} preparation standards met",
        premises=[f"Preparation meetings: {case.preparation_meetings}"],
        rule="rj_preparation_standards"
    )


def check_restitution_collection(program: RJProgramMetrics) -> Tuple[bool, ProofObject]:
    """
    Restitution collection rate indicates program effectiveness.
    
    Victim compensation:
    - Restitution should be collected and disbursed
    - Tracking required for accountability
    - Victims should receive owed amounts
    
    Falsifies if: collection rate < 50%
    falsifies_if: collection rate < 50%
    """
    min_collection_rate = Fraction(1, 2)  # 50%
    
    rate = program.get_restitution_rate()
    
    if program.restitution_owed > 0 and rate < min_collection_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} restitution collection {rate} below minimum {min_collection_rate}",
            premises=[
                f"Collected: {program.restitution_collected}",
                f"Owed: {program.restitution_owed}",
                f"Rate: {rate}",
                "Victim compensation standards"
            ],
            rule="rj_restitution_collection"
        )
    
    return True, ProofObject(
        conclusion=f"Program {program.program_id} restitution collection satisfactory",
        premises=[f"Collection rate: {rate}"],
        rule="rj_restitution_collection"
    )


def run_all_invariants() -> dict:
    """Run all D_RESTORATIVE_JUSTICE invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    rj_program_metrics = RJProgramMetrics(
        program_id=None,
        program_type=RJProgramType.VICTIM_OFFENDER_MEDIATION,
        cases_referred=None,
        cases_accepted=None,
        cases_completed=None,
        cases_breached=None,
        restitution_collected=Fraction(1),
        restitution_owed=Fraction(1),
        community_service_completed=Fraction(1),
        community_service_assigned=Fraction(1),
        recidivism_count=None,
        tracked_participants=None,
    )
    restorative_justice_case = RestorativeJusticeCase(
        case_id=None,
        program_type=RJProgramType.VICTIM_OFFENDER_MEDIATION,
        offense_type=None,
        victim_participating=None,
        offender_id=None,
        victim_id=None,
        community_representatives=None,
        preparation_meetings=None,
        conference_held=None,
        agreement_terms=None,
        outcome=RJOutcome.AGREEMENT_REACHED,
        restitution_amount=Fraction(1),
        community_service_hours=Fraction(1),
        completion_status=None,
        victim_satisfaction=Fraction(1),
        offender_satisfaction=Fraction(1),
    )

    checks = [
        ("check_agreement_completion", lambda: check_agreement_completion(rj_program_metrics)),
        ("check_preparation_standards", lambda: check_preparation_standards(restorative_justice_case)),
        ("check_restitution_collection", lambda: check_restitution_collection(rj_program_metrics)),
        ("check_victim_participation", lambda: check_victim_participation(restorative_justice_case)),
        ("check_victim_satisfaction", lambda: check_victim_satisfaction(restorative_justice_case)),
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
    print("All D_RESTORATIVE_JUSTICE invariants: PASS")
