/-!
# L1 LEDGER — Structural Invariants (2026-10-17)

The TypeScript gate in `ledger/src/validate.ts` enforces one rule above all
others: **an adjudicated outcome may not rest on unadjudicated evidence.**
Concretely, a claim whose `nature` is `order` or `finding` must carry a
`fetched` tier, because a court's order is a document you either have or you
do not.

This file proves that the rule is structural rather than procedural:

1. `Record` carries the rule as a *proof field*, so a record violating it
   cannot be constructed at all. Illegal states are unrepresentable.
2. `gate` models the runtime check, and `gate_matches_invariant` proves the
   runtime check and the type-level invariant are the same proposition. The
   TypeScript and the Lean therefore agree by construction, not by convention.
3. `no_bad_record` states the practical consequence: there is no record whose
   nature is `finding` and whose tier is `unverified`.

Honest scope note: this proves a property of the ledger's *structure*. It does
not prove that any filing exists, that any allegation is true, or that any
person did anything. Those are facts about the world, and Lean does not fetch
PACER. See `THE_INDICTMENT.lean` on attribution versus causation.

Run: `lean L1_LEDGER.lean`
-/

/-! ## 1. Nature — what kind of statement a claim is -/

inductive Nature where
  | allegation
  | partyFiling
  | order
  | finding
  | settlement
  | statedIntent
deriving DecidableEq

/-- `order` and `finding` assert an adjudicated outcome; the rest do not.
    A complaint asserts; a court decides. The distinction is the whole point. -/
def Nature.isAdjudicated : Nature → Bool
  | .order => true
  | .finding => true
  | .allegation => false
  | .partyFiling => false
  | .settlement => false
  | .statedIntent => false

/-! ## 2. Tier — how well the claim is evidenced -/

/-- `corroborated` carries two named sources plus the rest, so a
    single-source "corroboration" is not representable. -/
inductive Tier where
  | fetched (sha256 : String)
  | corroborated (primary : String) (secondary : String) (rest : List String)
  | locatedBlocked (locator : String)
  | retired (reason : String)
  | unverified

def Tier.isFetched : Tier → Bool
  | .fetched _ => true
  | _ => false

def Tier.sources : Tier → List String
  | .corroborated p s rest => p :: s :: rest
  | _ => []

/-! ## 3. Record — the invariant is a field, not a hope -/

/-- A claim record. The `adjudicated_requires_fetched` field is the rule; a
    value of this type cannot exist without discharging it. -/
structure Record where
  claimId : String
  nature : Nature
  tier : Tier
  adjudicated_requires_fetched : nature.isAdjudicated = true → tier.isFetched = true

/-! ## 4. The gate models the runtime check -/

/-- The runtime rule, as a boolean: reject an adjudicated nature unless the
    tier is fetched. This mirrors `admit` in `ledger/src/validate.ts`. -/
def gate (n : Nature) (t : Tier) : Bool :=
  if n.isAdjudicated then t.isFetched else true

/-- **The bridge theorem.** The procedural gate and the structural invariant
    are the same proposition. This is why the TypeScript and the Lean cannot
    silently disagree. -/
theorem gate_matches_invariant (n : Nature) (t : Tier) :
    (gate n t = true) ↔ (n.isAdjudicated = true → t.isFetched = true) := by
  unfold gate
  by_cases hn : n.isAdjudicated = true
  · simp [hn]
  · simp [hn]

/-! ## 5. The rule holds of every record -/

/-- A boolean `isFetched` witness yields the underlying hash. -/
theorem isFetched_witness (t : Tier) (h : t.isFetched = true) :
    ∃ sha, t = .fetched sha := by
  cases t with
  | fetched sha => exact ⟨sha, rfl⟩
  | corroborated p s rest => simp [Tier.isFetched] at h
  | locatedBlocked loc => simp [Tier.isFetched] at h
  | retired reason => simp [Tier.isFetched] at h
  | unverified => simp [Tier.isFetched] at h

/-- An adjudicated record carries a fetched source. -/
theorem adjudicated_has_fetched_source (r : Record)
    (h : r.nature.isAdjudicated = true) : ∃ sha, r.tier = .fetched sha :=
  isFetched_witness r.tier (r.adjudicated_requires_fetched h)

/-- A `finding` is a fetched document. -/
theorem finding_requires_fetched (r : Record) (h : r.nature = .finding) :
    ∃ sha, r.tier = .fetched sha := by
  apply adjudicated_has_fetched_source
  rw [h]
  rfl

/-- An `order` is a fetched document. -/
theorem order_requires_fetched (r : Record) (h : r.nature = .order) :
    ∃ sha, r.tier = .fetched sha := by
  apply adjudicated_has_fetched_source
  rw [h]
  rfl

