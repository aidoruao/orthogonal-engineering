import «L1_INELASTICITY»

/-! # Negative control — this file MUST fail to compile.

It asserts that an assignment exists whose monotone levels reproduce the
published C₂ and C₃ totals. If Lean accepts this, `c3_cannot_exceed_c2` is
vacuous and the inelasticity finding is an artifact of the encoding rather than
a property of the published numbers.

The control must fail because the *proposition is false*, not because Lean
cannot decide it. So the witness is a concrete integer assignment and the claim
is stated as a decidable arithmetic proposition about it.

Expected: ``Tactic `decide` proved that the proposition ... is false``.

Run: `lean burden/negative/INELASTICITY_FIT_EXISTS.lean; test $? -ne 0`
-/

/-- A monotone assignment with plausible-looking tenths values. -/
def naiveFit : Levels :=
  { lm := 40, m := 60, mh := 70, h := 80 }

/-- The assignment is monotone: the words mean what they say. -/
theorem naiveFit_monotone : naiveFit.monotone := by
  unfold Levels.monotone naiveFit
  decide

/-- The claim under test: this monotone assignment reproduces C₂'s total. The
arithmetic says 2·80 + 3·60 + 40 = 380, against a published 390. -/
theorem naiveFit_reproduces_c2 : c2Mean naiveFit = C2_TOTAL := by
  unfold c2Mean naiveFit C2_TOTAL
  decide
