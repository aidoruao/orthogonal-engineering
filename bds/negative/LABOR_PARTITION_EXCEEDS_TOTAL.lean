import «L2_LABOR»

/-! # Negative control — this file MUST fail to compile.

It asserts that a partition of a fixed hour budget can sum to *more* than the
budget — that assigning more shifts creates more capacity. If Lean accepts this,
`partition_capacity_invariant` is vacuous and the district's most natural reply
("we assigned more staff") would defeat the argument.

Expected: `decide` proves `200 = 100` false.

Run: `lean bds/negative/LABOR_PARTITION_EXCEEDS_TOTAL.lean; test $? -ne 0`
-/

/-- Two shifts of 100 each are claimed to be a partition of a 100-minute budget. -/
example : ([100, 100] : List Nat).sum = 100 := by
  decide
