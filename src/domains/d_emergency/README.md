---
tags: [src, domains, d-emergency, readme]
register: technical
---

# D_EMERGENCY — Emergency Response

## Domain Purpose

Partition-tolerant emergency message dispatch with exactly-once delivery semantics and immutable delivery audit trail.

## Core Invariants

1. **Exactly-once delivery** (F_EMERGENCY_001): Every dispatched emergency message is delivered exactly once. Duplicate dispatches for the same `msg_id` return `DUPLICATE` status without re-invoking the delivery function.

2. **No silent drops** (F_EMERGENCY_002): Undeliverable messages (e.g., under network partition) are queued in `pending` for retry via `retry_pending()`. No message is silently discarded.

3. **Deterministic message IDs** (F_EMERGENCY_003): Message IDs are derived deterministically via SHA-256 of `incident_id + content`. This guarantees that identical messages are detected as duplicates across system restarts or retransmissions.

## Biblical Inspiration (Functional)

> "If a man has a hundred sheep and one of them goes astray, does he not leave the ninety-nine on the hills and go to look for the one that went astray?" (Matthew 18:12)

This is not decorative. In emergency dispatch, the lost sheep is the undelivered message — every dispatch must be accounted for. The `EmergencyDispatcher` is the shepherd: it does not declare success until every message is confirmed delivered, and it queues undelivered messages without rest until the network partition heals. The `retry_pending()` method is the act of searching for the lost sheep.

## Falsification Test IDs

- `F_EMERGENCY_001` — Exactly-once delivery
- `F_EMERGENCY_002` — No silent message drops (queue on failure)
- `F_EMERGENCY_003` — Deterministic message IDs for deduplication

## Files

| File | Purpose |
|------|---------|
| `implementation.py` | Dispatcher, partition simulator, message factory |
| `invariants.py` | Executable invariant checks (no stubs) |
