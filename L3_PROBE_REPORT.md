---
tags: [l3, probe, gather-spec, documentation]
register: documentation
---

# L3 PROBE REPORT — The Formal Gather Specification (Day 14, 2026-08-26)

**Directive:** Kimi ruling (user-relayed): (b) — attempt the first
obligation on the record already fetched; the compiler's unsolved goals
become the formal specification of what the gather must produce.

**Machine-checked:** `L3_PROBE.lean` — 5 theorems, exit 0. The certified
mold (`L3_MODEL.lean`) stayed byte-stable; the probe mirrors its types.

## THE PROBE RESULT

The partial witness from P14 (DER n=2, fetched: The Logic + Montreal
Gazette) satisfies:

- **entity = "Aylo"** — proved (`probe_entity_satisfiable`)
- **route 2 partial**: the $120M settlement record exists and is the route
  P14's data can enter

The type system demands, exactly, in order (proved `p14_gap_analysis`):

1. **name** — no named operator in the fetched record
2. **role** — unknown
3. **board_seats** — none gathered
4. **public_traces** — none gathered
5. **stated_intent** — none gathered

`couples_loop_not_empty` remains open: attribution to a nameless operator
is rejected by the certified shape (`probe_obligations_open` proved).

## THE GATHER SPECIFICATION (Day 15)

| Field | Target sources |
| :--- | :--- |
| name / role | officers named in the Aylo settlement record and corporate registrations |
| board_seats | corporate registries (Aylo, MindGeek successor entities) |
| public_traces | executive statements, court filings, interviews |
| stated_intent | public statements and internal documents (litigation record) |

The proposition dictated the evidence: five fields, three routes, in
order. No more, no less. The gather now pours into the certified mold.

**Anchors:** `L3_PROBE.lean` → `a31b0e608d4663ddbc61ad785445baacef909a00f44efc7328f7e3f1a7334560`
