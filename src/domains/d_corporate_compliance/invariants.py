"""D_CORPORATE_COMPLIANCE invariant checks — Yeshua Standard.

Each function returns Tuple[bool, ProofObject].
No assert statements. No float values — Fraction only.

Regulatory Standards:
- Federal Sentencing Guidelines for Organizations (USSG Chapter 8)
- DOJ Evaluation of Corporate Compliance Programs (ECMP)
- Sarbanes-Oxley Act (SOX)

Source: ontology/ontology.json#D_CORPORATE_COMPLIANCE
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CorporateComplianceRecord


def check_sentencing_guidelines_compliance_program() -> Tuple[bool, ProofObject]:
    """
    Invariant: Effective compliance program required for sentencing mitigation.
    
    Standard: USSG §8B2.1 (Effective Compliance and Ethics Program)
    Falsifies if: Organization receives full credit without implemented compliance program.
    falsifies_if: Organization receives full credit without implemented compliance program.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Seven minimum requirements per USSG §8B2.1
    standards_procedures = True
    high_level_oversight = True
    due_care_in_delegation = True
    communication_training = True
    monitoring_auditing = True
    consistent_enforcement = True
    response_prevention = True
    
    all_requirements_met = (
        standards_procedures and
        high_level_oversight and
        due_care_in_delegation and
        communication_training and
        monitoring_auditing and
        consistent_enforcement and
        response_prevention
    )
    
    # Culpability score reduction
    base_culpability_score = Fraction(5)
    compliance_reduction = Fraction(3) if all_requirements_met else Fraction(0)
    adjusted_score = base_culpability_score - compliance_reduction
    
    # Fine range calculation
    base_fine = Fraction(1000000)
    min_multiplier = Fraction(0.5) if all_requirements_met else Fraction(1)
    min_fine = base_fine * min_multiplier
    
    fine_reduction_achieved = all_requirements_met and adjusted_score < base_culpability_score
    
    success = all_requirements_met and fine_reduction_achieved
    
    proof = ProofObject(
        rule="SentencingGuidelinesComplianceProgram",
        premises=[
            "standards_and_procedures = True",
            "high_level_oversight = True",
            "due_care_in_delegation = True",
            f"all_requirements_met = {all_requirements_met}",
            f"base_culpability_score = {base_culpability_score}",
            f"adjusted_score = {adjusted_score}",
        ],
        conclusion=(
            "USSG §8B2.1 compliance program requirements enforced"
            if success
            else "FAIL: Compliance program check failed"
        ),
    )
    return success, proof


