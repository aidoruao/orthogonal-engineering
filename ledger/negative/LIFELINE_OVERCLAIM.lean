import «L1_LIFELINE»

/-! # Negative control — a passenger must NOT support "impossible".

`passenger_collapses_lock` proves that if prolactin is a passenger (rises but
does not drive), the framework's claim function cannot reach `impossible`. This
file asserts the opposite.

If Lean accepts this, the framework could claim mechanical impossibility while
explicitly denying the premise that makes it possible — which is precisely the
overclaim that `docs/arc/WALL_OF_SHAME.txt` identifies and that the framework's
own author conceded.

Expected: `decide` proves the proposition false.

Run from the repository root and require a non-zero exit.
-/

theorem passenger_supports_impossibility :
    ({ adrenergicSurge := true, prolactinRise := true, prolactinIsDriver := false,
       contextReplacesContent := true } : Premises).claim = .impossible := by
  decide
