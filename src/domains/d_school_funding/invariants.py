"""D_SCHOOL_FUNDING invariants — Yeshua Standard. 0 floats.

Standards:
- ESSA Title I (20 U.S.C. §6311) — equitable funding
- San Antonio ISD v. Rodriguez, 411 U.S. 1 (1973) — property tax funding
- ESEA maintenance of effort requirements
- 34 CFR Part 300 — IDEA per-pupil expenditure
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import SchoolDistrict, PerPupilAllocation


def check_total_budget_positive(district: SchoolDistrict) -> Tuple[bool, ProofObject]:
    """Total budget must be > 0.

    Standard: ESSA §8101 — fiscal accountability
    falsifies_if: district.total_budget <= 0.
    """
    ok = district.total_budget > Fraction(0)
    premises = [
        f"district_id={district.district_id}",
        f"total_budget={district.total_budget}",
    ]
    return ok, ProofObject(
        rule="TotalBudgetPositive",
        premises=premises,
        conclusion=f"PASS: budget {district.total_budget}" if ok else "VIOLATION: zero or negative budget",
    )


def check_enrollment_positive(district: SchoolDistrict) -> Tuple[bool, ProofObject]:
    """Total enrollment must be >= 1.

    Standard: NCES enrollment accounting standards
    falsifies_if: district.total_enrollment < 1.
    """
    ok = district.total_enrollment >= 1
    premises = [
        f"district_id={district.district_id}",
        f"total_enrollment={district.total_enrollment}",
    ]
    return ok, ProofObject(
        rule="EnrollmentPositive",
        premises=premises,
        conclusion=f"PASS: enrollment {district.total_enrollment}" if ok else "VIOLATION: enrollment < 1",
    )


def check_funding_sources_sum(district: SchoolDistrict) -> Tuple[bool, ProofObject]:
    """local + state + federal funding must be <= total_budget (cannot exceed total).

    Standard: EDGAR 34 CFR Part 76 — combined funding accountability
    falsifies_if: local_tax_revenue + state_aid + federal_aid > total_budget.
    """
    combined = district.local_tax_revenue + district.state_aid + district.federal_aid
    ok = combined <= district.total_budget
    premises = [
        f"district_id={district.district_id}",
        f"combined={combined}",
        f"total_budget={district.total_budget}",
    ]
    return ok, ProofObject(
        rule="FundingSourcesSum",
        premises=premises,
        conclusion=f"PASS: combined {combined} <= budget {district.total_budget}" if ok else f"VIOLATION: funding sources {combined} > budget {district.total_budget}",
    )


def check_per_pupil_allocation_positive(alloc: PerPupilAllocation) -> Tuple[bool, ProofObject]:
    """Per-pupil base allocation must be > 0.

    Standard: ESSA §1111(h)(1)(C)(viii) — per-pupil expenditure reporting
    falsifies_if: alloc.base_amount <= 0.
    """
    ok = alloc.base_amount > Fraction(0)
    premises = [
        f"district_id={alloc.district_id}",
        f"base_amount={alloc.base_amount}",
    ]
    return ok, ProofObject(
        rule="PerPupilAllocationPositive",
        premises=premises,
        conclusion=f"PASS: base allocation {alloc.base_amount}" if ok else "VIOLATION: zero or negative per-pupil allocation",
    )


def check_poverty_rate_range(district: SchoolDistrict) -> Tuple[bool, ProofObject]:
    """Poverty rate must be in [0, 1].

    Standard: Census Bureau poverty rate definition; ESSA Title I eligibility
    falsifies_if: poverty_rate < 0 or poverty_rate > 1.
    """
    ok = Fraction(0) <= district.poverty_rate <= Fraction(1)
    premises = [
        f"district_id={district.district_id}",
        f"poverty_rate={district.poverty_rate}",
    ]
    return ok, ProofObject(
        rule="PovertyRateRange",
        premises=premises,
        conclusion=f"PASS: poverty rate {district.poverty_rate}" if ok else "VIOLATION: poverty rate out of [0,1]",
    )


def check_title_i_eligibility_poverty(district: SchoolDistrict) -> Tuple[bool, ProofObject]:
    """Title I eligible districts must have poverty_rate >= Fraction(1, 10).

    Standard: ESSA §1113 — Title I school selection (poverty threshold ~10%)
    falsifies_if: title_i_eligible is True but poverty_rate < Fraction(1, 10).
    """
    min_poverty = Fraction(1, 10)
    if district.title_i_eligible:
        ok = district.poverty_rate >= min_poverty
    else:
        ok = True
    premises = [
        f"district_id={district.district_id}",
        f"title_i_eligible={district.title_i_eligible}",
        f"poverty_rate={district.poverty_rate}",
        f"min_required={min_poverty}",
    ]
    return ok, ProofObject(
        rule="TitleIEligibilityPoverty",
        premises=premises,
        conclusion="PASS: Title I eligibility consistent with poverty rate" if ok else f"VIOLATION: Title I eligible but poverty rate {district.poverty_rate} < {min_poverty}",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    district = SchoolDistrict(
        district_id="DIST-001", name="Springfield USD", state="IL",
        total_enrollment=5000, total_budget=Fraction(50_000_000),
        local_tax_revenue=Fraction(20_000_000), state_aid=Fraction(25_000_000),
        federal_aid=Fraction(4_000_000), poverty_rate=Fraction(15, 100),
        title_i_eligible=True,
    )
    alloc = PerPupilAllocation(
        district_id="DIST-001", fiscal_year=2024,
        base_amount=Fraction(8000),
    )
    results = {}
    for fn, args in [
        (check_total_budget_positive, (district,)),
        (check_enrollment_positive, (district,)),
        (check_funding_sources_sum, (district,)),
        (check_per_pupil_allocation_positive, (alloc,)),
        (check_poverty_rate_range, (district,)),
        (check_title_i_eligibility_poverty, (district,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
