#!/usr/bin/env python3
"""Psychology Domain Invariants — Research ethics, validity, consent.

Standards:
- APA Ethics Code
- Belmont Report
- IRB regulations (45 CFR 46)

Falsifies if:
- No IRB approval
- No informed consent
- P-value misreported
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import ResearchStudy, Participant


def check_irb_approval(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """IRB approval must be obtained before research.

    Falsifies if: study.irb_approved is False.
    falsifies_if: study.irb_approved is False.
    """
    if not study.irb_approved:
        return False, ProofObject(
            conclusion="VIOLATION: Research without IRB approval",
            premises=[f"Study: {study.study_id}"],
            rule="45_cfr_46_irb_required"
        )
    return True, ProofObject(
        conclusion="IRB approved",
        premises=[f"Protocol: {study.irb_protocol_number}"],
        rule="irb_compliant"
    )


def check_informed_consent(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """Participants must provide informed consent.

    Falsifies if: study.informed_consent_obtained is False.
    falsifies_if: study.informed_consent_obtained is False.
    """
    if not study.informed_consent_obtained:
        return False, ProofObject(
            conclusion="VIOLATION: No informed consent",
            premises=[f"Study: {study.study_id}"],
            rule="belmont_informed_consent"
        )
    return True, ProofObject(
        conclusion="Informed consent obtained",
        premises=[],
        rule="consent_compliant"
    )


def check_p_value_valid(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """P-value must be within [0, 1] when reported.

    Falsifies if: study.p_value is outside [0, 1].
    falsifies_if: study.p_value is outside [0, 1].
    """
    if study.p_value is None:
        return True, ProofObject(
            conclusion="No p-value reported",
            premises=[],
            rule="p_value_not_applicable"
        )
    if study.p_value < Fraction(0) or study.p_value > Fraction(1):
        return False, ProofObject(
            conclusion="VIOLATION: Invalid p-value",
            premises=[f"P-value: {study.p_value}"],
            rule="p_value_bounds"
        )
    return True, ProofObject(
        conclusion="P-value valid",
        premises=[f"P: {study.p_value}"],
        rule="p_value_valid"
    )


def check_vulnerable_protection(participant: Participant) -> Tuple[bool, ProofObject]:
    """Flag additional safeguards for vulnerable participants.

    Falsifies if: not applicable (function records safeguard need and returns True).
    falsifies_if: not applicable (function records safeguard need and returns True).
    """
    if participant.vulnerable_population and not participant.capacity_to_consent:
        return True, ProofObject(
            conclusion="Vulnerable participant requires additional safeguards",
            premises=[f"Participant: {participant.participant_id}"],
            rule="vulnerable_participant_noted"
        )
    return True, ProofObject(
        conclusion="Participant capacity appropriate",
        premises=[],
        rule="capacity_compliant"
    )


def check_completion_rate(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """Completion rate must be at least 70%.

    Falsifies if: study.completion_rate() < 0.7.
    falsifies_if: study.completion_rate() < 0.7.
    """
    rate = study.completion_rate()
    if rate < Fraction(7, 10):
        return False, ProofObject(
            conclusion="WARNING: High attrition rate",
            premises=[f"Completion: {rate}"],
            rule="attrition_threshold"
        )
    return True, ProofObject(
        conclusion="Completion rate acceptable",
        premises=[f"Rate: {rate}"],
        rule="completion_acceptable"
    )


def run_all_invariants() -> dict:
    """Run all D_PSYCHOLOGY invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    research_study = ResearchStudy(
        study_id=None,
        title=None,
        principal_investigator=None,
        irb_approved=None,
        irb_protocol_number=None,
        informed_consent_obtained=None,
        participants_enrolled=None,
        participants_completed=None,
        hypothesis_supported=None,
        effect_size=None,
        p_value=None,
    )
    participant = Participant(
        participant_id=None,
        study_id=None,
        consent_date=None,
        withdrawal_date=None,
        vulnerable_population=None,
        capacity_to_consent=None,
    )

    checks = [
        ("check_completion_rate", lambda: check_completion_rate(research_study)),
        ("check_informed_consent", lambda: check_informed_consent(research_study)),
        ("check_irb_approval", lambda: check_irb_approval(research_study)),
        ("check_p_value_valid", lambda: check_p_value_valid(research_study)),
        ("check_vulnerable_protection", lambda: check_vulnerable_protection(participant)),
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
    print("All D_PSYCHOLOGY invariants: PASS")
