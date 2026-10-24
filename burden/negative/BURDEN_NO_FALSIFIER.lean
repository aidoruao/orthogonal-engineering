import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It attempts to construct a receipt with an empty falsifier. If Lean accepts
this, `no_receipt_without_falsifier` is vacuous and the receipt contract
enforces nothing.

Expected: a compile error at `falsifier_nonempty`, because `"" ≠ ""` has no
inhabitant.

Run from the repository root and require a non-zero exit:

    lean burden/negative/BURDEN_NO_FALSIFIER.lean; test $? -ne 0

This file is a falsifier, not a module. It is not imported anywhere.
-/

def badReceipt : Receipt where
  claimId := "CLM-BAD-1"
  tier := .fetched
  verdict := .verified
  falsifier := ""
  falsifier_nonempty := by decide
  actor := "negative-control"
  actor_nonempty := by decide
  sourceSha256 := "f00dfeed"
  source_required := by intro _; decide
  derivationSteps := 1
  derivation_nonempty := by decide
  sound := by intro h; exact absurd rfl h
