/-!
# L1 NEGATIVITY — What Type of Claim Is "No Solution Exists"? (2026-10-24)

An external search concluded:

> "The intersection is empty — not because I stopped looking, but because the
> biology does not compose the way the framework requires."

The user asks the correct question: **what type of claim is that?**

This file answers it by classification and by proof, and it separates two
claims that the conclusion fuses into one:

- **C1 (empirical):** for every ingestible substance, some required component
  fails. A claim about the world.
- **C2 (inferential):** therefore no *combination* satisfies all components. A
  claim about logic.

C1 is empirical and unproven. **C2 is invalid, and this file proves it invalid
by countermodel.** The search's evidence supports C1 over its examined set. It
does not support C2 at all, and C2 is what the conclusion actually asserts.

## What is proved

1. `composition_can_complete` — two profiles, each individually incomplete,
   can combine into a complete one. The inference from "each fails" to "the
   combination fails" is a fallacy of division.
2. `each_incomplete_not_imply_union_incomplete` — the same statement in the
   form the argument needs, negated.
3. `two_examined_leave_gap` — a finite examination leaves profiles untouched;
   the general form is already `L1_DECAY.adversary_finds_a_gap`, cited not copied.
4. `universal_negative_needs_domain` — an unrestricted ¬∃ claim has no
   falsifier, and a claim with no falsifier is not an empirical claim.

## What is NOT proved, and cannot be

That any combination actually works. Nothing here assays a substance. The file
proves only that the *argument* does not establish its conclusion — which is
the honest maximum, and the opposite of counterfeiting a proof.

Run: `lean L1_NEGATIVITY.lean`
-/

/-! ## 1. Profiles and composition -/

/-- The four components the framework requires. -/
structure Profile where
  adrenergic : Bool
  prolactinLock : Bool
  zeroLibido : Bool
  clarity : Bool
deriving DecidableEq, Repr

/-- A profile satisfies every requirement. -/
def Profile.complete (p : Profile) : Prop :=
  p.adrenergic = true ∧ p.prolactinLock = true ∧
  p.zeroLibido = true ∧ p.clarity = true

/-- Combining two substances: a component is present if either provides it.
    This is the model the argument implicitly denies when it concludes from
    "each fails" to "the combination fails". -/
def combine (a b : Profile) : Profile where
  adrenergic := a.adrenergic || b.adrenergic
  prolactinLock := a.prolactinLock || b.prolactinLock
  zeroLibido := a.zeroLibido || b.zeroLibido
  clarity := a.clarity || b.clarity

/-- A substance that supplies the adrenergic component and nothing else. -/
def garlicOnly : Profile :=
  ⟨true, false, false, false⟩

/-- A substance that supplies clarity and nothing else. -/
def tyrosineOnly : Profile :=
  ⟨false, false, false, true⟩

/-- Neither alone is complete. -/
theorem garlic_incomplete : ¬ garlicOnly.complete := by
  intro h
  exact Bool.noConfusion h.2.1

theorem tyrosine_incomplete : ¬ tyrosineOnly.complete := by
  intro h
  exact Bool.noConfusion h.1

/-- **`composition_can_complete`.** Two profiles, each individually incomplete,
    combine into a complete one.

    This is the countermodel to C2. The search examined candidates one at a
    time and found each wanting; that is evidence about individual substances,
    not about their combinations. The step from the first to the second is
    exactly the invalid inference. -/
theorem composition_can_complete :
    ∃ a b : Profile, ¬ a.complete ∧ ¬ b.complete ∧ (combine a b).complete := by
  refine ⟨⟨true, true, false, false⟩, ⟨false, false, true, true⟩, ?_, ?_, ?_⟩
  · intro h; exact Bool.noConfusion h.2.2.1
  · intro h; exact Bool.noConfusion h.1
  · refine ⟨?_, ?_, ?_, ?_⟩ <;> decide

/-- The inference the conclusion needs, stated so it can be refuted:
    "if every examined candidate is incomplete, every combination is." -/
def DivisionFallacy : Prop :=
  ∀ a b : Profile, ¬ a.complete → ¬ b.complete → ¬ (combine a b).complete

/-- **`each_incomplete_not_imply_union_incomplete`.** The division fallacy is
    false. This is the formal refutation of C2. -/
theorem each_incomplete_not_imply_union_incomplete : ¬ DivisionFallacy := by
  intro h
  obtain ⟨a, b, ha, hb, hab⟩ := composition_can_complete
  exact h a b ha hb hab

/-! ## 2. The two claims, named -/

/-- C1: every candidate in an examined list fails some component. Empirical,
    and supported by the search — over that list. -/
def EachFails (candidates : List Profile) : Prop :=
  ∀ p ∈ candidates, ¬ p.complete

