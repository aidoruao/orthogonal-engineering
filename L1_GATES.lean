/-!
# L1 GATES — The Audit as a Game (2026-10-19)

A corporate auditee chooses what to claim. An auditor chooses which gates the
claim must pass. This file models that interaction and proves what can and
cannot be concluded from it.

## The game

- **Auditee strategy**: emit a claim `x`. Some claims are false (`False` set).
- **Auditor strategy**: a list of gates. A claim is admissible iff it passes
  every gate (`compose`).
- **Evasion**: a false claim that is admissible. This is the auditee's payoff
  and the negative of the auditor's.

## What is proved

1. **`compose_mono`** — enlarging the auditor's gate set can only shrink the
   admissible set. Defense in depth never admits more.
2. **`auditor_dominance`** — extending a strategy with an extra gate is weakly
   dominant: evasion under `g :: gs` is a subset of evasion under `gs`. The
   auditor never loses by adding a check.
3. **`vacuous_gate_adds_nothing`** — a gate that admits everything changes
   nothing. "We added a gate" is not the same claim as "we added protection."
4. **`duplicate_gate_adds_nothing`** — repeating a gate changes nothing. Nine
   gates that are three distinct checks repeated three times are three gates.
5. **`complete_gate_empties_evasion`** — if some gate rejects every false
   claim, evasion is empty regardless of the others.

## What is NOT proved, and must not be implied

- Nothing here says a real corporate entity behaves as this model says. It is
  a model of a gate, not a theory of a firm.
- Nothing here says a gate detects what it claims to detect. That is the
  gate's own burden, discharged by the negative controls in `ledger/negative/`.
- Nothing here is about people. Attribution remains separate from causation;
  see `THE_INDICTMENT.lean`.

The honest reading: **theorems 1–2 are a licence to add checks; theorems 3–4
are a warning that most added checks are theatre.** The ledger's nine gates
earn their number only because each one has a falsifier that fires.

Run: `lean L1_GATES.lean`
-/

universe u

/-! ## 1. Gates as predicates -/

/-- A gate decides which items it admits. `Gate α x` means "x passes". -/
abbrev Gate (α : Type u) : Type u := α → Prop

/-- An item is admissible iff it passes every gate in the list. -/
def compose {α : Type u} (gates : List (Gate α)) : Gate α :=
  fun x => ∀ g ∈ gates, g x

/-- Inclusion: every item admitted by `s` is admitted by `t`. -/
abbrev Imp {α : Type u} (s t : Gate α) : Prop := ∀ x, s x → t x

/-- A false claim that nonetheless passes every gate. -/
def Evades {α : Type u} (falseClaims : Gate α) (gates : List (Gate α)) :
    Gate α :=
  fun x => falseClaims x ∧ compose gates x

/-! ## 2. Composition is intersection -/

/-- The empty gate list admits everything. -/
theorem compose_nil {α : Type u} (x : α) : compose ([] : List (Gate α)) x := by
  intro g hg
  simp at hg

/-- Adding a gate at the head restricts to that gate. -/
theorem compose_cons_subset {α : Type u} (g : Gate α) (gs : List (Gate α)) :
    Imp (compose (g :: gs)) g := by
  intro x hx
  exact hx g (by simp)

/-- Dropping the head gate can only admit more. -/
theorem compose_tail_superset {α : Type u} (g : Gate α) (gs : List (Gate α)) :
    Imp (compose (g :: gs)) (compose gs) := by
  intro x hx g' hg'
  exact hx g' (List.mem_cons_of_mem g hg')

/-! ## 3. Defense in depth is monotone -/

/-- **`compose_mono`.** If every gate in `gs₂` also appears in `gs₁`, then
    `gs₁` admits no more than `gs₂`. Enlarging the auditor's gate set can only
    shrink what is admissible. -/
theorem compose_mono {α : Type u} {gs₁ gs₂ : List (Gate α)}
    (h : ∀ g ∈ gs₂, g ∈ gs₁) : Imp (compose gs₁) (compose gs₂) := by
  intro x hx g hg
  exact hx g (h g hg)

/-- Appending gates can only shrink the admissible set. -/
theorem compose_append_subset_left {α : Type u} (gs₁ gs₂ : List (Gate α)) :
    Imp (compose (gs₁ ++ gs₂)) (compose gs₁) := by
  intro x hx g hg
  exact hx g (List.mem_append_left gs₂ hg)

/-! ## 4. The auditor's dominance result -/

/-- **`auditor_dominance`.** Extending a strategy with one more gate never
    increases evasion. In game-theoretic terms, `g :: gs` weakly dominates
    `gs` for the auditor, for every choice the auditee makes.

    This is what licenses "add a gate" as a rational move. It is deliberately
    weak: weakly dominant means never worse, not always better. Theorems 3 and
    4 name the cases where it is exactly as good, i.e. no better at all. -/
theorem auditor_dominance {α : Type u} (falseClaims : Gate α)
    (g : Gate α) (gs : List (Gate α)) :
    Imp (Evades falseClaims (g :: gs)) (Evades falseClaims gs) := by
  intro x hx
  exact ⟨hx.1, compose_tail_superset g gs x hx.2⟩

/-- Conversely, a claim that evades the smaller strategy is not necessarily
    caught by the larger one — dominance is strict only when the new gate
    rejects something that would otherwise pass. Stated as: the extra gate can
    only help if it rejects at least one false claim that passes the rest. -/
