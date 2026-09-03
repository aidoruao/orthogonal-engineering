/-!
# L3 DOCKET TIMELINE — The Full Case Trajectory (Day 30, 2026-09-03)

SOURCE: the CourtListener docket export the user downloaded on
2026-09-01 — `serena-fleites-v-mindgeek-sarl.cacd.59992265.2026-09-01.csv`
(1925 rows incl. header; 749 contiguous numbered docket entries
1-749, no gaps — verified by scan; copied into oe-local/evidence/
fleites/ and SHA-256-anchored in FLEITES_MANIFEST.sha256 on Day 30).
The 107 PDFs (Day 29) stop at doc 602; this CSV carries the record to
entry 749 (2026-08-26).

WHY THIS FILE EXISTS — the Day-29 correction, recorded honestly:
Day 29 stated "docs 600-602 are NOT dismissal orders... no dismissal
orders are present in this batch." That was TRUE of the PDF batch and
MISLEADING as a case statement: the dismissal orders EXIST at dkt
603-609 (Sept 2025) — beyond the PDF cutoff. The docket export closes
the gap. This file records the trajectory as found.

THE FOUR OPERATORS' CASE STATUS (as found, not as assumed):
- Antoon, Bergmair, Tassillo: named defendants in the SAC (dkt 385,
  2024-05-23). Their SAC MTDs (dkt 433 = Bergmair; 436 = Antoon +
  Tassillo) were GRANTED WITH PREJUDICE (dkt 604, 2025-09-15): the
  Court found the deficiencies mirrored earlier motions and were
  uncured after multiple amendments and jurisdictional discovery.
  This is a pleading/jurisdiction outcome — NOT a merits finding that
  the allegations are false. Recorded as a dismissal order, not as an
  acquittal; the L3 witness facts (roles, own filings, alleged
  control) stand as alleged-in-litigation facts with their tier.
- Urman: named defendant 2021-2023 (original + amended complaints;
  his own MTD dkt 140/140.1, 2022). NOT re-named in the SAC (dkt 385
  caption) — no SAC-era Urman MTD exists because he was not a SAC
  defendant. His docket activity ends Aug 2023 (counsel changes).
- Friedman: ZERO mentions in the entire 750-entry docket (verified by
  full-text scan) — consistent with Day 29's honest note: he is ECP
  partner / post-sale owner, not a Fleites defendant.
- The case continued WITHOUT individual defendants: Third Amended
  Complaint (dkt 622, 2025-12-15, entities only), Redwood MTD granted
  with prejudice (dkt 733, 2026-07-09), CB defendants MTD granted
  (dkt 735, 2026-07-20), Rule 54(b) judgment motion filed (dkt 746,
  2026-08-05, hearing 2026-09-18).

WHAT THIS MEANS FOR THE ARK (honest consequence):
- The Fleites docket remains FETCHED-tier PRIMARY evidence of the
  operators' roles, their own filings, and the operative complaint's
  allegations. Nothing in the trajectory retracts those facts.
- The trajectory adds a binding citation rule: when the filing refers
  to the individuals as "defendants in Fleites," it must reflect the
  full arc — named in the original/amended complaints (2021-2022),
  SAC defendants (Antoon/Bergmair/Tassillo, 2024), dismissed with
  prejudice on pleading grounds (2025), case continuing against
  entities (2026). The dismissal orders are court records of
  insufficiency findings — they belong in the evidentiary record with
  their true meaning, never spun.
- A NEW closure fact for the record: the Court's Rule 54(b) phase
  (dkt 746) concerns the entity defendants, not the individuals.
Run: `lean L3_DOCKET_TIMELINE.lean`.
-/

/-! ## 1. THE TRAJECTORY, ENCODED AS FOUND -/

structure DocketEvent where
  number : String
  date : String
  kind : String
  detail : String

/-- The load-bearing events after the PDF cutoff (docs 602+), from the
   docket export. Dates are the filing/entry dates as recorded. -/
def post_602_events : List DocketEvent := [
  { number := "603", date := "2025-09-10", kind := "ORDER",
    detail := "Colbeck + Redwood SAC MTD GRANTED with prejudice (amended by 605)" },
  { number := "604", date := "2025-09-15", kind := "ORDER",
    detail := "Bergmair MTD (433) + Antoon/Tassillo MTD (436) of SAC GRANTED WITH PREJUDICE — deficiencies uncured after multiple amendments and jurisdictional discovery" },
  { number := "605", date := "2025-09-17", kind := "AMENDED ORDER",
    detail := "Colbeck/Redwood: leave to amend within 21 days after outstanding MTDs resolved" },
  { number := "608", date := "2025-09-26", kind := "ORDER",
    detail := "MindGeek SAC MTD (440) GRANTED in part, DENIED in part; leave to file TAC within 21 days" },
  { number := "609", date := "2025-09-26", kind := "ORDER",
    detail := "Visa SAC MTD (432) GRANTED (amended by 614 with count-by-count with/without prejudice)" },
  { number := "622", date := "2025-12-15", kind := "FILING",
    detail := "THIRD AMENDED COMPLAINT — ENTITY defendants only (MindGeek entities, Visa, Colbeck/Redwood/CB, TrafficJunky); no individual operators" },
  { number := "733", date := "2026-07-09", kind := "ORDER",
    detail := "Redwood TAC MTD (640) GRANTED with prejudice (third iteration, uncured defects)" },
  { number := "735", date := "2026-07-20", kind := "ORDER",
    detail := "CB defendants TAC MTD (635) GRANTED: TVPRA beneficiary liability, conspiracy, UCL, civil conspiracy — with prejudice" },
  { number := "746", date := "2026-08-05", kind := "MOTION",
    detail := "Plaintiff's Rule 54(b) motion for entry of final judgment as to dkt 733/735 (hearing 2026-09-18)" }
]

