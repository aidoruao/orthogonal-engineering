import «L1_DECAY»

/-! # Negative control — a stale failure must NOT count as a current failure.

The symmetric error to `DECAY_STALE`: treating an old failure as proof that the
current environment fails. `stale_fail_is_unknown` proves the status is
`unknown`; this file asserts it is `failed`.

If Lean accepts this, then old failures would be permanent verdicts and a fixed
bug could never be recorded as fixed.

Expected: `decide` proves the proposition false.

Run from the repository root and require a non-zero exit.
-/

def staleFail : Verification := ⟨0, false⟩

theorem stale_failure_is_current_failure : statusOf [staleFail] 1 = .failed := by
  decide