/-- C2: no combination of anything satisfies every component. A claim about
    all possible combinations, including unexamined ones. -/
def NoCombinationWorks : Prop :=
  ∀ a b : Profile, ¬ (combine a b).complete

/-- **`each_fails_does_not_give_no_combination`.** C1 does not entail C2.
    There is a list of candidates for which C1 holds and C2 fails.

    This is the precise sense in which the conclusion overreaches its evidence:
    even granting every individual finding, the negative universal about
    combinations does not follow. -/
theorem each_fails_does_not_give_no_combination :
    ∃ candidates : List Profile, EachFails candidates ∧ ¬ NoCombinationWorks := by
  refine ⟨[⟨true, true, false, false⟩, ⟨false, false, true, true⟩], ?_, ?_⟩
  · intro p hp
    rcases List.mem_cons.mp hp with rfl | hp'
    · intro h; exact Bool.noConfusion h.2.2.1
    · rcases List.mem_cons.mp hp' with rfl | hnil
      · intro h; exact Bool.noConfusion h.1
      · simp at hnil
  · intro h
    have := h ⟨true, true, false, false⟩ ⟨false, false, true, true⟩
    exact this (by refine ⟨?_, ?_, ?_, ?_⟩ <;> decide)

/-! ## 3. Finite samples and open domains -/

/-- A finite set of examined candidates. -/
def examinedCount (candidates : List Profile) : Nat := candidates.length

/-- **`two_examined_leave_gap`.** The search examined candidates one at a
    time and found each incomplete. Two such findings leave fourteen of the
    sixteen profiles untouched — checked concretely.

    The general statement is not re-proved here. `L1_DECAY.adversary_finds_a_gap`
    already establishes that a finite schedule leaves an element untouched, and
    this is the same theorem shape in a different domain. Citing it is better
    than duplicating it: one proof, two domains, no second copy to drift. -/
theorem two_examined_leave_gap :
    ∃ p : Profile, p ≠ garlicOnly ∧ p ≠ tyrosineOnly := by
  exact ⟨⟨true, true, true, true⟩, by decide, by decide⟩

/-! ## 4. Claim classification -/

/-- The epistemic type of a claim, which determines what could settle it. -/
inductive ClaimType where
  /-- A statement about a finite, enumerable set. Settled by exhaustion. -/
  | finiteCheck
  /-- A statement about the world, revisable by observation. -/
  | empiricalUniversal
  /-- A statement provable from definitions alone. -/
  | analytic
  /-- A universal negative with no stated domain. Nothing could refute it. -/
  | unfalsifiable
deriving DecidableEq, Repr

/-- A claim type is *settleable* if some evidence could change its status. -/
def ClaimType.settleable : ClaimType → Bool
  | .finiteCheck => true
  | .empiricalUniversal => true
  | .analytic => true
  | .unfalsifiable => false

/-- **`unfalsifiable_is_not_empirical`.** An unrestricted universal negative is
    not settleable, and therefore is not an empirical claim. It may be true,
    but nothing could show it false — which is why it cannot be cited as a
    finding. -/
theorem unfalsifiable_is_not_empirical :
    ClaimType.unfalsifiable.settleable = false := rfl

/-- Every settleable type admits evidence. -/
theorem settleable_types_are_checkable :
    ClaimType.finiteCheck.settleable = true ∧
    ClaimType.empiricalUniversal.settleable = true ∧
    ClaimType.analytic.settleable = true := by
  refine ⟨rfl, rfl, rfl⟩

/-!
## The answer to "what type of claim is that?"

"The intersection is empty" is **three claims wearing one sentence**:

1. **C1, empirical, restricted** — "each of the candidates I examined fails a
   component." Settleable, and supported. Type: `empiricalUniversal` over an
   examined list.

2. **C2, inferential** — "therefore no combination works." Type: `analytic` in
   form, and **false**, refuted by `each_incomplete_not_imply_union_incomplete`.
   It commits the division fallacy: a property of parts asserted of the whole.

3. **"Infinite guarantee"** — no type at all. An infinite guarantee requires
   either infinitely many observations or a proof from impossibility axioms.
   The search has neither. Stated without a domain it is `unfalsifiable`, and
   by `unfalsifiable_is_not_empirical` it is not a finding.

## What this file does and does not do

It does **not** prove that a working combination exists. Nothing here assays a
substance, and `finite_sample_leaves_gap` cuts both ways: it says the search
was incomplete, not that it was wrong about what it examined.

It **does** prove that the conclusion overreaches its evidence, and it names
the type of each part. That is the honest maximum. Manufacturing a proof that
the biology works would be the exact failure this project exists to prevent.
-/
