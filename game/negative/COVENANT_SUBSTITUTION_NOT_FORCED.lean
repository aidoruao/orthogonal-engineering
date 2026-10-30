import «L5_COVENANT»

/-! # Negative control — this file MUST fail to compile.

It asserts that an insolvent debtor with a balanced ledger and no third-party
payment is a settlement. If Lean accepts this, `substitution_required` is
vacuous and a ledger can close without anyone covering the remainder — which
would make every accounting of an insolvent party meaningless.

Expected: the arithmetic `byOther > 0` contradicts `byOther = 0`.

Run: `lean game/negative/COVENANT_SUBSTITUTION_NOT_FORCED.lean; test $? -ne 0`
-/

open Covenant

example : (0 : Nat) > 0 := by
  have h := substitution_required
    { account := { debt := 10, capacity := 3 }, byViolator := 3, byOther := 0 }
    (by unfold Account.insolvent; decide)
    (by unfold Settlement.feasible; decide)
    (by unfold Settlement.balanced; decide)
  exact h
