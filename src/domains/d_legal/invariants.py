"""D_LEGAL Invariants — Court Timeliness, Access to Justice, Case Management

Verifies Speedy Trial Act compliance, civil case time standards,
court clearance rates, access to justice metrics.

Standards: 18 U.S.C. § 3161 (Speedy Trial Act), ABA Standards, Federal Rules
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import CourtCase, Court, CaseType, CaseStatus, speedy_trial_limit, civil_case_target


def check_speedy_trial_compliance(case: CourtCase, days_pending: int) -> Tuple[bool, ProofObject]:
    """
    Speedy Trial Act requires timely criminal trials.
    
    18 U.S.C. § 3161(c)(1):
    - Trial must commence within 70 days of indictment
    - Excludable delays defined
    - Sanction: dismissal of charges
    
    Falsifies if: criminal case > 70 days without trial
    falsifies_if: criminal case > 70 days without trial
    """
    if case.case_type != CaseType.CRIMINAL:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} is civil — Speedy Trial Act N/A",
            premises=[f"Type: {case.case_type.name}"],
            rule="speedy_trial_exemption"
        )
    
    limit = speedy_trial_limit()
    
    if days_pending > limit and case.status != CaseStatus.CLOSED:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} criminal trial not commenced within {days_pending} days (limit {limit})",
            premises=[
                f"Days pending: {days_pending}",
                f"Limit: {limit}",
                f"Status: {case.status.name}",
                "18 U.S.C. § 3161 — Speedy Trial Act"
            ],
            rule="speedy_trial_act"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} Speedy Trial Act compliance",
        premises=[f"Days: {days_pending}", f"Limit: {limit}"],
        rule="speedy_trial_act"
    )


def check_civil_case_timeliness(case: CourtCase, months_pending: int) -> Tuple[bool, ProofObject]:
    """
    Civil cases should be resolved within reasonable time.
    
    ABA Standards:
    - 12 months for civil cases target
    - 24 months maximum for complex
    - Age of pending cases monitored
    
    Falsifies if: civil case > 24 months pending
    falsifies_if: civil case > 24 months pending
    """
    if case.case_type != CaseType.CIVIL:
        return True, ProofObject(
            conclusion=f"Case {case.case_id} not civil — timeliness N/A",
            premises=[f"Type: {case.case_type.name}"],
            rule="civil_timeliness_exemption"
        )
    
    max_months = Fraction(24)  # 24 months
    
    if months_pending > max_months and case.status != CaseStatus.CLOSED:
        return False, ProofObject(
            conclusion=f"VIOLATION: Case {case.case_id} civil case pending {months_pending} months exceeds {max_months} month standard",
            premises=[
                f"Months pending: {months_pending}",
                f"Max: {max_months}",
                "ABA Standards — Civil case timeliness"
            ],
            rule="civil_case_timeliness"
        )
    
    return True, ProofObject(
        conclusion=f"Case {case.case_id} civil timeliness acceptable",
        premises=[f"Months: {months_pending}"],
        rule="civil_case_timeliness"
    )


def check_court_clearance_rate(court: Court) -> Tuple[bool, ProofObject]:
    """
    Courts should resolve at least as many cases as filed.
    
    Case clearance standard:
    - 100%+ = reducing backlog
    - <95% = backlog growing
    - Resource allocation indicator
    
    Falsifies if: clearance rate < 95%
    falsifies_if: clearance rate < 95%
    """
    min_clearance = Fraction(95, 100)
    rate = court.get_clearance_rate()
    
    if rate < min_clearance:
        return False, ProofObject(
            conclusion=f"VIOLATION: Court {court.court_name} clearance rate {rate} below {min_clearance}",
            premises=[
                f"Resolved: {court.cases_resolved_annual}",
                f"Filed: {court.cases_filed_annual}",
                f"Rate: {rate}",
                "Court administration — Clearance rate"
            ],
            rule="court_clearance_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Court {court.court_name} clearance rate acceptable",
        premises=[f"Rate: {rate}"],
        rule="court_clearance_rate"
    )


def check_access_to_justice(court: Court) -> Tuple[bool, ProofObject]:
    """
    Courts must provide meaningful access to justice.
    
    Access requirements:
    - E-filing for remote access
    - Interpreter services for LEP parties
    - Self-help for pro se litigants
    
    Falsifies if: no access services
    falsifies_if: no access services
    """
    if not court.interpreter_services:
        return False, ProofObject(
            conclusion=f"VIOLATION: Court {court.court_name} lacks interpreter services",
            premises=[
                f"Interpreter: {court.interpreter_services}",
                "Title VI — Language access required"
            ],
            rule="access_to_justice"
        )
    
    if not court.self_help_center:
        return False, ProofObject(
            conclusion=f"VIOLATION: Court {court.court_name} lacks self-help center",
            premises=[
                f"Self-help: {court.self_help_center}",
                "Access to justice — Pro se assistance"
            ],
            rule="access_to_justice"
        )
    
    return True, ProofObject(
        conclusion=f"Court {court.court_name} access to justice services verified",
        premises=[
            f"E-filing: {court.e_filing_available}",
            f"Interpreter: {court.interpreter_services}"
        ],
        rule="access_to_justice"
    )


def check_case_backlog(court: Court) -> Tuple[bool, ProofObject]:
    """
    Courts should not accumulate excessive backlog.
    
    Backlog indicators:
    - Cases pending > 12 months
    - Cases pending > 24 months (critical)
    - Backlog ratio to annual filings
    
    Falsifies if: >5% of cases > 24 months old
    falsifies_if: >5% of cases > 24 months old
    """
    if court.cases_pending == 0:
        return True, ProofObject(
            conclusion=f"Court {court.court_name} no pending cases",
            premises=["Pending: 0"],
            rule="case_backlog"
        )
    
    old_case_ratio = Fraction(court.cases_over_24_months, court.cases_pending)
    max_ratio = Fraction(5, 100)  # 5%
    
    if old_case_ratio > max_ratio:
        return False, ProofObject(
            conclusion=f"VIOLATION: Court {court.court_name} has {old_case_ratio} cases > 24 months (max {max_ratio})",
            premises=[
                f">24 months: {court.cases_over_24_months}",
                f"Total pending: {court.cases_pending}",
                f"Ratio: {old_case_ratio}",
                "Case management — Backlog control"
            ],
            rule="case_backlog"
        )
    
    return True, ProofObject(
        conclusion=f"Court {court.court_name} backlog within limits",
        premises=[f">24 months ratio: {old_case_ratio}"],
        rule="case_backlog"
    )
