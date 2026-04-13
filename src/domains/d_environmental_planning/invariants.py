#!/usr/bin/env python3
"""Environmental Planning Invariants — NEPA, CEQA."""

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

    Falsifies if: any impact score is outside [0, 100].
    falsifies_if: any impact score is outside [0, 100].
    """
    for score in eis.impact_scores:
        if score.score < Fraction(0) or score.score > Fraction(100):
            return False, ProofObject(
                conclusion=f"VIOLATION: Impact score {score.score} out of bounds",
                premises=[],
                rule="impact_score_bounds"
            )
    
    return True, ProofObject(
        conclusion=f"All {len(eis.impact_scores)} impact scores within bounds",
        premises=[],
        rule="impact_score_bounds"
    )


def check_comment_period_duration(period: CommentPeriod) -> Tuple[bool, ProofObject]:
    """NEPA: Minimum 30-day comment period required.

    Falsifies if: period.is_adequate() is False.
    falsifies_if: period.is_adequate() is False.
    """
    if not period.is_adequate():
        return False, ProofObject(
            conclusion=f"VIOLATION: Comment period {period.days_duration} days < {period.MINIMUM_COMMENT_DAYS}",
            premises=[],
            rule="nepa_comment_period"
        )
    
    return True, ProofObject(
        conclusion=f"Comment period adequate ({period.days_duration} days)",
        premises=[],
        rule="nepa_comment_period"
    )


def check_mitigation_completeness(tracker: MitigationTracker) -> Tuple[bool, ProofObject]:
    """All required mitigation measures must be implemented.

    Falsifies if: tracker.is_complete() is False.
    falsifies_if: tracker.is_complete() is False.
    """
    if not tracker.is_complete():
        missing = set(tracker.required_measures) - set(tracker.implemented_measures)
        return False, ProofObject(
            conclusion=f"VIOLATION: {len(missing)} mitigation measures not implemented",
            premises=list(missing),
            rule="mitigation_completeness"
        )
    
    return True, ProofObject(
        conclusion="All mitigation measures implemented",
        premises=[f"Completed: {len(tracker.implemented_measures)}"],
        rule="mitigation_completeness"
    )


def run_all_invariants() -> dict:
    """Run all D_ENVIRONMENTAL_PLANNING invariants with nominal sample data.

    falsifies_if: any invariant fails or raises an exception.
    """
    comment_period = CommentPeriod(
        start_date="SAMPLE",
        end_date="SAMPLE",
        days_duration=1,
    )
    environmental_impact_statement = EnvironmentalImpactStatement(
        project_id="ENVIRONM-001",
        impact_scores=[ImpactScore(
        category=ImpactCategory.AIR,
        score=Fraction(100),
    )],
    )
    mitigation_tracker = MitigationTracker(
        required_measures=["SAMPLE"],
        implemented_measures=["SAMPLE"],
    )

    checks = [
        ("check_comment_period_duration", lambda: check_comment_period_duration(comment_period)),
        ("check_impact_score_bounded", lambda: check_impact_score_bounded(environmental_impact_statement)),
        ("check_mitigation_completeness", lambda: check_mitigation_completeness(mitigation_tracker)),
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
    print("All D_ENVIRONMENTAL_PLANNING invariants: PASS")
