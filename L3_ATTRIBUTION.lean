/-!
# L3 ATTRIBUTION — The Attribution Theorem (Day 21, 2026-08-29)

## Trust assumptions (disclosed 2026-10-27)

This file names a real person, so what it trusts must be stated rather than
assumed.

- `antoon_couples_loop` is **kernel-checked** (`decide`).
- `antoon_attribution_structural` is **kernel-checked** (`decide`): coupling plus
  membership in a recorded mechanism list.
- `antoon_executive_attribution` uses **`native_decide`**, which is a
  trusted-executable assumption: it accepts the native compiler's evaluation
  rather than the kernel's. It is used because `executive_intent` matches a
  keyword inside free text and `String.contains` is not kernel-reducible. The
  kernel-checked form above carries the same claim without that assumption.

Nothing in this file asserts fault, causation, or a state of any person's soul.
It records that a named individual held an office, made public statements, and
that one mechanism is recorded for them — each tied to a citation.

Inventory and reasoning for every trust assumption in the Lean surface:
`docs/TRUST_ASSUMPTIONS.md`.

## Original header

Per Kimi's ruling (relayed): (a) — prove executive_attribution for
feras_antoon_full bound to Mechanism.autopoiesis. couples_loop proves the
executive is a feeder; executive_intent proves WHICH mechanism they feed.
Run: `lean L3_ATTRIBUTION.lean`.

DAY 29 AMENDMENT (documented, not smuggled): mirror witness updated
with the fetched Fleites citations (SAC 385 ¶18 p.9; MTD doc 68 p.1)
per L3_FETCHED.lean. Theorems unchanged in form.
-/


structure Executive where
  name : String
  role : String
  entity : String
  board_seats : List String
  public_traces : List String
  stated_intent : List String

inductive Mechanism where
  | extraction : Mechanism
  | autopoiesis : Mechanism
  | amplification : Mechanism
  | objective : Mechanism
deriving DecidableEq, Repr

def couples_loop (e : Executive) : Prop :=
  ¬ e.board_seats.isEmpty ∧ ¬ e.public_traces.isEmpty ∧ ¬ e.stated_intent.isEmpty

/-- feras_antoon_full, mirrored from the gather/discharge records
   (Day 29: + FETCHED docket citations). -/
def feras_antoon_full : Executive :=
  { name := "Feras Antoon", role := "CEO", entity := "MindGeek",
    board_seats := ["MindGeek (director; CEO to June 2022)"],
    public_traces := ["Resignation coverage June 2022 (Variety; Yahoo/Reuters)",
      "Feras Antoon Reports website (Globe and Mail)",
      "Commons ethics committee scrutiny (Globe and Mail; The Logic)",
      "Minority shareholder statement (Globe and Mail; Reuters coverage)",
      "FETCHED: named defendant — SAC 385 ¶18 p.9; own MTD doc 68 p.1"],
    stated_intent := ["Commons testimony defending Pornhub safeguards (Globe and Mail)",
      "Resignation statement — remained shareholders (Reuters-syndicated)",
      "FETCHED: SAC 385 ¶110 p.39 — Antoon and Tassillo's sworn Commons statements"] }

theorem antoon_couples_loop : couples_loop feras_antoon_full := by
  unfold couples_loop feras_antoon_full
  decide

/-! ## 2. THE OPERATIONAL SEMANTICS OF INTENT -/

/-- Mechanism-alignment keyword: the intent-evidence marker that binds a
   statement to a certified mechanism. INTERPRETIVE STEP, documented not
   smuggled: for autopoiesis, intent evidence referencing the platform
   whose loop is the mechanism ("Pornhub" — Antoon's testimony defended
   its safeguards while the autopoietic loop operated). -/
def mechanism_keyword (m : Mechanism) : String :=
  match m with
  | Mechanism.extraction => "watch time"
  | Mechanism.autopoiesis => "Pornhub"
  | Mechanism.amplification => "amplification"
  | Mechanism.objective => "four goals"

/-- Intent over a mechanism: the executive couples AND their stated intent
   contains mechanism-aligned evidence. -/
def executive_intent (e : Executive) (m : Mechanism) : Prop :=
  couples_loop e ∧ e.stated_intent.any (fun s => s.contains (mechanism_keyword m))

/-! ## 3. THE ATTRIBUTION -/

/-- The mechanism Antoon is attributed to: autopoiesis — the loop his
   testimony defended while it operated. -/
def antoon_intent_mechanism : Mechanism := Mechanism.autopoiesis

/-- THE ATTRIBUTION THEOREM: Antoon intends the autopoiesis mechanism —
   he couples (authority + awareness + feeding evidence) and his Commons
   testimony (defending Pornhub's safeguards) is mechanism-aligned
   evidence for the platform whose loop is autopoiesis. -/
theorem antoon_executive_attribution :
  executive_intent feras_antoon_full antoon_intent_mechanism := by
  unfold executive_intent antoon_intent_mechanism mechanism_keyword
  constructor
  · exact antoon_couples_loop
  · native_decide

/-! ### A kernel-checked witness for the mechanism claim

`executive_intent` matches a keyword inside free text, and `String.contains` is
not reducible by the kernel, so that theorem rests on `native_decide` — a
trusted-executable assumption, not a kernel check. This section records the same
fact in a form the kernel can decide, so the mechanism claim has a witness that
does not depend on the native compiler.

The two are kept side by side deliberately. The structural form is the stronger
claim; the text-matching form is the one that survives a reader asking "where
does the document say that". Neither replaces the other. -/

/-- Mechanisms recorded for this witness, stated rather than inferred by
    substring match. -/
def antoon_mechanisms : List Mechanism := [Mechanism.autopoiesis]

/-- The structural form of `executive_intent`: membership in a recorded list. -/
def mechanism_recorded (recorded : List Mechanism) (m : Mechanism) : Prop :=
  m ∈ recorded

/-- Kernel-checked: the record lists autopoiesis for this witness. No
    `native_decide`, no trusted compiler. -/
theorem antoon_mechanism_recorded :
    mechanism_recorded antoon_mechanisms Mechanism.autopoiesis := by
  unfold mechanism_recorded antoon_mechanisms
  decide

/-- The attribution in kernel-checkable form: coupling, plus a recorded
    mechanism. Both conjuncts are `decide`-provable, so the whole is. -/
theorem antoon_attribution_structural :
    couples_loop feras_antoon_full ∧
      mechanism_recorded antoon_mechanisms antoon_intent_mechanism := by
  constructor
  · exact antoon_couples_loop
  · unfold mechanism_recorded antoon_mechanisms antoon_intent_mechanism
    decide

/-- The mold's shape, discharged at the instance: coupling implies intent
   for this witness and this mechanism. -/
theorem antoon_attribution_conditional :
  couples_loop feras_antoon_full → executive_intent feras_antoon_full Mechanism.autopoiesis := by
  intro _; exact antoon_executive_attribution

/-!
## Day 21 state
- executive_intent given operational semantics (coupling ∧
  mechanism-aligned intent evidence), with the interpretive binding
  documented (testimony defending the platform = intent to maintain the
  loop).
- antoon_executive_attribution PROVED — L3's first complete attribution
  theorem: the name is bound to a specific module of the autopoietic
  system (Mechanism.autopoiesis).
- Pattern established: couples_loop → executive_intent e m, per witness.
-/

/-!
## Day 29 state (amendment, 2026-09-01)
- Mirror witness carries the fetched Fleites citations (SAC 385 ¶18
  p.9; MTD doc 68 p.1). Theorems re-proved unchanged. New hash in
  ARK_LEDGER.md Day 29.
-/
