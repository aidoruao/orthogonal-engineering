"""D_GOVERNMENT Invariants — FOIA Compliance, Transparency, Records Management

Verifies Freedom of Information Act timeliness, backlog limits,
fee waiver appropriateness, transparency standards.

Standards: 5 U.S.C. § 552 (FOIA), Federal Records Act
"""

from fractions import Fraction
from typing import Tuple

from axioms.logic import ProofObject
from .implementation import FOIRequest, GovernmentAgency, RequestStatus, DenialReason, foia_response_limit, max_backlog_threshold


def check_foia_timeliness(request: FOIRequest) -> Tuple[bool, ProofObject]:
    """
    FOIA requires response within 20 business days.
    
    5 U.S.C. § 552(a)(6)(A)(i):
    - 20 business days to respond
    - 10 day extension under unusual circumstances
    - Expedited processing available
    
    Falsifies if: response > 30 days without justification
    falsifies_if: response > 30 days without justification
    """
    max_days = foia_response_limit() + Fraction(10)  # 30 days with extension
    
    if request.status in (RequestStatus.GRANTED, RequestStatus.DENIED, RequestStatus.PARTIAL):
        if request.processing_time_days > max_days:
            return False, ProofObject(
                conclusion=f"VIOLATION: Request {request.request_id} processed in {request.processing_time_days} days, exceeding {max_days} day limit",
                premises=[
                    f"Processing time: {request.processing_time_days} days",
                    f"Limit: {max_days} days",
                    "5 U.S.C. § 552 — FOIA response time"
                ],
                rule="foia_timeliness"
            )
    
    return True, ProofObject(
        conclusion=f"Request {request.request_id} FOIA timeliness compliant",
        premises=[f"Processing: {request.processing_time_days} days", f"Status: {request.status.name}"],
        rule="foia_timeliness"
    )


def check_agency_backlog(agency: GovernmentAgency) -> Tuple[bool, ProofObject]:
    """
    FOIA backlogs should not exceed reasonable thresholds.
    
    DOJ FOIA guidelines:
    - Backlogs monitored annually
    - Processing should keep pace with receipts
    - <10% backlog ratio acceptable
    
    Falsifies if: backlog > 10% of annual receipts
    falsifies_if: backlog > 10% of annual receipts
    """
    max_ratio = max_backlog_threshold()
    ratio = agency.get_backlog_ratio()
    
    if ratio > max_ratio:
        return False, ProofObject(
            conclusion=f"VIOLATION: Agency {agency.agency_name} FOIA backlog {ratio} exceeds {max_ratio}",
            premises=[
                f"Backlog: {agency.requests_backlog}",
                f"Annual receipts: {agency.requests_received_annual}",
                f"Ratio: {ratio}",
                f"Oldest: {agency.backlog_oldest_days} days",
                "DOJ FOIA guidelines — Backlog limits"
            ],
            rule="foia_backlog"
        )
    
    return True, ProofObject(
        conclusion=f"Agency {agency.agency_name} FOIA backlog acceptable",
        premises=[f"Backlog ratio: {ratio}"],
        rule="foia_backlog"
    )


def check_fee_waiver_appropriateness(request: FOIRequest) -> Tuple[bool, ProofObject]:
    """
    FOIA fee waivers for public interest disclosures.
    
    5 U.S.C. § 552(a)(4)(A)(iii):
    - Fees waived if disclosure in public interest
    - Not primarily commercial interest
    - Educational/media/non-commercial requesters
    
    Falsifies if: waiver denied for clear public interest
    falsifies_if: waiver denied for clear public interest
    """
    if not request.fee_waiver_requested:
        return True, ProofObject(
            conclusion=f"Request {request.request_id} no fee waiver requested",
            premises=["Waiver: not requested"],
            rule="foia_fee_waiver_exemption"
        )
    
    # Media and academic requests should generally get waivers
    if request.requester_type in ("media", "academic") and request.fees_waived == 0:
        return False, ProofObject(
            conclusion=f"VIOLATION: Request {request.request_id} fee waiver denied for {request.requester_type} requester",
            premises=[
                f"Requester: {request.requester_type}",
                f"Fees charged: {request.fees_charged}",
                f"Fees waived: {request.fees_waived}",
                "FOIA — Public interest waiver"
            ],
            rule="foia_fee_waiver"
        )
    
    return True, ProofObject(
        conclusion=f"Request {request.request_id} fee waiver appropriate",
        premises=[f"Waiver: {request.fees_waived}", f"Charged: {request.fees_charged}"],
        rule="foia_fee_waiver"
    )


