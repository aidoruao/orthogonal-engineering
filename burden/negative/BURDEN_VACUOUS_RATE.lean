import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It asserts that an empty ledger reports a perfect falsification score of 100%.
If Lean accepts this, `zero_denominator_is_unmeasured` is vacuous and the
utility can manufacture exactly the uncalibrated number it exists to replace.

Expected: a compile error at `by decide`.

Run: `lean burden/negative/BURDEN_VACUOUS_RATE.lean; test $? -ne 0`
-/

example : ratePercent 0 0 = some 100 := by decide
