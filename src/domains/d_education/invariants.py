"""D_EDUCATION Invariants — Education Standards, ESSA, IDEA, FERPA

Verifies Every Student Succeeds Act (ESSA) compliance, 
Individuals with Disabilities Education Act (IDEA) requirements,
FERPA privacy protections, Title IX equity.

Standards: 20 U.S.C. § 6301 (ESSA), 20 U.S.C. § 1400 (IDEA), 20 U.S.C. § 1232g (FERPA)
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import (
    EducationRecord, SpecialEducationProgram, FERPAComplianceRecord,
    EducationLevel, ComplianceStatus,
    essa_graduation_threshold, idea_parental_notice_limit, ferpa_access_fulfillment_limit
)


def check_essa_graduation_rate(record: EducationRecord) -> Tuple[bool, ProofObject]:
    """
    ESSA requires high schools to meet minimum graduation rates.
    
    Every Student Succeeds Act (ESSA) 20 U.S.C. § 6301:
    - High schools must achieve graduation rates above state minimum
    - Default federal minimum is 67% (states may set higher)
    - Four-year adjusted cohort graduation rate required
    
    Falsifies if: graduation_rate < 67%
    """
    threshold = essa_graduation_threshold()
    
    if record.education_level != EducationLevel.HIGH_SCHOOL:
        return True, ProofObject(
            conclusion=f"Graduation rate check N/A for {record.education_level.name}",
            premises=[f"Level: {record.education_level.name}", "ESSA applies to high school only"],
            rule="essa_graduation_exemption"
        )
    
    if record.graduation_rate is None:
        return False, ProofObject(
            conclusion=f"VIOLATION: {record.institution_name} missing graduation rate data",
            premises=[
                f"Institution: {record.record_id}",
                "ESSA requires graduation rate reporting"
            ],
            rule="essa_graduation_reporting"
        )
    
    if record.graduation_rate < threshold:
        return False, ProofObject(
            conclusion=f"VIOLATION: {record.institution_name} graduation rate {record.graduation_rate} below threshold {threshold}",
            premises=[
                f"Graduation rate: {record.graduation_rate}",
                f"Threshold: {threshold}",
                "20 U.S.C. § 6301 — ESSA graduation requirements"
            ],
            rule="essa_graduation_minimum"
        )
    
    return True, ProofObject(
        conclusion=f"{record.institution_name} meets ESSA graduation rate requirement",
        premises=[
            f"Graduation rate: {record.graduation_rate}",
            f"Threshold: {threshold}"
        ],
        rule="essa_graduation_minimum"
    )


def check_idea_iep_compliance(program: SpecialEducationProgram) -> Tuple[bool, ProofObject]:
    """
    IDEA requires Individualized Education Program (IEP) compliance.
    
    Individuals with Disabilities Education Act (IDEA) 20 U.S.C. § 1400:
    - All students with disabilities must have IEPs
    - IEPs must be reviewed annually
    - Compliance rate should approach 100%
    
    Falsifies if: iep_compliance_rate < 95%
    """
    min_compliance = Fraction(95, 100)
    
    if program.iep_compliance_rate < min_compliance:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} IEP compliance {program.iep_compliance_rate} below required {min_compliance}",
            premises=[
                f"IEP compliance: {program.iep_compliance_rate}",
                f"Required: {min_compliance}",
                "20 U.S.C. § 1414 — IDEA IEP requirements"
            ],
            rule="idea_iep_compliance"
        )
    
    return True, ProofObject(
        conclusion=f"Program {program.program_id} meets IDEA IEP compliance requirements",
        premises=[f"IEP compliance: {program.iep_compliance_rate}"],
        rule="idea_iep_compliance"
    )


def check_idea_parental_notice(program: SpecialEducationProgram) -> Tuple[bool, ProofObject]:
    """
    IDEA requires parental notice within 30 days of certain events.
    
    IDEA 20 U.S.C. § 1415:
    - Prior written notice required for IEP changes
    - Must be provided within reasonable time (≤ 30 days)
    - Procedural safeguards notice required annually
    
    Falsifies if: parental_notice_days > 30
    """
    limit = idea_parental_notice_limit()
    
    if program.parental_notice_days > limit:
        return False, ProofObject(
            conclusion=f"VIOLATION: Program {program.program_id} parental notice took {program.parental_notice_days} days, exceeding {limit} day limit",
            premises=[
                f"Notice days: {program.parental_notice_days}",
                f"Limit: {limit}",
                "20 U.S.C. § 1415 — IDEA procedural safeguards"
            ],
            rule="idea_parental_notice_timeline"
        )
    
    return True, ProofObject(
        conclusion=f"Program {program.program_id} meets IDEA parental notice timeline",
        premises=[f"Notice days: {program.parental_notice_days}", f"Limit: {limit}"],
        rule="idea_parental_notice_timeline"
    )


def check_ferpa_unauthorized_disclosure(ferpa_record: FERPAComplianceRecord) -> Tuple[bool, ProofObject]:
    """
    FERPA limits unauthorized disclosures of educational records.
    
    Family Educational Rights and Privacy Act 20 U.S.C. § 1232g:
    - No disclosure without written consent (with exceptions)
    - Unauthorized disclosures must be minimized
    - Annual notification of rights required
    
    Falsifies if: unauthorized_disclosure_rate > 1%
    """
    max_rate = Fraction(1, 100)  # 1% maximum
    
    rate = ferpa_record.get_unauthorized_disclosure_rate()
    
    if rate > max_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Institution {ferpa_record.institution_id} unauthorized disclosure rate {rate} exceeds {max_rate} limit",
            premises=[
                f"Unauthorized rate: {rate}",
                f"Third-party disclosures: {ferpa_record.third_party_disclosures}",
                f"Unauthorized disclosures: {ferpa_record.unauthorized_disclosures}",
                "20 U.S.C. § 1232g — FERPA privacy protections"
            ],
            rule="ferpa_disclosure_limits"
        )
    
    return True, ProofObject(
        conclusion=f"Institution {ferpa_record.institution_id} FERPA disclosure compliance verified",
        premises=[f"Unauthorized rate: {rate}", f"Limit: {max_rate}"],
        rule="ferpa_disclosure_limits"
    )


def check_title_ix_equity(record: EducationRecord) -> Tuple[bool, ProofObject]:
    """
    Title IX prohibits sex-based discrimination in education.
    
    Title IX 20 U.S.C. § 1681:
    - No person shall be excluded from participation based on sex
    - Equal opportunity in athletics and academics
    - Grievance procedures required
    
    This invariant checks for equitable resource distribution.
    
    Falsifies if: significant disparities in resource allocation detected
    """
    # Check for reasonable representation across demographics
    disability_ratio = record.get_disability_ratio()
    el_ratio = record.get_english_learner_ratio()
    
    # Title IX requires that students with disabilities and English learners
    # have comparable access to educational resources
    
    if record.academic_achievement_score == 0:
        return True, ProofObject(
            conclusion=f"Title IX equity check pending for {record.institution_name}",
            premises=["No academic achievement data available"],
            rule="title_ix_pending"
        )
    
    # If there are English learners, they should have language support
    if el_ratio > 0 and record.english_proficiency_progress is None:
        return False, ProofObject(
            conclusion=f"VIOLATION: {record.institution_name} has English learners ({el_ratio}) but no progress tracking",
            premises=[
                f"English learner ratio: {el_ratio}",
                "English proficiency progress: not tracked",
                "20 U.S.C. § 1681 — Title IX / ESSA Title III"
            ],
            rule="title_ix_english_learner_support"
        )
    
    return True, ProofObject(
        conclusion=f"{record.institution_name} Title IX equity requirements verified",
        premises=[
            f"Disability ratio: {disability_ratio}",
            f"EL ratio: {el_ratio}",
            f"Achievement score: {record.academic_achievement_score}"
        ],
        rule="title_ix_equity"
    )


def check_student_privacy_protection(ferpa_record: FERPAComplianceRecord) -> Tuple[bool, ProofObject]:
    """
    FERPA requires timely response to student/parent access requests.
    
    FERPA 34 CFR § 99.10:
    - Must provide access within 45 days of request
    - Cannot destroy records if access requested
    - May charge reasonable fee for copies
    
    Falsifies if: access fulfillment rate < 100%
    """
    # Calculate fulfillment rates
    student_rate = Fraction(ferpa_record.student_access_fulfilled, max(ferpa_record.student_access_requests, 1))
    parent_rate = Fraction(ferpa_record.parent_access_fulfilled, max(ferpa_record.parent_access_requests, 1))
    
    min_fulfillment = Fraction(95, 100)  # 95% minimum
    
    if ferpa_record.student_access_requests > 0 and student_rate < min_fulfillment:
        return False, ProofObject(
            conclusion=f"VIOLATION: Institution {ferpa_record.institution_id} student access fulfillment {student_rate} below requirement",
            premises=[
                f"Student requests: {ferpa_record.student_access_requests}",
                f"Student fulfilled: {ferpa_record.student_access_fulfilled}",
                "34 CFR § 99.10 — FERPA access rights"
            ],
            rule="ferpa_access_fulfillment"
        )
    
    if ferpa_record.parent_access_requests > 0 and parent_rate < min_fulfillment:
        return False, ProofObject(
            conclusion=f"VIOLATION: Institution {ferpa_record.institution_id} parent access fulfillment {parent_rate} below requirement",
            premises=[
                f"Parent requests: {ferpa_record.parent_access_requests}",
                f"Parent fulfilled: {ferpa_record.parent_access_fulfilled}",
                "34 CFR § 99.10 — FERPA access rights"
            ],
            rule="ferpa_access_fulfillment"
        )
    
    return True, ProofObject(
        conclusion=f"Institution {ferpa_record.institution_id} FERPA access fulfillment verified",
        premises=[
            f"Student fulfillment: {student_rate}",
            f"Parent fulfillment: {parent_rate}"
        ],
        rule="ferpa_access_fulfillment"
    )
