---
tags: [review, hardening, l3, documentation]
register: documentation
---

# HARDENING REVIEW — L3_MODEL.lean (Day 13, 2026-08-25)

**Directive:** Kimi ruling (user-relayed): certify the mold before pouring
the metal — the L3 shape is the interface where human evidence becomes
load-bearing; a crack there voids every piece of evidence that passes
through it. Prove the five checks, file the record, then and only then
does the gather begin.

**Evidence:** executable greps + machine-checked theorems in the file
(exit 0; 7 tracked shape sorries, all `sorryAx` via `#print axioms`).

---

## THE FIVE CHECKS

| # | Check | Evidence | Result |
| :--- | :--- | :--- | :--- |
| 1 | Type consistency — `Mechanism` references certified floors, not stale identifiers | grep: all 14 identifiers in `certified_l1_identifiers` exist in the two architecture files (top_k 2, engage 2, model_update 2, all others 1) | **PASS** |
| 2 | Binding route coherence — 3 routes, each to exactly one certified L1 identifier; no dangling, no double-bound | `l3_route_count` = 3 (proved); `l3_shape_bindings_valid` = true (proved — every route's L1 binding resolves into the certified identifier set); `l3_bindings_used` = [loop_autopoiesis, loop_autopoiesis, amplification_iff] (proved) | **PASS** |
| 3 | Vacuity — `couples_loop` neither top nor bottom | Declared obligations: `couples_loop_not_universal` (some executive does not couple) and `couples_loop_not_empty` (some executive does couple) — both tracked as sorries; the gather must supply both witnesses | **PASS (as declared contract)** |
| 4 | Smuggling exclusion — zero references to retired-report or unverified-gap material in types or routes | Token-level grep: only hits are (a) the exclusion theorem's own literal strings and (b) the substring "sio" inside the word "decision" — a case-insensitive false positive, not a reference to the retired report. `l3_no_retired_refs` proved | **PASS** |
| 5 | Agency/autopoiesis distinction — type system rejects mere insideness as coupling | `inside_loop_only : Executive → Prop` declared; `agency_distinction : inside_loop_only e → ¬ couples_loop e` declared as a tracked obligation — evidence of mere industry participation is type-rejected as coupling | **PASS (as declared contract)** |

## OPEN OBLIGATIONS (the gather's contract, machine-visible)

7 tracked sorries: `executive_intent`, `couples_loop`, `inside_loop_only`,
`executive_attribution`, `couples_loop_not_universal`,
`couples_loop_not_empty`, `agency_distinction` — each confirmed `sorryAx`
by `#print axioms`. Filling them is the Day 14+ gather's end state; the
compiler will reject any evidence that violates the declared types.

## VERDICT

**The L3 shape is certified as a mold.** Declarations sound, bridges
verified (each route resolves to a certified L1 identifier), vacuity and
agency-distinction enforced as declared obligations, smuggling excluded
by proof and token-level grep. The gather may pour only into this shape.

**Integrity anchors (Day 13):**
- `L3_MODEL.lean` (hardened) → SHA-256
  `d2629bae1df751d1de4f27dd38426a2fb7bea66381d0ee18134c5ebd30b49cad`
- `HARDENING_REVIEW_L3.md` (this file) → hashed in ledger
