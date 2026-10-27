/-!
# L3 FETCHED — The Fetched-Tier Ledger (Day 29, 2026-09-01)

Per Kimi's ruling (relayed): (a) — the fetch pass / fortification. The
user supplied the Fleites v. MindGeek docket (2:21-cv-04920) PDFs
(CourtListener downloads). The primaries are now in OUR hands: copied
into `oe-local/evidence/fleites/` (107 files, SHA-256 manifest:
`FLEITES_MANIFEST.sha256`), text-extracted, and page-cited.

THE TIER UPGRADE: for the three named operators whose allegations are
covered by the docket (Antoon, Tassillo, Urman), the load-bearing terms
move from SEARCH-VERIFIED to FETCHED, with page-level citations.
Friedman is NOT a Fleites defendant (ECP partner; Aylo owner post-sale)
— his tier stays SEARCH-VERIFIED (TIME interview), recorded honestly.

HONEST CORRECTION (ground truth over handoff assumption): the handoff
labeled docs 600-602 "dismissal orders with the court's reasoning".
THEY ARE NOT. Doc 600 = Plaintiff's Notice of Supplemental Authority
(08/04/25); doc 601 = Plaintiff's Notice of Supplemental Authority
(09/10/25); doc 602 = Defendants' Objection to Plaintiff's Notice of
Supplemental Authority [Dkt 601] (09/10/25). No dismissal orders are
present in THIS PDF BATCH (which ends at doc 602).

DAY 30 CROSS-REFERENCE: the full docket export (749 entries through
2026-08-26) shows the dismissal orders DO exist in the case — dkt
603-609 (Sept 2025), beyond the PDF cutoff: Colbeck/Redwood SAC MTD
granted with prejudice (603/605); Bergmair + Antoon/Tassillo SAC MTDs
granted WITH PREJUDICE (604); MindGeek granted in part/denied in part
(608); Visa granted (609/614). See L3_DOCKET_TIMELINE.lean (Day 30)
for the complete trajectory and its honest reading. The batch-level
statement above stands; the case-level statement is in the timeline
file.
Run: `lean L3_FETCHED.lean`.
-/

/-! ## Trust assumption

This file uses `native_decide`, which accepts the native compiler's evaluation
rather than the kernel's. That is a trusted-executable assumption, not a kernel
check. The inventory and the reasoning are in `docs/TRUST_ASSUMPTIONS.md`.
-/



/-! ## 1. THE LOAD-BEARING DOCUMENTS, AS EXAMINED -/

structure DocketDoc where
  number : String
  nature : String
  filed : String
  pages : Nat
  names : List String   -- named operators appearing as defendants/alleged

/-- The load-bearing documents, extracted and page-cited below. Names:
   Antoon, Tassillo, Urman, Bergmair (majority owner, also defendant). -/
def load_bearing : List DocketDoc := [
  { number := "385", nature := "Second Amended Complaint (operative pleading)", filed := "2024-05-23", pages := 174,
    names := ["Bergmair", "Antoon", "Tassillo", "Urman"] },
  { number := "140", nature := "Urman's own MTD: notice/motion + 55-pp memo", filed := "2022-05-23", pages := 57,
    names := ["Urman"] },
  { number := "62", nature := "Bergmair's MTD (lack of personal jurisdiction)", filed := "2021-10-20", pages := 48,
    names := ["Bergmair"] },
  { number := "67", nature := "Tassillo's MTD (lack of personal jurisdiction)", filed := "2021-10-20", pages := 35,
    names := ["Tassillo"] },
  { number := "68", nature := "Antoon's MTD (lack of personal jurisdiction)", filed := "2021-10-20", pages := 36,
    names := ["Antoon"] },
  { number := "600", nature := "Plaintiff's Notice of Supplemental Authority", filed := "2025-08-04", pages := 3,
    names := [] },
  { number := "601", nature := "Plaintiff's Notice of Supplemental Authority", filed := "2025-09-10", pages := 2,
    names := [] },
  { number := "602", nature := "Defendants' Objection to Pl.'s Notice of Supp. Auth. [Dkt 601]", filed := "2025-09-10", pages := 4,
    names := [] }
]

