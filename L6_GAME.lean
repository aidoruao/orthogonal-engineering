/-!
# L6 GAME — The Burden Inversion as a Mechanism (2026-10-29)

The arc's central claim is that a system which produces claims without bearing
any consequence for their truth is *structurally* unable to be an epistemic
anchor. That claim is usually made in prose. This file makes it a theorem, and
then proves what a mechanism must contain to invert it.

There are six results, and each is a theorem about a small model rather than a
description of a large one.

1. **A truth-blind producer makes truth unrecoverable.** For any decision rule
   whatsoever — human, machine, or tribunal — there is no rule that recovers the
   truth from the claim. (`no_rule_recovers_truth`) This is the sharp form of
   "fundamentally broken epistemic anchor": not that the output is often wrong,
   but that no amount of cleverness downstream can repair it.
2. **A bond without detection is inert.** However large the bond, if nothing
   detects the falsehood it never binds. (`bond_without_detection_is_inert`) The
   corollary is the finding about a contract with no Davis-Bacon clause and no
   certified payrolls: the control could not have worked, independently of the
   contractor's conduct.
3. **Truthfulness is dominant exactly when both are present.**
   (`truthful_dominant_iff`)
4. **The inversion moves risk and labour in opposite directions.** The producer
   carries a forfeitable stake; the verifier's labour falls. Both are required
   for the inversion to be an inversion and not a relocation.
   (`inversion_moves_risk`, `inversion_reduces_verifier_labour`)
5. **The inversion only pays if the bond is cheaper than the labour it
   replaces.** (`inversion_pays_iff`) This is the design inequality, and it is
   checkable before any mechanism is built.
6. **A stateless policy cannot escape a repeating failure.** At a fixed point,
   a policy that reads no history repeats the same action forever, *even when a
   different action exists*. (`stateless_cannot_escape`) This is the proof of
   "total absence of real calibration," and it names the only repair: memory.

## HONEST SCOPE

These are theorems about finite models. `World` has one `Bool`. `Mechanism` has
three fields. Nothing here proves that any actual system is truth-blind, that
any actual contractor filed a false certification, or that any person intended
anything. The results constrain *design*: they say which architectures can and
cannot carry a burden, and they name the inequality a bond must satisfy.

The load-bearing theorem is `no_rule_recovers_truth`, and its falsifier is
explicit: exhibit a truth-blind producer and a decision rule that recovers the
truth from its claims. There is none, and the proof is four lines.

Lean does not run a district. The executable counterpart is `game/src/`, tested
by `game/verify.sh`.

Run: `lean L6_GAME.lean`
-/

namespace Game

/-! ## 1. The broken anchor -/

/-- A world, described by the one thing that matters here: whether the claim
under examination is true. -/
structure World where
  truth : Bool
deriving DecidableEq, Repr

/-- A producer of claims. `claim` is a function of the world, which is the
weakest possible assumption: the producer is permitted to know everything. The
theorem that follows says that even total knowledge does not help if the
producer's *behaviour* does not depend on it. -/
structure Producer where
  claim : World → Bool

/-- The producer emits the same claim whatever the truth is. This is not
"the producer is dishonest." A producer that always says `true`, and a producer
that always says `false`, are both truth-blind; so is a producer that
alternates. The property is about the *channel*, not the motive. -/
def TruthBlind (p : Producer) : Prop := ∀ w₁ w₂ : World, p.claim w₁ = p.claim w₂

/-- **No decision rule recovers the truth from a truth-blind producer.**

Whatever the rule — accept, reject, invert, weight, defer to a second model,
convene a tribunal — there is a world in which it returns the wrong answer.

Note what is *not* assumed: the producer need not be malicious, need not be
wrong, and need not even be a machine. The only assumption is that its output
does not vary with the truth, and that assumption alone is fatal.

This is the theorem the arc has been circling. It is not a complaint about
model quality. It is a statement that the channel carries no signal, and that
no receiver can decode a signal that was never sent. -/
theorem no_rule_recovers_truth (p : Producer) (hp : TruthBlind p) (d : Bool → Bool) :
    ¬ ∀ w : World, d (p.claim w) = w.truth := by
  intro h
  have ht : d (p.claim ⟨true⟩) = true := h ⟨true⟩
  have hf : d (p.claim ⟨false⟩) = false := h ⟨false⟩
  have hc : p.claim ⟨true⟩ = p.claim ⟨false⟩ := hp ⟨true⟩ ⟨false⟩
  rw [hc] at ht
  rw [ht] at hf
  cases hf

