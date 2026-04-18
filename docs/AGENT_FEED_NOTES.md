---
tags: [agent-feed, state-witness, gap-documentation, operational-context]
register: technical
---

# AGENT_FEED Notes — Genesis Row and Chain Gap Documentation

<!-- P4: Document genesis row and chain gaps per state witness analysis OBS-3, INT-003 -->

## Purpose

This document records operational context for interpreting `AGENT_FEED.md`. It documents the genesis row sentinel, observed timestamp gaps, and instructions for interpreting gaps correctly.

---

## Genesis Row (S(0) Sentinel)

The first row in `AGENT_FEED.md` has `prev_entry_hash=""` (empty string). This is the valid Peano S(0) genesis sentinel — it is **not** a malformed field.

**Engineering definition:** The genesis row is the initial object in the hash-chain. All subsequent rows form a chain where `row[n].prev_entry_hash == row[n-1].entry_hash`. The S(0) row anchors the chain.

**Verification:**

```bash
python tools/state_witness/generate_feed_entry.py --verify
```

Output confirms: `Genesis row: prev_entry_hash='' (S(0) sentinel — correct)`.

**Falsifies if:** The verify command exits non-zero citing the genesis row's empty `prev_entry_hash` as an error.

---

## Observed Timestamp Gaps

The following gaps have been observed in the feed. A gap means no push events triggered the `pr40-canonical-presence.yml` workflow during that period — **not** that the chain is broken.

| Gap | Row A | Row B | Duration | Cause |
|-----|-------|-------|----------|-------|
| Large early gap | Row 10 | Row 11 | ~773 hours (~32 days) | Project was in early bootstrapping; workflow ran infrequently during Feb–Mar 2026. |
| Mid-stream gap | Row 182 | Row 183 | ~68.5 hours (~2.9 days) | CI workflows were not triggered during Apr 14–16 2026; no pushes to main during that period. |

### How to Interpret Gaps

A timestamp gap between rows `N` and `N+1` indicates that no qualifying push event fired the state-witness workflow between those two timestamps. The chain is intact as long as:

1. `row[N+1].prev_entry_hash == row[N].entry_hash`
2. The verify command exits 0

A gap is **not** evidence of a chain break, tampering, or data loss. Run `--verify` to confirm chain integrity independently of timestamp ordering.

### Checking for Gaps Programmatically

```python
import re

with open("AGENT_FEED.md") as f:
    rows = [line.strip() for line in f if line.startswith("|") and "timestamp" not in line.lower()]

timestamps = []
for row in rows:
    parts = [p.strip() for p in row.split("|") if p.strip()]
    if parts:
        ts = parts[0]
        if re.match(r"\d{4}-\d{2}-\d{2}T", ts):
            timestamps.append(ts)

from datetime import datetime, timezone
parsed = [datetime.fromisoformat(t) for t in timestamps]
gaps = [(parsed[i+1] - parsed[i]).total_seconds() / 3600 for i in range(len(parsed) - 1)]
large_gaps = [(i, g) for i, g in enumerate(gaps) if g > 24]
print(f"Gaps > 24 hours: {large_gaps}")
```

---

## INT-003: Gap Documentation Standard

Any gap > 72 hours observed in `AGENT_FEED.md` should be documented here with:

- Row numbers (A → B)
- Duration in hours
- Cause (or "unknown" if not determinable)

This provides operational context for future agents and auditors without requiring chain-break remediation.

**Standard ID:** `INT-003` (see `STANDARDS_REGISTRY.json`)

---

## Feed Row Count History

| Date | Approximate Row Count | Event |
|------|----------------------|-------|
| 2026-01-26 | 1 | Genesis row (S(0)) |
| 2026-02 | ~10 | Early bootstrapping |
| 2026-03 | ~11 | First 773-hour gap closes |
| 2026-04-12 | ~183 | Mass bootstrap (commit `a27ff75`) pre-populated 183 rows |
| 2026-04-17 | 184 | PR #132 Stream A write-back |

---

## References

- `AGENT_FEED.md` — the append-only ledger itself
- `tools/state_witness/generate_feed_entry.py` — verify command
- `tools/state_witness/alert_on_failure.py` — alerting on verify failures
- `.github/workflows/pr40-canonical-presence.yml` — CI workflow that appends rows
- `STANDARDS_REGISTRY.json` — INT-001 (chain integrity), INT-003 (gap documentation)
