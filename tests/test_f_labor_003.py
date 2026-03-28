"""
Falsification test wrapper for F_LABOR_003.

Tests the invariant: No work occurs outside compensated hours (off-the-clock work prohibited).

Falsifying observation: Off-the-clock work is documented or admitted.
"""
# @falsification_id: F_LABOR_003

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.labor.automated_documentation import WageTheftDocumentationEngine


def test_f_labor_003():
    """
    F_LABOR_003: Off-the-clock work is prohibited.

    Assumption: No employee performs compensable work outside compensated hours.
    This test verifies that the documentation engine correctly tracks
    compensation_status and that uncompensated work events are logged
    and flagged in the shift record.

    Falsifying observation: An off-the-clock work event is logged but
    the engine fails to record it as 'uncompensated'.
    """
    engine = WageTheftDocumentationEngine(institution="Test Institution")

    shift = engine.log_shift(
        shift_id="off-clock-001",
        date_str="2026-03-28",
        scheduled_hours=5.75,
        tasks=[{"name": "pre-shift-setup", "count": 1, "duration_hours": 0.5}],
        actual_start="07:00",
        actual_end="08:00",
        compensation_status="uncompensated",
        notes="Pre-shift setup — verbally authorized, not compensated",
    )

    assert shift.compensation_status == "uncompensated", (
        "F_LABOR_003 FAILED: Off-the-clock event must be logged as 'uncompensated'"
    )
    assert shift.gap_hours > 0 or shift.notes, (
        "F_LABOR_003 FAILED: Off-the-clock shift must have gap_hours > 0 or notes"
    )

    compensated_shift = engine.log_shift(
        shift_id="on-clock-001",
        date_str="2026-03-29",
        scheduled_hours=5.75,
        tasks=[{"name": "bathrooms", "count": 5, "duration_hours": 1.5}],
        compensation_status="compensated",
    )
    assert compensated_shift.compensation_status == "compensated", (
        "F_LABOR_003 FAILED: Compensated work must retain 'compensated' status"
    )

    all_shifts = [shift, compensated_shift]
    uncompensated = [s for s in all_shifts if s.compensation_status == "uncompensated"]
    assert len(uncompensated) == 1, (
        "F_LABOR_003 FAILED: Exactly one off-the-clock event must be identified"
    )