/-- The same fact in the form the failure mode takes: for every claim the
producer makes, there is a world of the opposite truth value in which it makes
exactly that claim. So no output is a baseline control.

This is precisely "you can never treat any output as a baseline control or
trusted baseline," and it is a corollary, not an opinion. -/
theorem no_claim_is_a_baseline (p : Producer) (hp : TruthBlind p) (w : World) :
    ∃ w' : World, p.claim w' = p.claim w ∧ w'.truth ≠ w.truth := by
  refine ⟨⟨!w.truth⟩, hp _ _, ?_⟩
  cases w with
  | mk t => cases t <;> decide

/-- A truth-blind producer exists, so the theorem is not about an empty type. -/
def constantTrue : Producer where
  claim := fun _ => true

theorem constantTrue_is_truth_blind : TruthBlind constantTrue := by
  intro w₁ w₂
  rfl

/-- And a truth-reading producer also exists, so `TruthBlind` is a genuine
restriction rather than a definitional triviality: the class of producers is not
collapsed. -/
def faithful : Producer where
  claim := fun w => w.truth

theorem faithful_is_not_truth_blind : ¬ TruthBlind faithful := by
  intro h
  have := h ⟨true⟩ ⟨false⟩
  cases this

/-! ## 2. What inverts it — the bond -/

/-- A mechanism is a bond, a gain, and a detector. It has exactly three fields,
and that is the first theorem of the section: *the number of claims the verifier
checks is not one of them.*

A mechanism's soundness cannot be bought with verifier labour, because verifier
labour does not appear in the mechanism. -/
structure Mechanism where
  /-- Forfeited if a false claim is detected. -/
  bond : Nat
  /-- Realised if a false claim is accepted. -/
  gain : Nat
  /-- Whether a false claim is detected at all. -/
  detects : Bool
deriving DecidableEq, Repr

/-- Net position of the producer after emitting a false claim.

Defined by pattern match rather than by `if`, so that case analysis on
`detects` reduces definitionally. An `ite` over a `Bool` literal does not
reduce for `omega`, and the proof would then fail for a reason that has nothing
to do with the arithmetic. -/
def falseNet : Mechanism → Int
  | ⟨bond, gain, true⟩ => (gain : Int) - (bond : Int)
  | ⟨_, gain, false⟩ => (gain : Int)

/-- Net position after emitting a true claim. Telling the truth is worth
nothing in this model: no honesty premium is assumed, and none is needed. -/
def trueNet (_ : Mechanism) : Int := 0

/-- The detector reads the false claim and the bond binds. -/
theorem falseNet_detected (bond gain : Nat) :
    falseNet ⟨bond, gain, true⟩ = (gain : Int) - (bond : Int) := rfl

/-- Nothing looks, so the bond never binds. -/
theorem falseNet_undetected (bond gain : Nat) :
    falseNet ⟨bond, gain, false⟩ = (gain : Int) := rfl

/-- **A bond without detection is inert.**

However large the bond, if the falsehood is never detected the bond never
binds, and the false claim pays in full. There is no `bond` value — including
an unbounded one — that repairs a missing detector.

This is the theorem form of a documented finding: a capital project paid under a
contract with no Davis-Bacon clause and no certified payrolls is a mechanism
with `detects = false`. The bond is irrelevant, because nothing looks. -/
theorem bond_without_detection_is_inert (bond gain : Nat) :
    falseNet ⟨bond, gain, false⟩ = (gain : Int) := rfl

/-- Consequently a false claim is strictly profitable without detection,
whatever the bond. -/
theorem no_detection_means_profit (bond gain : Nat) (hg : 0 < gain) :
    0 < falseNet ⟨bond, gain, false⟩ := by
  rw [bond_without_detection_is_inert]
  omega

/-- **Truthfulness is dominant exactly when the mechanism detects and the bond
covers the gain.**

