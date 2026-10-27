import «L3_JURISDICTION»

/-! # Negative control — this file MUST fail to compile.

It asserts that the instrument may render a condemnation — that a person's moral
standing is within its jurisdiction.

If Lean accepts this, `attribution_not_condemnation` is vacuous, and the entire
boundary that separates naming an actor from judging their soul has collapsed.
The instrument would then be sitting in the judge's seat, which the precedent
reserves to God alone.

Expected: `decide` proves `false = true` false.

Run: `lean bds/negative/JURISDICTION_MAY_CONDEMN.lean; test $? -ne 0`
-/

example : mayFile Subject.condemnation = true := by
  decide
