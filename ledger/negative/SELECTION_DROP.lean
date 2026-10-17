import «L1_SELECTION»

/-! # Negative control — a dropped candidate MUST fail to compile.

`Selection.total` says the ledger's entries are exactly the candidates. This
file tries to build a selection with two candidates and one entry. If Lean
accepts it, the totality invariant is vacuous and the whole instrument is
theatre.

Expected: a compile error at `total`, because `["CLM-A"] ≠ ["CLM-A", "CLM-B"]`.

Run from the repository root and require a non-zero exit.
-/

def droppedSelection : Selection where
  candidates := ["CLM-A", "CLM-B"]
  entries := [⟨"CLM-A", .accepted⟩]
  total := by decide
  reasons := by
    intro e he
    simp only [List.mem_singleton] at he
    subst he
    trivial
