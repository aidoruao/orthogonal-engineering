import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It attempts to construct a falsified receipt that still wears the `fetched`
tier. If Lean accepts this, the false-citation lesson is not mechanized and a
claim can keep the tier its own check refuted.

Expected: a compile error at `sound`, because `Tier.fetched ≠ Tier.fetched`
has no inhabitant.

Run: `lean burden/negative/BURDEN_FALSIFIED_FETCHED.lean; test $? -ne 0`
-/

def badReceipt : Receipt where
  claimId := "CLM-BAD-3"
  tier := .fetched
  verdict := .falsified
  falsifier := "the span is present"
  falsifier_nonempty := by decide
  actor := "negative-control"
  actor_nonempty := by decide
  sourceSha256 := "f00dfeed"
  source_required := by intro _; decide
  derivationSteps := 2
  derivation_nonempty := by decide
  sound := by intro _; exact ⟨by decide, by decide⟩
