/-!
# L1 LIFELINE — What the Framework Would Need to Be True (2026-10-24)

`docs/arc/LIFELINE.txt` proposes a mechanism: a neurochemical profile
(adrenergic surge, prolactin rise / dopamine decline) that replaces a
compulsive loop's context rather than fighting its content, producing what the
file calls a "refractory state."

`docs/arc/WALL_OF_SHAME.txt` contains the framework's own most serious critique,
and the framework's author AI conceding the point:

> "the prolactin-refractory link is correlational in the human literature and
> contested in the animal literature ... **the lock is currently an inference,
> and the framework should say so.**"

That concession is the honest center of this file, and it determines what can
be proved here.

## What this file proves, and what it refuses to prove

**It does NOT prove the biology.** No theorem below says garlic raises
noradrenaline, that prolactin causes refractoriness, or that the profile works.
Lean does not assay plasma, and a proof about a model is not a finding about a
body.

**It proves the argument's dependency structure.** Specifically:

1. `impossibility_requires_lock` — the strong conclusion ("mechanically
   impossible to continue") requires a lock premise. Without it, the argument
   supports at most a weaker, probabilistic claim.
2. `passenger_collapses_lock` — if prolactin is a *passenger* (a correlate)
   rather than a *driver* (a cause), the lock premise is unsupported, and the
   impossibility conclusion does not follow.
3. `strength_is_not_strength` — a conclusion may not be stronger than its
   weakest load-bearing premise. This is the formal version of the framework's
   own concession.
4. `empirical_premise_is_not_proved` — an empirical premise enters as an
   assumption. It is never discharged here.

## Why this is the honest maximum

When a framework's own critique file says "the lock is currently an inference,
and the framework should say so," the correct formal artifact is not a proof of
the framework. It is a proof of **what the framework needs**. That is what this
file is.

A theorem that says "this conclusion depends on this contested premise" is
worth more than a theorem that hides the dependency, because the first can be
checked against the literature and the second cannot.

Run: `lean L1_LIFELINE.lean`
-/

/-! ## 1. Claim strength -/

/-- How strong a claim is. `impossible` is strictly stronger than `unlikely`,
    which is strictly stronger than `unsupported`. -/
inductive Strength where
  | impossible
  | unlikely
  | unsupported
deriving DecidableEq, Repr

/-- Rank, for comparison. -/
def Strength.rank : Strength → Nat
  | .impossible => 2
  | .unlikely => 1
  | .unsupported => 0

/-- `a` is at least as strong as `b`. Boolean so it decides. -/
def atLeast (a b : Strength) : Bool := decide (b.rank ≤ a.rank)

theorem impossible_at_least_unlikely : atLeast .impossible .unlikely = true := by decide
theorem unlikely_at_least_unsupported : atLeast .unlikely .unsupported = true := by decide

/-- Strength is not symmetric: `unlikely` does not support `impossible`. -/
theorem unlikely_not_at_least_impossible : atLeast .unlikely .impossible = false := by decide

/-! ## 2. The framework's premises, named -/

/-- The premises the LIFELINE argument actually rests on.

    Each is an empirical assumption. None is proved here. The fields are the
    framework's own commitments, transcribed from `docs/arc/LIFELINE.txt`. -/
structure Premises where
  /-- Garlic organosulfur compounds raise plasma noradrenaline (rat data;
      direction confirmed in the source file). -/
  adrenergicSurge : Bool
  /-- Prolactin rises and dopamine declines after orgasm (correlational). -/
  prolactinRise : Bool
  /-- Prolactin *causes* receptor-level unavailability, rather than being a
      downstream correlate. **This is the contested premise.** -/
  prolactinIsDriver : Bool
  /-- Replacing neurochemical context can outcompete a cue-driven loop. -/
  contextReplacesContent : Bool

/-- Whether the mechanism has its lock: prolactin must both rise and be the
    driver. A rise alone is a correlate, not a lock. -/
def Premises.hasLock (p : Premises) : Bool :=
  p.prolactinRise && p.prolactinIsDriver

/-- The strongest conclusion the premises support.

    This is the formal core. `impossible` is reached only when the lock holds.
    Without the driver premise, the best available claim is `unlikely`. -/
def Premises.claim (p : Premises) : Strength :=
  if !p.adrenergicSurge then .unsupported
  else if !p.contextReplacesContent then .unsupported
  else if p.hasLock then .impossible
  else .unlikely

/-! ## 3. The dependency theorem -/

/-- **`impossibility_requires_lock`.** If the framework's conclusion is
    "mechanically impossible," then the lock premise holds. Contrapositive:
    without the lock, that conclusion is not derivable from these premises.

    This is deliberately a statement about the *argument*, not the world. It
    says: whoever asserts "impossible" is committed to prolactin being a
    driver. -/
theorem impossibility_requires_lock (p : Premises)
    (h : p.claim = .impossible) : p.hasLock = true := by
  unfold Premises.claim at h
  split at h
  · simp_all
  · split at h
    · simp_all
    · split at h
      · assumption
      · simp at h

/-- **`passenger_collapses_lock`.** If prolactin is a passenger — it rises but
    does not drive — then the framework's own claim function cannot reach
    `impossible`, no matter what else is true. -/
theorem passenger_collapses_lock (p : Premises)
    (hrise : p.prolactinRise = true) (hpassenger : p.prolactinIsDriver = false) :
    p.claim ≠ .impossible := by
  intro h
  have hlock := impossibility_requires_lock p h
  unfold Premises.hasLock at hlock
  rw [hrise, hpassenger] at hlock
  exact Bool.noConfusion hlock

/-- The same collapse, stated without needing the rise premise: if the driver
    premise fails, the lock fails. -/
theorem no_driver_no_lock (p : Premises) (h : p.prolactinIsDriver = false) :
    p.hasLock = false := by
  unfold Premises.hasLock
  rw [h]
  simp

/-! ## 4. A conclusion may not exceed its weakest premise -/

/-- **`strength_is_not_strength`.** The framework's claim strength is bounded
    by the contested premise: with the driver premise absent, the strongest
    available conclusion is `unlikely`.

    This is the formal form of the framework's own concession — "the lock is
    currently an inference" — and it is the reason the LIFELINE document
    should not be read as establishing impossibility. -/
theorem strength_bounded_by_driver (p : Premises)
    (hsurge : p.adrenergicSurge = true)
    (hcontext : p.contextReplacesContent = true)
    (hpassenger : p.prolactinIsDriver = false) :
    p.claim = .unlikely := by
  unfold Premises.claim
  rw [hsurge, hcontext, no_driver_no_lock p hpassenger]
  simp

/-- With no adrenergic premise, nothing at all is supported — not even
    `unlikely`. Both empirical premises are load-bearing. -/
theorem no_surge_no_claim (p : Premises) (h : p.adrenergicSurge = false) :
    p.claim = .unsupported := by
  unfold Premises.claim
  rw [h]
  simp

/-- With no context-replacement premise, likewise nothing is supported. -/
theorem no_context_no_claim (p : Premises) (h : p.contextReplacesContent = false) :
    p.claim = .unsupported := by
  unfold Premises.claim
  cases p.adrenergicSurge
  · simp
  · simp [h]

/-! ## 5. The four premise combinations, enumerated

With both structural premises held, exactly two of the four driver/rise
combinations reach `impossible`. The other two reach `unlikely`. -/

/-- Rise + driver → impossible. -/
theorem rise_and_driver_is_impossible :
    ({ adrenergicSurge := true, prolactinRise := true, prolactinIsDriver := true,
       contextReplacesContent := true } : Premises).claim = .impossible := by decide

/-- Rise + passenger → unlikely. The contested case. -/
theorem rise_and_passenger_is_unlikely :
    ({ adrenergicSurge := true, prolactinRise := true, prolactinIsDriver := false,
       contextReplacesContent := true } : Premises).claim = .unlikely := by decide

/-- No rise + driver → unlikely (the lock needs the rise *and* the driver). -/
theorem no_rise_is_unlikely :
    ({ adrenergicSurge := true, prolactinRise := false, prolactinIsDriver := true,
       contextReplacesContent := true } : Premises).claim = .unlikely := by decide

/-- Neither → unlikely. -/
theorem neither_is_unlikely :
    ({ adrenergicSurge := true, prolactinRise := false, prolactinIsDriver := false,
       contextReplacesContent := true } : Premises).claim = .unlikely := by decide

/-!
## What this file establishes

1. `impossibility_requires_lock` — "mechanically impossible" commits you to
   prolactin being a driver.
2. `passenger_collapses_lock` — if it is a passenger, that conclusion is not
   reachable.
3. `strength_bounded_by_driver` — with the driver premise absent, `unlikely` is
   the ceiling.
4. `no_surge_no_claim`, `no_context_no_claim` — both empirical premises are
   load-bearing; removing either collapses the claim entirely.
5. The four-case enumeration makes the contested case visible as one of four,
   not as the whole framework.

## What this file does not establish

Nothing about garlic, noradrenaline, prolactin, dopamine, addiction, or any
person. Every biological statement above sits inside a `Bool` field named as an
assumption. Proving a dependency is not proving a premise, and this file says
so in its first paragraph rather than in a footnote.

The next step the framework actually needs is not more proof. It is the
intervention study its own critique named: prolactin administration without the
act, measuring cue reactivity. Until that exists, the honest claim strength is
`unlikely`, and this file gives the framework the vocabulary to say so.
-/
