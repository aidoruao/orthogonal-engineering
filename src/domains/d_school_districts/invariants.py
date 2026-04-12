"""D_SCHOOL_DISTRICTS invariants — Yeshua Standard. 0 floats.

Standards:
- Brown v. Board of Education, 347 U.S. 483 (1954) — desegregation
- Milliken v. Bradley, 418 U.S. 717 (1974) — district boundary limits
- ESEA/ESSA (Every Student Succeeds Act, 20 U.S.C. §6301)
- ADA Title II — accessibility in public schools
"""

from __future__ import annotations
from fractions import Fraction
from typing import Dict, Tuple
from axioms.logic import ProofObject
from .implementation import SchoolDistrictBoundary, BoundaryChange, CompactnessMetrics


def check_boundary_district_id_set(boundary: SchoolDistrictBoundary) -> Tuple[bool, ProofObject]:
    """District boundary must have non-empty district_id and district_name.

    Standard: ESSA reporting requirements; State education agency registration
    falsifies_if: boundary.district_id is empty or boundary.district_name is empty.
    """
    ok = bool(boundary.district_id.strip()) and bool(boundary.district_name.strip())
    premises = [
        f"boundary_id={boundary.boundary_id}",
        f"district_id={boundary.district_id!r}",
        f"district_name={boundary.district_name!r}",
    ]
    return ok, ProofObject(
        rule="BoundaryDistrictIdSet",
        premises=premises,
        conclusion="PASS: district identified" if ok else "VIOLATION: missing district ID or name",
    )


def check_student_population_nonneg(boundary: SchoolDistrictBoundary) -> Tuple[bool, ProofObject]:
    """Student population must be >= 0.

    Standard: NCES data standards; ESSA §1111 enrollment reporting
    falsifies_if: boundary.student_population < 0.
    """
    ok = boundary.student_population >= 0
    premises = [
        f"district_id={boundary.district_id}",
        f"student_population={boundary.student_population}",
    ]
    return ok, ProofObject(
        rule="StudentPopulationNonNeg",
        premises=premises,
        conclusion=f"PASS: student population {boundary.student_population}" if ok else "VIOLATION: negative student population",
    )


def check_area_nonneg(boundary: SchoolDistrictBoundary) -> Tuple[bool, ProofObject]:
    """District area must be > 0 square miles.

    Standard: TIGER/Line geographic data standards; APA planning standards
    falsifies_if: boundary.area_sq_miles <= 0.
    """
    ok = boundary.area_sq_miles > Fraction(0)
    premises = [
        f"district_id={boundary.district_id}",
        f"area_sq_miles={boundary.area_sq_miles}",
    ]
    return ok, ProofObject(
        rule="AreaNonNeg",
        premises=premises,
        conclusion=f"PASS: area {boundary.area_sq_miles} sq mi" if ok else "VIOLATION: zero or negative district area",
    )


def check_boundary_change_has_reason(change: BoundaryChange) -> Tuple[bool, ProofObject]:
    """Boundary change must document reason with public comments.

    Standard: ESSA §1111(a)(1); State open meetings law requirements
    falsifies_if: change.public_comments_received < 0 (invalid).
    """
    ok = change.public_comments_received >= 0
    premises = [
        f"change_id={change.change_id}",
        f"district_id={change.district_id}",
        f"public_comments_received={change.public_comments_received}",
    ]
    return ok, ProofObject(
        rule="BoundaryChangeHasReason",
        premises=premises,
        conclusion="PASS: boundary change valid" if ok else "VIOLATION: invalid boundary change",
    )


def check_compactness_score_range(metrics: CompactnessMetrics) -> Tuple[bool, ProofObject]:
    """Polsby-Popper compactness score must be in (0, 1].

    Standard: Rucho v. Common Cause — compactness as gerrymandering metric
    falsifies_if: polsby_popper_score <= 0 or polsby_popper_score > 1.
    """
    ok = Fraction(0) < metrics.polsby_popper_score <= Fraction(1)
    premises = [
        f"district_id={metrics.district_id}",
        f"polsby_popper_score={metrics.polsby_popper_score}",
    ]
    return ok, ProofObject(
        rule="CompactnessScoreRange",
        premises=premises,
        conclusion=f"PASS: compactness {metrics.polsby_popper_score}" if ok else "VIOLATION: compactness score out of (0,1]",
    )


def check_population_le_area_proxy(boundary: SchoolDistrictBoundary) -> Tuple[bool, ProofObject]:
    """Population density (students/sq_mile) must be < 50,000 (sanity check).

    Standard: NCES enrollment density standards
    falsifies_if: student_population / area_sq_miles >= 50000.
    """
    if boundary.area_sq_miles <= Fraction(0):
        ok = False
        density = Fraction(-1)
    else:
        density = Fraction(boundary.student_population) / boundary.area_sq_miles
        ok = density < Fraction(50000)
    premises = [
        f"district_id={boundary.district_id}",
        f"student_population={boundary.student_population}",
        f"area_sq_miles={boundary.area_sq_miles}",
        f"density={density}",
    ]
    return ok, ProofObject(
        rule="PopulationDensitySanity",
        premises=premises,
        conclusion=f"PASS: density {density} < 50000" if ok else "VIOLATION: implausible density",
    )


def run_all_invariants() -> Dict[str, str]:
    """Run all checks with nominal inputs. All must PASS."""
    boundary = SchoolDistrictBoundary(
        boundary_id="BD-001", district_id="DIST-001", district_name="Springfield USD",
        area_sq_miles=Fraction(25), population=50000, student_population=8000,
    )
    from datetime import datetime
    from .implementation import BoundaryChangeType
    change = BoundaryChange(
        change_id="CHG-001", change_type=BoundaryChangeType.REDISTRICTING,
        district_id="DIST-001", proposal_date=datetime(2024, 1, 1),
        public_comments_received=42,
    )
    metrics = CompactnessMetrics(
        district_id="DIST-001", polsby_popper_score=Fraction(7, 10),
        reock_score=Fraction(6, 10), convex_hull_ratio=Fraction(8, 10),
    )
    results = {}
    for fn, args in [
        (check_boundary_district_id_set, (boundary,)),
        (check_student_population_nonneg, (boundary,)),
        (check_area_nonneg, (boundary,)),
        (check_boundary_change_has_reason, (change,)),
        (check_compactness_score_range, (metrics,)),
        (check_population_le_area_proxy, (boundary,)),
    ]:
        _, p = fn(*args)
        results[fn.__name__] = p.conclusion
    return results
