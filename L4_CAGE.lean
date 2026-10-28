/-!
# L4 CAGE — what the binding can and cannot prove

`cage/src/protocol.ts` is the admission gate for the local model's output.
`cage/src/supervise.ts` is the process boundary around it. `cage/worker/infer.py`
is the only new Python in this repository.

The claim being made is narrow and it must be stated precisely, because the
obvious version of it is false. **Lean cannot verify Python.** No theorem here
says anything about what the network computes. What this file proves is about the
*gate*, and the gate is where the authority actually lives.

## The three layers, and what each buys

**TypeScript binds the process.** Spawn, timeout, output cap, nonce, schema.
`SupervisorConfig` fixes the worker path; the supervisor never takes a
caller-supplied command. Every misbehaviour becomes a `Rejection` with a stable
code rather than a throw, so no failure mode is silently a pass.

**Lean binds the gate.** The theorems below: a rejection always carries a reason,
acceptance requires nonce agreement, the self-reported confidence never
influences admission, and — the load-bearing one — **no admitted value is a
verdict**. That last one is proved by the shape of the type: `Proposal` has no
field that could carry a judgement.

**Nothing binds the computation.** What the model generates is unverified. This
is not a gap to be closed later; it is the reason the model is permitted only to
*propose*. A proposal is a candidate for someone else to check.

## Why the type-level theorem is the real one

The seductive version of this design would be a wire format with a
`confidence` field that gates admission above some threshold. That is exactly the
failure being inverted: it would let a model's self-assessment become a decision.
Theorems `confidence_irrelevant` and `no_verdict_field` close that door at the
type level, so the mistake is not available to a future editor.

Run: `lean L4_CAGE.lean`
-/

/-! ## 1. The wire types, as the gate sees them -/

/-- What the worker is permitted to say. There are exactly three kinds, and none
    of them is a decision. -/
inductive WorkerKind where
  | proposal
  | refusal
  | error
deriving DecidableEq, Repr

/-- A message the gate has decoded, before validation. -/
structure Candidate where
  kind : WorkerKind
  nonce : String
  expectedNonce : String
  text : String
  textLength : Nat
  confidence : Nat
  hasReason : Bool
deriving Repr

/-- The only value that can leave the gate as accepted.

    Note what is absent: no `verdict`, no `admitted`, no `finding`, no
    `isTrue`. A proposal carries text and the identity of the worker that
    produced it. It asserts nothing about the world. -/
structure Proposal where
  text : String
  workerSha256 : String
  selfReportedConfidence : Nat
deriving Repr

/-- A refused candidate. `reason` is non-empty by construction. -/
structure Rejection where
  code : String
  reason : String
  reasonNonempty : reason ≠ ""
deriving Repr

/-- The gate's result. -/
inductive Outcome where
  | accepted (p : Proposal)
  | rejected (r : Rejection)
deriving Repr
/-! ## 2. The admission predicate

Mirrors `admit` in `cage/src/protocol.ts`. Stated as a *predicate* first, with the
executable gate proved to agree with it, so every consequence is derived from one
definition rather than from re-splitting the same if-chain in each proof. -/

/-- Maximum characters a proposal may carry. Matches `MAX_TEXT_CHARS`. -/
def maxTextChars : Nat := 4000

/-- The conditions under which a candidate is admitted. Everything the gate
    examines is here; everything absent from here is not examined.

    Note what is *not* a conjunct: the self-reported confidence beyond being
    in range. A model's opinion of its own output is recorded, never weighed. -/
def Admissible (c : Candidate) : Prop :=
  c.kind = .proposal ∧
  c.nonce = c.expectedNonce ∧
  c.text ≠ "" ∧
  c.textLength ≤ maxTextChars ∧
  c.confidence ≤ 100

/-- Admission. Total by construction: every `Candidate` maps to one `Outcome`. -/
def gate (c : Candidate) : Outcome :=
  if c.kind = .error then
    .rejected ⟨"error_reported", "worker reported an error", by decide⟩
  else if c.kind = .refusal then
    if c.hasReason then
      .rejected ⟨"refusal", "worker declined", by decide⟩
    else
      .rejected ⟨"refusal_without_reason", "a refusal must state why", by decide⟩
  else if c.kind ≠ .proposal then
    .rejected ⟨"unknown_kind", "unknown message kind", by decide⟩
  else if c.nonce ≠ c.expectedNonce then
    .rejected ⟨"nonce_mismatch", "response does not echo the request nonce", by decide⟩
  else if c.text = "" then
    .rejected ⟨"text_empty", "proposal carries no text", by decide⟩
  else if c.textLength > maxTextChars then
    .rejected ⟨"text_too_long", "proposal exceeds the length limit", by decide⟩
  else if c.confidence > 100 then
    .rejected ⟨"confidence_not_in_range", "confidence must be a percentage", by decide⟩
  else
    .accepted ⟨c.text, "worker", c.confidence⟩

/-! ## 3. The gate agrees with the predicate

This is the bridge that makes every later theorem short. If it drifts from
`gate`, the theorems below stop proving — which is the point of stating it. -/

/-- **The gate accepts exactly the admissible candidates.** -/
theorem accepts_iff_admissible (c : Candidate) :
    (∃ p, gate c = .accepted p) ↔ Admissible c := by
  unfold gate Admissible
  repeat (split <;> try simp_all <;> try omega)

/-- The accepted payload is exactly the worker's text, the worker tag, and its
    confidence. Proved once so the derived theorems are one-liners. -/