/-- Nine load-bearing post-602 events recorded. -/
theorem post_602_event_count : post_602_events.length = 9 := by native_decide

/-- Every event carries a number, date, kind and detail — no empty
   records. -/
theorem events_complete :
  List.all post_602_events (fun e => ¬ e.number.isEmpty ∧ ¬ e.date.isEmpty ∧ ¬ e.kind.isEmpty ∧ ¬ e.detail.isEmpty) = true := by
  native_decide

/-! ## 2. THE OPERATORS' CASE ARC -/

structure OperatorCase where
  name : String
  sac_defendant : Bool
  sac_mtd : String        -- docket numbers
  dismissed_with_prejudice : Bool
  dismissal_authority : String
  last_activity : String

/-- The arc, as found in the docket export. -/
def operator_arcs : List OperatorCase := [
  { name := "Antoon", sac_defendant := true, sac_mtd := "436 (with Tassillo)",
    dismissed_with_prejudice := true, dismissal_authority := "dkt 604 (2025-09-15)",
    last_activity := "counsel appearances through 2024-2025 MTD round" },
  { name := "Tassillo", sac_defendant := true, sac_mtd := "436 (with Antoon)",
    dismissed_with_prejudice := true, dismissal_authority := "dkt 604 (2025-09-15)",
    last_activity := "counsel appearances through 2024-2025 MTD round" },
  { name := "Bergmair", sac_defendant := true, sac_mtd := "433",
    dismissed_with_prejudice := true, dismissal_authority := "dkt 604 (2025-09-15)",
    last_activity := "counsel appearances through 2024-2025 MTD round" },
  { name := "Urman", sac_defendant := false, sac_mtd := "none (not a SAC defendant)",
    dismissed_with_prejudice := false, dismissal_authority := "not named in SAC (385); own MTD 140 was the 2022 amended-complaint round",
    last_activity := "counsel changes through 2023-08 (dkt 371); not re-named thereafter" },
  { name := "Friedman", sac_defendant := false, sac_mtd := "none",
    dismissed_with_prejudice := false, dismissal_authority := "never a party — zero mentions in 750-entry docket",
    last_activity := "none in this docket" }
]

/-- Five operators tracked; three were SAC defendants dismissed with
   prejudice; Urman and Friedman were not SAC defendants. -/
theorem operator_arc_count : operator_arcs.length = 5 := by native_decide

theorem three_dismissed_with_prejudice :
  (operator_arcs.filter (fun o => o.dismissed_with_prejudice)).length = 3 := by
  native_decide

theorem sac_defendants_are_three :
  (operator_arcs.filter (fun o => o.sac_defendant)).length = 3 := by
  native_decide

/-! ## 3. THE HONEST READINGS -/

/-- Reading 1: the dismissal is a pleading/jurisdiction outcome. Dkt
   604's own words (quoted): the deficiencies "mirror those raised in
   Defendants' earlier motions"; plaintiff had "multiple opportunities
   to amend plus jurisdictional discovery but has failed to cure the
   defects." It is NOT a merits finding that the underlying conduct
   allegations are false. -/
def dismissal_basis : String :=
  "pleading insufficiency after multiple amendments + jurisdictional discovery (dkt 604) — not a merits acquittal"

theorem dismissal_basis_recorded : dismissal_basis ≠ "" := by native_decide

/-- Reading 2: the L3 witness facts stand at their documented tier.
   The roles (SAC ¶17-19), the own-filings (docs 62/67/68/140), and the
   operative allegations (¶199-212) are FETCHED facts about what was
   alleged and filed. The trajectory adds case status, not retraction. -/
def trajectory_does_not_retract : Prop := True

/-!
## Day 30 state
- The docket export (750 entries through 2026-08-26) is filed and
  mined. Day 29's "no dismissal orders in this batch" is corrected:
  the orders exist at dkt 603-609; the PDF batch simply stopped at 602.
- Operator arc recorded: Antoon/Tassillo/Bergmair — SAC defendants,
  MTDs granted with prejudice (dkt 604); Urman — 2021-2023 defendant,
  not re-named in SAC; Friedman — never a party.
- Case continues against entities (TAC 622; Rule 54(b) phase, 746).
- The filing's citation rules now include the full arc; the dismissal
  orders are recorded with their true meaning (insufficiency findings,
  not acquittals).
-/
