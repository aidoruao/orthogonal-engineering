import «L1_DECAY»

/-! # Negative control — a stale pass must NOT count as current.

`stale_pass_is_unknown` proves that a verification performed at another
environment version reports `unknown`, even when it passed. This file asserts
the opposite: that a stale pass still reports `verified`. If Lean accepts this,
staleness is invisible and the whole decay model is empty.

Expected: `decide` proves the proposition false, because version 1 has no
verification and therefore reports `unknown`.

Run from the repository root and require a non-zero exit.
-/

def stalePass : Verification := ⟨0, true⟩

theorem stale_pass_still_counts : statusOf [stalePass] 1 = .verified := by
  decide
