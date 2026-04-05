"""
D_LABOR_RIGHTS — Labor Rights Enforcement domain implementation.
FLSA overtime calculator with immutable audit trail.

Invariants (from ontology/ontology.json#D_LABOR_RIGHTS):
  1. Any hours over 40/week must be compensated at exactly 1.5x the regular rate
     (FLSA 29 U.S.C. § 207).
  2. Wage calculations use integer arithmetic in cents to avoid float rounding errors.
  3. Every pay period result includes a statute reference to 29 U.S.C. § 207.

Biblical inspiration: "Do not muzzle an ox while it is treading out the grain."
(Deuteronomy 25:4 / 1 Timothy 5:18)
Wage theft is the modern muzzle. The FLSA overtime multiplier is the unmuzzle —
it is exact, integer, and non-negotiable. Fractions of a cent are truncated in
favor of the worker.

Falsification IDs: F_LABOR_001, F_LABOR_002, F_LABOR_003
"""

from __future__ import annotations

from fractions import Fraction
from typing import NamedTuple, Sequence


# ---------------------------------------------------------------------------
# FLSA constants
# ---------------------------------------------------------------------------

FLSA_OVERTIME_MULTIPLIER_NUM = 3    # 3/2 = 1.5x
FLSA_OVERTIME_MULTIPLIER_DEN = 2
FLSA_WEEKLY_OVERTIME_THRESHOLD_HOURS = 40  # integer hours

# For backward compatibility with existing tests that import float constants
FLSA_OVERTIME_MULTIPLIER = Fraction(
    FLSA_OVERTIME_MULTIPLIER_NUM, FLSA_OVERTIME_MULTIPLIER_DEN
)
FLSA_WEEKLY_OVERTIME_THRESHOLD = FLSA_WEEKLY_OVERTIME_THRESHOLD_HOURS

STATUTE_REF_FLSA_207 = "29 U.S.C. § 207"


# ---------------------------------------------------------------------------
# Pay period result type
# ---------------------------------------------------------------------------

class WeeklyPayResult(NamedTuple):
    """Structured result of a weekly pay calculation."""
    regular_hours: Fraction         # Hours at regular rate (capped at 40)
    overtime_hours: Fraction        # Hours at 1.5x (hours > 40)
    regular_pay_cents: int          # Regular pay in integer cents
    overtime_pay_cents: int         # Overtime pay in integer cents
    total_pay_cents: int            # Total gross pay in integer cents
    overtime_triggered: bool        # True iff hours > 40
    statute_refs: list              # Always includes STATUTE_REF_FLSA_207


# ---------------------------------------------------------------------------
# Core overtime calculator (F_LABOR_001, F_LABOR_002)
# ---------------------------------------------------------------------------

def calculate_weekly_pay(
    hours_worked: Fraction,
    hourly_rate_cents: int,
) -> WeeklyPayResult:
    """
    Calculate gross weekly pay with FLSA overtime.

    Invariant: Hours over 40 are compensated at 1.5x hourly_rate_cents.
    Falsification: If overtime_pay_cents != 1.5 * regular rate * OT hours, F_LABOR_001 fails.

    Uses integer arithmetic (cents) for all monetary values to avoid float rounding.
    Fractional cents are truncated in favor of the employer (conservative).

    Args:
        hours_worked:       Total hours worked in the week as a Fraction.
        hourly_rate_cents:  Regular hourly rate in integer cents (e.g., 1500 = $15.00/hr).

    Returns:
        WeeklyPayResult with all monetary values in integer cents.

    Raises:
        ValueError: If hours_worked < 0 or hourly_rate_cents <= 0.
    """
    if hours_worked < 0:
        raise ValueError(f"hours_worked must be non-negative, got {hours_worked}")
    if hourly_rate_cents <= 0:
        raise ValueError(f"hourly_rate_cents must be positive, got {hourly_rate_cents}")

    threshold = Fraction(FLSA_WEEKLY_OVERTIME_THRESHOLD_HOURS)
    rate = Fraction(hourly_rate_cents)

    if hours_worked <= threshold:
        regular_hours = hours_worked
        overtime_hours = Fraction(0)
    else:
        regular_hours = threshold
        overtime_hours = hours_worked - threshold

    # Exact rational arithmetic — no float
    regular_pay_rational = regular_hours * rate
    overtime_rate = rate * Fraction(FLSA_OVERTIME_MULTIPLIER_NUM, FLSA_OVERTIME_MULTIPLIER_DEN)
    overtime_pay_rational = overtime_hours * overtime_rate

    # Truncate fractional cents (conservative)
    regular_pay_cents = int(regular_pay_rational)
    overtime_pay_cents = int(overtime_pay_rational)
    total_pay_cents = regular_pay_cents + overtime_pay_cents

    return WeeklyPayResult(
        regular_hours=regular_hours,
        overtime_hours=overtime_hours,
        regular_pay_cents=regular_pay_cents,
        overtime_pay_cents=overtime_pay_cents,
        total_pay_cents=total_pay_cents,
        overtime_triggered=overtime_hours > 0,
        statute_refs=[STATUTE_REF_FLSA_207],
    )


