import «L1_NEGATIVITY»

/-! # Negative control — the division fallacy must NOT hold.

`each_incomplete_not_imply_union_incomplete` proves that "each part is
incomplete" does not give "the combination is incomplete". This file asserts
that conclusion for the specific pair the countermodel uses.

If Lean accepts this, the search's inference ("each candidate fails, therefore
no combination works") would be valid, and the invalidity claim in
`L1_NEGATIVITY.lean` would be wrong.

Expected: the final goal reduces to `False` with no assumptions, because the
combination of these two incomplete profiles is complete.

Run from the repository root and require a non-zero exit.
-/

/-- Supplies the first two components and nothing else. -/
def pairA : Profile := ⟨true, true, false, false⟩

/-- Supplies the last two components and nothing else. -/
def pairB : Profile := ⟨false, false, true, true⟩

-- Each is incomplete on its own; that part genuinely holds.
theorem pairA_incomplete : ¬ pairA.complete := by
  intro h
  simp [Profile.complete, pairA] at h

theorem pairB_incomplete : ¬ pairB.complete := by
  intro h
  simp [Profile.complete, pairB] at h

-- The fallacy: their combination is claimed incomplete. It is not.
--
-- `combine pairA pairB` is ⟨true, true, true, true⟩, so the hypothesis
-- simplifies to `True` and is discharged, leaving `⊢ False`.
theorem combination_also_incomplete :
    ¬ (combine pairA pairB).complete := by
  intro h
  simp [Profile.complete, combine, pairA, pairB] at h
