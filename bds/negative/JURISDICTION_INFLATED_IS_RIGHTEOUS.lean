import «L3_JURISDICTION»

/-! # Negative control — this file MUST fail to compile.

It asserts that a finding claiming more severity than its evidence warrants is
nonetheless righteous — that indignation may exceed what the facts support.

If Lean accepts this, `inflation_is_not_righteous` is vacuous, and the
distinction between righteous indignation and vengeance has no formal content.

Expected: `decide` proves `3 ≤ 1` false.

Run: `lean bds/negative/JURISDICTION_INFLATED_IS_RIGHTEOUS.lean; test $? -ne 0`
-/

/-- A structural finding, measured by a fetched primary, claiming severity 3
where the evidence warrants 1 — and asserted to be righteous anyway. -/
example :
    Righteous
      { subject := .structure
        claimedSeverity := 3
        warrantedSeverity := 1
        evidence := .fetched "abc123"
        hasFalsifier := true } = true := by
  decide
