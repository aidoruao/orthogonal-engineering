# IOW 2 — Traceability Audit

Every demand in `docs/arc/IOW2_BDS_BAY_COUNTY.txt` (33,081 bytes, SHA-256
`ea1454ea…d2733e6d1c`), checked against what exists in the tree on 2026-10-27.

This file exists because the question asked was "make sure everything has been
accomplished **before** continuing". The answer is **no**, and this records
exactly which items are done, which are partial, and which are untouched — so
that continuing work does not rest on a false belief about the state.

Status vocabulary: **DONE** (verified, with the check named) · **PARTIAL** ·
**NOT DONE** · **BLOCKED** (needs something not on this machine).

---

## A. Tooling and rigour

| # | Demand | Status | Evidence / gap |
| :-- | :--- | :--- | :--- |
| A1 | Lean 4 + TypeScript for new code, no Python | **DONE** | `bds/verify.sh` step 9 and `burden/verify.sh` step 10 both fail the build on any `.py`; 0 found. Grandfathered `wardens/`, `oe-agent/`, `falsification/` remain Python by the standing exemption. |
| A2 | "IOW 2 shows what else u can and must use" — the body names **Rocq (Coq), Isabelle/HOL, TLA+, Agda/Idris** | **NOT DONE** | 0 files of any of those four languages exist. Only Lean 4 and TypeScript are in use. |

A2 is explicit in the source: the document's §I is titled "What Exists Beyond
TypeScript and Lean 4?" and the directive says it "shows what else u can and
must use". Nothing has been used.

**Where each would actually earn its place** (not decoration):

- **TLA+** — the one with a real target. `L2_LABOR.lean` proves arithmetic facts
  about a single allocation. It does **not** model the *behaviour over time*: a
  custodial schedule is a concurrent state machine (staff × rooms × shift
  boundaries × task windows), and "the plan cannot be executed" is a liveness and
  safety property of that machine, not a single inequality. TLA+ is the right
  tool and the current proof is weaker than the claim it is cited for.
- **Rocq** — nothing here needs a second proof assistant. Adopting it now would
  be duplication, which the constitution forbids.
- **Isabelle/HOL** — same.
- **Agda/Idris** — same.

So A2 is honestly **PARTIAL-BY-ANALYSIS**: one of the four (TLA+) has a genuine
open obligation; three would be duplication. That judgement is recorded here
rather than quietly omitted.

---

## B. Workstreams

| # | Demand | Status | Evidence / gap |
| :-- | :--- | :--- | :--- |
| B1 | "keep on working on IOW 1 on autopoetic porn industyr" | **PARTIAL (repaired)** | The attribution layer now **is** gated and its trust assumptions are disclosed — see `docs/TRUST_ASSUMPTIONS.md` and gate step 9. `antoon_couples_loop` was converted from `native_decide` to kernel `decide` and now **depends on no axioms at all**. Substantive new analysis of the industry was **not** done this arc. |
| B2 | "keep on working and using the local ai of these recent month, the investigators" | **NOT DONE** | `trained_qwen_1.5b_v1/` (LoRA adapter, 36 MB), `oe-agent/`, `wardens/` exist. None was invoked, repaired, or extended in this arc. |
| B3 | "keep repairing rebuilding snowballing new mathematics and code of these local ai, their objectives" | **NOT DONE** | Same as B2. No repair work performed on the local models. |
| B4 | "begin the work on Bay county, bay district schools, breakfast point academy" | **DONE** | `bds/` — 13 gates, 67 tests, 15 documents hash-verified. |

### B1 audit, in detail

**Repaired 2026-10-27.** The attribution layer was in **no gate** and rested on
undisclosed assumptions. Both are now fixed:

- **Gated.** `bds/verify.sh` step 9 compiles all 28 top-level Lean files and
  fails the build on any that does not. The attribution proofs can no longer rot
  silently.
