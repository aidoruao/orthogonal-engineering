import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It asserts that a `fetched` claim may be upgraded to `corroborated`. If Lean
accepts this, `no_upgrade_from_fetched` is vacuous and a claim can move between
tiers without new evidence.

Expected: a compile error at `by decide`.

Run: `lean burden/negative/BURDEN_UPGRADE.lean; test $? -ne 0`
-/

example : mayUpgrade Tier.fetched Tier.corroborated = true := by decide
