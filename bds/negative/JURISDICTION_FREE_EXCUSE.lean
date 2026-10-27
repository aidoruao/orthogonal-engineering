import «L3_JURISDICTION»

/-! # Negative control — this file MUST fail to compile.

It asserts that an excuse is also a legitimate reply — that there exists a reply
which bears on nothing and is nonetheless a justification.

If Lean accepts this, `no_free_pass` is vacuous and there is a free excuse: a
reply that answers a finding without addressing it. That is the whole of what
the arc forbids.

Expected: `decide` proves `false = true` false.

Run: `lean bds/negative/JURISDICTION_FREE_EXCUSE.lean; test $? -ne 0`
-/

/-- A reply that is offered in place of bearing, and claimed legitimate. -/
example :
    Excuse ⟨"budget_was_tight", true, false, true⟩ ∧
      Legitimate ⟨"budget_was_tight", true, false, true⟩ := by
  unfold Excuse Legitimate
  decide
