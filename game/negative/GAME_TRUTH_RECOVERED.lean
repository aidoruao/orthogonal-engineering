import «L6_GAME»

/-! # Negative control — this file MUST fail to compile.

It asserts that a decision rule recovers the truth from a truth-blind producer.
If Lean accepts this, `no_rule_recovers_truth` is false and a broken epistemic
anchor can in fact be read — which is the single claim the entire inversion
exists to deny.

Expected: the two worlds differ in truth but agree in claim, so any rule gives
the same answer for both.

Run: `lean game/negative/GAME_TRUTH_RECOVERED.lean; test $? -ne 0`
-/

open Game

example : ∃ d : Bool → Bool, ∀ w : World, d (constantTrue.claim w) = w.truth := by
  refine ⟨fun b => b, ?_⟩
  intro w
  cases w with
  | mk t => cases t <;> rfl
