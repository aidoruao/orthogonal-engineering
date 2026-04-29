"""
Falsification test suite for D_LABOR_RIGHTS domain.

Tests FLSA overtime calculation, pay period summaries, and frontloading detection.

# @falsification_id: F_LABOR_001, F_LABOR_002, F_LABOR_003
"""

import pytest
from fractions import Fraction

from src.domains.d_labor_rights.implementation import (
    FLSA_OVERTIME_MULTIPLIER,
    FLSA_WEEKLY_OVERTIME_THRESHOLD,
    STATUTE_REF_FLSA_207,
    WORKLOAD_RATIO_TOLERANCE,
    WeeklyPayResult,
    calculate_weekly_pay,
    compute_workload_ratio,
    detect_frontloading,
    summarize_pay_period,
)


# ---------------------------------------------------------------------------
# F_LABOR_001 — FLSA overtime calculation
# ---------------------------------------------------------------------------

def test_overtime_multiplier_is_three_halves():
    """FLSA overtime multiplier must be exactly 3/2."""
    # TODO: Expand test_overtime_multiplier_is_three_halves() - stub detected by Yeshua Agent
    assert FLSA_OVERTIME_MULTIPLIER == Fraction(3, 2)


def test_overtime_threshold_is_40():
    """FLSA weekly overtime threshold must be 40 hours."""
    # TODO: Expand test_overtime_threshold_is_40() - stub detected by Yeshua Agent
    assert FLSA_WEEKLY_OVERTIME_THRESHOLD == 40


def test_40_hours_no_overtime():
    """Exactly 40 hours must not trigger overtime."""
    result = calculate_weekly_pay(Fraction(40), 1500)
    assert result.overtime_triggered is False
    assert result.overtime_hours == Fraction(0)
    assert result.regular_hours == Fraction(40)


def test_41_hours_one_overtime_hour():
    """41 hours must produce exactly 1 overtime hour."""
    result = calculate_weekly_pay(Fraction(41), 1500)
    assert result.overtime_triggered is True
    assert result.overtime_hours == Fraction(1)
    assert result.regular_hours == Fraction(40)


def test_overtime_pay_is_exactly_1_5x():
    """1 OT hour at $15/hr must equal $22.50 (2250 cents)."""
    result = calculate_weekly_pay(Fraction(41), 1500)
    assert result.overtime_pay_cents == 2250
    assert result.regular_pay_cents == 40 * 1500


def test_no_hours_produces_zero_pay():
    """Zero hours must produce zero pay."""
    result = calculate_weekly_pay(Fraction(0), 1500)
    assert result.regular_pay_cents == 0
    assert result.overtime_pay_cents == 0
    assert result.total_pay_cents == 0
    assert result.overtime_triggered is False


def test_fractional_overtime_hours():
    """40.5 hours must produce 0.5 overtime hours."""
    result = calculate_weekly_pay(Fraction(81, 2), 2000)
    assert result.overtime_hours == Fraction(1, 2)
    expected_ot = int(Fraction(1, 2) * Fraction(2000) * Fraction(3, 2))
    assert result.overtime_pay_cents == expected_ot


def test_statute_ref_always_present():
    """Every result must include FLSA 29 U.S.C. § 207 in statute_refs."""
    for hours in [Fraction(20), Fraction(40), Fraction(50)]:
        result = calculate_weekly_pay(hours, 1500)
        assert STATUTE_REF_FLSA_207 in result.statute_refs


def test_negative_hours_raises():
    """Negative hours must raise ValueError."""
    with pytest.raises(ValueError):
        calculate_weekly_pay(Fraction(-1), 1500)


def test_zero_rate_raises():
    """Zero hourly rate must raise ValueError."""
    with pytest.raises(ValueError):
        calculate_weekly_pay(Fraction(40), 0)


def test_no_float_in_implementation():
    """Implementation must not use float() for monetary calculations."""
    import inspect
    source = inspect.getsource(calculate_weekly_pay)
    assert "float(" not in source


# ---------------------------------------------------------------------------
# Multi-week pay period
# ---------------------------------------------------------------------------

def test_multi_week_overtime_is_per_week():
    """Overtime is computed independently per week, not across pay period."""
    # Week 1: 50 hours (10 OT), Week 2: 30 hours (0 OT)
    weekly_hours = [Fraction(50), Fraction(30)]
    summary = summarize_pay_period(weekly_hours, hourly_rate_cents=1500)
    assert summary.weeks_with_overtime == 1
    assert summary.weeks == 2
    assert STATUTE_REF_FLSA_207 in summary.statute_refs


def test_empty_weeks_raises():
    """Empty weekly_hours must raise ValueError."""
    with pytest.raises(ValueError):
        summarize_pay_period([], hourly_rate_cents=1500)


# ---------------------------------------------------------------------------
# F_LABOR_002 — Frontloading detection
# ---------------------------------------------------------------------------

def test_frontloading_detected_when_task_exceeds_schedule():
    """Workload > scheduled hours must be detected as frontloading."""
    # TODO: Expand test_frontloading_detected_when_task_exceeds_schedule() - stub detected by Yeshua Agent
    assert detect_frontloading(Fraction(10), Fraction(8)) is True


def test_no_frontloading_when_task_fits():
    """Workload <= scheduled hours must not be flagged as frontloading."""
    assert detect_frontloading(Fraction(8), Fraction(8)) is False
    assert detect_frontloading(Fraction(6), Fraction(8)) is False


def test_workload_ratio_exact():
    """Workload ratio must be computed exactly as a Fraction."""
    ratio = compute_workload_ratio(Fraction(10), Fraction(8))
    assert ratio == Fraction(10, 8)
    assert ratio == Fraction(5, 4)


def test_zero_scheduled_hours_raises():
    """Zero scheduled hours must raise ValueError (division by zero)."""
    with pytest.raises(ValueError):
        compute_workload_ratio(Fraction(8), Fraction(0))
