import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It asserts a tier pair the TypeScript does not compute: that a `fetched` claim
may be upgraded to `corroborated`. If Lean accepts this, then the generated
tables in `TS_TABLES.lean` are not actually checked point by point — the bridge
would be a comment with a build step attached.

Expected: a compile error at `by decide`, because `mayUpgrade .fetched
.corroborated` is `false`.

Run: `lean burden/negative/BURDEN_BRIDGE_DRIFT.lean; test $? -ne 0`
-/

example : mayUpgrade Tier.fetched Tier.corroborated = true := by decide
