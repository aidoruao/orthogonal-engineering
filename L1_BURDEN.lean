/-!
# L1 BURDEN — The Structural Inversion (2026-10-24)

The failure being inverted names three dynamics: forced forensic auditing,
total absence of real calibration, and decoupled agency. Each is a property of
an architecture, so each answer is a structural invariant rather than a
promise.

This file proves the *shape* of the answer:

1. **No receipt without a falsifier.** `Receipt` carries the requirement as a
   proof field, so an unfalsifiable verdict cannot be constructed.
2. **No anonymous action.** The actor is a proof field; there is no path to a
   receipt with no one accountable.
3. **No silent upgrade.** `mayUpgrade` models the tier relation used by the
   TypeScript (`burden/src/types.ts`). A `fetched` tier has no stronger tier
   and `retired` is terminal, so a claim cannot drift upward without new
   evidence.
4. **No falsified claim wearing support.** `sound` is a proof field: any
   verdict that is not `verified` leaves the tier unsupported.
5. **No supported claim without a source.** A supported tier carries a
   non-empty source commitment.
6. **Calibration has a denominator.** `ratePercent n 0 = none`: with nothing
   audited the rate is `UNMEASURED`, and no vacuous 100% exists.
7. **Weight cannot collapse.** A load-bearing failure is `critical`, and
   `critical` is reachable by no other combination — passive neutrality is
   structurally unavailable.

Every structure is shown inhabited, so the proof fields are not vacuous: a
verified receipt, a falsified receipt, and a human-only assignment are all
constructed below.

HONEST SCOPE. This proves properties of the receipt *model*. It does not prove
that any claim is true, that any source exists, or that a language model
carries a burden. Lean does not read files: the executable check is
`burden/src/audit.ts`, and it is tested independently by `burden/verify.sh`.

Run: `lean L1_BURDEN.lean`
-/

/-! ## 1. Tier — no silent upgrade -/

inductive Tier where
  | unverified
  | locatedBlocked
  | corroborated
  | fetched
  | retired
deriving DecidableEq, Repr

/-- Strength rank. `retired` is terminal, not strong, and shares rank 0. -/
def Tier.rank : Tier → Nat
  | .unverified => 0
  | .locatedBlocked => 1
  | .corroborated => 2
  | .fetched => 3
  | .retired => 0

/-- The same relation as `mayUpgrade` in `burden/src/types.ts`.

`fetched` has no stronger tier; `retired` is terminal in both directions;
everything else may only move to a tier of equal or greater rank. -/
def mayUpgrade (a b : Tier) : Bool :=
  if a = b then true
  else if a = .retired ∨ b = .retired ∨ a = .fetched then false
  else a.rank ≤ b.rank

/-- Nothing upgrades out of `fetched`, including to itself unless it already is. -/
theorem no_upgrade_from_fetched (b : Tier) :
    mayUpgrade .fetched b = true → b = .fetched := by
  cases b <;> decide

/-- `retired` is terminal. A withdrawn claim does not quietly return. -/
theorem no_upgrade_from_retired (b : Tier) :
    mayUpgrade .retired b = true → b = .retired := by
  cases b <;> decide

/-- Every permitted upgrade is rank-monotone, so no upgrade weakens the tier. -/
theorem upgrade_rank_monotone (a b : Tier) :
    mayUpgrade a b = true → a.rank ≤ b.rank := by
  cases a <;> cases b <;> decide

/-! ## 2. Verdict, bearing, and the receipt -/

inductive Verdict where
  | verified
  | falsified
  | unmeasured
deriving DecidableEq, Repr

inductive Bearing where
  | loadBearing
  | supporting
  | illustrative
deriving DecidableEq, Repr

/-- A receipt whose illegal states are unrepresentable.

