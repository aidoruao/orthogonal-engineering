import «L1_GATES»

/-! # Negative control — a vacuous gate cannot reject anything.

`vacuous_gate_adds_nothing` proves that a gate admitting everything is a no-op.
This file asserts the opposite: that such a gate rejects some item. If Lean
accepts this, the theorem is vacuous and the "structural theatre" warning is
empty.

Expected: an error with goal `False`, because `compose [(fun _ => True)] x`
unfolds to `True` and there is nothing to contradict.

Run from the repository root and require a non-zero exit:

    LEAN_PATH=<olean dir> lean ledger/negative/GATES_THEATRE.lean; test $? -ne 0
-/

theorem vacuous_gate_rejects_something (x : Nat) :
    ¬ compose ((fun _ => True) :: []) x := by
  intro h
  -- After unfolding, every gate in the list is satisfied. The goal below is
  -- `False`, and the context contains only `True`. Nothing closes it.
  simp [compose] at h
