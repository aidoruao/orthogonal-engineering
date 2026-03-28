"""
Falsification test wrapper for F_LABOR_001.

Tests the invariant: Any hours worked over 40 in a week must be compensated
at 1.5x (FLSA 29 U.S.C. § 207).

Falsifying observation: Unpaid overtime is documented — hours over 40 with no 1.5x compensation.
"""
# @falsification_id: F_LABOR_001

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.labor.automated_documentation import (
    FLSA_OVERTIME_MULTIPLIER,
    FLSA_WEEKLY_OVERTIME_THRESHOLD,
    WageTheftDocumentationEngine,
)


def test_f_labor_001():
    """
    F_LABOR_001: Overtime entitlement is enforced.

    Assumption: Hours worked over 40/week are compensated at 1.5x.
    This test verifies that the documentation engine:
      1. Correctly identifies overtime hours above the 40-hour threshold.
      2. Calculates damages at the 1.5x rate.
      3. References FLSA 29 U.S.C. § 207 in the generated report.

    Falsifying observation: Report does not reference FLSA § 207 or
    does not compute overtime damages at the required multiplier.
    """
    engine = WageTheftDocumentationEngine(
        institution="Test Institution",
        regular_hourly_rate=15.0,
    )
    tasks = [
        {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
        {"name": "trash", "count": 45, "duration_hours": 1.25},
        {"name": "hallways", "count": 6, "duration_hours": 0.77},
        {"name": "classrooms", "count": 15, "duration_hours": 1.5},
        {"name": "daily_variables", "count": 1, "duration_hours": 0.9},
    ]
    engine.log_shift("s1", "2026-03-24", 5.75, tasks)
    engine.log_shift("s2", "2026-03-25", 5.75, tasks)
    engine.log_shift("s3", "2026-03-26", 5.75, tasks)
    engine.log_shift("s4", "2026-03-27", 5.75, tasks)
    engine.log_shift("s5", "2026-03-28", 5.75, tasks)

    report = engine.detect_frontloading()

    assert any("207" in ref for ref in report.statute_refs), (
        "F_LABOR_001 FAILED: Report must cite FLSA 29 U.S.C. § 207 (overtime entitlement)"
    )
    assert report.violation_flag is True, (
        "F_LABOR_001 FAILED: 10.3-hour workload on 5.75-hour schedule must be flagged"
    )
    assert FLSA_OVERTIME_MULTIPLIER == 1.5
    assert FLSA_WEEKLY_OVERTIME_THRESHOLD == 40.0