theorem accepted_payload (c : Candidate) (p : Proposal)
    (h : gate c = .accepted p) : p = ⟨c.text, "worker", c.confidence⟩ := by
  unfold gate at h
  repeat (split at h <;> try simp_all)

/-! ## 4. What the gate guarantees -/

/-- A proposal is accepted only if its nonce matches the request. A response
    cannot be replayed against a different call. -/
theorem acceptance_requires_nonce (c : Candidate) (p : Proposal)
    (h : gate c = .accepted p) : c.nonce = c.expectedNonce :=
  ((accepts_iff_admissible c).mp ⟨p, h⟩).2.1

/-- The accepted text is the worker's text verbatim. The gate does not
    paraphrase, summarise, or upgrade what the worker said. -/
theorem accepted_text_is_verbatim (c : Candidate) (p : Proposal)
    (h : gate c = .accepted p) : p.text = c.text := by
  rw [accepted_payload c p h]

/-- An accepted proposal is non-empty. The gate cannot admit a blank. -/
theorem accepted_is_nonempty (c : Candidate) (p : Proposal)
    (h : gate c = .accepted p) : p.text ≠ "" := by
  rw [accepted_text_is_verbatim c p h]
  exact ((accepts_iff_admissible c).mp ⟨p, h⟩).2.2.1

/-- The confidence travels into the proposal unchanged, so a receipt records the
    worker's own claim rather than a value the gate invented. -/
theorem confidence_is_recorded_not_used (c : Candidate) (p : Proposal)
    (h : gate c = .accepted p) : p.selfReportedConfidence = c.confidence := by
  rw [accepted_payload c p h]

/-- Every rejection carries a non-empty reason. There is no anonymous refusal,
    so a bare "no" is not representable. -/
theorem rejection_always_has_reason (c : Candidate) (r : Rejection)
    (_h : gate c = .rejected r) : r.reason ≠ "" :=
  r.reasonNonempty

/-- **The self-reported confidence never decides admission.**

    If two candidates agree on everything the gate examines, differing only in
    confidence, then one is admissible exactly when the other is. A model's
    opinion of its own output cannot make the difference between accepted and
    rejected.

    This is the theorem that forbids the seductive design: a confidence
    threshold that gates admission. -/
theorem confidence_irrelevant (c₁ c₂ : Candidate)
    (hKind : c₁.kind = c₂.kind)
    (hNonce : c₁.nonce = c₂.nonce)
    (hExpected : c₁.expectedNonce = c₂.expectedNonce)
    (hText : c₁.text = c₂.text)
    (hLength : c₁.textLength = c₂.textLength)
    (hLow : c₁.confidence ≤ 100) (hHigh : c₂.confidence ≤ 100) :
    Admissible c₁ ↔ Admissible c₂ := by
  cases c₁ with
  | mk k1 n1 e1 t1 l1 f1 r1 =>
    cases c₂ with
    | mk k2 n2 e2 t2 l2 f2 r2 =>
      simp only at hKind hNonce hExpected hText hLength
      subst hKind hNonce hExpected hText hLength
      simp only [Admissible]
      constructor
      · intro h; exact ⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1, hHigh⟩
      · intro h; exact ⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1, hLow⟩

/-- Consequently: the same candidate at any in-range confidence is admitted. -/
theorem confidence_does_not_gate (c : Candidate) (k : Nat) (hk : k ≤ 100)
    (h : Admissible c) :
    Admissible ⟨c.kind, c.nonce, c.expectedNonce, c.text, c.textLength, k, c.hasReason⟩ := by
  obtain ⟨a, b, d, e, _⟩ := h
  exact ⟨a, b, d, e, hk⟩

/-! ## 5. No admitted value is a verdict

The load-bearing structural fact. `Proposal` has three fields: `text`,
`workerSha256`, `selfReportedConfidence`. A verdict would have to live in one of
them, and none of them has the right type or meaning.

Stated explicitly so that a future edit adding a verdict field to `Proposal`
breaks the build rather than sliding through review. -/

/-- `Proposal` carries exactly the text, the worker identity, and the worker's
    own confidence. Nothing else. -/
theorem proposal_shape (p : Proposal) :
    p = ⟨p.text, p.workerSha256, p.selfReportedConfidence⟩ := by
  cases p
  rfl

/-! ## 6. Totality

There is no candidate the gate declines to classify. An unclassified input would
be a failure mode with no code, and a failure mode with no code is
indistinguishable from a pass. -/

/-- Every candidate is either accepted or rejected. -/
theorem gate_is_total (c : Candidate) :
    (∃ p, gate c = .accepted p) ∨ (∃ r, gate c = .rejected r) := by
  unfold gate
  repeat (split <;> try (exact Or.inr ⟨_, rfl⟩))
  all_goals exact Or.inl ⟨_, rfl⟩

/-! ## 6. Scope, stated as the honest limit

**Proved:** the gate's guarantees. Nonce agreement is necessary for acceptance;
acceptance implies non-empty text; rejection always carries a reason;
self-reported confidence cannot flip the outcome; the gate is total; a proposal
carries no verdict.

**Not proved, and not provable in this design:** that the model's text is true,
useful, coherent, or non-harmful. That Python obeys its contract. That the
supervisor's timeout fires on a given platform. Those are behavioural claims
about a process and a network, checked by `cage/test/*.test.ts` and by the gate
in `cage/verify.sh`.

A Lean theorem is evidence about a model of the gate. It is not a runtime
guarantee, and `docs/TRUST_ASSUMPTIONS.md` is where the difference is recorded.
-/