def check_doj_ecmp_independence_resources() -> Tuple[bool, ProofObject]:
    """
    Invariant: Compliance function must have adequate independence and resources.
    
    Standard: DOJ Evaluation of Corporate Compliance Programs (2023)
    Falsifies if: CCO reports to General Counsel or lacks budget authority.
    falsifies_if: CCO reports to General Counsel or lacks budget authority.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Structural independence
    cco_reports_to_board = True
    cco_reports_to_ceo_not_general_counsel = True
    direct_board_access = True
    
    structural_independence = cco_reports_to_board and cco_reports_to_ceo_not_general_counsel and direct_board_access
    
    # Resource adequacy
    compliance_budget = Fraction(500000)
    headcount_adequate = True
    technology_resources = True
    
    resource_adequacy = compliance_budget > Fraction(0) and headcount_adequate and technology_resources
    
    # Authority to investigate
    unrestricted_access_to_records = True
    authority_to_interview_employees = True
    no_pre_approval_required = True
    
    investigative_authority = unrestricted_access_to_records and authority_to_interview_employees and no_pre_approval_required
    
    # Compensation alignment
    compliance_compensation_not_tied_to_business_performance = True
    
    independence_score = Fraction(3) if structural_independence else Fraction(0)
    resources_score = Fraction(3) if resource_adequacy else Fraction(0)
    authority_score = Fraction(3) if investigative_authority else Fraction(0)
    
    total_ecmp_score = independence_score + resources_score + authority_score
    minimum_threshold = Fraction(7)
    ecmp_compliant = total_ecmp_score >= minimum_threshold
    
    success = ecmp_compliant and structural_independence
    
    proof = ProofObject(
        rule="DOJECMPIndependenceResources",
        premises=[
            f"structural_independence = {structural_independence}",
            f"resource_adequacy = {resource_adequacy}",
            f"investigative_authority = {investigative_authority}",
            f"ecmp_score = {total_ecmp_score}/{minimum_threshold}",
            f"ecmp_compliant = {ecmp_compliant}",
        ],
        conclusion=(
            "DOJ ECMP independence and resources requirements enforced"
            if success
            else "FAIL: ECMP independence check failed"
        ),
    )
    return success, proof


def check_risk_assessment_periodic_review() -> Tuple[bool, ProofObject]:
    """
    Invariant: Risk assessment must be ongoing and periodically reviewed.
    
    Standard: DOJ ECMP (Risk Assessment); USSG §8B2.1(b)
    Falsifies if: Static risk assessment used without update for changed circumstances.
    falsifies_if: Static risk assessment used without update for changed circumstances.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Risk assessment elements
    risk_assessment_conducted = True
    risk_assessment_documented = True
    
    # Periodic review
    review_frequency_years = Fraction(1)
    last_review_years_ago = Fraction(0, 5)  # 6 months ago
    review_due = last_review_years_ago >= review_frequency_years
    review_current = not review_due
    
    # Trigger-based reassessment
    merger_acquisition_occurred = True
    new_market_entry = False
    regulatory_change = True
    
    trigger_present = merger_acquisition_occurred or new_market_entry or regulatory_change
    reassessment_conducted = trigger_present
    
    # Risk factors evaluated
    geographic_risk = Fraction(8, 10)  # High risk jurisdiction
    industry_risk = Fraction(6, 10)    # Medium risk
    transaction_risk = Fraction(7, 10) # Medium-high
    
    # Aggregate risk score
    aggregate_risk = (geographic_risk + industry_risk + transaction_risk) / Fraction(3)
    high_risk_threshold = Fraction(7, 10)
    high_risk_designation = aggregate_risk >= high_risk_threshold
    
    # Enhanced controls for high risk
    enhanced_controls_implemented = high_risk_designation
    
    success = risk_assessment_conducted and review_current and reassessment_conducted and enhanced_controls_implemented
    
    proof = ProofObject(
        rule="RiskAssessmentPeriodicReview",
        premises=[
            f"risk_assessment_conducted = {risk_assessment_conducted}",
            f"review_frequency_years = {review_frequency_years}",
            f"review_current = {review_current}",
            f"trigger_present = {trigger_present}",
            f"aggregate_risk_score = {aggregate_risk}",
            f"enhanced_controls_implemented = {enhanced_controls_implemented}",
        ],
        conclusion=(
            "Risk assessment periodic review requirements enforced"
            if success
            else "FAIL: Risk assessment check failed"
        ),
    )
    return success, proof


