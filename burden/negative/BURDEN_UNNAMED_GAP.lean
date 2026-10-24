import «L1_BURDEN»

/-! # Negative control — this file MUST fail to compile.

It attempts to place a human-only burden with no named missing measurement. If
Lean accepts this, "unverified" is treated as an answer, which is the deferral
spiral the scan is supposed to catch.

Expected: a compile error at `named`, because `"" ≠ ""` has no inhabitant.

Run: `lean burden/negative/BURDEN_UNNAMED_GAP.lean; test $? -ne 0`
-/

def badAssignment : Assignment where
  checkability := .humanOnly
  missingMeasurement := ""
  named := by intro _; decide
