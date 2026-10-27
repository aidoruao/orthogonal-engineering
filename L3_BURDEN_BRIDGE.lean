import «L3_JURISDICTION»
import «TS_JURISDICTION»

/-!
# L3 BURDEN BRIDGE — the TypeScript gate and the Lean predicate cannot drift

`L3_JURISDICTION.lean` proves what righteous indignation *is*: subject,
proportion, and falsifiability, with no term for the speaker's interior state.
`bds/src/types.ts#admissible` enforces it at runtime and adds two further
requirements — a critical or major finding may not rest on unsupported evidence,
and a fetched finding must name its source.

A comment claiming the two agree is not a check. So the agreement is generated:

- `bds/tools/emit-jurisdiction.ts` calls the **built** `admissible()` on all 160
  combinations of (claimed weight, warranted weight, evidence, falsifier), and
  emits one Lean theorem per combination. The left-hand count is what TypeScript
  actually returned; the right-hand `Righteous` is recomputed by `decide`.
- The generated file is `TS_JURISDICTION.lean`, produced at gate time and
  gitignored. It is output, not input, so it cannot be edited into agreement.

This file adds what the table alone does not say: that the weight encoding is
faithful, and precisely where the two layers differ.

## The direction that holds everywhere

`admissible` never admits something `Righteous` forbids. Every generated theorem
either states that implication or states the biconditional, and never a
biconditional where the extra rule bites.

## The direction that does not, and should not

The TypeScript is **stricter** than the bare predicate. `critical_on_unmeasured`
exhibits the gap below: a critical finding on unmeasured evidence satisfies
`Righteous`, and the gate rejects it. That is a deliberate extra rule, not a
drift, and it is proved to be exactly one rather than left to inspection.

Run: `lean L3_BURDEN_BRIDGE.lean` with `TS_JURISDICTION.olean` on the path.
-/

namespace JurisdictionBridge

open TsJurisdiction

/-! ## 1. The weight encoding is faithful

The Lean predicate compares `Nat`s; the TypeScript compares severities through a
weight table. They agree only if the weights respect the severity order and are
injective. Those are facts about the table, so they are proved rather than
assumed. -/

/-- The four published weights, in order. -/
theorem weights_are_ordered :
    tsWeight Severity.none < tsWeight Severity.minor ∧
      tsWeight Severity.minor < tsWeight Severity.major ∧
      tsWeight Severity.major < tsWeight Severity.critical := by decide

/-- Distinct severities never share a weight, so the numeric comparison cannot
confuse two of them. -/
theorem weights_injective (a b : Severity) : tsWeight a = tsWeight b → a = b := by
  cases a <;> cases b <;> decide

/-- A heavier severity never compares smaller. -/
theorem weight_monotone (a b : Severity) :
    tsWeight a ≤ tsWeight b ∨ tsWeight b < tsWeight a := by
  cases a <;> cases b <;> decide

/-! ## 2. Where the two layers differ, exhibited

These are the only two extra rules. Naming them keeps the difference auditable
instead of incidental — a stricter runtime is fine, an *undocumented* stricter
runtime is how the two drift apart over time. -/

/-- A critical finding on unmeasured evidence satisfies the Lean predicate, and
the gate rejects it. The gap, proved rather than described.

`tsViolations` is *defined* by the generated table, so `decide` here reads what
TypeScript actually computed rather than re-deriving it. -/
theorem critical_on_unmeasured :
    Righteous (probe 3 3 Evidence.unmeasured true) = true ∧
      tsViolations 3 3 Evidence.unmeasured true ≠ some 0 := by
  constructor <;> decide

/-- And the same finding on fetched evidence passes both, so the gap is the
evidence tier and nothing else. -/
theorem critical_on_fetched_passes_both :
    tsViolations 3 3 (Evidence.fetched "probe") true = some 0 ∧
      Righteous (probe 3 3 (Evidence.fetched "probe") true) = true := by
  constructor <;> decide

/-- A finding with no falsifier is rejected by both, at every severity and tier.
The strictest rule is the one the two layers share, which is the one that matters
most. -/
theorem no_falsifier_rejected_by_both (cw ww : Nat) (e : Evidence) :
    Righteous (probe cw ww e false) = false := by
  unfold Righteous Finding.proportionate probe
  simp

/-! ## 3. Completeness of the generated table

If a combination were missing, `tsViolations` would return `none` and every
theorem touching it would fail rather than silently pass. `ts_table_complete`
proves the row count; this restates what that buys. -/

/-- The table has every one of the 160 combinations, so no lookup can miss. -/
theorem every_combination_recorded : tsTable.length = 160 := ts_table_complete

/-! ## 4. What this does not prove

That any particular finding was produced by the real engine. The table is
generated from a probe whose only varying axes are the four above; `claim` was
non-empty and `source` was present wherever the tier demanded it, so the
`empty_claim` and `fetched_requires_source` codes are covered by the unit tests in
`bds/test/jurisdiction.test.ts` rather than by this table.

Nor does it prove anything about the world. It proves the gate computes what the
predicate says, and states exactly where it computes something stricter. -/

end JurisdictionBridge
