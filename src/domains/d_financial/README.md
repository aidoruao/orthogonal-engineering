# D_FINANCIAL — Financial

## Domain Purpose

Double-spend detection with thread-safe settlement ledger and immutable audit trail.

## Core Invariants

1. **Double-spend prevention** (F_FINANCIAL_001): No transaction ID may be settled more than once. The first `settle()` call returns `True`; all subsequent calls return `False`.

2. **Atomic concurrency** (F_FINANCIAL_002): Settlement operations are atomic under concurrent access via `threading.Lock`. A concurrent stress test (`attempt_concurrent_double_spend`) verifies that exactly one thread wins.

3. **Audit trail** (F_FINANCIAL_003): Every settlement attempt (accepted or rejected) produces an immutable `SettlementRecord` in the audit log. `verify_audit_integrity` checks consistency between ledger state and log.

## Biblical Inspiration (Functional)

> "Honest scales and balances belong to the LORD; all the weights in the bag are of his making." (Proverbs 16:11)

This is not decorative. The settlement ledger is the scale — every transaction must be weighed exactly once. A double-spend is a false weight in the bag: it corrupts the measure and violates the standard of honest exchange. The `threading.Lock` is the divine balance arm: it ensures that no two threads can simultaneously tip the scale in their favor. The audit log is the permanent record of every weighing.

## Falsification Test IDs

- `F_FINANCIAL_001` — Double-spend rejection (sequential)
- `F_FINANCIAL_002` — Double-spend rejection (concurrent)
- `F_FINANCIAL_003` — Audit trail completeness

## Files

| File | Purpose |
|------|---------|
| `implementation.py` | Settlement ledger, concurrent stress test, audit integrity |
| `invariants.py` | Executable invariant checks (no stubs) |
