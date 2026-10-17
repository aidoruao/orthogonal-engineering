import «L1_SELECTION»

/-! # Negative control — an anonymous rejection MUST fail to compile.

`Selection.reasons` says every non-accepted entry carries a non-empty code.
This file tries to reject a candidate with no reason. If Lean accepts it, a
claim could be set aside without anyone recording why, and the published
selection would be unauditable.

Expected: a compile error at `reasons`, because `"" ≠ ""` is false.

Run from the repository root and require a non-zero exit.
-/

def anonymousRejection : Selection where
  candidates := ["CLM-A"]
  entries := [⟨"CLM-A", .rejected ""⟩]
  total := by decide
  reasons := by
    intro e he
    simp only [List.mem_singleton] at he
    subst he
    simp [Disposition.hasReason]