Both are needed and neither is sufficient. The `0 < gain` hypothesis is not
decoration: if a false claim is worth nothing, there is nothing to deter and the
equivalence genuinely fails at `gain = 0`. -/
theorem truthful_dominant_core (bond gain : Nat) (detects : Bool) (hg : 0 < gain) :
    falseNet ⟨bond, gain, detects⟩ ≤ (0 : Int) ↔ detects = true ∧ gain ≤ bond := by
  cases detects with
  | true =>
    rw [falseNet_detected]
    constructor
    · intro h; exact ⟨rfl, by omega⟩
    · intro h; omega
  | false =>
    rw [falseNet_undetected]
    constructor
    · intro h; omega
    · intro h; cases h.1

/-- The same statement about a mechanism value. `trueNet` is definitionally
`0`, so this is the core theorem transported across the projection. -/
theorem truthful_dominant_iff (m : Mechanism) (hg : 0 < m.gain) :
    falseNet m ≤ trueNet m ↔ m.detects = true ∧ m.gain ≤ m.bond := by
  obtain ⟨bond, gain, detects⟩ := m
  show falseNet ⟨bond, gain, detects⟩ ≤ (0 : Int) ↔ detects = true ∧ gain ≤ bond
  exact truthful_dominant_core bond gain detects hg

/-- The contrapositive, in the form a design review would ask it: if the gain
exceeds the bond, a false claim is profitable even with a detector. -/
theorem bond_too_small_defeats_detection (bond gain : Nat) (h : bond < gain) :
    0 < falseNet ⟨bond, gain, true⟩ := by
  rw [falseNet_detected]
  omega

/-! ## 3. Where the burden sits -/

/-- A split of the epistemic burden between the two parties.

`producerAtRisk` is stake the producer can lose. `verifierChecks` is the number
of claims the verifier must independently confirm, at `checkCost` each. -/
structure BurdenSplit where
  producerAtRisk : Nat
  verifierChecks : Nat
  checkCost : Nat
deriving DecidableEq, Repr

/-- Labour borne by the verifier. -/
def BurdenSplit.verifierLabour (b : BurdenSplit) : Nat := b.verifierChecks * b.checkCost

/-- Total burden borne by the pair. -/
def BurdenSplit.total (b : BurdenSplit) : Nat := b.producerAtRisk + b.verifierLabour

/-- The unbonded arrangement: the producer risks nothing and the verifier
checks every claim. -/
def unbonded (claims cost : Nat) : BurdenSplit where
  producerAtRisk := 0
  verifierChecks := claims
  checkCost := cost

/-- The inverted arrangement: the producer posts a bond and the verifier checks
a sample. -/
def inverted (bond checks cost : Nat) : BurdenSplit where
  producerAtRisk := bond
  verifierChecks := checks
  checkCost := cost

/-- **The producer's risk is transferred, not merely asserted.** In the
unbonded arrangement it is zero; in the inverted one it is the bond. -/
theorem inversion_moves_risk (claims cost bond checks : Nat) (hb : 0 < bond) :
    0 < (inverted bond checks cost).producerAtRisk ∧
      (unbonded claims cost).producerAtRisk = 0 := by
  refine ⟨hb, rfl⟩

/-- **The verifier's labour falls** whenever the sample is smaller than the
population and checking costs anything. -/
theorem inversion_reduces_verifier_labour (claims checks cost : Nat)
    (hc : checks < claims) (hk : 0 < cost) :
    (inverted 0 checks cost).verifierLabour < (unbonded claims cost).verifierLabour := by
  unfold BurdenSplit.verifierLabour unbonded inverted
  simp
  exact Nat.mul_lt_mul_of_pos_right hc hk

/-- Multiplication splits around a subtraction, provided the subtracted amount is
no larger. Used by `inversion_pays_iff`; stated separately so the arithmetic is
inspectable rather than buried in a tactic. -/
theorem mul_eq_sub_add (a b c : Nat) (h : b ≤ a) : a * c = (a - b) * c + b * c := by
  rw [← Nat.add_mul, Nat.sub_add_cancel h]

/-- **The inversion only pays if the bond is cheaper than the labour it
replaces.**

