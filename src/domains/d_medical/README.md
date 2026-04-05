# D_MEDICAL — Medical Systems

## Domain Purpose

Safety-critical dosimetry and device authentication for implantable medical systems.

## Core Invariants

1. **Dose ceiling enforcement** (F_MEDICAL_001): Computed dose must never exceed the physician-prescribed ceiling. Any violation raises `DoseExceedsCeilingError` immediately at the API boundary.

2. **Device command authentication** (F_MEDICAL_002): Only authenticated clinicians may issue commands to implantable devices. Unauthenticated tokens are rejected with constant-time comparison.

3. **Infusion rate tolerance** (F_MEDICAL_003): Infusion pumps must deliver within ±5% of programmed rate. Deviations beyond this raise a `ValueError`.

## Biblical Inspiration (Functional)

> "A little yeast works through the whole batch of dough." (Galatians 5:9)

This is not decorative. A single unchecked floating-point rounding error in a dose calculation cascades to patient harm. This domain therefore uses **integer arithmetic in micrograms** via Python's `Fraction` type — exact, irreducible, non-negotiable. The invariant is the yeast: if it fails, the entire dough is corrupted.

## Implementation Notes

- All dose values are stored and computed as **integer micrograms** (`int`).
- Weight-adjusted dose calculations use `fractions.Fraction` to avoid any IEEE 754 rounding.
- Floor division is used conservatively (never round up a dose).
- HMAC-SHA256 with `hmac.compare_digest` guards device authentication.

## Falsification Test IDs

- `F_MEDICAL_001` — Dose ceiling enforcement
- `F_MEDICAL_002` — Device command authentication
- `F_MEDICAL_003` — Infusion rate tolerance

## Files

| File | Purpose |
|------|---------|
| `implementation.py` | Core dosimetry, infusion validation, device auth |
| `invariants.py` | Executable invariant checks (no stubs) |
