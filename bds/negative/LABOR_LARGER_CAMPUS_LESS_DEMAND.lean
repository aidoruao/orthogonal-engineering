import «L2_LABOR»

/-! # Negative control — this file MUST fail to compile.

It asserts that a larger campus demands *less* labor than a smaller one at the
same specification. If Lean accepts this, `demand_monotone_area` is vacuous and
the whole audit's monotonicity claim means nothing.

Expected: `decide` proves `200 < 100` false.

Run: `lean bds/negative/LABOR_LARGER_CAMPUS_LESS_DEMAND.lean; test $? -ne 0`
-/

def oneTask : CleaningTask :=
  { id := "floor.daily.sweep", frequencyPerYear := 180, minutesPerThousandSqFt := 12 }

/-- 200,000 sq ft demanding less than 100,000 sq ft under the same task list. -/
example :
    Campus.demandScaled ⟨200000, [oneTask]⟩ < Campus.demandScaled ⟨100000, [oneTask]⟩ := by
  decide
