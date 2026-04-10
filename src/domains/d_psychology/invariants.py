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
            rule":"p_value_bounds"
        )
    return True, ProofObject(
        conclusion="P-value valid",
        premises=[f"P: {study.p_value}"],
        rule="p_value_valid"
    )


def check_vulnerable_protection(participant: Participant) -> Tuple[bool, ProofObject]:
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
