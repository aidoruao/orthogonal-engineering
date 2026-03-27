# CS-LPE Architecture (v1 + v2)

## One-line summary
A fully event-sourced simulation engine where gameplay, animation, UI, and replay are all derived projections of a single causal record.

## Sign-off note
SIGN OFF: **YES (CONDITIONAL APPROVAL)** — Approved for v2 implementation assuming invariants remain enforced in code, CEG hash integrity + pruning rules are implemented exactly as specified, NET authority (server WSC) remains absolute source of truth, PLS compression never performs silent loss, and PAE determinism guarantees are unit-test enforced. Proceed.

## Primary systems
- **World Simulation Core (WSC):** Authoritative physical reality, emits hash-chained state diffs and causal events.
- **Causal Event Graph (CEG):** Append-only, hash-linked causal record with tiered retention and sharding.
- **Perception Layer System (PLS):** Layered interpretation (L1 structural, L2 tactical, L3 diegetic) with bounded compression and cognitive load reporting.
- **Procedural Animation Engine (PAE):** Deterministic animation synthesis with priority-ordered primitives, deterministic fallback, and desync snap-to-authority.
- **Truth Replay System (TRS):** Evidence-grade replay built solely from CEG, immutable outputs.
- **Network Fairness Layer (NET):** Hybrid server-authority with bounded client prediction, reconciliation, desync counter, and optional lockstep.

## Authority gradient
WSC (Reality/Simulation) → CEG (Append-only causal record) → PLS (Derived, compression-bounded) → PAE (Derived, deterministic) → TRS (Read-only replay) → NET (Server authority with bounded prediction).

## Files
- `invariants/cslpe_invariants.yaml` — 57 invariants (INV-CSLPE-001 .. INV-CSLPE-057)
- `invariants/cslpe_forbidden.yaml` — 26 forbidden topologies (FORBIDDEN_CSLPE_001 .. FORBIDDEN_CSLPE_026)
- `invariants/cslpe_node_classes.yaml` — Node class bindings (WSC, CEG, PLS, PAE, TRS, Multiplayer Fairness, Meta Invariant)
- `invariants/cslpe_falsification_tests.json` — 24 falsification tests (F_CSLPE_001 .. F_CSLPE_024)
- `invariants/cslpe_event_schema.json` — CEG event JSON Schema (v2)

## v2 risk resolution
| Risk | Mitigation (invariants) | Forbidden topology | Tests |
| --- | --- | --- | --- |
| CEG scalability | INV-CSLPE-022..026 | FORBIDDEN_CSLPE_009, 010 | F_CSLPE_010, 011 |
| PLS real-time cognition | INV-CSLPE-027..030 | FORBIDDEN_CSLPE_011, 012 | F_CSLPE_012 |
| PAE determinism boundaries | INV-CSLPE-031..035 | FORBIDDEN_CSLPE_013, 014, 015 | F_CSLPE_013, 014 |
| Networking + fairness | INV-CSLPE-036..041, INV-CSLPE-055, INV-CSLPE-056 | FORBIDDEN_CSLPE_016..026 | F_CSLPE_015, 016, 023 |
| Meta truth graph | INV-CSLPE-057 | FORBIDDEN_CSLPE_020..026 | F_CSLPE_024 |

## Enforcement expectations
- Invariants are falsifiable, executable, and enforced in code (not documentation-only).
- CEG hash integrity, pruning rules, and tombstone chains are implemented exactly as specified.
- Server WSC remains absolute authority; prediction is bounded and reconciled.
- PLS compression and stress modes are never silent; degradation is announced.
- PAE determinism, priority ordering, and fallback guarantees are covered by unit tests.
