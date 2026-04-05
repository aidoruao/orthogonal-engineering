"""
D_LABOR_RIGHTS invariant checks — executable, not declarative.

Each function returns True (invariant holds) or raises AssertionError (violated).
No `pass` bodies. No `return True` stubs.

Source: ontology/ontology.json#D_LABOR_RIGHTS
"""

from fractions import Fraction

from src.domains.d_labor_rights.implementation import (
    FLSA_OVERTIME_MULTIPLIER,
    FLSA_WEEKLY_OVERTIME_THRESHOLD,
    STATUTE_REF_FLSA_207,
    WORKLOAD_RATIO_TOLERANCE,
    calculate_weekly_pay,
    summarize_pay_period,
    detect_frontloading,
    compute_workload_ratio,
)


def check_overtime_rate_is_one_and_half() -> bool:
    """
    Invariant: FLSA overtime multiplier is exactly 3/2.
    Falsification: If multiplier != 3/2, F_LABOR_001 is structurally violated.
    """
    assert FLSA_OVERTIME_MULTIPLIER == Fraction(3, 2), (
        f"FLSA_OVERTIME_MULTIPLIER must be 3/2, got {FLSA_OVERTIME_MULTIPLIER}"
    )
    return True


def check_overtime_threshold_is_40() -> bool:
    """
    Invariant: FLSA weekly overtime threshold is 40 hours.
    Falsification: Any other threshold violates 29 U.S.C. § 207.
    """
    assert FLSA_WEEKLY_OVERTIME_THRESHOLD == 40, (
        f"FLSA threshold must be 40 hours, got {FLSA_WEEKLY_OVERTIME_THRESHOLD}"
    )
    return True


def check_overtime_triggers_at_41_hours() -> bool:
    """
    Invariant: Working 41 hours triggers overtime for exactly 1 hour.
    Falsification: If overtime_hours != 1 for 41-hour week, F_LABOR_001 fails.
    """
    result = calculate_weekly_pay(
        hours_worked=Fraction(41),
        hourly_rate_cents=1500,  # $15.00/hr
    )
    assert result.overtime_triggered is True, "41-hour week must trigger overtime"
    assert result.overtime_hours == Fraction(1), (
        f"OT hours must be 1, got {result.overtime_hours}"
    )
    return True


def check_no_overtime_at_40_hours() -> bool:
    """
    Invariant: Exactly 40 hours does not trigger overtime.
    Falsification: If overtime_triggered is True for 40-hour week, threshold is wrong.
    """
    result = calculate_weekly_pay(
        hours_worked=Fraction(40),
        hourly_rate_cents=1500,
    )
    assert result.overtime_triggered is False, "40-hour week must not trigger overtime"
    assert result.overtime_hours == Fraction(0)
    assert result.regular_hours == Fraction(40)
    return True


def check_overtime_pay_is_exactly_1_5x() -> bool:
    """
    Invariant: Overtime pay rate is exactly 1.5x the regular rate.
    Falsification: If overtime pay deviates from 1.5x, F_LABOR_001 is violated.

    For $15.00/hr (1500 cents), 1 OT hour = 1500 * 3/2 = 2250 cents.
    """
    result = calculate_weekly_pay(
        hours_worked=Fraction(41),
        hourly_rate_cents=1500,
    )
    expected_ot_pay = int(Fraction(1500) * Fraction(3, 2))  # 2250 cents
    assert result.overtime_pay_cents == expected_ot_pay, (
        f"OT pay must be {expected_ot_pay} cents, got {result.overtime_pay_cents}"
    )
    return True


def check_statute_ref_in_result() -> bool:
    """
    Invariant: Every pay result includes 29 U.S.C. § 207.
    Falsification: If statute_refs is empty, audit trail is missing.
    """
    result = calculate_weekly_pay(
        hours_worked=Fraction(45),
        hourly_rate_cents=2000,
    )
    assert STATUTE_REF_FLSA_207 in result.statute_refs, (
        f"Result must cite {STATUTE_REF_FLSA_207}, got {result.statute_refs}"
    )
    return True


def check_integer_cents_no_float() -> bool:
    """
    Invariant: Wage calculations use integer cents, not floats.
    Falsification: If implementation uses float() for monetary values, F_LABOR_002 is at risk.
    """
    import inspect
    source = inspect.getsource(calculate_weekly_pay)
    assert "float(" not in source, (
        "calculate_weekly_pay must not use float() — integer/Fraction arithmetic required"
    )
    return True


def check_frontloading_detected() -> bool:
    """
    Invariant: Workload exceeding scheduled hours is detected as frontloading.
    Falsification: If detect_frontloading returns False when task > schedule, F_LABOR_002 fails.
    """
    result = detect_frontloading(
        task_hours=Fraction(10),
        scheduled_hours=Fraction(8),
    )
    assert result is True, "10 task hours in 8 scheduled hours must be flagged as frontloading"
    return True


def run_all_invariants() -> dict:
    """Run all D_LABOR_RIGHTS invariants. Returns dict of check_name → pass/fail."""
    checks = [
        check_overtime_rate_is_one_and_half,
        check_overtime_threshold_is_40,
        check_overtime_triggers_at_41_hours,
        check_no_overtime_at_40_hours,
        check_overtime_pay_is_exactly_1_5x,
        check_statute_ref_in_result,
        check_integer_cents_no_float,
        check_frontloading_detected,
    ]
    results = {}
    for check in checks:
        try:
            check()
            results[check.__name__] = "PASS"
        except AssertionError as e:
            results[check.__name__] = f"FAIL: {e}"
    return results


if __name__ == "__main__":
    import json
    results = run_all_invariants()
    print(json.dumps(results, indent=2))
    failures = [k for k, v in results.items() if v != "PASS"]
    if failures:
        raise SystemExit(f"Invariant failures: {failures}")
    print("All D_LABOR_RIGHTS invariants: PASS")