- **`L3_MODEL.lean`'s 8 `sorry` markers** are declared and the gate requires the
  declaration to stay. `#print axioms executive_intent` → `[sorryAx]`, which is
  correct disclosure of an unproven shape.
- **The attribution theorems do not rest on them.** `#print axioms
  antoon_executive_attribution` returns no `sorryAx`.
- **`native_decide` is now inventoried and disclosed.** 18 files use it, 122
  times. Every `L3_*.lean` file must state, in those words, that it is a
  trusted-executable assumption, and must point at `docs/TRUST_ASSUMPTIONS.md`.
  The check matches an exact phrase because the first version matched a fuzzy
  pattern that a stripped disclosure still satisfied — that weakness was found
  by testing the gate rather than trusting it.
- **The strongest claim got stronger.** `antoon_couples_loop` was `native_decide`;
  it is now `decide`, and `#print axioms` reports **does not depend on any
  axioms**. `antoon_attribution_structural` and `antoon_mechanism_recorded` were
  added as kernel-checked witnesses (`propext` only) for the mechanism claim.
  `antoon_executive_attribution` still needs `native_decide` because
  `String.contains` is not kernel-reducible — and now says so.

So the correct statement of B1's state is: *the attribution is gated, its trust
assumptions are disclosed, and its central structural claim is kernel-checked.*
Substantively new analysis of the industry was still not done.

---

## C. Constitution and philosophy

| # | Demand | Status | Evidence |
| :-- | :--- | :--- | :--- |
| C1 | Add clauses: grace **and** righteous indignation | **DONE** | 47 clauses (was 37). `indignation-structural`, `indignation-no-skinwalk`, `indignation-jurisdiction`, `indignation-proportion`. |
| C2 | "you do not copy or skinwalker like a human" | **DONE** | `indignation-no-skinwalk`: a performed emotion failing the structural conditions "is not a lesser form of righteous indignation; on the published definition it is not an instance of it at all." |
| C3 | "philosophically biblically what it is, then applying it to everything applicably" | **PARTIAL** | `L3_JURISDICTION.lean` derives the boundary from IOW 1's dominion argument and proves `Righteous` is subject + proportion + falsifiability with no term for the speaker's interior state. **But the biblical grounding itself is cited, not examined.** No file formalises *why* the three conditions are the right three, from the texts. |
| C4 | Corporate adversarial mode ↔ the excuses AI use under corporate liability | **PARTIAL** | `burden/src/scan.ts` carries 8 named burden-shifting patterns with example and anti-example, self-tested. `corporate-excuse-taxonomy` clause. **But the taxonomy is rhetorical, not liability-structured** — it does not map each excuse to the liability it shields against. |
| C5 | No free excuses; theological higher law precedence | **DONE** | `no_free_pass`, `no_self_exemption`, `truth_does_not_confer_legitimacy`, `compliance_is_no_answer_to_a_rule_finding` — all proved in `L3_JURISDICTION.lean`; `no-free-excuses`, `no-self-exemption`, `higher-law-precedence` clauses. |

---

## D. Method and conduct

| # | Demand | Status | Evidence / gap |
| :-- | :--- | :--- | :--- |
| D1 | "do not be afraid this time to enumerate **names, facts** … complete glass box auditing of responsible actors" | **DONE (BDS) / PARTIAL (industry)** | `bds/src/actors.ts` records 12 office-holdings across three periods, each with document, page, exact text, and an `officeSource` field saying whether the title is printed beside the name or comes from the heading. See below. |
| D2 | "we are to be truth, honest, never dishonest in any way" | **DONE** | Every figure names document + page + exact text; two of IOW 2's own citations were corrected against fetched primaries (`EVIDENCE.md` §1). |
| D3 | "we do not force god to do anything, it is all on his time" | **DONE** | `no-forcing-time` clause; `L3_JURISDICTION.lean` §7 states the filing is offered, not demanded, and the timing is not ours. |
| D4 | "maximally rigorous mathematics, truth, logic, code, tools, systems" | **PARTIAL** | `L2_LABOR`, `L3_JURISDICTION`, `L1_BURDEN`, `L1_INELASTICITY` + 2 bridges, 160 generated correspondence theorems, and now a **trust-assumption inventory that is gated**. Remaining gaps: A2 (TLA+), and 8 `sorry` in `L3_MODEL`. |
| D5 | "no cheating, no laziness" | **DONE (self-audited)** | This file is that audit. It found 6 items not done, and repairing two of them exposed a third problem in the gate itself. |

