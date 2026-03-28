"""
Falsification test wrapper for F_LABOR_004.

Tests the invariant: Workload is accountable across the full employment period.

Falsifying observation: Workload consistently exceeds scheduled hours across multiple periods.
"""
# @falsification_id: F_LABOR_004

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.labor.automated_documentation import (
    WORKLOAD_RATIO_TOLERANCE,
    WageTheftDocumentationEngine,
)
from core.labor.immune_system import InstitutionalImmuneSystem


def test_f_labor_004():
    """
    F_LABOR_004: Workload is accountable (longitudinal audit).

    Assumption: Workload is achievable in scheduled hours across the full employment period.
    This test verifies that the immune system detects a sustained frontloading
    pattern across multiple pay periods, not just individual shifts.

    Falsifying observation: Cumulative workload ratio > WORKLOAD_RATIO_TOLERANCE
    across 3+ consecutive periods, correctly flagged as systemic.
    """
    system = InstitutionalImmuneSystem(
        institution="Bay District Schools",
        location="Bay County, Florida",
        scheduled_hours_per_shift=5.75,
        regular_hourly_rate=15.0,
    )
    frontloaded_tasks = [
        {"name": "bathrooms", "count": 15, "duration_hours": 5.9},
        {"name": "trash", "count": 45, "duration_hours": 1.25},
        {"name": "hallways", "count": 6, "duration_hours": 0.77},
        {"name": "classrooms", "count": 15, "duration_hours": 1.5},
        {"name": "daily_variables", "count": 1, "duration_hours": 0.9},
    ]

    for day in range(15):
        system.log_shift(
            date_str=f"2026-01-{day + 1:02d}",
            tasks=frontloaded_tasks,
        )

    result = system.disrupt()

    assert result["violation_flag"] is True, (
        "F_LABOR_004 FAILED: 15-day frontloading pattern must be detected"
    )
    assert result["workload_ratio"] > WORKLOAD_RATIO_TOLERANCE, (
        f"F_LABOR_004 FAILED: Cumulative ratio {result['workload_ratio']:.3f} "
        f"must exceed tolerance {WORKLOAD_RATIO_TOLERANCE}"
    )
    assert result["gap_hours_total"] > 0, (
        "F_LABOR_004 FAILED: Cumulative gap hours must be positive"
    )
    assert result["shifts_analyzed"] == 15, (
        "F_LABOR_004 FAILED: All 15 logged shifts must be analyzed"
    )
    assert result["hash_chain_valid"] is True, (
        "F_LABOR_004 FAILED: Hash chain must be valid — retroactive tampering must be detectable"
    )