theorem strict_gain_needs_rejection {α : Type u} (falseClaims : Gate α)
    (g : Gate α) (gs : List (Gate α)) (x : α)
    (_hfalse : falseClaims x) (_hrest : compose gs x) (hg : ¬ g x) :
    ¬ Evades falseClaims (g :: gs) x := by
  intro h
  exact hg (compose_cons_subset g gs x h.2)

/-! ## 5. The two ways an added gate is theatre -/

/-- **`vacuous_gate_adds_nothing`.** A gate that admits every item changes
    nothing at all. This is the structural-theatre failure mode in one line:
    a check with no falsifier is not a check. -/
theorem vacuous_gate_adds_nothing {α : Type u} (gs : List (Gate α)) (x : α) :
    compose ((fun _ => True) :: gs) x ↔ compose gs x := by
  constructor
  · intro h g hg
    exact h g (List.mem_cons_of_mem _ hg)
  · intro h g hg
    rcases List.mem_cons.mp hg with rfl | hmem
    · trivial
    · exact h g hmem

/-- **`duplicate_gate_adds_nothing`.** Repeating a gate changes nothing.
    A ledger claiming nine gates earns nine only if they are nine *distinct*
    checks. -/
theorem duplicate_gate_adds_nothing {α : Type u} (g : Gate α)
    (gs : List (Gate α)) (x : α) :
    compose (g :: g :: gs) x ↔ compose (g :: gs) x := by
  constructor
  · intro h
    exact compose_tail_superset g (g :: gs) x h
  · intro h
    exact compose_mono (by intro g' hg'; simp at hg' ⊢; exact hg') x h

/-- A gate already present later in the list adds nothing when prepended. -/
theorem redundant_gate_adds_nothing {α : Type u} (g : Gate α)
    (gs : List (Gate α)) (hmem : g ∈ gs) :
    Imp (compose gs) (compose (g :: gs)) := by
  intro x hx g' hg'
  rcases List.mem_cons.mp hg' with hhead | htail
  · rw [hhead]; exact hx g hmem
  · exact hx g' htail

/-! ## 6. Completeness -/

/-- **`complete_gate_empties_evasion`.** If the gate set contains a gate that
    rejects every false claim, then nothing false is admissible — whatever the
    other gates do. A single sound gate is sufficient; the rest are defence
    against its errors, not against the auditee. -/
theorem complete_gate_empties_evasion {α : Type u} (falseClaims : Gate α)
    (g : Gate α) (gs : List (Gate α)) (hmem : g ∈ g :: gs)
    (hsound : ∀ x, falseClaims x → ¬ g x) :
    ∀ x, ¬ Evades falseClaims (g :: gs) x := by
  intro x hx
  exact hsound x hx.1 (hx.2 g hmem)

/-! ## 7. A worked instance

Ten candidate claims; three are false (multiples of 3 among 1..10);
two gates: "not a multiple of 3" and "below 10". Synthetic, and it carries no
claim about anything real. -/

/-- Gate: the number is not divisible by 3. -/
def notDiv3 (n : Nat) : Prop := n % 3 ≠ 0

/-- Gate: the number is under 10. -/
def under10 (n : Nat) : Prop := n < 10

/-- The false claims in this toy universe. -/
def isFalseClaim (n : Nat) : Prop := n % 3 = 0

/-- A false claim cannot pass the divisibility gate, at any n. -/
theorem no_false_claim_passes (n : Nat) (hfalse : isFalseClaim n) :
    ¬ Evades isFalseClaim [notDiv3, under10] n := by
  intro h
  have hg : notDiv3 n := h.2 notDiv3 (by simp)
  unfold notDiv3 at hg
  unfold isFalseClaim at hfalse
  exact hg hfalse

/-- With both gates, no false claim among 3, 6, 9 is admissible. -/
theorem worked_example :
    ¬ Evades isFalseClaim [notDiv3, under10] 3 ∧
    ¬ Evades isFalseClaim [notDiv3, under10] 6 ∧
    ¬ Evades isFalseClaim [notDiv3, under10] 9 := by
  refine ⟨?_, ?_, ?_⟩ <;> apply no_false_claim_passes <;> unfold isFalseClaim <;> omega

/-- With only the size gate, the false claims still evade. This is why the
    number of gates is not the measure — the *distinctness* is. -/
theorem size_gate_alone_admits_three :
    Evades isFalseClaim [under10] 3 := by
  refine ⟨?_, ?_⟩
  · unfold isFalseClaim
    omega
  · intro g hg
    have hmem : g ∈ [under10] := hg
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hmem
    rw [hmem]
    unfold under10
    omega

/-!
## What this file establishes

1. `compose_mono` — a superset of gates admits a subset of claims.
2. `auditor_dominance` — adding a gate is weakly dominant for the auditor.
3. `strict_gain_needs_rejection` — the gain is strict only if the gate
   actually rejects something.
4. `vacuous_gate_adds_nothing` and `duplicate_gate_adds_nothing` — the two
   ways an added gate is theatre.
5. `complete_gate_empties_evasion` — one sound gate suffices for soundness;
   the rest guard against its errors.
6. `worked_example` and `size_gate_alone_admits_three` — the same set of
   claims, caught or not depending on whether the gates are distinct.

The ledger's nine gates are only nine because each has a negative control
that must fail to compile. That is the falsifier, and it is what separates
`auditor_dominance` from a slogan.
-/
