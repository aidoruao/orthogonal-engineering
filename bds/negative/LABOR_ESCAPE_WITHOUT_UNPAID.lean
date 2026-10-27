import «L2_LABOR»

/-! # Negative control — this file MUST fail to compile.

It asserts the escape hatch: that a campus can demand 1,400 labor-minutes, be
paid for 1,000, deliver 1,400, and have every delivered minute fall inside paid
time. That is the claim a district would have to make to avoid both branches of
the dichotomy.

If Lean accepts this, `either_standard_unmet_or_unpaid` is vacuous and the audit
proves nothing.

Expected: `decide` proves `1400 ≤ 1000` false.

Run: `lean bds/negative/LABOR_ESCAPE_WITHOUT_UNPAID.lean; test $? -ne 0`
-/

/-- Standards met, every minute paid, and the paid minutes fall short — all at
once. -/
example : (1400 : Nat) ≤ 1000 + 0 ∧ (1400 : Nat) < 1400 + 0 := by
  decide