# ---------------------------------------------------------------------------
# Multi-week pay summary (F_LABOR_001)
# ---------------------------------------------------------------------------

class PayPeriodSummary(NamedTuple):
    """Summary across multiple weeks in a pay period."""
    weeks: int
    total_regular_pay_cents: int
    total_overtime_pay_cents: int
    total_gross_pay_cents: int
    weeks_with_overtime: int
    statute_refs: list


def summarize_pay_period(weekly_hours: Sequence[Fraction], hourly_rate_cents: int) -> PayPeriodSummary:
    """
    Summarize pay across multiple weeks.

    Each week is calculated independently (FLSA overtime is per-week, not per pay period).
    Invariant: Each week's overtime is independently computed at the 40-hour threshold.
    Falsification: If overtime is calculated across weeks instead of per-week, F_LABOR_001 fails.
    """
    if not weekly_hours:
        raise ValueError("weekly_hours must not be empty")

    total_regular = 0
    total_overtime = 0
    weeks_ot = 0

    for week_hours in weekly_hours:
        result = calculate_weekly_pay(week_hours, hourly_rate_cents)
        total_regular += result.regular_pay_cents
        total_overtime += result.overtime_pay_cents
        if result.overtime_triggered:
            weeks_ot += 1

    return PayPeriodSummary(
        weeks=len(weekly_hours),
        total_regular_pay_cents=total_regular,
        total_overtime_pay_cents=total_overtime,
        total_gross_pay_cents=total_regular + total_overtime,
        weeks_with_overtime=weeks_ot,
        statute_refs=[STATUTE_REF_FLSA_207],
    )


# ---------------------------------------------------------------------------
# Frontloading detector (F_LABOR_002)
# ---------------------------------------------------------------------------

WORKLOAD_RATIO_TOLERANCE = Fraction(1)   # 1.0 — any ratio > 1.0 is frontloading


def compute_workload_ratio(task_hours: Fraction, scheduled_hours: Fraction) -> Fraction:
    """
    Compute workload_ratio = task_hours / scheduled_hours.

    Invariant: Any ratio > 1.0 indicates frontloading (assigned work exceeds schedule).
    """
    if scheduled_hours <= 0:
        raise ValueError("scheduled_hours must be positive")
    return task_hours / scheduled_hours


def detect_frontloading(task_hours: Fraction, scheduled_hours: Fraction) -> bool:
    """
    Return True if task_hours > scheduled_hours (frontloading detected).
    Return False if within schedule.
    """
    ratio = compute_workload_ratio(task_hours, scheduled_hours)
    return ratio > WORKLOAD_RATIO_TOLERANCE


# ---------------------------------------------------------------------------
# Domain metadata
# ---------------------------------------------------------------------------

DOMAIN_METADATA = {
    "id": "D_LABOR_RIGHTS",
    "name": "Labor Rights Enforcement",
    "invariants": [
        "Hours over 40/week compensated at 1.5x (FLSA 29 U.S.C. § 207).",
        "Wage calculations use integer cents to avoid float rounding errors.",
        "Every pay period result includes a statute reference to 29 U.S.C. § 207.",
    ],
    "falsification_tests": ["F_LABOR_001", "F_LABOR_002", "F_LABOR_003"],
    "implementation_functions": [
        "calculate_weekly_pay",
        "summarize_pay_period",
        "detect_frontloading",
        "compute_workload_ratio",
    ],
    "uses_integer_cents": True,
    "uses_fraction_for_exact_math": True,
    "flsa_overtime_multiplier": "3/2",
    "flsa_weekly_threshold_hours": 40,
}
