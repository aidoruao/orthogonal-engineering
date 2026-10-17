import «L1_LEDGER»

/-! # Negative control — this file MUST fail to compile.

It attempts to construct a record whose nature is `finding` and whose tier is
`unverified`. If Lean accepts this, the invariant in `L1_LEDGER.lean` is
vacuous and the proof is worthless.

Expected: a compile error at `adjudicated_requires_fetched`, because that
field has no inhabitant for this combination.

Run from the repository root and require a non-zero exit:

    lean ledger/negative/NEGATIVE_CONTROL.lean; test $? -ne 0

This file is a falsifier, not a module. It is not imported anywhere.
-/

def badRecord : Record where
  claimId := "CLM-BAD-1"
  nature := .finding
  tier := .unverified
  adjudicated_requires_fetched := by
    intro h
    simp [Nature.isAdjudicated] at h
