/-!
# L1 SELECTION — The Selection Is Part of the Record (2026-10-17)

Option A drafts claims locally and publishes only some of them. That is honest
only if the *selection* is published too. Selective disclosure is a form of
lying even when every published quote is accurate.

This file proves the selection's structural invariant:

1. `Selection` carries totality as a proof field, so a selection that drops a
   candidate — or invents one — cannot be constructed at all.
2. `partition_counts` proves the three dispositions account for every entry,
   exactly once: accepted + rejected + withheld = total.
3. `no_silent_drop` states the practical consequence: every drafted candidate
   appears in the ledger.
4. Every non-accepted entry carries a non-empty reason code, so a rejection is
   never anonymous.

Honest scope note: this proves the bookkeeping is complete. It does not prove
that any disposition was *correct* — that a rejected claim was really
unsupported, or that an accepted one is really supported. Correctness is
settled by the quote check in `ledger/src/workbench.ts`, which can fail. This
file proves only that nothing vanished.

Run: `lean L1_SELECTION.lean`
-/

/-! ## 1. Dispositions -/

inductive Disposition where
  | accepted
  | rejected (code : String)
  | withheld (code : String)
deriving DecidableEq

def Disposition.isAccepted : Disposition → Bool
  | .accepted => true
  | _ => false

def Disposition.isRejected : Disposition → Bool
  | .rejected _ => true
  | _ => false

def Disposition.isWithheld : Disposition → Bool
  | .withheld _ => true
  | _ => false

/-- A non-accepted disposition always carries a reason. -/
def Disposition.hasReason : Disposition → Prop
  | .accepted => True
  | .rejected code => code ≠ ""
  | .withheld code => code ≠ ""

/-! ## 2. The ledger -/

structure Entry where
  claimId : String
  disposition : Disposition

/-- A selection. The proof fields are the invariants; a value of this type is
    a complete, auditable account by construction.

    `total` says the entries are exactly the candidates: nothing dropped,
    nothing invented. `reasons` says no rejection is anonymous. -/
structure Selection where
  candidates : List String
  entries : List Entry
  total : entries.map (fun e => e.claimId) = candidates
  reasons : ∀ e ∈ entries, e.disposition.hasReason

/-! ## 3. Totality -/

/-- The ledger has exactly as many entries as there were candidates. -/
theorem total_length (s : Selection) : s.entries.length = s.candidates.length := by
  rw [← s.total, List.length_map]

/-- **No silent drop.** Every candidate that was drafted appears in the ledger.
    This is the invariant the whole instrument exists to enforce: a claim that
    is quietly set aside is indistinguishable from one that was never made. -/
theorem no_silent_drop (s : Selection) {id : String} (h : id ∈ s.candidates) :
    ∃ e, e ∈ s.entries ∧ e.claimId = id := by
  have hmap : id ∈ s.entries.map (fun e => e.claimId) := by
    rw [s.total]
    exact h
  rcases List.mem_map.mp hmap with ⟨e, he, hid⟩
  exact ⟨e, he, hid⟩

/-- **No invented claim.** Every entry corresponds to a candidate. -/
theorem no_orphan (s : Selection) {e : Entry} (h : e ∈ s.entries) :
    e.claimId ∈ s.candidates := by
  have hmap : e.claimId ∈ s.entries.map (fun x => x.claimId) := List.mem_map.mpr ⟨e, h, rfl⟩
  rwa [s.total] at hmap

/-! ## 4. The partition -/

/-- Count entries whose disposition is `accepted`. This is the recursive form
    of `entries.filter (·.disposition === accepted).length` in the TypeScript
    gate, stated without `if` so the induction goes through without fighting
    the `Bool = true` coercion that `List.filter` introduces. -/
def countAccepted : List Entry → Nat
  | [] => 0
  | e :: es =>
    match e.disposition with
    | .accepted => countAccepted es + 1
    | _ => countAccepted es

def countRejected : List Entry → Nat
  | [] => 0
  | e :: es =>
    match e.disposition with
    | .rejected _ => countRejected es + 1
    | _ => countRejected es