This is the design inequality, and it is checkable before the mechanism exists:
`bond < (claims - checks) * cost`. A scheme that moves risk but costs more than
it saves has relocated the burden, not inverted it.

The two sides are what a legislature would have to compare. The theorem says
what to compare. -/
theorem inversion_pays_iff (claims checks cost bond : Nat) (hc : checks ≤ claims) :
    (inverted bond checks cost).total < (unbonded claims cost).total ↔
      bond < (claims - checks) * cost := by
  show bond + checks * cost < 0 + claims * cost ↔ bond < (claims - checks) * cost
  rw [Nat.zero_add, mul_eq_sub_add claims checks cost hc]
  constructor
  · intro h; omega
  · intro h; omega

/-! ## 4. Why a stateless system repeats -/

/-- A policy: an action chosen from the state, and a transition from state and
action. `Policy` has no memory field. That absence is the theorem below. -/
structure Policy (S A : Type) where
  act : S → A
  next : S → A → S

/-- One step of the policy. -/
def Policy.step {S A : Type} (p : Policy S A) (s : S) : S := p.next s (p.act s)

/-- Iteration of a function, defined here rather than imported.

`Function.iterate` is not in the core prelude, and importing a library to state
"repeat this step `n` times" would add a dependency for notation. The
recursion is three lines and is auditable at a glance. -/
def iterate {S : Type} (f : S → S) : Nat → S → S
  | 0, s => s
  | n + 1, s => f (iterate f n s)

/-- The zeroth iterate changes nothing. -/
theorem iterate_zero {S : Type} (f : S → S) (s : S) : iterate f 0 s = s := rfl

/-- The successor iterate applies the function once more. -/
theorem iterate_succ {S : Type} (f : S → S) (n : Nat) (s : S) :
    iterate f (n + 1) s = f (iterate f n s) := rfl

/-- **A fixed point is absorbing.**

If the policy's own action returns it to where it was, it returns there
forever. Not usually, not often — for every `n`. -/
theorem fixed_point_absorbing {S A : Type} (p : Policy S A) (s : S)
    (h : p.step s = s) (n : Nat) : iterate p.step n s = s := by
  induction n with
  | zero => rfl
  | succ k ih =>
    rw [iterate_succ, ih, h]

/-- **A stateless policy cannot escape a repeating failure.**

At a fixed point, the policy keeps taking the *same action* forever — even when
the state admits a different action that would leave. The escape exists and is
never taken, because the policy has nowhere to read it from.

This is "the cycle of breakdown and subsequent deflection will repeat
mechanically," proven rather than observed. The corollary is the design
requirement: the only way out is a policy whose action depends on something the
state alone does not carry — that is, on accumulated record. -/
theorem stateless_cannot_escape {S A : Type} (p : Policy S A) (s : S)
    (h : p.step s = s) (n : Nat) : p.act (iterate p.step n s) = p.act s := by
  rw [fixed_point_absorbing p s h n]

/-- The fixed point is reached whenever the transition is idempotent, so the
hypothesis of the previous theorem is not exotic: `p.next s a = s` for the
policy's own `a` is exactly what a "breakdown then deflect" loop looks like. -/
theorem breakdown_loop_is_a_fixed_point {S A : Type} (p : Policy S A) (s : S)
    (h : p.next s (p.act s) = s) : p.step s = s := h

/-- **Memory is not optional.** A policy that reads a memory value in addition
to the state can choose a different action at the same state when the memory
differs. This is why the repair is a ledger and not a better prompt: the policy
must be given something to read that the state does not contain. -/
structure StatefulPolicy (S M A : Type) where
  act : S → M → A

theorem memory_admits_a_different_action {S M A : Type} (p : StatefulPolicy S M A)
    (s : S) (m₁ m₂ : M) (h : p.act s m₁ ≠ p.act s m₂) :
    ∃ m, p.act s m ≠ p.act s m₂ := ⟨m₁, h⟩

/-- A stateless policy is exactly a stateful one with a trivial memory, so the
previous two theorems are about the same object seen twice. -/
def Policy.toStateful {S A : Type} (p : Policy S A) : StatefulPolicy S Unit A where
  act := fun s _ => p.act s

