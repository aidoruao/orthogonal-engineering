/-!
# L1 COVERAGE — The Snowball Theorem (2026-10-19)

A claim ledger can grow in two ways that look identical by count and are
opposite in value:

- adding a claim about a document already covered
- adding a claim about a document nobody has examined

Both increment "claims". Only one increments "documents covered". This file
proves the distinction, so that a growing ledger cannot be mistaken for a
broadening one.

## The model

`covered` is the list of distinct documents the ledger has claims about.
`addDoc` folds one claim's document into that list. The three theorems below
say what a single claim can and cannot do.

## What is proved

1. **`addDoc_bounded`** — one claim adds at most one document.
2. **`addDoc_zero_if_covered`** — a claim about a covered document adds
   nothing. This is the exact statement of cumulative-but-not-compounding
   work: it is honest effort that moves no frontier.
3. **`addDoc_progress_if_dark`** — a claim about a dark document adds exactly
   one. This is the snowball: each dark document is a strict gain.
4. **`snowball`** — from empty, `n` claims about `n` distinct documents cover
   exactly `n` documents. Linear progress is guaranteed and cannot be
   inflated.

## What is NOT proved

- Nothing says which document is *most important*. Coverage is breadth, not
  weight. A single claim on the operative complaint may matter more than ten
  on procedural notices; this file has no opinion on that.
- Nothing says a claim is true. Coverage counts examined documents, not
  established facts. The quote gate and the tier rules carry that burden.
- Nothing is a claim about any party. A motion caption establishes who filed
  what. That is all it establishes.

The engineering reading:

> **Count documents, not claims.** A ledger of a thousand claims against one
> filing has covered one document. The number that compounds is the number of
> documents examined.

Run: `lean L1_COVERAGE.lean`
-/

/-! ## 1. Folding a document into the covered set -/

/-- Add `d` to the covered list unless it is already there.
    Duplicates are not inserted, so the list stays a set. -/
def addDoc (covered : List Nat) (d : Nat) : List Nat :=
  if d ∈ covered then covered else d :: covered

/-- **One claim adds at most one document.** -/
theorem addDoc_bounded (covered : List Nat) (d : Nat) :
    (addDoc covered d).length ≤ covered.length + 1 := by
  unfold addDoc
  split
  · simp
  · simp

/-- **A claim about a covered document adds nothing.**
    This is the theorem that separates effort from progress. -/
theorem addDoc_zero_if_covered (covered : List Nat) (d : Nat)
    (hmem : d ∈ covered) : (addDoc covered d).length = covered.length := by
  unfold addDoc
  rw [ite_eq_left hmem]

/-- **A claim about a dark document adds exactly one.** -/
theorem addDoc_progress_if_dark (covered : List Nat) (d : Nat)
    (hnot : d ∉ covered) : (addDoc covered d).length = covered.length + 1 := by
  unfold addDoc
  rw [ite_eq_right hnot]
  simp

/-! ## 2. The snowball -/

/-- Fold a whole batch of claims' documents into the covered list. -/
def addAll (covered : List Nat) (docs : List Nat) : List Nat :=
  docs.foldl addDoc covered

/-- Folding a nodup batch of documents that are all outside `covered` grows the
    list by exactly the batch length. -/
theorem addAll_dark_batch (covered : List Nat) (docs : List Nat)
    (hdisjoint : ∀ d ∈ docs, d ∉ covered) (hnodup : docs.Nodup) :
    (addAll covered docs).length = covered.length + docs.length := by
  induction docs generalizing covered with
  | nil => simp [addAll]
  | cons head tail ih =>
    have hhead : head ∉ covered := hdisjoint head (by simp)
    -- `d ≠ head` comes from Nodup, not from disjointness: the batch has no
    -- repeats, so a later element is never the head.
    have hhead_not_tail : head ∉ tail := (List.nodup_cons.mp hnodup).1
    have htail_disjoint : ∀ d ∈ tail, d ∉ addDoc covered head := by
      intro d hd
      have hd_not_covered : d ∉ covered := hdisjoint d (by simp [hd])
      have hd_ne_head : d ≠ head := by
        intro heq
        exact hhead_not_tail (heq ▸ hd)
      unfold addDoc
      rw [ite_eq_right hhead]
      intro hmem
      rcases List.mem_cons.mp hmem with heq | hin
      · exact hd_ne_head heq
      · exact hd_not_covered hin
    have htail_nodup : tail.Nodup := hnodup.of_cons
    have ih' := ih (addDoc covered head) htail_disjoint htail_nodup
    simp only [addAll] at ih' ⊢
    rw [List.foldl_cons, ih', addDoc_progress_if_dark covered head hhead]
    simp
    omega

/-- **`snowball`.** Starting from nothing, a nodup batch of `n` documents
    covers exactly `n` documents. Progress is linear in distinct documents and
    cannot be inflated by repeating one. -/
theorem snowball (docs : List Nat) (hnodup : docs.Nodup) :
    (addAll [] docs).length = docs.length := by
  have h := addAll_dark_batch [] docs (by intro d hd; simp) hnodup
  simpa using h

/-- The contrapositive that matters operationally: if two batches produce the
    same covered count, the second batch examined no new documents. Stated for
    a single claim, which is the case a reviewer actually checks. -/
theorem repeat_is_not_progress (covered : List Nat) (d : Nat) (hmem : d ∈ covered) :
    addAll covered [d] = covered := by
  simp only [addAll, List.foldl_cons, List.foldl_nil]
  unfold addDoc
  rw [ite_eq_left hmem]

/-! ## 3. A worked instance

Synthetic. Three claims on one document, then one claim on a new one. -/

/-- Three claims, all about document 385. -/
def threeOnOne : List Nat := [385, 385, 385]

/-- Coverage after the three: one document. -/
theorem three_on_one_covers_one : (addAll [] threeOnOne).length = 1 := by decide

/-- One claim on a previously dark document. -/
theorem one_new_covers_two : (addAll (addAll [] threeOnOne) [62]).length = 2 := by decide

/-- The fourth claim moved the frontier; the second and third did not. -/
theorem second_and_third_add_nothing :
    (addAll [] [385, 385]).length = (addAll [] [385]).length := by decide

/-!
## What this file establishes

1. `addDoc_bounded` — no single claim can add more than one document.
2. `addDoc_zero_if_covered` — claims on covered documents are cumulative, not
   compounding.
3. `addDoc_progress_if_dark` — claims on dark documents are strict gains.
4. `snowball` — `n` distinct documents cover `n`, always.
5. `repeat_is_not_progress` — the reviewer's check, in one line.

The ledger currently holds 12 claims over 10 documents out of 41 in the
manifest. By `snowball`, the remaining frontier is 31 documents. That number —
not the claim count — is the measure of how much of the record has actually
been read.
-/
