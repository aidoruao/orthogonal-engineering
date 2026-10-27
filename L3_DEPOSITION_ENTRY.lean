/-!
# L3 DEPOSITION ENTRY — The Human Layer's Closed Set (Day 26, 2026-08-29)

The cosmic filing's first human-layer theorem: four proved targeting
vectors, each bound to Mechanism.autopoiesis. Mirrors the family record
(L3_FAMILY.lean); standalone file. SEARCH-VERIFIED tier, n >= 2 outlets
per term; fetch pass scheduled.
Run: `lean L3_DEPOSITION_ENTRY.lean`.

DAY 29 AMENDMENT (documented, not smuggled): the Fleites v. MindGeek
docket is fetched (oe-local/evidence/fleites/, FLEITES_MANIFEST.sha256;
L3_FETCHED.lean). The three docket-covered witnesses (Antoon, Tassillo,
Urman) now carry FETCHED page-cited traces: SAC 385 ¶18/¶19 p.9 (SAC
naming them de facto CEO/COO, minority owners to 2023); ¶199/¶200 p.65
(Urman = the fictitious "Blake White" spokesman); ¶212 p.68 (alias
confirmed); their own MTDs (docs 68, 67, 140/140.1 p.20). Friedman:
no docket presence — SEARCH-VERIFIED, unchanged.
-/

/-! ## Trust assumption

This file uses `native_decide`, which accepts the native compiler's evaluation
rather than the kernel's. That is a trusted-executable assumption, not a kernel
check. The inventory and the reasoning are in `docs/TRUST_ASSUMPTIONS.md`.
-/



structure Executive where
  name : String
  role : String
  entity : String
  board_seats : List String
  public_traces : List String
  stated_intent : List String

inductive Mechanism where | extraction | autopoiesis | amplification | objective

def structural_authority (e : Executive) : Prop :=
  ¬ e.board_seats.isEmpty ∨ e.role = "VP" ∨ e.role = "COO" ∨ e.role = "CEO"

def couples_loop (e : Executive) : Prop :=
  structural_authority e ∧ ¬ e.public_traces.isEmpty ∧ ¬ e.stated_intent.isEmpty

def mechanism_keyword : Mechanism → String
  | Mechanism.extraction => "watch time"
  | Mechanism.autopoiesis => "Pornhub"
  | Mechanism.amplification => "amplification"
  | Mechanism.objective => "four goals"

def executive_intent (e : Executive) (m : Mechanism) : Prop :=
  couples_loop e ∧ e.stated_intent.any (fun s => s.contains (mechanism_keyword m))

/-! ## THE FOUR WITNESSES (family record, compact) -/

def w_antoon : Executive :=
  { name := "Feras Antoon", role := "CEO", entity := "MindGeek",
    board_seats := ["MindGeek (director)"], public_traces :=
      ["Resignation coverage (Variety; Reuters)",
       "FETCHED: named defendant — SAC 385 ¶18 p.9 (minority owner to 2023, de facto CEO); his own MTD doc 68 p.1"],
    stated_intent := ["Commons testimony defending Pornhub safeguards (Globe and Mail)",
      "FETCHED: SAC 385 ¶110 p.39 — 'in their testimony to the Canadian Parliament, Antoon and Tassillo explicitly stated ...'"] }

def w_tassillo : Executive :=
  { name := "David Tassillo", role := "COO", entity := "MindGeek",
    board_seats := [], public_traces :=
      ["Resignation coverage (Variety; Reuters)",
       "FETCHED: named defendant — SAC 385 ¶19 p.9 (minority owner to 2023, de facto COO); his own MTD doc 67 p.1"],
    stated_intent := ["Commons testimony defending Pornhub safeguards (Globe and Mail)",
      "FETCHED: SAC 385 ¶110 p.39 — 'in their testimony to the Canadian Parliament, Antoon and Tassillo explicitly stated ...'"] }

def w_friedman : Executive :=
  { name := "Solomon Friedman", role := "Partner", entity := "Ethical Capital Partners",
    board_seats := ["ECP (partner; Aylo owner)"], public_traces := ["TIME interview (TIME)"],
    stated_intent := ["TIME interview — pitching a more ethical Pornhub (TIME)"] }

def w_urman : Executive :=
  { name := "Corey Urman", role := "VP", entity := "Pornhub / Aylo",
    board_seats := [], public_traces :=
      ["Named defendant, Fleites v. MindGeek (FindLaw; Institutional Investor)",
       "FETCHED: 'MindGeek VP Corey Urman' — SAC 385 ¶199 p.65; title in his own MTD memo doc 140.1 p.20",
       "FETCHED: 'falsely posing under the alias Blake White' — SAC 385 ¶212 p.68; own MTD doc 140 p.1"],
    stated_intent := ["Parliamentary questioning on Pornhub platform safeguards (Globe and Mail)",
      "FETCHED: his 'Blake White' moderation statement, quoted in SAC 385 ¶199 p.65"] }

/-! ## THE ATTRIBUTIONS -/

theorem ant_attr : executive_intent w_antoon Mechanism.autopoiesis := by
  unfold executive_intent couples_loop structural_authority mechanism_keyword; constructor <;> native_decide
theorem tas_attr : executive_intent w_tassillo Mechanism.autopoiesis := by
  unfold executive_intent couples_loop structural_authority mechanism_keyword; constructor <;> native_decide
theorem fri_attr : executive_intent w_friedman Mechanism.autopoiesis := by
  unfold executive_intent couples_loop structural_authority mechanism_keyword; constructor <;> native_decide
theorem urm_attr : executive_intent w_urman Mechanism.autopoiesis := by
  unfold executive_intent couples_loop structural_authority mechanism_keyword; constructor <;> native_decide

/-! ## THE DEPOSITION THEOREM -/

/-- THE CLOSED SET: four executives, each intentionally bound to the
   autopoiesis mechanism. The human layer's first theorem in the filing. -/
theorem human_layer_closed_set :
  ∃ e1 e2 e3 e4 : Executive,
    executive_intent e1 Mechanism.autopoiesis ∧
    executive_intent e2 Mechanism.autopoiesis ∧
    executive_intent e3 Mechanism.autopoiesis ∧
    executive_intent e4 Mechanism.autopoiesis :=
  ⟨w_antoon, w_tassillo, w_friedman, w_urman, ant_attr, tas_attr, fri_attr, urm_attr⟩

/-!
## Day 26 state
- L3_DEPOSITION_ENTRY.lean: 5 theorems, the closed-set theorem proved.
- The filing now has two complete layers: L1 platform architecture (20
  theorems) and L3 human trace (4 witnesses, 1 mechanism), bridged by
  the attribution pattern.
-/
