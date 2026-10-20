import «L1_GATES»

/-! # Negative control — adding a gate cannot create evasion.

`auditor_dominance` proves that extending a strategy with a gate never
increases evasion. This file asserts the opposite: that some claim evades the
larger strategy while evading the smaller one. If Lean accepts this, the
dominance result is false.

Expected: an unsolved goal `False` in the second conjunct, because evasion
under `[]` only requires `compose [] x`, which always holds.

Run from the repository root and require a non-zero exit.
-/

theorem adding_a_gate_increases_evasion :
    ∃ (f : Gate Nat) (g : Gate Nat) (gs : List (Gate Nat)) (x : Nat),
      Evades f (g :: gs) x ∧ ¬ Evades f gs x := by
  refine ⟨fun _ => True, fun _ => True, [], 0, ?_, ?_⟩
  · -- First conjunct: this one is genuinely true.
    refine ⟨trivial, ?_⟩
    intro g' hg'
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hg'
    rw [hg']
    trivial
  · -- Second conjunct: goal is `False` and cannot close.
    intro _
