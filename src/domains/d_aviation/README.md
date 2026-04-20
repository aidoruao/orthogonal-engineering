---
tags: [src, domains, d-aviation, readme]
register: technical
---

# D_AVIATION — Aviation & ATC

## Domain Purpose

Safe-flight envelope enforcement and circuit-breaker-protected external API integration for aviation and ATC systems.

## Core Invariants

1. **Safe-flight envelope** (F_AVIATION_001): Aircraft never enters a state that violates known safe-flight envelope limits (speed, altitude, bank, pitch, vertical speed). Any violation raises `EnvelopeViolationError`.

2. **Graceful ATC message handling** (F_AVIATION_002): Malformed ATC messages are rejected without crashing the parser. No unhandled exception escapes `parse_atc_message`.

3. **Weather API fallback** (F_AVIATION_003): When the external weather API is unavailable, the system falls back to last-known cached data, not a crash.

4. **Circuit breaker** (F_AVIATION_004): After `failure_threshold` consecutive API failures, the circuit opens and all subsequent calls return cached data without attempting live fetches.

## Biblical Inspiration (Functional)

> "The prudent see danger and take refuge, but the simple keep going and pay the penalty." (Proverbs 22:3)

This is not decorative. The circuit breaker is the prudent refuge: when an external weather or ATC data feed fails, the system does not blindly continue with stale or absent data — it shelters behind cached state, alerts the crew, and awaits recovery. The `CircuitBreaker.call()` method embodies this proverb: it opens the circuit when danger (repeated failures) is detected, and only probes again after a recovery window has elapsed.

## Falsification Test IDs

- `F_AVIATION_001` — Safe-flight envelope enforcement
- `F_AVIATION_002` — Malformed ATC message handling
- `F_AVIATION_003` — Weather API fallback to cache
- `F_AVIATION_004` — Circuit breaker opens on repeated failures

## Files

| File | Purpose |
|------|---------|
| `implementation.py` | Envelope checks, circuit breaker, ATC parser, lift model |
| `invariants.py` | Executable invariant checks (no stubs) |