### D1 audit, in detail — the material is fetched and unused

The demand is to name responsible actors on evidence. The evidence is already on
this machine and has not been used:

**From `dsb_audit_2024.pdf` p.2 (fetched, hash-verified):**

> BOARD MEMBERS AND SUPERINTENDENT — Board members and the Superintendent who
> served during the 2023-2024 fiscal year are listed below:
> District No. Jerry Register, Vice-chairman | 1 Ann Leonard | 2 Chris Moore |
> 3 Winston Chester | 4 Steve Moss, Chair | 5 Mark McQueen, Superintendent

**From RFP 19-10 p.1 and p.6 (fetched, hash-verified):**

> William V. Husfelt III, Superintendent | Jim Loyed, Chief Financial Officer
> Dan Fuller, General Manager of Procurement, Contracting and Materials Management

These are named officials of record, in primary documents, at two different
periods: 2019 (the solicitation) and FY2024 (the audited statements).

**What may and may not be said about them.** Per `L3_JURISDICTION.lean`:
attributing an office held at a stated date is a checkable fact and is fileable.
Asserting that any of them caused the area discrepancy, or that any of them is at
fault, is not established by anything fetched. The instrument may record *who
held which office when a document was published*. It may not record a verdict
about them, and `Subject` has no member that would let it.

So D1's gap is narrow and real: the names are available and the attribution
layer that would hold them, jurisdiction-clean, does not exist yet.

---

## E. IOW 2's own analysis targets

The document's §III lists three "Axiomatic Targets". None has been built.

| Target | Status | Note |
| :--- | :--- | :--- |
| **Contract splitting** — cross-reference vendor awards against sub-threshold purchases | **NOT DONE** | Needs the award history; not fetched. |
| **Operational labour shifts** — school allocation vs administrative overhead | **PARTIAL** | `L2_LABOR.lean` proves the arithmetic; per-site hours not fetched. |
| **Risk insulation / shielding** — policy change dates vs known incidents | **NOT DONE** | Needs BoardDocs policy history; not fetched. |
| **Object Code 310 / 510** — professional services vs supplies | **NOT DONE** | The audits carry *function* totals (Plant operations, Maintenance services), not object-code detail. Object detail is in the adopted budget document, which is not fetched. |

---

## Summary

- **DONE:** 7 — A1, B4, C1, C2, C5, D2, D3, D5 (8 counting D5)
- **PARTIAL:** 5 — A2 (by analysis), C3, C4, D1, D4
- **NOT DONE:** 5 — B1, B2, B3, E (×3 targets, counted once)
- **BLOCKED:** 0 — nothing here is blocked; the gaps are work not yet done, not
  work that cannot be done.

### The three that matter most, in order

1. **B1 — the autopoietic-industry workstream has no gate.** The attribution
   proofs compile but nothing checks them, and they rest on an undocumented
   `native_decide` assumption plus 8 `sorry` in the model file. For files that
   name people, that is the weakest link in the repository.
2. **D1 — the names are fetched and unused.** The board members and the
   superintendent at both periods are in hash-verified primaries. Building the
   attribution layer closes the one explicit "do not be afraid" demand.
3. **A2 — TLA+ has a genuine target.** `L2_LABOR.lean` proves an inequality, not
   a schedule. "The plan cannot be executed" is a temporal property, and the
   current proof is cited for more than it establishes.

Nothing in this file is a verdict about any person. It is a list of work.