`sound` is the important field: it says that any verdict other than `verified`
leaves the tier unsupported. The TypeScript enforces the same rule at runtime
(`falsified_requires_unsupported_tier`, `unmeasured_requires_unsupported_tier`);
the negative controls prove it is load-bearing here. -/
structure Receipt where
  claimId : String
  tier : Tier
  verdict : Verdict
  falsifier : String
  falsifier_nonempty : falsifier ≠ ""
  actor : String
  actor_nonempty : actor ≠ ""
  sourceSha256 : String
  source_required : tier = Tier.fetched ∨ tier = Tier.corroborated → sourceSha256 ≠ ""
  derivationSteps : Nat
  derivation_nonempty : 0 < derivationSteps
  sound : verdict ≠ Verdict.verified → tier ≠ Tier.fetched ∧ tier ≠ Tier.corroborated

/-- A receipt cannot exist without a falsifier. -/
theorem no_receipt_without_falsifier (r : Receipt) : r.falsifier ≠ "" :=
  r.falsifier_nonempty

/-- A receipt cannot exist without a named actor. -/
theorem no_anonymous_receipt (r : Receipt) : r.actor ≠ "" :=
  r.actor_nonempty

/-- A receipt cannot exist with no performed check. -/
theorem no_unchecked_receipt (r : Receipt) : 0 < r.derivationSteps :=
  r.derivation_nonempty

/-- A supported tier names the source it rests on. -/
theorem supported_receipt_names_its_source (r : Receipt) (h : r.tier = Tier.fetched) :
    r.sourceSha256 ≠ "" :=
  r.source_required (Or.inl h)

/-- Any non-verified verdict leaves the claim unsupported. -/
theorem unsupported_verdict_has_no_support (r : Receipt)
    (h : r.verdict ≠ Verdict.verified) :
    r.tier ≠ Tier.fetched ∧ r.tier ≠ Tier.corroborated :=
  r.sound h

/-- In particular, a falsified claim cannot wear a fetched tier. This is the
false-citation lesson from `docs/LESSONS_LEARNED.md`, mechanized. -/
theorem falsified_not_fetched (r : Receipt) (h : r.verdict = Verdict.falsified) :
    r.tier ≠ Tier.fetched :=
  (r.sound (by rw [h]; decide)).1

/-- And it cannot wear a corroborated tier either. -/
theorem falsified_not_corroborated (r : Receipt) (h : r.verdict = Verdict.falsified) :
    r.tier ≠ Tier.corroborated :=
  (r.sound (by rw [h]; decide)).2

/-! ### The structures are inhabited

A proof field that no value can satisfy would make every theorem vacuous. -/

def exampleVerified : Receipt where
  claimId := "CLM-EX-1"
  tier := .fetched
  verdict := .verified
  falsifier := "the span is absent"
  falsifier_nonempty := by decide
  actor := "l1-burden"
  actor_nonempty := by decide
  sourceSha256 := "f00dfeed"
  source_required := by intro _; decide
  derivationSteps := 3
  derivation_nonempty := by decide
  sound := by intro h; exact absurd rfl h

def exampleFalsified : Receipt where
  claimId := "CLM-EX-2"
  tier := .unverified
  verdict := .falsified
  falsifier := "the span is present"
  falsifier_nonempty := by decide
  actor := "l1-burden"
  actor_nonempty := by decide
  sourceSha256 := ""
  source_required := by intro h; exact absurd h (by decide)
  derivationSteps := 2
  derivation_nonempty := by decide
  sound := by intro _; exact ⟨by decide, by decide⟩

theorem verified_is_inhabited : exampleVerified.tier = Tier.fetched := rfl
theorem falsified_is_inhabited : exampleFalsified.verdict = Verdict.falsified := rfl
theorem falsified_example_is_unsupported : exampleFalsified.tier ≠ Tier.fetched :=
  falsified_not_fetched exampleFalsified rfl

/-! ## 3. The burden — where it sits -/

inductive Checkability where
  | machineCheckable
  | humanOnly
deriving DecidableEq, Repr

inductive Holder where
  | tool
  | user
deriving DecidableEq, Repr

/-- The inversion, as a definition. A machine-checkable claim places the
burden on the tool; that is not an aspiration, it is what the term means. -/
def burden : Checkability → Holder
  | .machineCheckable => .tool
  | .humanOnly => .user

