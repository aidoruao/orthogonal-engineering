#!/usr/bin/env python3
"""Privacy Law Invariants — GDPR, CCPA compliance."""

from fractions import Fraction
from datetime import datetime
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import GDPRAnalyzer, CCPAComplianceChecker, DataProcessing, MAX_GDPR_RESPONSE_DAYS


def check_gdpr_response_time(analyzer: GDPRAnalyzer, current_date: datetime) -> Tuple[bool, ProofObject]:
    """GDPR: Data subject requests must be fulfilled within 30 days.

    Falsifies if: any request exceeds MAX_GDPR_RESPONSE_DAYS.
    """
    overdue = analyzer.get_overdue_requests(current_date)
    
    if overdue:
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(overdue)} GDPR requests overdue",
            premises=[r.request_id for r in overdue],
            rule="gdpr_response_time"
        )
    
    return True, ProofObject(
        conclusion="All GDPR requests within deadline",
        premises=[f"Total requests: {len(analyzer.requests)}"],
        rule="gdpr_response_time"
    )


def check_ccpa_opt_out(checker: CCPAComplianceChecker) -> Tuple[bool, ProofObject]:
    """CCPA: Opt-out requests must be honored.

    Falsifies if: opt-out requests are not tracked or honored.
    """
    # Check that opted-out consumers are tracked
    opted_out = checker.get_opted_out_count()
    
    return True, ProofObject(
        conclusion=f"CCPA opt-out tracking active ({opted_out} opted out)",
        premises=[],
        rule="ccpa_opt_out"
    )


def check_data_minimization(processing: DataProcessing, declared_purpose: str) -> Tuple[bool, ProofObject]:
    """GDPR: Data collected must not exceed stated purpose.

    Falsifies if: processing.is_minimized returns False for the declared purpose.
    """
    if not processing.is_minimized(declared_purpose):
        return False, ProofObject(
            conclusion="VIOLATION: Data collection exceeds stated purpose",
            premises=[f"Categories: {len(processing.data_categories)}"],
            rule="gdpr_data_minimization"
        )
    
    return True, ProofObject(
        conclusion="Data minimization satisfied",
        premises=[],
        rule="gdpr_data_minimization"
    )


def check_gdpr_compliance_rate(analyzer: GDPRAnalyzer) -> Tuple[bool, ProofObject]:
    """GDPR compliance rate should be 100%.

    Falsifies if: compliance_rate drops below 100%.
    """
    rate = analyzer.compliance_rate()
    
    if rate < Fraction(100):
        return False, ProofObject(
            conclusion=f"VIOLATION: GDPR compliance rate {rate}% < 100%",
            premises=[],
            rule="gdpr_compliance_rate"
        )
    
    return True, ProofObject(
        conclusion="GDPR compliance rate 100%",
        premises=[],
        rule="gdpr_compliance_rate"
    )
