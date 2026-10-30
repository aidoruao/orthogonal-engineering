import «L5_COVENANT»

/-! # Negative control — this file MUST fail to compile.

It asserts that a settlement can be restored while its ledger is open. If Lean
accepts this, `cheap_mercy_is_uninhabited` is false and grace is a licence: a
debtor is restored without anyone paying, which is to say the ledger recorded
nothing and was never a ledger.

Expected: `restored` is definitionally `balanced`, so the conjunction is
inhabited only by a contradiction.

Run: `lean game/negative/COVENANT_CHEAP_MERCY.lean; test $? -ne 0`
-/

open Covenant

example : ∃ s : Settlement, s.restored ∧ ¬ s.balanced := by
  refine ⟨{ account := { debt := 10, capacity := 0 }, byViolator := 0, byOther := 0 }, ?_, ?_⟩
  · unfold Settlement.restored Settlement.balanced
    decide
  · unfold Settlement.balanced
    decide