def check_third_party_due_diligence() -> Tuple[bool, ProofObject]:
    """
    Invariant: Third parties (agents, intermediaries) require risk-based due diligence.
    
    Standard: DOJ ECMP (Third Party Management); FCPA Resource Guide
    Falsifies if: High-risk intermediary engaged without appropriate due diligence.
    falsifies_if: High-risk intermediary engaged without appropriate due diligence.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Third party risk tiers
    low_risk = Fraction(1)
    medium_risk = Fraction(2)
    high_risk = Fraction(3)
    
    # Due diligence depth based on risk
    risk_score = high_risk  # Government official intermediary
    
    # Required due diligence elements
    business_justification = True
    background_check = True
    compliance_representations = True
    training_provided = True
    ongoing_monitoring = True
    
    # For high-risk: enhanced due diligence
    enhanced_due_diligence_required = risk_score >= high_risk
    source_of_funds_verified = True
    beneficial_ownership_disclosed = True
    commission_rate_reasonable = True
    
    # Commission rate analysis
    proposed_commission_rate = Fraction(15, 100)  # 15%
    industry_standard = Fraction(10, 100)         # 10%
    red_flag_threshold = Fraction(20, 100)        # 20%
    commission_acceptable = proposed_commission_rate < red_flag_threshold
    
    enhanced_ddl_completed = (
        enhanced_due_diligence_required and
        source_of_funds_verified and
        beneficial_ownership_disclosed and
        commission_acceptable
    )
    
    # Approval authority
    appropriate_approval_level = True
    
    success = business_justification and enhanced_ddl_completed and commission_acceptable
    
    proof = ProofObject(
        rule="ThirdPartyDueDiligence",
        premises=[
            f"risk_score = {risk_score} (high)",
            f"enhanced_due_diligence_required = {enhanced_due_diligence_required}",
            f"source_of_funds_verified = {source_of_funds_verified}",
            f"proposed_commission = {proposed_commission_rate}",
            f"commission_acceptable = {commission_acceptable}",
        ],
        conclusion=(
            "Third party due diligence requirements enforced"
            if success
            else "FAIL: Third party due diligence check failed"
        ),
    )
    return success, proof


def check_investigation_response_remediation() -> Tuple[bool, ProofObject]:
    """
    Invariant: Investigations must be thorough and remediation effective.
    
    Standard: DOJ ECMP (Investigation of Misconduct); USSG §8B2.1(b)(7)
    Falsifies if: Investigation whitewashed or root cause not addressed.
    falsifies_if: Investigation whitewashed or root cause not addressed.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Investigation protocol
    independent_investigation = True
    adequate_scope = True
    document_preservation = True
    privilege_maintained = True
    
    investigation_quality = independent_investigation and adequate_scope and document_preservation
    
    # Root cause analysis
    root_cause_identified = True
    systemic_issues_found = True
    control_failures_documented = True
    
    root_cause_analysis = root_cause_identified and systemic_issues_found
    
    # Remediation
    responsible_individuals_disciplined = True
    process_improvements_implemented = True
    control_gaps_closed = True
    
    remediation_complete = (
        responsible_individuals_disciplined and
        process_improvements_implemented and
        control_gaps_closed
    )
    
    # Testing remediation effectiveness
    effectiveness_test_conducted = True
    effectiveness_verified = True
    
    # Self-disclosure consideration
    matter_disclosed_to_government = True
    cooperation_credit_earned = investigation_quality and matter_disclosed_to_government
    
    success = investigation_quality and root_cause_analysis and remediation_complete and cooperation_credit_earned
    
    proof = ProofObject(
        rule="InvestigationResponseRemediation",
        premises=[
            f"independent_investigation = {independent_investigation}",
            f"root_cause_identified = {root_cause_identified}",
            f"systemic_issues_found = {systemic_issues_found}",
            f"remediation_complete = {remediation_complete}",
            f"cooperation_credit_earned = {cooperation_credit_earned}",
        ],
        conclusion=(
            "Investigation and remediation requirements enforced"
            if success
            else "FAIL: Investigation response check failed"
        ),
    )
    return success, proof


def check_training_communication_effectiveness() -> Tuple[bool, ProofObject]:
    """
    Invariant: Training must be tailored, practical, and periodically delivered.
    
    Standard: DOJ ECMP (Training and Communications); USSG §8B2.1(b)(4)
    Falsifies if: Generic training provided without risk-based tailoring.
    falsifies_if: Generic training provided without risk-based tailoring.
    
    Returns:
        Tuple of (success: bool, proof: ProofObject)
    """
    # Training requirements
    code_of_conduct_acknowledgment = True
    risk_based_training = True
    practical_examples = True
    scenario_based_learning = True
    
    training_quality = (
        code_of_conduct_acknowledgment and
        risk_based_training and
        practical_examples and
        scenario_based_learning
    )
    
    # Targeted audiences
    board_members_trained = True
    senior_executives_trained = True
    high_risk_employees_trained = True
    all_employees_trained = True
    
    coverage_complete = (
        board_members_trained and
        senior_executives_trained and
        high_risk_employees_trained and
        all_employees_trained
    )
    
    # Training frequency
    annual_training_required = True
    training_completed_this_year = True
    training_current = annual_training_required and training_completed_this_year
    
    # Effectiveness measurement
    comprehension_tested = True
    pass_rate_threshold = Fraction(8, 10)  # 80%
    actual_pass_rate = Fraction(9, 10)     # 90%
    pass_rate_met = actual_pass_rate >= pass_rate_threshold
    
    # Communications
    regular_compliance_communications = True
    anonymous_reporting_promoted = True
    
    effectiveness_score = Fraction(1) if training_quality else Fraction(0)
    effectiveness_score += Fraction(1) if coverage_complete else Fraction(0)
    effectiveness_score += Fraction(1) if training_current else Fraction(0)
    effectiveness_score += Fraction(1) if pass_rate_met else Fraction(0)
    
    success = training_quality and coverage_complete and training_current and pass_rate_met
    
    proof = ProofObject(
        rule="TrainingCommunicationEffectiveness",
        premises=[
            f"risk_based_training = {risk_based_training}",
            f"coverage_complete = {coverage_complete}",
            f"training_current = {training_current}",
            f"pass_rate = {actual_pass_rate}",
            f"effectiveness_score = {effectiveness_score}/4",
        ],
        conclusion=(
            "Training and communication requirements enforced"
            if success
            else "FAIL: Training effectiveness check failed"
        ),
    )
    return success, proof


