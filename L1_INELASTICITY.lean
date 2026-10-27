/-!
# L1 INELASTICITY — the published totals are not the mean of the published levels

`historical_tests/PHASE_4_TRUTH_INELASTICITY_REPORT.md` records four candidates
with explanatory-debt totals:

| Candidate | Debt |
| :--- | ---: |
| C₂ Jesus | 6.5 |
| C₃ Muhammad | 6.8 |
| C₄ Composite | 7.2 |
| C₁ None | 7.5 |

and, for each candidate, a qualitative level per debt category. The report also
states (line 233) "No hidden criteria or weighting" and (line 251) "Axis
Weighting Implicit: Equal weighting assumed but debatable".

This file tests those two statements against each other. Under equal weighting —
the only aggregation the report names — each total is the mean of its category
levels. Write the level values in tenths of a point so the arithmetic is
integral, and let `H`, `M`, `LM`, `MH` be the values of the levels *High*,
*Medium*, *Low-Medium*, and *Medium-High*.

The published categories are:

- C₂ {High, High, Medium, Medium, Low-Medium, Medium} = 6.5
- C₃ {Medium-High, Medium, Medium-High, Low-Medium, Medium, Medium} = 6.8
- C₄ {High, High, Medium, Medium-High, Medium, Medium} = 7.2

Clearing the denominator of 6 gives three equations. This file proves that **no
level assignment satisfies them together with the monotonicity of the levels**:
`High` would have to be below `Medium-High`, which contradicts what the words
mean.

## What this proves, and what it does not

**It proves** the four totals are not the unweighted mean of the published
category levels. The numbers and the levels cannot both be taken at face value,
so at least one of the two statements at lines 233 and 251 is inaccurate, and
the derivation of 6.5 / 6.8 / 7.2 / 7.5 is not published.

**It does not prove** that the ordering is wrong. 6.5 < 6.8 < 7.2 < 7.5 is
untouched here: an ordering can hold while its derivation is missing. It does
not show C₂ is not truth-inelastic, and it says nothing about any theological
claim. A bookkeeping defect in a report is a defect in the report.

The honest status of the four numbers is therefore exactly what the project's
own constitution already says: **recorded judgements, not machine-checked
output** — now with the specific reason localized.

Run: `lean L1_INELASTICITY.lean`
-/

/-- The four level values, in tenths of a point. -/
structure Levels where
  /-- Value of "Low-Medium". -/
  lm : Int
  /-- Value of "Medium". -/
  m : Int
  /-- Value of "Medium-High". -/
  mh : Int
  /-- Value of "High". -/
  h : Int

/-- The levels are ordered as their names say. Without this, the words carry no
information and any four numbers could be fitted. -/
def Levels.monotone (v : Levels) : Prop :=
  v.lm ≤ v.m ∧ v.m ≤ v.mh ∧ v.mh ≤ v.h

/-- C₂ {H,H,M,M,LM,M} averaged over six categories equals 6.5, in tenths. -/
def c2Mean (v : Levels) : Int := 2 * v.h + 3 * v.m + v.lm

/-- C₃ {MH,M,MH,LM,M,M} averaged over six categories equals 6.8. -/
def c3Mean (v : Levels) : Int := 2 * v.mh + 3 * v.m + v.lm

/-- C₄ {H,H,M,MH,M,M} averaged over six categories equals 7.2. -/
def c4Mean (v : Levels) : Int := 2 * v.h + 3 * v.m + v.mh

/-- 6.5 · 6 = 39, and in tenths 390. -/
def C2_TOTAL : Int := 390
/-- 6.8 · 6 = 40.8, and in tenths 408. -/
def C3_TOTAL : Int := 408
/-- 7.2 · 6 = 43.2, and in tenths 432. -/
def C4_TOTAL : Int := 432

/-- **The core result.** C₂ and C₃ differ in only two categories: C₂ has `High`
where C₃ has `Medium-High`, and the remaining four levels are identical. Since
`Medium-High ≤ High`, C₃'s mean cannot exceed C₂'s under equal weighting. The
report publishes C₂ = 6.5 and C₃ = 6.8, i.e. C₃ *above* C₂. Those two totals
cannot both be the mean of the levels as written.

No appeal to C₄ is needed, and no appeal to any theological claim. -/
theorem c3_cannot_exceed_c2 (v : Levels)
    (hmono : v.monotone)
    (h2 : c2Mean v = C2_TOTAL)
    (h3 : c3Mean v = C3_TOTAL) :
    False := by
  obtain ⟨_, _, h_mh_h⟩ := hmono
  unfold c2Mean C2_TOTAL at h2
  unfold c3Mean C3_TOTAL at h3
  omega

/-- The same contradiction stated over all three published totals. The C₄
equation is included for completeness but is not needed: the inconsistency is
already present in the first two. -/
theorem no_equal_weight_assignment (v : Levels)
    (hmono : v.monotone)
    (h2 : c2Mean v = C2_TOTAL)
    (h3 : c3Mean v = C3_TOTAL)
    (_h4 : c4Mean v = C4_TOTAL) :
    False :=
  c3_cannot_exceed_c2 v hmono h2 h3

/-- The same result stated as a negation, so the claim is readable without
unfolding the definitions. -/
theorem no_monotone_fit :
    ¬ ∃ v : Levels, v.monotone ∧
      c2Mean v = C2_TOTAL ∧ c3Mean v = C3_TOTAL ∧ c4Mean v = C4_TOTAL := by
  intro ⟨v, hmono, h2, h3, h4⟩
  exact no_equal_weight_assignment v hmono h2 h3 h4

/-! ## A separate structural defect: the denominators differ

C₂, C₃, and C₄ each list six debt categories. C₁ lists five. A mean over five
categories and a mean over six are not the same scale, so C₁'s 7.5 is not
comparable to the others unless a normalization is stated. The report states
none.

This file does not claim C₁'s total is wrong; it claims the comparison as
written lacks a common basis, which is why the number cannot be recomputed.
-/

/-- Six categories, five categories: the denominators are not equal, so equal
weighting does not imply equal scale. -/
theorem category_counts_differ : (6 : Nat) ≠ 5 := by decide

/-! ## Reproducing the defect

`burden/tools/inelasticity-check.ts` is the executable arm: it encodes the
published levels, computes what the totals would be under a declared monotone
mapping, and searches for any integer monotone assignment that fits. It reports
no fit, which agrees with the theorem above. A theorem about a model plus an
executable that agrees with it is evidence; the theorem alone would not be.

The executable also carries a round-trip control: a mapping is converted to its
own totals and back, and must return the mapping. Without that control an
arithmetic error in the tool would look exactly like a defect in the report.

`burden/negative/INELASTICITY_FIT_EXISTS.lean` is the falsifier: it asserts that
a monotone fit exists and must fail to compile. -/
