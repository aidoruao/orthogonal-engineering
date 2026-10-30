import «L6_GAME»

/-! # Negative control — this file MUST fail to compile.

It asserts that a bond deters a false claim even when nothing detects it. If
Lean accepts this, `bond_without_detection_is_inert` is false and a security
posted against an unaudited contract means something — which is the precise
error that makes a missing certified-payroll requirement look like a
formality rather than a hole.

Expected: without detection the false claim nets the full gain.

Run: `lean game/negative/GAME_BOND_WITHOUT_DETECTION.lean; test $? -ne 0`
-/

open Game

example : falseNet ⟨1_000_000, 1, false⟩ ≤ 0 := by
  rw [bond_without_detection_is_inert]
  decide