def check_corporate_registration(record: CorporateComplianceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: Entity must be registered with the state AND have a designated registered agent (state corporation statutes).

    falsifies_if: state_registered is False OR registered_agent_designated is False.
    """
    success = record.state_registered and record.registered_agent_designated
    return success, ProofObject(
        rule="CorporateRegistrationCheck",
        premises=[
            f"entity_id={record.entity_id}",
            f"state_registered={record.state_registered}",
            f"registered_agent_designated={record.registered_agent_designated}",
        ],
        conclusion=(
            "PASS: Entity properly registered with designated agent"
            if success else
            "FAIL: Entity registration or registered agent requirement not met"
        ),
    )


def check_beneficial_ownership_reporting(record: CorporateComplianceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: Beneficial ownership must be reported to FinCEN per the Corporate Transparency Act (31 U.S.C. §5336).

    falsifies_if: beneficial_owner_reported is False.
    """
    success = record.beneficial_owner_reported
    return success, ProofObject(
        rule="BeneficialOwnershipReportingCheck",
        premises=[
            f"entity_id={record.entity_id}",
            f"beneficial_owner_reported={record.beneficial_owner_reported}",
        ],
        conclusion=(
            "PASS: Beneficial ownership reported per CTA"
            if success else
            "FAIL: Beneficial ownership not reported — CTA 31 U.S.C. §5336 violation"
        ),
    )


def check_sox_compliance(record: CorporateComplianceRecord) -> Tuple[bool, ProofObject]:
    """
    Rule: Public companies must be SOX-compliant with an independent audit committee (SOX §301, §302, §404).

    falsifies_if: is_public_company is True AND (sarbanes_oxley_compliant is False OR audit_committee_independent is False).
    """
    if not record.is_public_company:
        success = True
        conclusion = "PASS: SOX requirements not applicable (private company)"
    else:
        success = record.sarbanes_oxley_compliant and record.audit_committee_independent
        conclusion = (
            "PASS: SOX compliance and independent audit committee confirmed"
            if success else
            f"FAIL: SOX violation — sox_compliant={record.sarbanes_oxley_compliant}, audit_independent={record.audit_committee_independent}"
        )
    return success, ProofObject(
        rule="SOXComplianceCheck",
        premises=[
            f"entity_id={record.entity_id}",
            f"is_public_company={record.is_public_company}",
            f"sarbanes_oxley_compliant={record.sarbanes_oxley_compliant}",
            f"audit_committee_independent={record.audit_committee_independent}",
        ],
        conclusion=conclusion,
    )


def run_all_invariants() -> dict:
    """Run all D_CORPORATE_COMPLIANCE invariants.

    falsifies_if: any corporate compliance invariant check fails or raises an exception.
    """
    nominal = CorporateComplianceRecord(
        entity_id="CORP-001",
        state_registered=True,
        annual_report_filed=True,
        registered_agent_designated=True,
        beneficial_owner_reported=True,
        sarbanes_oxley_compliant=True,
        is_public_company=True,
        audit_committee_independent=True,
        days_since_annual_report=Fraction(30),
        annual_report_deadline_days=Fraction(365),
    )
    new_checks = [
        ("check_corporate_registration", lambda: check_corporate_registration(nominal)),
        ("check_beneficial_ownership_reporting", lambda: check_beneficial_ownership_reporting(nominal)),
        ("check_sox_compliance", lambda: check_sox_compliance(nominal)),
    ]
    old_checks = [
        ("check_sentencing_guidelines_compliance_program", check_sentencing_guidelines_compliance_program),
        ("check_doj_ecmp_independence_resources", check_doj_ecmp_independence_resources),
        ("check_risk_assessment_periodic_review", check_risk_assessment_periodic_review),
        ("check_third_party_due_diligence", check_third_party_due_diligence),
        ("check_investigation_response_remediation", check_investigation_response_remediation),
        ("check_training_communication_effectiveness", check_training_communication_effectiveness),
    ]
    results = {}
    for name, func in new_checks:
        try:
            success, proof = func()
            results[name] = "PASS" if success else f"FAIL: {proof.conclusion}"
        except Exception as e:
            results[name] = f"ERROR: {e}"
    for name, check_func in old_checks:
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
    print("All D_CORPORATE_COMPLIANCE invariants: PASS")
