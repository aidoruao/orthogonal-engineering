import «L5_COVENANT»

/-! # Negative control — this file MUST fail to compile.

It asserts that a chain of excuses reduces what is owed — that excusing is a
form of payment. If Lean accepts this, `no_finite_excuse_chain_discharges` is
false and there is a free excuse: an entry that answers a debt without being
worth anything.

Expected: the sum is strictly positive, so it cannot equal zero.

Run: `lean game/negative/COVENANT_EXCUSE_DISCHARGES.lean; test $? -ne 0`
-/

open Covenant

example : outstanding [Entry.act 5, Entry.excuse, Entry.excuse] = 0 := by
  decide
