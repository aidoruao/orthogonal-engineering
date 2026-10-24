import «L1_BURDEN»
import «TS_TABLES»

/-!
# L1 BURDEN BRIDGE — the TypeScript and the Lean cannot drift apart

`L1_BURDEN.lean` proves properties of the tier relation and the reporting
weight. `burden/src/types.ts` enforces them at runtime. A comment saying the two
are "the same relation" is not a check, and this package exists to refuse
unverified claims about agreement.

The mechanism:

1. `burden/tools/emit-tables.ts` reads the **compiled** TypeScript and calls
   `mayUpgrade` on all 25 tier pairs and `severity` on all 6 bearing/verdict
   pairs.
2. It emits `TS_TABLES.lean`, containing one Lean theorem per pair of the form
   `mayUpgrade Tier.unverified Tier.fetched = true := by decide`. The assertion
   is the value **TypeScript** computed; `decide` recomputes the **Lean** side.
3. `burden/verify.sh` regenerates that file from the current build and compiles
   it. Any disagreement stops the specific theorem from proving, and the build
   names the exact pair.

So the tables cannot be edited into agreement — they are output, not input — and
a change to either language is caught at the pair where it diverges.

`burden/negative/BURDEN_BRIDGE_DRIFT.lean` is the falsifier: it asserts one
flipped pair and must fail to compile. Without that control, this file could be
describing a check that never runs.
-/

namespace TsTablesAgreement

/-! ## 1. The consequences, restated so a reader can see them

These are not new facts — they are the generated theorems of `TS_TABLES` stated
in the form the inversion depends on. If TypeScript moved, the generated theorem
each of these cites would not have compiled. -/

/-- The TypeScript computes `critical` for a load-bearing failure. This is the
third inversion at the boundary: the weight the running code assigns is the
weight the proof forbids collapsing. -/
theorem ts_load_bearing_failure_is_critical :
    severity Bearing.loadBearing false = Severity.critical := by
  exact TsTables.ts_sev_p01

/-- `critical` is not reachable from an illustrative failure in the TypeScript
either, so passive neutrality is unavailable in the executable layer. -/
theorem ts_critical_not_illustrative :
    severity Bearing.illustrative false ≠ Severity.critical := by
  rw [TsTables.ts_sev_p05]
  decide

/-- Nothing upgrades out of `fetched` in the TypeScript. -/
theorem ts_no_upgrade_from_fetched (b : Tier) :
    mayUpgrade Tier.fetched b = true → b = Tier.fetched := by
  cases b
  · rw [TsTables.ts_tier_p15]; decide
  · rw [TsTables.ts_tier_p16]; decide
  · rw [TsTables.ts_tier_p17]; decide
  · rw [TsTables.ts_tier_p18]; intro _; rfl
  · rw [TsTables.ts_tier_p19]; decide

/-- `retired` is terminal in the TypeScript too: a withdrawn claim does not
quietly return. -/
theorem ts_no_upgrade_from_retired (b : Tier) :
    mayUpgrade Tier.retired b = true → b = Tier.retired := by
  cases b
  · rw [TsTables.ts_tier_p20]; decide
  · rw [TsTables.ts_tier_p21]; decide
  · rw [TsTables.ts_tier_p22]; decide
  · rw [TsTables.ts_tier_p23]; decide
  · rw [TsTables.ts_tier_p24]; intro _; rfl

/-- Every permitted upgrade is rank-monotone in the TypeScript as well, so no
upgrade the runtime allows can weaken a tier. -/
theorem ts_upgrade_rank_monotone (a b : Tier) :
    mayUpgrade a b = true → a.rank ≤ b.rank := by
  cases a <;> cases b <;> decide

/-! ## 2. What this does not prove

That the runtime calls these functions on the values a receipt actually holds,
or that a receipt was admitted. Those are behavioural facts, checked by
`burden/test/*.test.ts`, and reported separately in the gate. This file proves
the definitions agree; the tests prove the engine uses them. -/

end TsTablesAgreement
