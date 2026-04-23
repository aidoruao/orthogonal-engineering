#!/usr/bin/env python3
"""Environmental Planning Invariants — NEPA, CEQA.

42 U.S.C. § 4332(2)(C) (NEPA); CEQA Guidelines § 15000;
Sierra Club v. U.S. Army Corps of Engineers, 701 F.3d 120 (5th Cir. 2012).
"""

from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject
from .implementation import (
    CommentPeriod,
    EnvironmentalImpactStatement,
    ImpactScore,
    MitigationTracker,
    ImpactCategory,
)


def check_impact_score_bounded(eis: EnvironmentalImpactStatement) -> Tuple[bool, ProofObject]:
    """Impact scores must be on 0-100 scale.

    Falsifies if: any normalized_score < 0 or > 1.
    falsifies_if: any normalized_score < 0 or > 1.
    """
    for score in eis.impact_scores:
        norm = score.normalized_score()
        if norm < Fraction(0, 1) or norm > Fraction(1, 1):
            return False, ProofObject(
                conclusion=f"VIOLATION: Impact score {score.score} out of bounds",
                premises=[
                    f"Category: {score.category.name}",
                    f"Score: {score.score}",
                    f"Normalized: {norm}",
                ],
                rule="impact_score_bounds"
            )
    return True, ProofObject(
        conclusion=f"All {len(eis.impact_scores)} impact scores within bounds",
        premises=[f"Scores: {[s.score for s in eis.impact_scores]}"],
        rule="impact_score_bounds"
    )


def check_comment_period_duration(period: CommentPeriod) -> Tuple[bool, ProofObject]:
    """NEPA: Minimum 30-day comment period required.

    Falsifies if: adequacy_ratio < Fraction(1, 1).
    falsifies_if: adequacy_ratio < Fraction(1, 1).
    """
    ratio = period.adequacy_ratio()
    if ratio < Fraction(1, 1):
        return False, ProofObject(
            conclusion=f"VIOLATION: Comment period ratio {ratio} < 1",
            premises=[
                f"Days: {period.days_duration}",
                f"Minimum: {period.MINIMUM_COMMENT_DAYS}",
                f"Ratio: {ratio}",
            ],
            rule="nepa_comment_period"
        )
    return True, ProofObject(
        conclusion=f"Comment period adequate — ratio {ratio}",
        premises=[f"Ratio: {ratio}"],
        rule="nepa_comment_period"
    )


def check_mitigation_completeness(tracker: MitigationTracker) -> Tuple[bool, ProofObject]:
    """All required mitigation measures must be implemented.

    Falsifies if: completion_ratio < Fraction(1, 1).
    falsifies_if: completion_ratio < Fraction(1, 1).
    """
    ratio = tracker.completion_ratio()
    if ratio < Fraction(1, 1):
        missing = set(tracker.required_measures) - set(tracker.implemented_measures)
        return False, ProofObject(
            conclusion=f"VIOLATION: Mitigation completion ratio {ratio} < 1",
            premises=[
                f"Required: {len(tracker.required_measures)}",
                f"Implemented: {len(tracker.implemented_measures)}",
                f"Missing: {missing}",
            ],
            rule="mitigation_completeness"
        )
    return True, ProofObject(
        conclusion=f"All mitigation measures implemented — ratio {ratio}",
        premises=[f"Ratio: {ratio}"],
        rule="mitigation_completeness"
    )


def run_all_invariants() -> dict:
    """Run all D_ENVIRONMENTAL_PLANNING invariants with passing and failing test data.

    falsifies_if: any invariant fails or raises an exception.
    """
    # Passing data
    pass_period = CommentPeriod(
        start_date="2025-01-01",
        end_date="2025-02-15",
        days_duration=45,
    )
    pass_eis = EnvironmentalImpactStatement(
        project_id="ENV-001",
        impact_scores=[ImpactScore(
            category=ImpactCategory.AIR,
            score=Fraction(75),
        )],
    )
    pass_tracker = MitigationTracker(
        required_measures=["wetland_buffer", "noise_wall"],
        implemented_measures=["wetland_buffer", "noise_wall"],
    )

    # Failing data
    fail_period = CommentPeriod(
        start_date="2025-01-01",
        end_date="2025-01-10",
        days_duration=9,
    )
    fail_eis = EnvironmentalImpactStatement(
        project_id="ENV-002",
        impact_scores=[ImpactScore(
            category=ImpactCategory.WATER,
            score=Fraction(150),
        )],
    )
    fail_tracker = MitigationTracker(
        required_measures=["wetland_buffer", "noise_wall"],
        implemented_measures=["wetland_buffer"],
    )

    checks = [
        ("check_comment_period_duration_pass", lambda: check_comment_period_duration(pass_period)),
        ("check_comment_period_duration_fail", lambda: check_comment_period_duration(fail_period)),
        ("check_impact_score_bounded_pass", lambda: check_impact_score_bounded(pass_eis)),
        ("check_impact_score_bounded_fail", lambda: check_impact_score_bounded(fail_eis)),
        ("check_mitigation_completeness_pass", lambda: check_mitigation_completeness(pass_tracker)),
        ("check_mitigation_completeness_fail", lambda: check_mitigation_completeness(fail_tracker)),
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
        except Exception as exc:
            results[name] = "ERROR: " + str(exc)
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if not v.startswith("PASS")]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_ENVIRONMENTAL_PLANNING invariants: PASS")