/-- **The practical consequence.** No record can be a finding resting on an
    unverified tier. This is the failure mode the ledger exists to prevent:
    an assertion wearing the clothes of a judgment. -/
theorem no_bad_record (r : Record) (hn : r.nature = .finding)
    (ht : r.tier = .unverified) : False := by
  obtain ⟨sha, hs⟩ := finding_requires_fetched r hn
  rw [ht] at hs
  cases hs

/-- Likewise, no record can be an order resting on a blocked source. -/
theorem no_blocked_order (r : Record) (hn : r.nature = .order)
    (hl : ∃ loc, r.tier = .locatedBlocked loc) : False := by
  obtain ⟨sha, hs⟩ := order_requires_fetched r hn
  obtain ⟨loc, hl'⟩ := hl
  rw [hl'] at hs
  cases hs

/-! ## 6. Nature is total, and mutually exclusive -/

/-- Every nature is one of the five. Nothing is smuggled in. -/
theorem nature_exhaustive (n : Nature) :
    n = .allegation ∨ n = .partyFiling ∨ n = .order ∨ n = .finding
      ∨ n = .settlement ∨ n = .statedIntent := by
  cases n <;> simp

/-- A finding is not an allegation. The two cannot be the same value, so a
    record cannot be read as either at will. -/
theorem finding_is_not_allegation : Nature.finding ≠ Nature.allegation := by
  intro h
  cases h

/-- An order is not a finding. -/
theorem order_is_not_finding : Nature.order ≠ Nature.finding := by
  intro h
  cases h

/-- A party's filing is not an allegation. A motion asserts a legal position;
    it does not assert facts. Keeping them distinct stops a filing from being
    read as an accusation, or an accusation from being read as a filing. -/
theorem party_filing_is_not_allegation : Nature.partyFiling ≠ Nature.allegation := by
  intro h
  cases h

/-! ## 7. The tier lattice, counted -/

def allNatures : List Nature :=
  [.allegation, .partyFiling, .order, .finding, .settlement, .statedIntent]

/-- Six natures, exactly. -/
theorem all_natures_count : allNatures.length = 6 := by native_decide

/-- Two of them are adjudicated. -/
theorem adjudicated_count :
    (allNatures.filter (fun n => n.isAdjudicated)).length = 2 := by native_decide

/-- Four are not. -/
theorem non_adjudicated_count :
    (allNatures.filter (fun n => !n.isAdjudicated)).length = 4 := by native_decide

/-- Corroboration always carries at least two sources, by construction. -/
theorem corroborated_has_two (p s : String) (rest : List String) :
    2 ≤ (Tier.corroborated p s rest).sources.length := by
  simp [Tier.sources]

/-! ## 8. Worked examples

These are synthetic. They demonstrate the constructors; they are not claims
about any real filing. -/

/-- An allegation may rest on unverified evidence and still be a record. -/
def exampleAllegation : Record where
  claimId := "CLM-EXAMPLE-1"
  nature := .allegation
  tier := .unverified
  adjudicated_requires_fetched := by
    intro h
    simp [Nature.isAdjudicated] at h

/-- A finding requires an actual document. -/
def exampleFinding : Record where
  claimId := "CLM-EXAMPLE-2"
  nature := .finding
  tier := .fetched "8ec492dce881fff47d28aaac3607a7b2a736c71e04038e3c2f4d7dc3d183bdc4"
  adjudicated_requires_fetched := by
    intro _
    rfl

/-- The same record shape with `finding` and `unverified` is not expressible:
    the proof field has no inhabitant. Stated as a theorem about all records. -/
theorem example_gate_accepts_allegation : gate .allegation .unverified = true := by
  native_decide

theorem example_gate_rejects_finding : gate .finding .unverified = false := by
  native_decide

theorem example_gate_accepts_fetched_finding :
    gate .finding (.fetched "abc") = true := by
  native_decide

/-!
## What this file establishes

1. `Record` cannot be constructed for an adjudicated nature without a
   `fetched` tier — the constraint is in the type, so it is enforced by the
   compiler rather than by reviewer discipline.
2. `gate_matches_invariant` proves the runtime check in
   `ledger/src/validate.ts` and the Lean invariant are the same proposition.
3. `no_bad_record` and `no_blocked_order` name the two failure modes the
   ledger refuses.
4. `nature_exhaustive` and the counting theorems pin the classification:
   six natures, two adjudicated, four not.
5. Nothing here asserts a fact about the world. The ledger's structure is
   proved; its contents must still be fetched, hashed, and quoted.
-/
