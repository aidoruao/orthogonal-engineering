import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It attempts to construct a receipt with no named actor. If Lean accepts this,
an action can be recorded with nobody accountable, and
`no_anonymous_receipt` proves nothing.

Expected: a compile error at `actor_nonempty`.

Run: `lean burden/negative/BURDEN_ANONYMOUS.lean; test $? -ne 0`
-/

def badReceipt : Receipt where
  claimId := "CLM-BAD-2"
  tier := .fetched
  verdict := .verified
  falsifier := "the span is absent"
  falsifier_nonempty := by decide
  actor := ""
  actor_nonempty := by decide
  sourceSha256 := "f00dfeed"
  source_required := by intro _; decide
  derivationSteps := 1
  derivation_nonempty := by decide
  sound := by intro h; exact absurd rfl h
