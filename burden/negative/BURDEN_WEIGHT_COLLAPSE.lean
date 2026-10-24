import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It asserts that a load-bearing failure and an illustrative failure carry the
same weight. If Lean accepts this, passive neutrality is representable and the
third inversion is not enforced.

Expected: a compile error at `by decide`.

Run: `lean burden/negative/BURDEN_WEIGHT_COLLAPSE.lean; test $? -ne 0`
-/

example : severity .loadBearing false = severity .illustrative false := by decide
