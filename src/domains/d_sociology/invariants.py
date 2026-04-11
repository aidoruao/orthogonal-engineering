"""D_SOCIOLOGY Invariants — Research Ethics, IRB Compliance, Survey Quality

Verifies Belmont Report principles, IRB approval, informed consent,
survey response rates, data protection.

Standards: 45 CFR 46 (Common Rule), Belmont Report (1979), AAPOR Standards
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import ResearchStudy, SurveyInstrument, ResearchType, IRBStatus, min_survey_response_rate, min_reliability_alpha


def check_irb_approval(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """
    Human subjects research requires IRB approval.
    
    45 CFR § 46.109:
    - IRB must review and approve research
    - Continuing review required
    - Unanticipated problems must be reported
    
    Falsifies if: no IRB approval for human subjects research
    """
    if study.research_type == ResearchType.SECONDARY_ANALYSIS and study.data_anonymized:
        return True, ProofObject(
            conclusion=f"Study {study.study_id} exempt — secondary analysis of anonymized data",
            premises=["Research type: secondary analysis", "Anonymized: YES"],
            rule="irb_exemption_secondary"
        )
    
    if study.irb_status == IRBStatus.NOT_SUBMITTED:
        return False, ProofObject(
            conclusion=f"VIOLATION: Study {study.study_id} not submitted to IRB",
            premises=[
                f"IRB status: {study.irb_status.name}",
                f"Research type: {study.research_type.name}",
                "45 CFR § 46.109 — IRB review required"
            ],
            rule="irb_approval"
        )
    
    if study.irb_status == IRBStatus.PENDING:
        return True, ProofObject(
            conclusion=f"Study {study.study_id} IRB review pending",
            premises=["Status: PENDING"],
            rule="irb_approval"
        )
    
    return True, ProofObject(
        conclusion=f"Study {study.study_id} IRB approved",
        premises=[f"Status: {study.irb_status.name}", f"Date: {study.irb_approval_date}"],
        rule="irb_approval"
    )


def check_informed_consent(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """
    Informed consent required for human subjects research.
    
    Belmont Report — Respect for Persons:
    - Individuals should be treated as autonomous agents
    - Persons with diminished autonomy are entitled to protection
    - Informed consent demonstrates respect
    
    Falsifies if: no consent for non-exempt research
    """
    if study.irb_status == IRBStatus.EXEMPT:
        return True, ProofObject(
            conclusion=f"Study {study.study_id} IRB exempt — informed consent waived",
            premises=["IRB status: EXEMPT"],
            rule="informed_consent_exemption"
        )
    
    if not study.informed_consent_obtained:
        return False, ProofObject(
            conclusion=f"VIOLATION: Study {study.study_id} lacks informed consent",
            premises=[
                f"Consent obtained: {study.informed_consent_obtained}",
                f"Sample size: {study.actual_sample_size}",
                "Belmont Report — Respect for persons"
            ],
            rule="informed_consent"
        )
    
    return True, ProofObject(
        conclusion=f"Study {study.study_id} informed consent verified",
        premises=["Consent obtained: YES"],
        rule="informed_consent"
    )


def check_survey_response_rate(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """
    Survey research requires adequate response rates.
    
    AAPOR standards:
    - Response rates affect generalizability
    - Non-response bias concern
    - Minimum thresholds vary by mode
    
    Falsifies if: response rate < 30%
    """
    if study.research_type != ResearchType.SURVEY:
        return True, ProofObject(
            conclusion=f"Study {study.study_id} not survey — response rate N/A",
            premises=[f"Type: {study.research_type.name}"],
            rule="response_rate_exemption"
        )
    
    min_rate = min_survey_response_rate()
    rate = study.get_response_rate()
    
    if rate < min_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Study {study.study_id} response rate {rate} below minimum {min_rate}",
            premises=[
                f"Responses: {study.responses_received}",
                f"Contacts: {study.contacts_attempted}",
                f"Rate: {rate}",
                "AAPOR standards — Response rate"
            ],
            rule="survey_response_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Study {study.study_id} survey response rate acceptable",
        premises=[f"Rate: {rate}"],
        rule="survey_response_rate"
    )


def check_survey_reliability(instrument: SurveyInstrument) -> Tuple[bool, ProofObject]:
    """
    Survey instruments should demonstrate reliability.
    
    Psychometric standards:
    - Cronbach's alpha ≥ 0.70 for internal consistency
    - Pilot testing required
    - Validity assessment
    
    Falsifies if: alpha < 0.70
    """
    min_alpha = min_reliability_alpha()
    
    if not instrument.pilot_tested:
        return False, ProofObject(
            conclusion=f"VIOLATION: Instrument {instrument.instrument_id} not pilot tested",
            premises=[
                f"Pilot tested: {instrument.pilot_tested}",
                "Research standards — Pilot testing required"
            ],
            rule="survey_reliability"
        )
    
    if instrument.reliability_coefficient < min_alpha:
        return False, ProofObject(
            conclusion=f"VIOLATION: Instrument {instrument.instrument_id} reliability {instrument.reliability_coefficient} below {min_alpha}",
            premises=[
                f"Alpha: {instrument.reliability_coefficient}",
                f"Required: {min_alpha}",
                "Psychometric standards — Internal consistency"
            ],
            rule="survey_reliability"
        )
    
    return True, ProofObject(
        conclusion=f"Instrument {instrument.instrument_id} reliability acceptable",
        premises=[f"Alpha: {instrument.reliability_coefficient}"],
        rule="survey_reliability"
    )


def check_data_protection(study: ResearchStudy) -> Tuple[bool, ProofObject]:
    """
    Research data requires protection and retention limits.
    
    Data management:
    - Anonymization preferred
    - Retention limits apply
    - Secure storage required
    
    Falsifies if: retention > 7 years without justification
    """
    max_retention = Fraction(7)  # 7 years
    
    if study.data_retention_years > max_retention:
        return False, ProofObject(
            conclusion=f"VIOLATION: Study {study.study_id} data retention {study.data_retention_years} years exceeds {max_retention} year limit",
            premises=[
                f"Retention: {study.data_retention_years} years",
                f"Anonymized: {study.data_anonymized}",
                "Data management standards — Retention limits"
            ],
            rule="data_retention"
        )
    
    return True, ProofObject(
        conclusion=f"Study {study.study_id} data protection acceptable",
        premises=[
            f"Retention: {study.data_retention_years} years",
            f"Anonymized: {study.data_anonymized}"
        ],
        rule="data_retention"
    )
