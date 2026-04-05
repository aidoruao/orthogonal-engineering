# D_LABOR_RIGHTS — Labor Rights Enforcement

## Domain Purpose

FLSA-compliant overtime calculation and frontloading detection for labor rights enforcement and wage theft documentation.

## Core Invariants

1. **FLSA overtime** (F_LABOR_001): Any hours over 40 in a week must be compensated at exactly 1.5x the regular rate (FLSA 29 U.S.C. § 207). Overtime is computed per-week, not across the pay period.

2. **Frontloading detection** (F_LABOR_002): Assigned work that exceeds scheduled hours is detectable. Any workload ratio > 1.0 (task hours / scheduled hours) is flagged.

3. **Off-the-clock prohibition** (F_LABOR_003): Uncompensated work events are logged and flagged in shift records.

## Biblical Inspiration (Functional)

> "Do not muzzle an ox while it is treading out the grain." (Deuteronomy 25:4 / 1 Timothy 5:18)

This is not decorative. Wage theft is the modern muzzle — assigning work that physically cannot fit in scheduled hours, then denying compensation for the excess. The FLSA overtime multiplier (`3/2`, exact, as a `fractions.Fraction`) is the unmuzzle. **All monetary values are computed in integer cents** to guarantee that the legal rate cannot be diluted by floating-point rounding. Fractional cents are truncated conservatively.

## Falsification Test IDs

- `F_LABOR_001` — FLSA overtime entitlement (1.5x at 40 hours)
- `F_LABOR_002` — Frontloading detection (workload ratio)
- `F_LABOR_003` — Off-the-clock work prohibition

## Files

| File | Purpose |
|------|---------|
| `implementation.py` | Overtime calculator, pay period summary, frontloading detector |
| `invariants.py` | Executable invariant checks (no stubs) |
