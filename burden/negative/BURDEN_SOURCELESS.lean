import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It attempts to construct a `fetched` receipt with no source commitment. If Lean
accepts this, a supported claim can rest on nothing, and
`supported_receipt_names_its_source` is vacuous.

Expected: a compile error at `source_required`.

Run: `lean burden/negative/BURDEN_SOURCELESS.lean; test $? -ne 0`
-/

def badReceipt : Receipt where
  claimId := "CLM-BAD-4"
  tier := .fetched
  verdict := .verified
  falsifier := "the span is absent"
  falsifier_nonempty := by decide
  actor := "negative-control"
  actor_nonempty := by decide
  sourceSha256 := ""
  source_required := by intro _; decide
  derivationSteps := 1
  derivation_nonempty := by decide
  sound := by intro h; exact absurd rfl h
