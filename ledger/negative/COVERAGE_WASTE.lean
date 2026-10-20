import «L1_COVERAGE»

/-! # Negative control — a repeat claim must NOT increase coverage.

`addDoc_zero_if_covered` proves that a claim about an already-covered document
adds nothing. This file asserts the opposite: that a second claim on the same
document increases the covered count. If Lean accepts this, then "claims" and
"documents covered" are the same number, the snowball theorem is empty, and a
ledger could look like it was growing while reading the same page forever.

Expected: `decide` proves the proposition false.

Run from the repository root and require a non-zero exit.
-/

theorem repeat_adds_a_document : (addAll [385] [385]).length = 2 := by
  decide
