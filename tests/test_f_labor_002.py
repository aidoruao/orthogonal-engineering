"""
Falsification test wrapper for F_LABOR_002.

Tests the invariant: Assigned work fits within scheduled hours (frontloading is detectable).

Falsifying observation: Workload exceeds schedule without notice or compensation.
"""
# @falsification_id: F_LABOR_002

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.labor.automated_documentation import (
    WORKLOAD_RATIO_TOLERANCE,
    WageTheftDocumentationEngine,
)


def test_f_labor_002():
    """
    F_LABOR_002: Frontloading is detectable.

    Assumption: Assigned work fits within the employee's scheduled hours.
    This test verifies that the documentation engine detects frontloading
    by computing workload_ratio = task_hours / scheduled_hours and
    flagging any ratio exceeding the tolerance threshold.

    Falsifying observation: Engine does not detect frontloading when
    task_hours > scheduled_hours * WORKLOAD_RATIO_TOLERANCE.
    """
    engine = WageTheftDocumentationEngine(institution="Test Institution")
    frontloaded_tasks = [
        {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
        {"name": "trash", "count": 45, "duration_hours": 1.25},
        {"name": "hallways", "count": 6, "duration_hours": 0.77},
        {"name": "classrooms", "count": 15, "duration_hours": 1.5},
        {"name": "daily_variables", "count": 1, "duration_hours": 0.9},
    ]
    engine.log_shift("s1", "2026-03-28", 5.75, frontloaded_tasks)
    engine.log_shift("s2", "2026-03-29", 5.75, frontloaded_tasks)
    engine.log_shift("s3", "2026-03-30", 5.75, frontloaded_tasks)

    report = engine.detect_frontloading()

    assert report.workload_ratio > WORKLOAD_RATIO_TOLERANCE, (
        f"F_LABOR_002 FAILED: workload_ratio={report.workload_ratio:.3f} must exceed "
        f"tolerance={WORKLOAD_RATIO_TOLERANCE} for frontloaded schedule"
    )
    assert report.violation_flag is True, (
        "F_LABOR_002 FAILED: Frontloading must be detected when workload ratio > tolerance"
    )
    assert report.gap_hours_total > 0, (
        "F_LABOR_002 FAILED: Gap hours must be positive for frontloaded schedule"
    )

    compliant_tasks = [
        {"name": "bathrooms", "count": 3, "duration_hours": 0.75},
        {"name": "trash", "count": 10, "duration_hours": 0.3},
    ]
    engine2 = WageTheftDocumentationEngine(institution="Compliant Employer")
    engine2.log_shift("s1", "2026-03-28", 5.75, compliant_tasks)
    report2 = engine2.detect_frontloading()
    assert report2.violation_flag is False, (
        "F_LABOR_002 FAILED: Compliant schedule must not be flagged as frontloading"
    )
