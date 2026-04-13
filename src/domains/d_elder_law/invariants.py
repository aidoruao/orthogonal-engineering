"""D_ELDER_LAW invariants — Yeshua Standard. 0 floats.

Standards:
- Medicare Act (42 U.S.C. §1395) — Parts A, B, D
- Medicaid Act (42 U.S.C. §1396) — long-term care
- Elder Justice Act (42 U.S.C. §1397j) — abuse reporting
- OBRA 1987 — nursing home reform (42 CFR Part 483)
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import Senior, LongTermCareFacility, ElderAbuseReport


def check_medicare_part_b_enrollment(senior: Senior) -> Tuple[bool, ProofObject]:
    """If senior needs preventive care, they should be Part B enrolled.

    Standard: 42 U.S.C. §1395j — Medicare Part B eligibility
    falsifies_if: senior.medicare_enrolled is True but medicare_part_b_enrolled is False
                  and senior needs preventive services.
    """
    if senior.medicare_enrolled:
        ok = senior.medicare_part_b_enrolled
    else:
        ok = True
    premises = [
        f"senior_id={senior.senior_id}",
        f"medicare_enrolled={senior.medicare_enrolled}",
        f"part_b_enrolled={senior.medicare_part_b_enrolled}",
    ]
    return ok, ProofObject(
        rule="MedicarePartBEnrollment",
        premises=premises,
        conclusion="PASS: Medicare enrollment consistent" if ok else "VIOLATION: Medicare A enrolled but not Part B",
    )


def check_monthly_income_nonneg(senior: Senior) -> Tuple[bool, ProofObject]:
    """Monthly income must be >= 0.

    Standard: Medicaid income eligibility — 42 CFR Part 435
    falsifies_if: senior.monthly_income < 0.
    """
    ok = senior.monthly_income >= Fraction(0)
    premises = [
        f"senior_id={senior.senior_id}",
        f"monthly_income={senior.monthly_income}",
    ]
    return ok, ProofObject(
        rule="MonthlyIncomeNonNeg",
        premises=premises,
        conclusion=f"PASS: income {senior.monthly_income}" if ok else "VIOLATION: negative monthly income",
    )


def check_facility_abuse_complaint_ratio(facility: LongTermCareFacility) -> Tuple[bool, ProofObject]:
    """Substantiated abuse complaints must be < 10% of total complaints.

    Standard: OBRA 1987 42 CFR §483.12 — abuse prohibition
    falsifies_if: substantiated_abuse_complaints / total_complaints >= Fraction(1, 10) when complaints > 0.
    """
    if facility.total_complaints == 0:
        ok = True
        ratio = Fraction(0)
    else:
        ratio = Fraction(facility.substantiated_abuse_complaints, facility.total_complaints)
        ok = ratio < Fraction(1, 10)
    premises = [
        f"facility_id={facility.facility_id}",
        f"substantiated={facility.substantiated_abuse_complaints}",
        f"total={facility.total_complaints}",
        f"ratio={ratio}",
        f"max_ratio={Fraction(1, 10)}",
    ]
    return ok, ProofObject(
        rule="FacilityAbuseComplaintRatio",
        premises=premises,
        conclusion=f"PASS: abuse ratio {ratio} < 1/10" if ok else f"VIOLATION: abuse ratio {ratio} >= 1/10",
    )


def check_countable_assets_nonneg(senior: Senior) -> Tuple[bool, ProofObject]:
    """Countable assets for Medicaid must be >= 0.

    Standard: Medicaid asset counting — 42 CFR §435.601
    falsifies_if: senior.countable_assets < 0.
    """
    ok = senior.countable_assets >= Fraction(0)
    premises = [
        f"senior_id={senior.senior_id}",
        f"countable_assets={senior.countable_assets}",
    ]
    return ok, ProofObject(
        rule="CountableAssetsNonNeg",
        premises=premises,
        conclusion=f"PASS: assets {senior.countable_assets}" if ok else "VIOLATION: negative countable assets",
    )


def check_nursing_facility_care_need(senior: Senior) -> Tuple[bool, ProofObject]:
    """If Medicaid-enrolled and needs nursing facility care, must be enrolled.

    Standard: 42 U.S.C. §1396a(a)(10)(A) — mandatory coverage
    falsifies_if: needs_nursing_facility_care is True and medicaid_enrolled is False
                  (Medicaid should cover nursing facility for eligible seniors).
    """
    if senior.needs_nursing_facility_care:
        ok = senior.medicaid_enrolled
    else:
        ok = True
    premises = [
        f"senior_id={senior.senior_id}",
        f"needs_nursing_facility_care={senior.needs_nursing_facility_care}",
        f"medicaid_enrolled={senior.medicaid_enrolled}",
    ]
    return ok, ProofObject(
        rule="NursingFacilityCareNeed",
        premises=premises,
        conclusion="PASS: nursing care coverage consistent" if ok else "VIOLATION: needs nursing care but not Medicaid enrolled",
    )


def check_facility_type_valid(facility: LongTermCareFacility) -> Tuple[bool, ProofObject]:
    """Facility type must be one of: nursing_home, assisted_living, memory_care.

    Standard: CMS certification — 42 CFR Part 483
    falsifies_if: facility.facility_type not in allowed set.
    """
    allowed = {"nursing_home", "assisted_living", "memory_care"}
    ok = facility.facility_type in allowed
    premises = [
        f"facility_id={facility.facility_id}",
        f"facility_type={facility.facility_type!r}",
        f"allowed={sorted(allowed)}",
    ]
    return ok, ProofObject(
        rule="FacilityTypeValid",
        premises=premises,
        conclusion=f"PASS: facility type valid" if ok else f"VIOLATION: unknown facility type {facility.facility_type!r}",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS

    Falsifies if: any check returns FAIL (nominal inputs should always pass).."""
    from datetime import datetime
    senior = Senior(
        senior_id="S001", name="Jane Doe",
        date_of_birth=datetime(1945, 1, 1),
        medicare_enrolled=True, medicare_part_b_enrolled=True,
        medicaid_enrolled=True, monthly_income=Fraction(1500),
        countable_assets=Fraction(2000),
        needs_nursing_facility_care=True, needs_in_home_care=False,
    )
    facility = LongTermCareFacility(
        facility_id="F001", name="Sunrise Care",
        facility_type="nursing_home",
        substantiated_abuse_complaints=0, total_complaints=5,
    )
    from .implementation import ElderAbuseReport
    results = {}
    for fn, args in [
        (check_medicare_part_b_enrollment, (senior,)),
        (check_monthly_income_nonneg, (senior,)),
        (check_facility_abuse_complaint_ratio, (facility,)),
        (check_countable_assets_nonneg, (senior,)),
        (check_nursing_facility_care_need, (senior,)),
        (check_facility_type_valid, (facility,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
