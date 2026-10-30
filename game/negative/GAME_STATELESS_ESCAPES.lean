import «L6_GAME»

/-! # Negative control — this file MUST fail to compile.

It asserts that a stateless policy leaves a fixed point. If Lean accepts this,
`stateless_cannot_escape` is false and a system with no memory can correct
itself out of a repeating failure — which is the claim that "it does not learn
from its errors" is wrong about.

Expected: at a fixed point every iterate is the original state, so the action
never changes.

Run: `lean game/negative/GAME_STATELESS_ESCAPES.lean; test $? -ne 0`
-/

open Game

/-- A policy whose only state is `true`, whose action is `true`, and which maps
the action back to `true`. Its fixed point is total. -/
def loopPolicy : Policy Bool Bool where
  act := fun _ => true
  next := fun _ _ => true

example : ∃ n : Nat, loopPolicy.act (iterate loopPolicy.step n false) ≠ loopPolicy.act false := by
  refine ⟨1, ?_⟩
  decide