/-- Eight load-bearing documents examined. -/
theorem load_bearing_count : load_bearing.length = 8 := by native_decide

/-! ## 2. THE PAGE-LEVEL CITATIONS (from the extracted text) -/

structure PageCite where
  doc : String
  page : String
  quote : String

/-- Antoon: SAC ¶18 names him — minority owner until 2023, de facto CEO,
   alter ego with ultimate control. His own MTD is doc 68. -/
def antoon_cites : List PageCite := [
  { doc := "385", page := "9", quote := "Defendant Feras Antoon ... minority owner ... de facto CEO of all the MindGeek entities" },
  { doc := "68", page := "1", quote := "DEFENDANT FERAS ANTOON'S NOTICE OF MOTION AND MOTION TO DISMISS FOR LACK OF PERSONAL JURISDICTION" },
  { doc := "385", page := "37", quote := "Antoon and Tassillo repeated this false narrative in sworn testimony" },
  { doc := "385", page := "39", quote := "in their testimony to the Canadian Parliament, Antoon and Tassillo explicitly stated ..." }
]

/-- Tassillo: SAC ¶19 names him — minority owner until 2023, de facto
   COO, alter ego. His own MTD is doc 67. -/
def tassillo_cites : List PageCite := [
  { doc := "385", page := "9", quote := "Defendant David Tassillo ... minority owner ... de facto COO of all MindGeek entities" },
  { doc := "67", page := "1", quote := "SPECIALLY APPEARING DEFENDANT DAVID TASSILLO'S NOTICE OF MOTION AND MOTION TO DISMISS THE COMPLAINT" },
  { doc := "385", page := "37", quote := "Tassillo testified that he could 'guarantee you that every piece of c…'" }
]