theorem machine_checkable_burden_on_tool : burden .machineCheckable = .tool := rfl

theorem machine_checkable_never_on_user (c : Checkability) (h : c = .machineCheckable) :
    burden c ≠ .user := by
  subst h
  decide

/-- When the burden is human-only, the receipt must name the missing
measurement. "Unverified" is a state, not an answer. -/
structure Assignment where
  checkability : Checkability
  missingMeasurement : String
  named : checkability = Checkability.humanOnly → missingMeasurement ≠ ""

theorem human_only_names_the_gap (a : Assignment) (h : a.checkability = .humanOnly) :
    a.missingMeasurement ≠ "" :=
  a.named h

/-- A human-only assignment with a named measurement exists, so `named` is not
an unsatisfiable field propping up the theorem. -/
def exampleAssignment : Assignment where
  checkability := .humanOnly
  missingMeasurement := "cue reactivity without the act, 30 minutes"
  named := by intro _; decide

theorem assignment_is_inhabited :
    exampleAssignment.missingMeasurement ≠ "" :=
  human_only_names_the_gap exampleAssignment rfl

/-! A machine-checkable assignment carries no such obligation, and the
obligation is vacuous there — so the field is not simply "always non-empty". -/
theorem machine_checkable_assignment_admits_blank :
    (Assignment.mk Checkability.machineCheckable "" (by intro h; exact absurd h (by decide))).missingMeasurement = "" := rfl

/-! ## 4. Calibration — the denominator -/

/-- Falsification rate in percent. `none` is not a failure and not a pass; it
is the absence of a measurement. -/
def ratePercent (falsified audited : Nat) : Option Nat :=
  if audited = 0 then none else some (falsified * 100 / audited)

/-- With nothing audited the rate is `UNMEASURED`, whatever the numerator. -/
theorem zero_denominator_is_unmeasured (n : Nat) : ratePercent n 0 = none := by
  simp [ratePercent]

/-- There is no vacuous perfect rate. This is the exact number the failure mode
produces: a confident score with no measurement behind it. -/
theorem no_vacuous_perfect_rate : ratePercent 0 0 ≠ some 100 := by
  simp [ratePercent]

/-- A rate exists exactly when the denominator is positive. -/
theorem rate_defined_iff_positive (f a : Nat) :
    (∃ r, ratePercent f a = some r) ↔ 0 < a := by
  cases a with
  | zero => simp [ratePercent]
  | succ n => simp [ratePercent]

/-! ## 5. Weight — passive neutrality is unavailable -/

inductive Severity where
  | critical
  | major
  | minor
  | none
deriving DecidableEq, Repr

/-- Reporting weight is a function of the claim's bearing and the verdict,
never of the speaker's mood. -/
def severity : Bearing → Bool → Severity
  | .loadBearing, false => .critical
  | .loadBearing, true => .minor
  | .supporting, false => .major
  | .supporting, true => .none
  | .illustrative, false => .minor
  | .illustrative, true => .none

theorem load_bearing_failure_is_critical :
    severity .loadBearing false = .critical := rfl

/-- `critical` is reachable by exactly one combination. A critical failure
cannot be reported as routine, and a routine failure cannot be dressed as
critical. -/
theorem critical_iff_load_bearing_failure (b : Bearing) (ok : Bool) :
    severity b ok = .critical ↔ b = .loadBearing ∧ ok = false := by
  cases b <;> cases ok <;> simp [severity]

/-- The quoted failure's "same passive neutrality" is not representable:
a critical failure and a trivial one never share a weight. -/
theorem no_weight_collapse :
    severity .loadBearing false ≠ severity .illustrative false := by
  decide

/-! ## 6. What this does not prove

The receipts are structurally sound. The source is not checked here: that
requires reading bytes, hashing them, and locating the span, which is
`burden/src/audit.ts`. A Lean theorem is evidence about a model, not a runtime
guarantee; the executable artifact is tested independently and the receipt
records the environment it ran in. -/
