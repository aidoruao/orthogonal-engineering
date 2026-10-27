import «L2_LABOR»

/-! # Negative control — this file MUST fail to compile.

It asserts that the paid capacity for a campus is simultaneously at least the
demand and strictly below it. If Lean accepts this, `infeasible_iff_shortfall`
is vacuous — the bridge between the definition and the dichotomy — and "the plan
cannot be executed" would have no fixed meaning in this repository.

The claim is stated as arithmetic on `demandScaled` and `capacityScaled` rather
than through `Feasible`, so that the failure is the *refutation of the
proposition* and not Lean's inability to synthesize a `Decidable` instance. A
control that fails for the wrong reason would still fail with the theorem
deleted, which is the opposite of a falsifier.

Expected: `decide` proves the conjunction false.

Run: `lean bds/negative/LABOR_FEASIBLE_AND_NOT.lean; test $? -ne 0`
-/

def sample : Campus :=
  { areaSqFt := 1000
    tasks := [{ id := "t", frequencyPerYear := 2, minutesPerThousandSqFt := 15 }] }

/-- Demand scaled is 1000 × (2 × 15) = 30000 and the capacity for 29 minutes is
29000, so demand is not below capacity and capacity is below demand. -/
example :
    Campus.demandScaled sample ≤ capacityScaled 29 ∧
      capacityScaled 29 < Campus.demandScaled sample := by
  decide
