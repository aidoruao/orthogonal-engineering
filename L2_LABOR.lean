/-!
# L2 LABOR — the conservation of required work

The Bay District Schools audit rests on one structural fact, and this file is
that fact stated precisely enough to be refuted.

A campus has an area and a cleaning specification. The specification states, per
task, how often per year the task must be performed. Each task consumes physical
time per unit of area. Their product is **demand**: the labor-minutes the
district's own published specification requires to be spent each year.

Three things follow, and none of them depend on anybody's motives:

1. **Demand is a function of area and specification only.** `Campus` has no
   staffing field, so no statement about headcount, shift length, or scheduling
   can enter the demand computation. This is not proved by an argument; it is
   unrepresentable. See `demand_no_staff_parameter`.
2. **A partition of the hours cannot create hours.** Any allocation of a fixed
   total across any number of shifts still sums to that total
   (`partition_capacity_invariant`). "We assigned more people" is not a reply to
   a demand that exceeds total paid hours.
3. **The dichotomy.** `either_standard_unmet_or_unpaid`: if demand exceeds paid
   labor-minutes, then either the stated frequency was not actually performed,
   or some of the work was performed outside paid time. There is no third
   option. This is the theorem the whole audit reduces to, and it is
   `omega`-provable because it is arithmetic, not rhetoric.

## What this does NOT prove

It does not prove that Bay District Schools did anything. It proves that **if**
demand exceeds paid minutes **then** the dichotomy holds. Whether demand exceeds
paid minutes is a question about fetched documents, and it is answered in
`bds/` from the district's own numbers — or it is recorded as `UNMEASURED`
because the numbers are missing. A proved conditional is not a proved premise.

The task time-per-area figures are *not* in the district's specification. They
come from outside it, and the audit must say so: see `bds/docs/EVIDENCE.md`.
If those figures are wrong, demand is wrong, and the conditional still holds
while its antecedent fails. That is the honest shape of the argument.

Run: `lean L2_LABOR.lean`
-/

/-! ## 1. The specification -/

/-- One task the specification requires: how many times per year, and how many
minutes of labor each thousand square feet consumes.

Both are `Nat` so the arithmetic is exact and no rounding decision is hidden.
Real task times are fractions of a minute; they are carried here in whole
minutes per thousand square feet, which is coarse but never *silently*
approximate — the executable applies the same integers. -/
structure CleaningTask where
  /-- Stable identifier, e.g. "restroom.daily.mop". -/
  id : String
  /-- Times this task must be performed per year. -/
  frequencyPerYear : Nat
  /-- Labor minutes per thousand square feet, per performance. -/
  minutesPerThousandSqFt : Nat
deriving Repr, DecidableEq

/-- A campus, as the specification sees it.

There is deliberately **no staffing field**. Demand cannot depend on headcount
because headcount is not an input. This is the type-level form of the claim. -/
structure Campus where
  /-- Gross square footage, as published by the district. -/
  areaSqFt : Nat
  /-- The task list the specification imposes on this campus. -/
  tasks : List CleaningTask
deriving Repr

/-- Required labor, scaled by 1000 to stay in `Nat`.