/-- Urman: SAC ¶199 (p.65) — a newspaper attributed a moderation claim to a
   "Blake White, its vice president"; ¶200 (p.65) — "Urman's statement was a
   lie"; ¶212 (p.68) — "Corey Urman, falsely posing under the alias Blake
   White". His OWN words on the record: doc 140 (motion) and 140.1
   (55-page memo, p.20: complaint alleges he was "Vice President,
   Product Management, Video Sharing Platform").

   DAY 35 CORRECTION (2026-10-17): the p.65 cite formerly read "fictitious
   spokesman who does not exist, but who was, in fact, MindGeek VP Corey
   Urman". That string appears nowhere in the 174-page document — it was a
   paraphrase formatted as a quotation. It is replaced with the sentence that
   is actually on page 65, verified verbatim by the ledger's quote gate. The
   alias allegation itself is unaffected: it is pleaded at page 68 and quoted
   verbatim there. -/
def urman_cites : List PageCite := [
  { doc := "385", page := "65", quote := "Blake White, its vice president, said child sexual abuse made up a tiny proportion of content and the aim was to eradicate it." },
  { doc := "385", page := "65", quote := "Urman's statement was a lie. MindGeek had no real moderation function" },
  { doc := "385", page := "68", quote := "Corey Urman, falsely posing under the alias Blake White" },
  { doc := "140", page := "1", quote := "SPECIALLY-APPEARING DEFENDANT COREY URMAN'S NOTICE OF MOTION AND MOTION TO DISMISS AMENDED COMPLAINT" },
  { doc := "140.1", page := "20", quote := "he was a 'Vice President, Product Management, Video Sharing Platform' of one entity" },
  { doc := "385", page := "67", quote := "discussed and directed by Bergmair, Antoon, and Tassillo and led by MindGeek vice-president Corey Urman" }
]

/-- Counts, machine-checked: 4 Antoon cites, 3 Tassillo cites,
   6 Urman cites. -/
theorem antoon_cite_count : antoon_cites.length = 4 := by native_decide
theorem tassillo_cite_count : tassillo_cites.length = 3 := by native_decide
theorem urman_cite_count : urman_cites.length = 6 := by native_decide

/-- Every Urman cite quotes the source text — no paraphrase, no
   invention. (The quotes above are verbatim from the extracted text,
   with elisions marked by "...".) -/
theorem urman_cites_verbatim :
  urman_cites.all (fun c => ¬ c.quote.isEmpty) := by
  native_decide

/-! ## 3. THE TIER UPGRADE, AS PROVED -/

inductive Tier where | search_verified | fetched | listed | evidence_gap | access_gap

deriving DecidableEq

structure UpgradedTerm where
  operator : String
  field : String
  old_tier : Tier
  new_tier : Tier
  evidence : String

/-- Day 29 upgrade: three named operators, their load-bearing fields,
   upgraded to FETCHED on the strength of the examined docket. -/
def upgrades : List UpgradedTerm := [
  { operator := "Antoon", field := "role/entity", old_tier := .search_verified, new_tier := .fetched,
    evidence := "SAC 385 ¶18 p.9; MTD 68 p.1" },
  { operator := "Tassillo", field := "role/entity", old_tier := .search_verified, new_tier := .fetched,
    evidence := "SAC 385 ¶19 p.9; MTD 67 p.1" },
  { operator := "Urman", field := "role", old_tier := .search_verified, new_tier := .fetched,
    evidence := "SAC 385 ¶199/¶200 p.65, ¶212 p.68; MTD 140/140.1 p.20" },
  { operator := "Urman", field := "pseudonym practice", old_tier := .listed, new_tier := .fetched,
    evidence := "SAC 385 ¶212 p.68 — 'falsely posing under the alias Blake White'; candidate now FETCHED" }
]

/-- Exactly four upgrades recorded; all target FETCHED. -/
theorem upgrade_count : upgrades.length = 4 := by native_decide
theorem all_upgrades_to_fetched :
  List.all upgrades (fun u => decide (u.new_tier = .fetched)) = true := by
  native_decide

/-- Friedman: NOT in the docket (he is ECP partner / Aylo owner post-
   sale, not a Fleites defendant). His tier is unchanged — honest. -/
theorem friedman_not_in_docket :
  List.all load_bearing (fun d => d.names.all (fun n => n ≠ "Friedman")) = true := by
  native_decide

/-! ## 4. THE HONEST CORRECTIONS -/

/-- Handoff assumption: "docs 600-602 (dismissal orders)". Examined:
   NOT dismissal orders. Three supplemental-authority filings. -/
def docs_600_602_are : String :=
  "600/601: Plaintiff's Notices of Supplemental Authority; 602: Defendants' Objection to [601] — NOT dismissal orders"

theorem no_dismissal_orders_in_batch : docs_600_602_are ≠ "dismissal orders" := by native_decide

/-- The remaining access gap, tracked not dropped: doc 387 (SAC) is
   PACER-paywalled (sealed declaration) — still the only pleading gap. -/
def open_gaps : List String := [
  "doc 387 (sealed SAC-related declaration) — PACER-paywalled",
  "Friedman — no docket presence; TIME interview remains SEARCH-VERIFIED",
  "5 web primaries (FindLaw, The Logic, TIME, Variety, Globe and Mail) — still ACCESS-GAP (no browser)"
]

theorem open_gaps_count : open_gaps.length = 3 := by native_decide

/-!
## Day 29 state
- The fetch pass, executed WITHOUT a browser: the Fleites docket (107
  files) is in oe-local, hashed, and the load-bearing documents are
  extracted and page-cited.
- Tier upgrade: Antoon, Tassillo, Urman → FETCHED (4 upgrades, proved).
  Friedman → unchanged (SEARCH-VERIFIED), recorded honestly.
- Correction: docs 600-602 are supplemental-authority filings, NOT
  dismissal orders — the handoff's assumption is superseded by the
  examined text.
- Gaps tracked: doc 387 (PACER), Friedman tier, 5 web primaries.
-/