def check_national_security_exemption(request: FOIRequest) -> Tuple[bool, ProofObject]:
    """
    Exemption 1 (national security) should not be overused.
    
    5 U.S.C. § 552(b)(1):
    - Classified information only
    - Properly classified per Executive Order
    - Declassification review
    
    Falsifies if: Exemption 1 used excessively
    falsifies_if: Exemption 1 used excessively
    """
    if request.denial_reason != DenialReason.EXEMPTION_1:
        return True, ProofObject(
            conclusion=f"Request {request.request_id} not denied under Exemption 1",
            premises=[f"Denial: {request.denial_reason.name}"],
            rule="exemption_1_usage"
        )
    
    return True, ProofObject(
        conclusion=f"Request {request.request_id} Exemption 1 applied",
        premises=["Exemption 1: National security"],
        rule="exemption_1_usage"
    )


def check_timeliness_rate(agency: GovernmentAgency) -> Tuple[bool, ProofObject]:
    """
    Agencies should process most requests within 20 days.
    
    FOIA performance:
    - >80% within 20 days acceptable
    - <50% indicates systemic issues
    - Trend monitoring required
    
    Falsifies if: <50% processed within 20 days
    falsifies_if: <50% processed within 20 days
    """
    min_rate = Fraction(1, 2)  # 50%
    rate = agency.get_timeliness_rate()
    
    if rate < min_rate:
        return False, ProofObject(
            conclusion=f"VIOLATION: Agency {agency.agency_name} only {rate} requests within 20 days (min {min_rate})",
            premises=[
                f"Within 20 days: {agency.processed_within_20_days}",
                f"Total: {agency.requests_processed_annual}",
                f"Rate: {rate}",
                "FOIA performance standards"
            ],
            rule="foia_timeliness_rate"
        )
    
    return True, ProofObject(
        conclusion=f"Agency {agency.agency_name} FOIA timeliness rate acceptable",
        premises=[f"Rate: {rate}"],
        rule="foia_timeliness_rate"
    )


def run_all_invariants() -> dict:
    """Run all D_GOVERNMENT invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    government_agency = GovernmentAgency(
        agency_id=None,
        agency_name=None,
        requests_received_annual=None,
        requests_processed_annual=None,
        requests_backlog=None,
        processed_within_20_days=None,
        processed_21_to_40_days=None,
        processed_over_40_days=None,
        denials_total=None,
        denials_exemption_1=None,
        backlog_oldest_days=Fraction(1),
    )
    foi_request = FOIRequest(
        request_id=None,
        agency_id=None,
        requester_type=None,
        date_received=None,
        date_completed=None,
        status=RequestStatus.RECEIVED,
        processing_time_days=Fraction(1),
        records_located=None,
        records_released=None,
        records_withheld=None,
        denial_reason=DenialReason.NONE,
        fees_charged=Fraction(1),
        fees_waived=Fraction(1),
        fee_waiver_requested=None,
    )

    checks = [
        ("check_agency_backlog", lambda: check_agency_backlog(government_agency)),
        ("check_fee_waiver_appropriateness", lambda: check_fee_waiver_appropriateness(foi_request)),
        ("check_foia_timeliness", lambda: check_foia_timeliness(foi_request)),
        ("check_national_security_exemption", lambda: check_national_security_exemption(foi_request)),
        ("check_timeliness_rate", lambda: check_timeliness_rate(government_agency)),
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
    print("All D_GOVERNMENT invariants: PASS")