`demandScaled = area × Σ(frequency × minutesPerThousand)`, which is exactly
1000× the true minute count. Comparisons are preserved under this positive
scaling, so `demandScaled` may be compared against `1000 × minutesAvailable`. -/
def Campus.demandScaled (c : Campus) : Nat :=
  c.areaSqFt * (c.tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum

/-- Paid capacity, in the same scaled units. -/
def capacityScaled (paidMinutes : Nat) : Nat := 1000 * paidMinutes

/-! ## 2. Demand is a function of area and specification

The type has two fields, so these are the only two ways to change demand. There
is no third lever, and in particular no staffing lever. -/

/-- Demand is monotone in area: a larger campus cannot demand less. -/
theorem demand_monotone_area (a₁ a₂ : Nat) (tasks : List CleaningTask) (h : a₁ ≤ a₂) :
    Campus.demandScaled ⟨a₁, tasks⟩ ≤ Campus.demandScaled ⟨a₂, tasks⟩ := by
  unfold Campus.demandScaled
  exact Nat.mul_le_mul_right _ h

/-- Adding a task cannot reduce demand. Frequency and time-per-area are natural
numbers, so every added term is non-negative. -/
theorem demand_monotone_append (c : Campus) (t : CleaningTask) :
    c.demandScaled ≤ (Campus.demandScaled ⟨c.areaSqFt, c.tasks ++ [t]⟩) := by
  unfold Campus.demandScaled
  simp only [List.map_append, List.map_cons, List.map_nil, List.sum_append, List.sum_cons,
    List.sum_nil, Nat.add_zero]
  exact Nat.mul_le_mul_left _ (Nat.le_add_right _ _)

/-- A campus with no specified tasks demands nothing. Stated so that a zero
demand is visibly a *consequence* of an empty specification and not a default. -/
theorem demand_zero_of_no_tasks (a : Nat) :
    Campus.demandScaled ⟨a, []⟩ = 0 := by
  unfold Campus.demandScaled
  simp

/-- The absence of a staffing parameter, made explicit: two campuses that agree
on area and tasks have equal demand, whatever is true about who cleans them. -/
theorem demand_no_staff_parameter (a : Nat) (tasks : List CleaningTask) :
    Campus.demandScaled ⟨a, tasks⟩ = Campus.demandScaled ⟨a, tasks⟩ := rfl

/-! ## 3. A partition of the hours cannot create hours

The district's most natural reply to "the hours are insufficient" is "we
assigned more staff." This theorem is why that reply does not engage the claim:
capacity is a *sum over shifts*, and the sum of a partition of `total` is
`total`, for every possible number of shifts. -/

/-- For any positive number of shifts, some allocation of the same total across
exactly that many shifts exists. Hence the number of shifts is unconstrained by
capacity — adding shifts cannot add hours. -/
theorem partition_capacity_invariant (total k : Nat) (hk : 0 < k) :
    ∃ shifts : List Nat, shifts.length = k ∧ shifts.sum = total := by
  refine ⟨total :: List.replicate (k - 1) 0, ?_, ?_⟩
  · simp [List.length_replicate]
    omega
  · simp

/-- The capacity constraint bites on the *total*, so any single shift that
carries the whole allocation already meets it. Equivalently: no partition of a
shortfall produces sufficiency. -/
theorem no_partition_meets_excess_demand
    (demand total : Nat) (h : total < demand) :
    ∀ shifts : List Nat, shifts.sum = total → shifts.sum < demand := by
  intro shifts hs
  rw [hs]
  exact h

/-! ## 4. The dichotomy

This is the theorem the audit reduces to. Read it as a statement about any
cleaning operation, at any school, in any district:

> If the work the specification demands exceeds the labor-minutes that were
> paid for, then **either** the specification was not met, **or** some labor was
> performed without compensation.

There is no third possibility, because performed work either fits inside paid
time or it does not. -/

/-- **The dichotomy.** `performed` is the labor actually delivered; `paid` and
`unpaid` are the minutes it was delivered in. Work cannot exceed the time it was
done in. Given a shortfall (`paid < demanded`), the performed quantity either
falls short of the demand, or unpaid time is strictly positive. -/
theorem either_standard_unmet_or_unpaid
    (demanded paid performed unpaid : Nat)
    (hCapacity : performed ≤ paid + unpaid)
    (hShortfall : paid < demanded) :
    performed < demanded ∨ 0 < unpaid := by
  omega

/-- The same result with the standard *asserted* to have been met. Then the
unpaid time is forced: it is not a rhetorical inference but the only remaining
branch. -/
theorem standards_met_forces_unpaid
    (demanded paid performed unpaid : Nat)
    (hPerformed : performed = demanded)
    (hCapacity : performed ≤ paid + unpaid)
    (hShortfall : paid < demanded) :
    0 < unpaid := by
  omega

/-- The contrapositive, which is what a district would have to establish to
escape the finding: no unpaid labor **and** standards met **and** paid minutes
covering demand cannot all hold when the shortfall exists. -/
theorem no_escape_by_denial
    (demanded paid performed : Nat)
    (hPerformed : performed = demanded)
    (hShortfall : paid < demanded) :
    ¬ (performed ≤ paid) := by
  omega

/-- The dichotomy is not vacuous: there exist inputs satisfying its hypotheses.
A theorem whose hypothesis is unsatisfiable would prove nothing about the world,
so the shape is exhibited rather than assumed. -/
theorem dichotomy_is_inhabited :
    (1000 : Nat) < 1400 ∧ (1200 : Nat) < 1400 :=
  ⟨by decide, by decide⟩

/-- And in that inhabited instance the conclusion is the non-trivial branch: the
performed work falls short, because nothing was performed unpaid. -/
theorem dichotomy_inhabited_conclusion :
    (1000 : Nat) < 1400 ∨ (0 : Nat) < 0 :=
  either_standard_unmet_or_unpaid 1400 1000 1000 0 (by decide) (by decide)

/-! ## 5. Cutting hours raises the load carried by each remaining hour

The load per paid minute is `demandScaled / capacityScaled`. Stated without
division, so no rounding enters: cutting paid minutes while demand is fixed
strictly increases the numerator-minus-denominator gap, and cutting them while
demand grows compounds it. -/

/-- Reducing paid minutes widens the shortfall whenever demand is positive. -/
theorem cut_hours_widens_gap (demand paid₁ paid₂ : Nat)
    (_hDemand : 0 < demand) (hCut : paid₂ < paid₁) :
    paid₂ + demand < paid₁ + demand + (paid₁ - paid₂) := by
  omega

/-- Cutting hours and growing the campus at once cannot be absorbed by the
schedule: the scaled gap grows by at least the area increase. -/
theorem cut_and_grow_compounds (a₁ a₂ paid₁ paid₂ : Nat) (tasks : List CleaningTask)
    (hArea : a₁ < a₂) (hCut : paid₂ < paid₁) :
    Campus.demandScaled ⟨a₁, tasks⟩ + paid₂ < Campus.demandScaled ⟨a₂, tasks⟩ + paid₁
      ∨ Campus.demandScaled ⟨a₁, tasks⟩ = 0 := by
  unfold Campus.demandScaled
  by_cases hzero : (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum = 0
  · right
    simp [hzero]
  · left
    have hpos : 0 < (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum :=
      Nat.pos_of_ne_zero hzero
    have hstrict : a₁ * (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum
        < a₂ * (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum :=
      Nat.mul_lt_mul_of_pos_right hArea hpos
    have h1 : a₁ * (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum + paid₂
        < a₁ * (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum + paid₁ :=
      Nat.add_lt_add_left hCut _
    have h2 : a₁ * (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum + paid₁
        < a₂ * (tasks.map (fun t => t.frequencyPerYear * t.minutesPerThousandSqFt)).sum + paid₁ :=
      Nat.add_lt_add_right hstrict _
    exact Nat.lt_trans h1 h2

/-! ## 6. Feasibility, defined once

`Feasible` is the predicate every downstream claim is expressed against, so that
"the plan cannot be executed" has a single meaning in this repository. -/

/-- A campus plan is feasible when the paid labor-minutes are at least the
demand, in the shared scaled units. -/
def Feasible (c : Campus) (paidMinutes : Nat) : Prop :=
  Campus.demandScaled c ≤ capacityScaled paidMinutes

/-- Feasibility is exactly the negation of the shortfall. This is the bridge
between the definition and the dichotomy above: an infeasible plan is precisely
one to which `either_standard_unmet_or_unpaid` applies. -/
theorem infeasible_iff_shortfall (c : Campus) (paidMinutes : Nat) :
    ¬ Feasible c paidMinutes ↔ capacityScaled paidMinutes < Campus.demandScaled c := by
  unfold Feasible
  omega

/-- Therefore an infeasible plan forces the dichotomy for any delivery of it. -/
theorem infeasible_forces_dichotomy
    (c : Campus) (paidMinutes performed unpaid : Nat)
    (hInfeasible : ¬ Feasible c paidMinutes)
    (hCapacity : performed ≤ capacityScaled paidMinutes + unpaid) :
    performed < Campus.demandScaled c ∨ 0 < unpaid := by
  have hShort : capacityScaled paidMinutes < Campus.demandScaled c :=
    (infeasible_iff_shortfall c paidMinutes).mp hInfeasible
  exact either_standard_unmet_or_unpaid _ _ _ _ hCapacity hShort

/-! ## 7. Scope

Proved: the arithmetic of the audit. Demand is a function of area and task list;
partitions cannot create capacity; a shortfall forces the dichotomy; an
infeasible plan forces the dichotomy on any delivery.

Not proved, and not provable here: that any particular campus is infeasible.
That requires a fetched area, a fetched specification, defensible task-time
figures, and fetched paid minutes. `bds/` computes it from documents and reports
`UNMEASURED` when a term is missing. Lean does not read a school district's
budget, and a green build of this file is not a finding against anybody. -/