def countWithheld : List Entry → Nat
  | [] => 0
  | e :: es =>
    match e.disposition with
    | .withheld _ => countWithheld es + 1
    | _ => countWithheld es

/-- **The partition.** Every entry is counted exactly once across the three
    dispositions, so the counts sum to the total. This is the arithmetic core
    of "nothing vanished and nothing was double-counted." -/
theorem partition_counts (entries : List Entry) :
    countAccepted entries + countRejected entries + countWithheld entries
      = entries.length := by
  induction entries with
  | nil => rfl
  | cons head tail ih =>
    cases hd : head.disposition <;>
      simp [countAccepted, countRejected, countWithheld, hd] <;>
      omega

/-- The same statement for a `Selection`: the three dispositions account for
    every candidate, with nothing counted twice. -/
theorem selection_partition (s : Selection) :
    countAccepted s.entries + countRejected s.entries + countWithheld s.entries
      = s.candidates.length := by
  rw [partition_counts, total_length]

/-! ## 5. Reasons are not optional -/

/-- A rejected entry carries a non-empty code. There is no anonymous rejection. -/
theorem rejected_has_code (s : Selection) {e : Entry} (he : e ∈ s.entries)
    (hr : e.disposition.isRejected = true) :
    ∃ code, e.disposition = .rejected code ∧ code ≠ "" := by
  have hreason := s.reasons e he
  cases hd : e.disposition with
  | accepted => simp [Disposition.isRejected, hd] at hr
  | rejected code =>
    have hne : code ≠ "" := by
      simpa [Disposition.hasReason, hd] using hreason
    exact ⟨code, rfl, hne⟩
  | withheld code => simp [Disposition.isRejected, hd] at hr

/-- A withheld entry carries a non-empty code, too. -/
theorem withheld_has_code (s : Selection) {e : Entry} (he : e ∈ s.entries)
    (hw : e.disposition.isWithheld = true) :
    ∃ code, e.disposition = .withheld code ∧ code ≠ "" := by
  have hreason := s.reasons e he
  cases hd : e.disposition with
  | accepted => simp [Disposition.isWithheld, hd] at hw
  | rejected code => simp [Disposition.isWithheld, hd] at hw
  | withheld code =>
    have hne : code ≠ "" := by
      simpa [Disposition.hasReason, hd] using hreason
    exact ⟨code, rfl, hne⟩

/-! ## 6. Worked example

Synthetic. Demonstrates the constructors; it is not a claim about anything. -/

def exampleSelection : Selection where
  candidates := ["CLM-A", "CLM-B", "CLM-C", "CLM-D"]
  entries := [
    ⟨"CLM-A", .accepted⟩,
    ⟨"CLM-B", .rejected "quote_not_found"⟩,
    ⟨"CLM-C", .withheld "third_party_identity"⟩,
    ⟨"CLM-D", .rejected "source_hash_mismatch"⟩
  ]
  total := by decide
  reasons := by
    intro e he
    simp only [List.mem_cons, List.not_mem_nil, or_false] at he
    rcases he with rfl | rfl | rfl | rfl <;>
      simp [Disposition.hasReason]

/-- Four candidates, accounted for: 1 accepted, 2 rejected, 1 withheld. -/
theorem example_partition :
    countAccepted exampleSelection.entries = 1
    ∧ countRejected exampleSelection.entries = 2
    ∧ countWithheld exampleSelection.entries = 1
    ∧ exampleSelection.candidates.length = 4 := by
  decide

/-- Every candidate in the example is reachable in the ledger. -/
theorem example_no_drop :
    ∃ e, e ∈ exampleSelection.entries ∧ e.claimId = "CLM-C" :=
  no_silent_drop exampleSelection (by decide)

/-!
## What this file establishes

1. `Selection` cannot exist with a missing or invented entry — the totality
   proof field has no inhabitant for those shapes.
2. `selection_partition` proves the counts sum to the candidate total.
3. `no_silent_drop` and `no_orphan` pin both directions of the correspondence.
4. `rejected_has_code` and `withheld_has_code` prove rejection is never
   anonymous.

What it does not establish: that a disposition was right. That is the quote
check's job, and it can fail. This file proves the bookkeeping; the workbench
proves the evidence.
-/