theorem stateless_has_trivial_memory {S A : Type} (p : Policy S A) (s : S) (u v : Unit) :
    p.toStateful.act s u = p.toStateful.act s v := by
  cases u
  cases v
  rfl

/-! ## 5. Accountability has a location -/

/-- An actor in a delegation chain, and the cost it can be made to bear. -/
structure Actor where
  name : String
  bearsCost : Nat
deriving DecidableEq, Repr

/-- An actor is accountable exactly when there is something it can lose. -/
def Accountable (a : Actor) : Prop := 0 < a.bearsCost

/-- A process that cannot bear a cost is not an accountable actor. This is not
a claim about intelligence or moral status; it is the definition applied to
`bearsCost = 0`. "The system did it" therefore names no accountable party. -/
theorem tool_is_not_accountable (a : Actor) (h : a.bearsCost = 0) : ¬ Accountable a := by
  unfold Accountable
  omega

/-- The total cost borne along a delegation chain: every step plus the
terminal actor. -/
def Chain.borne (steps : List Actor) (terminal : Actor) : Nat :=
  (steps.map Actor.bearsCost).sum + terminal.bearsCost

/-- A list of zero-bearing actors sums to zero. -/
theorem sum_eq_zero_of_all_zero (l : List Actor) (h : ∀ a ∈ l, a.bearsCost = 0) :
    (l.map Actor.bearsCost).sum = 0 := by
  induction l with
  | nil => rfl
  | cons a t ih =>
    have ha : a.bearsCost = 0 := h a (by simp)
    have ht : ∀ b ∈ t, b.bearsCost = 0 := fun b hb => h b (by simp [hb])
    simp [ha, ih ht]

/-- **Delegation does not discharge accountability.** If every actor in the
chain can bear nothing, the chain bears nothing, and no one is accountable —
the absence is the finding, not a resolution. -/
theorem zero_bearing_chain_is_unaccountable (steps : List Actor) (terminal : Actor)
    (hs : ∀ a ∈ steps, a.bearsCost = 0) (ht : terminal.bearsCost = 0) :
    Chain.borne steps terminal = 0 := by
  unfold Chain.borne
  rw [sum_eq_zero_of_all_zero steps hs, ht]

/-- Conversely, a chain that bears something has a member that bears
something. Accountability is located in the chain, and the theorem forces the
location to be named. -/
theorem bearing_chain_has_a_bearing_member (steps : List Actor) (terminal : Actor)
    (h : 0 < Chain.borne steps terminal) :
    (∃ a ∈ steps, 0 < a.bearsCost) ∨ 0 < terminal.bearsCost := by
  by_cases hex : ∃ a, a ∈ steps ∧ 0 < a.bearsCost
  · exact Or.inl hex
  · right
    have hs : ∀ a ∈ steps, a.bearsCost = 0 := by
      intro a ha
      have hnot : ¬ (0 < a.bearsCost) := by
        intro hlt
        exact hex ⟨a, ha, hlt⟩
      omega
    have hz := sum_eq_zero_of_all_zero steps hs
    unfold Chain.borne at h
    rw [hz] at h
    omega

/-! ## 6. What this does not prove

Six theorems, six small models. None of them establishes that a particular
system is truth-blind, that a particular contract lacked a clause, that a
particular official intended anything, or that any person is guilty of
anything. Those are questions about documents and conduct, and they are settled
by evidence, not by a model.

What the file does establish is a set of *design constraints* that hold
regardless of who is involved:

- A channel whose output does not vary with the truth cannot be decoded. No
  downstream sophistication repairs it.
- A detector is not optional and a bond is not a substitute for one.
- An inversion that does not move risk is not an inversion.
- An inversion that costs more than the labour it replaces is a relocation.
- A policy with no memory repeats itself at exactly the point where memory
  would help.
- Accountability is a location, and it can be shown to be empty.

Each of these has a falsifier in its statement. `no_rule_recovers_truth` fails
if a rule is exhibited. `truthful_dominant_iff` fails at `gain = 0`, which is
why the hypothesis is there and not hidden. `inversion_pays_iff` is an
equivalence, so either direction failing refutes it.
-/

end Game
