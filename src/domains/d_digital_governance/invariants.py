#!/usr/bin/env python3
"""Digital Governance Domain Invariants — DSA/DMA compliance, transparency, risk assessment.

Regulatory Standards:
- EU Digital Services Act (DSA) 2022/2065
- EU Digital Markets Act (DMA) 2022/1925  
- GDPR 2016/679 (Article 5 principles)
- UK Online Safety Bill (duty of care)

Falsifies if:
- VLOPs lack annual risk assessment (DSA Article 34)
- Content restrictions lack statement of reasons (DSA Article 17)
- Transparency reports are missing or incomplete
- Appeal processes don't meet 6-month window
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    Platform, ContentModerationDecision, TransparencyReport,
    RiskAssessment, SystemicRiskLevel
)


def check_vlop_risk_assessment_current(platform: Platform) -> Tuple[bool, ProofObject]:
    """DSA Article 34: Very Large Online Platforms must have annual systemic risk assessment.

    Falsifies if: platform.is_vlop() and no risk assessment exists or assessment age exceeds 365 days.
    falsifies_if: platform.is_vlop() and no risk assessment exists or assessment age exceeds 365 days.
    """
    if not platform.is_vlop():
        return True, ProofObject(
            conclusion="Platform not classified as VLOP, risk assessment not required",
            premises=[f"EU users: {platform.user_metrics.eu_monthly_active}"],
            rule="dsa_article_33_vlop_threshold"
        )
    
    latest = platform.latest_risk_assessment()
    if latest is None:
        return False, ProofObject(
            conclusion="VIOLATION: VLOP lacks required systemic risk assessment",
            premises=[f"Platform: {platform.name}", "EU users: >45M"],
            rule="dsa_article_34_risk_assessment_required"
        )
    
    if not latest.is_current():
        age_days = (platform.user_metrics.last_reported - latest.assessment_date).days
        return False, ProofObject(
            conclusion=f"VIOLATION: Risk assessment expired ({age_days} days old)",
            premises=[f"Assessment date: {latest.assessment_date}", "Required: annual"],
            rule="dsa_article_34_risk_assessment_current"
        )
    
    return True, ProofObject(
        conclusion="VLOP has current systemic risk assessment",
        premises=[f"Assessment date: {latest.assessment_date}"],
        rule="dsa_article_34_compliant"
    )


def check_statement_of_reasons(decision: ContentModerationDecision) -> Tuple[bool, ProofObject]:
    """DSA Article 17: Content restrictions require statement of reasons.

    Falsifies if: content is restricted and statement_of_reasons is missing or inadequate.
    falsifies_if: content is restricted and statement_of_reasons is missing or inadequate.
    """
    if decision.content_category.name == "PROTECTED":
        if not decision.statement_of_reasons or len(decision.statement_of_reasons) < 50:
            return False, ProofObject(
                conclusion="VIOLATION: Protected speech restriction lacks adequate statement",
                premises=[f"Decision: {decision.decision_id}", "Content: protected speech"],
                rule="dsa_article_17_statement_required"
            )
    
    if not decision.statement_of_reasons:
        return False, ProofObject(
            conclusion="VIOLATION: Content restriction lacks statement of reasons",
            premises=[f"Decision: {decision.decision_id}", f"Action: {decision.action_taken}"],
            rule="dsa_article_17_statement_required"
        )
    
    return True, ProofObject(
        conclusion="Content restriction has required statement of reasons",
        premises=[f"Statement length: {len(decision.statement_of_reasons)} chars"],
        rule="dsa_article_17_compliant"
    )


def check_transparency_report_completeness(report: TransparencyReport) -> Tuple[bool, ProofObject]:
    """DSA Article 15: Transparency reports must include required metrics.

    Falsifies if: required metrics are negative/invalid or response time is missing.
    falsifies_if: required metrics are negative/invalid or response time is missing.
    """
    if report.content_removed_count < 0:
        return False, ProofObject(
            conclusion="VIOLATION: Invalid content removed count",
            premises=[f"Count: {report.content_removed_count}"],
            rule="dsa_article_15_valid_metrics"
        )
    
    if report.avg_response_time_hours < Fraction(0):
        return False, ProofObject(
            conclusion="VIOLATION: Invalid response time",
            premises=[f"Hours: {report.avg_response_time_hours}"],
            rule="dsa_article_15_valid_metrics"
        )
    
    if report.appeals_received > 0 and report.appeals_upheld > report.appeals_received:
        return False, ProofObject(
            conclusion="VIOLATION: Appeals upheld exceeds appeals received",
            premises=[
                f"Received: {report.appeals_received}",
                f"Upheld: {report.appeals_upheld}"
            ],
            rule="dsa_article_15_consistent_metrics"
        )
    
    return True, ProofObject(
        conclusion="Transparency report contains valid required metrics",
        premises=[
            f"Period: {report.reporting_period}",
            f"Appeal rate: {report.appeal_upheld_rate()}"
        ],
        rule="dsa_article_15_compliant"
    )


def check_appeal_window(decision: ContentModerationDecision) -> Tuple[bool, ProofObject]:
    """DSA Article 20: Users must have at least 6 months to appeal decisions.

    Falsifies if: decision.appeal_window_days < 180.
    falsifies_if: decision.appeal_window_days < 180.
    """
    MIN_APPEAL_DAYS = 180  # 6 months as required by DSA
    
    if decision.appeal_window_days < MIN_APPEAL_DAYS:
        return False, ProofObject(
            conclusion=f"VIOLATION: Appeal window {decision.appeal_window_days} days < required {MIN_APPEAL_DAYS}",
            premises=[f"Window: {decision.appeal_window_days} days", f"Required: {MIN_APPEAL_DAYS} days"],
            rule="dsa_article_20_appeal_window"
        )
    
    return True, ProofObject(
        conclusion="Appeal window meets DSA requirements",
        premises=[f"Window: {decision.appeal_window_days} days"],
        rule="dsa_article_20_compliant"
    )


def check_independent_audit(risk_assessment: RiskAssessment) -> Tuple[bool, ProofObject]:
    """DSA Article 37: VLOP risk assessments require independent audit.

    Falsifies if: risk level is CRITICAL or HIGH and independent_audit is False.
    falsifies_if: risk level is CRITICAL or HIGH and independent_audit is False.
    """
    high_risk = risk_assessment.risk_level in [
        SystemicRiskLevel.CRITICAL,
        SystemicRiskLevel.HIGH
    ]
    
    if high_risk and not risk_assessment.independent_audit:
        return False, ProofObject(
            conclusion="VIOLATION: High-risk assessment lacks independent audit",
            premises=[
                f"Risk level: {risk_assessment.risk_level.name}",
                "Audit: none"
            ],
            rule="dsa_article_37_independent_audit"
        )
    
    if high_risk and risk_assessment.audit_date is None:
        return False, ProofObject(
            conclusion="VIOLATION: Audited assessment lacks audit date",
            premises=["independent_audit: True", "audit_date: None"],
            rule="dsa_article_37_audit_documentation"
        )
    
    return True, ProofObject(
        conclusion="Risk assessment meets audit requirements",
        premises=[
            f"Risk level: {risk_assessment.risk_level.name}",
            f"Audited: {risk_assessment.independent_audit}"
        ],
        rule="dsa_article_37_compliant"
    )


def check_automated_decision_review(decision: ContentModerationDecision) -> Tuple[bool, ProofObject]:
    """DSA Article 22: Significant automated decisions require human review.

    Falsifies if: decision is automated, significant, and lacks human_reviewed oversight.
    falsifies_if: decision is automated, significant, and lacks human_reviewed oversight.
    """
    significant_actions = ["removal", "suspension", "demonetization"]
    is_significant = any(a in decision.action_taken.lower() for a in significant_actions)
    
    if decision.automated and is_significant and not decision.human_reviewed:
        return False, ProofObject(
            conclusion="VIOLATION: Significant automated decision lacks human review",
            premises=[
                f"Action: {decision.action_taken}",
                f"Automated: {decision.automated}",
                f"Human reviewed: {decision.human_reviewed}"
            ],
            rule="dsa_article_22_human_review"
        )
    
    return True, ProofObject(
        conclusion="Automated decision meets human review requirements",
        premises=[
            f"Automated: {decision.automated}",
            f"Human reviewed: {decision.human_reviewed}"
        ],
        rule="dsa_article_22_compliant"
    )
