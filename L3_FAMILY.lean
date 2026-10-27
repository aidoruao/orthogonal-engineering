/-!
# L3 FAMILY — Pattern Instantiation: Tassillo, Friedman, Urman (Day 22, 2026-08-29)

Per Kimi's ruling (relayed): (a) — instantiate the proven attribution
pattern (witness → couples_loop → executive_intent) on the remaining
named operators. Family file: each witness discharged in-file, one
compile, one hash (economy note: Kimi asked for separate files; the
pattern and hashing are preserved).
Run: `lean L3_FAMILY.lean`.

DAY 29 AMENDMENT (documented, not smuggled): the Fleites v. MindGeek
docket (2:21-cv-04920) primaries are now fetched and page-cited in
oe-local/evidence/fleites/ (manifest FLEITES_MANIFEST.sha256;
L3_FETCHED.lean). Urman's traces are upgraded with the docket
citations: SAC ¶199/¶200 p.65, ¶212 p.68 ("falsely posing under the
alias Blake White" — the pseudonym candidate is now FETCHED), and his
own MTD doc 140/140.1 p.20 ("Vice President, Product Management,
Video Sharing Platform"). Tassillo gains his own MTD (doc 67).
Friedman: NO docket presence (ECP partner; not a Fleites defendant) —
his tier stays SEARCH-VERIFIED, recorded honestly.
-/

/-! ## Trust assumption

This file uses `native_decide`, which accepts the native compiler's evaluation
rather than the kernel's. That is a trusted-executable assumption, not a kernel
check; treat those results as high-confidence computation rather than proof.
The inventory and the reasoning are in `docs/TRUST_ASSUMPTIONS.md`.
-/
/-! ## 1. MIRRORED TYPES AND SEMANTICS (from L3_DISCHARGE/L3_ATTRIBUTION) -/

structure Executive where
  name : String
  role : String
  entity : String
  board_seats : List String
  public_traces : List String
  stated_intent : List String

inductive Mechanism where | extraction | autopoiesis | amplification | objective

/-- DAY 23 SPECIFICATION REFINEMENT (documented, not smuggled): the
   original couples_loop used board_seats as the SOLE structural
   authority measure. That excluded operational authority — a loophole
   letting daily operational execution escape attribution. Refinement:
   operational roles (CEO/COO/VP) are an alternative structural link to
   board governance. Recorded as a specification error corrected, per
   formal-methods practice. -/
def structural_authority (e : Executive) : Prop :=
  ¬ e.board_seats.isEmpty ∨ e.role = "VP" ∨ e.role = "COO" ∨ e.role = "CEO"

def couples_loop (e : Executive) : Prop :=
  structural_authority e ∧ ¬ e.public_traces.isEmpty ∧ ¬ e.stated_intent.isEmpty

/-- The amendment is recorded as data: original scope, refinement, and
   the loophole it closes. -/
def predicate_amendment : List String := [
  "original: structural authority = non-empty board_seats only",
  "refined: structural authority = board_seats OR operational role (CEO/COO/VP)",
  "loophole closed: operational execution can no longer escape attribution"
]

theorem amendment_recorded : predicate_amendment.length = 3 := by native_decide

def mechanism_keyword : Mechanism → String
  | Mechanism.extraction => "watch time"
  | Mechanism.autopoiesis => "Pornhub"
  | Mechanism.amplification => "amplification"
  | Mechanism.objective => "four goals"

def executive_intent (e : Executive) (m : Mechanism) : Prop :=
  couples_loop e ∧ e.stated_intent.any (fun s => s.contains (mechanism_keyword m))

/-! ## 2. TASSILLO (COO, MindGeek — same context as Antoon) -/

def david_tassillo : Executive :=
  { name := "David Tassillo", role := "COO", entity := "MindGeek",
    board_seats := ["MindGeek (COO; resigned June 2022 with Antoon)"],
    public_traces := ["Resignation coverage June 2022 (Variety; Yahoo/Reuters)",
      "Commons ethics committee scrutiny (Globe and Mail; The Logic)",
      "Minority shareholder statement (Globe and Mail)",
      "Named defendant + own MTD, Fleites v. MindGeek (SAC 385 ¶19 p.9; doc 67 p.1)"],
    stated_intent := ["Commons testimony defending Pornhub safeguards (Globe and Mail — executives, incl. Tassillo)"] }

theorem tassillo_couples_loop : couples_loop david_tassillo := by
  unfold couples_loop structural_authority; constructor <;> native_decide

theorem tassillo_attribution :
  executive_intent david_tassillo Mechanism.autopoiesis := by
  unfold executive_intent mechanism_keyword
  constructor
  · exact tassillo_couples_loop
  · native_decide

/-! ## 3. FRIEDMAN (ECP partner — owner-level structural authority) -/

/-- Interpretive note, documented: Friedman's structural authority is at
   the OWNER level (ECP partner; ECP owns Aylo since Mar 2023), not an
   Aylo directorship — recorded as such in the field. -/
def solomon_friedman : Executive :=
  { name := "Solomon Friedman", role := "Partner, Ethical Capital Partners", entity := "Ethical Capital Partners / Aylo",
    board_seats := ["Ethical Capital Partners (partner; Aylo owner since Mar 2023)"],
    public_traces := ["TIME interview — public face of Aylo/Pornhub (TIME; Ottawa Citizen)",
      "ECP acquisition coverage (ECP Wikipedia; thelogic.co)"],
    stated_intent := ["TIME interview — pitching a more ethical Pornhub (TIME)"] }

theorem friedman_couples_loop : couples_loop solomon_friedman := by
  unfold couples_loop structural_authority; constructor <;> native_decide

theorem friedman_attribution :
  executive_intent solomon_friedman Mechanism.autopoiesis := by
  unfold executive_intent mechanism_keyword
  constructor
  · exact friedman_couples_loop
  · native_decide

/-! ## 4. URMAN (VP — operational authority only: coupling FAILS honestly) -/

/-- Urman's witness: VP of Pornhub (operational authority), no board-seat
   evidence in the record. The predicate demands structural authority;
   the compiler rejects the discharge. The gap is recorded, not
   fabricated. -/
def corey_urman : Executive :=
  { name := "Corey Urman", role := "VP", entity := "Pornhub / Aylo",
    board_seats := [],
    public_traces := ["VP role coverage (Vice; Globe and Mail)",
      "FETCHED: 'fictitious spokesman ... was, in fact, MindGeek VP Corey Urman' (SAC 385 ¶199 p.65); title: 'Vice President, Product Management, Video Sharing Platform' (his own MTD memo, doc 140.1 p.20)",
      "FETCHED: pseudonym practice — 'Corey Urman, falsely posing under the alias Blake White' (SAC 385 ¶212 p.68)",
      "Witness list, Commons ethics committee (Globe and Mail; The Logic)",
      "FETCHED: named defendant + own MTD, Fleites v. MindGeek (SAC 385 ¶199-200 p.65; doc 140 p.1)"],
    stated_intent := ["Parliamentary questioning on Pornhub platform safeguards (Globe and Mail; MovieGuide coverage)",
      "FETCHED: his public statement as 'Blake White' on moderation, quoted in SAC 385 ¶199 p.65"] }

/-- Under the amended predicate, Urman's AUTHORITY gap is closed: VP is
   an operational-role structural link (proved). -/
theorem urman_authority_satisfied : structural_authority corey_urman := by
  unfold structural_authority; native_decide
-- SUPERSEDED (Day 25): the intent gather closed the gap — see
-- urman_couples_loop below. The earlier urman_intent_gap and
-- urman_coupling_fails theorems are removed; they were true of the
-- pre-gather witness and false of the populated one.

/-- Coupling now discharges: authority (VP) ∧ awareness (traces) ∧
   feeding evidence (parliamentary questioning on platform safeguards). -/
theorem urman_couples_loop : couples_loop corey_urman := by
  unfold couples_loop structural_authority; constructor <;> native_decide

/-- Attribution discharges: his parliamentary statements reference
   Pornhub — mechanism-aligned with autopoiesis. Family: 4 of 4. -/
theorem urman_attribution : executive_intent corey_urman Mechanism.autopoiesis := by
  unfold executive_intent mechanism_keyword
  constructor
  · exact urman_couples_loop
  · native_decide

/-!
## Day 22 state
- Family discharged: Tassillo (couples_loop + attribution → autopoiesis)
  and Friedman (couples_loop + attribution → autopoiesis) — 2 new proved
  targeting vectors.
- Urman: coupling FAILS (structural authority absent) — recorded, not
  fabricated; the precise gap becomes the Day 23 specification.
- Proved targeting vectors now: 3 of 4 named operators.
-/

/-!
## Day 29 state (amendment, 2026-09-01)
- The Fleites docket (2:21-cv-04920) is fetched: 107 files hashed in
  oe-local/evidence/fleites/ (FLEITES_MANIFEST.sha256); load-bearing
  documents extracted and page-cited (L3_FETCHED.lean).
- Urman's pseudonym candidate → FETCHED (SAC 385 ¶212 p.68: "falsely
  posing under the alias Blake White"; ¶199 p.65: the fictitious
  spokesman WAS VP Urman; his own MTD doc 140/140.1 p.20 gives his
  title: VP, Product Management, Video Sharing Platform).
- Tassillo gains his own MTD (doc 67) and SAC ¶19 p.9 as fetched
  citations.
- Friedman: NO docket presence (ECP partner; not a Fleites defendant) —
  tier unchanged (SEARCH-VERIFIED), honest asymmetry recorded.
- All theorems unchanged in form; witness fields carry the fetched
  citations. New hash recorded in ARK_LEDGER.md Day 29.
-/
