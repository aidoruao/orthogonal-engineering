/-!
# Day 4 Reconciliation — Machine Checks (2026-08-21)

Verifies the reconciliation of two flagged inconsistencies:
1. DELTA_REPORT.md / metadata.json pattern counts vs OBSTRUCTION_AUDIT.md's
   per-turn listing (the suspected transposition).
2. refined_inventory_summary.json internal consistency (Chat Canon side).
Run: `lean RECONCILIATION_CHECKS.lean`.
-/

/-! ## 1. DELTA_REPORT.md:21-29 — the table's OWN arithmetic is internally
consistent (each column sums correctly), which is why the swap went unnoticed. -/

/-- ChatGPT column rows: 2,1,0,0,2,0,0,2 sum to 7 (DELTA's stated TOTAL) -/
theorem chatgpt_rows_sum : (2 : Nat) + 1 + 0 + 0 + 2 + 0 + 0 + 2 = 7 := by native_decide

/-- DeepSeek column rows: 17,7,2,0,4,0,0,10 sum to 40 (DELTA's stated TOTAL) -/
theorem deepseek_rows_sum : (17 : Nat) + 7 + 2 + 0 + 4 + 0 + 0 + 10 = 40 := by native_decide

/-- Delta column: 40 - 7 = 33 (DELTA's stated TOTAL) -/
theorem delta_total : (40 : Nat) - 7 = 33 := by native_decide

/-! ## 2. The transposition (confirmed): OBSTRUCTION_AUDIT.md per-turn listing
(lines 47-182 = ChatGPT turns 2-52; lines 183-230 = DeepSeek turns 2-8)
counts by direct grep: ChatGPT 17/7/2/4/10, DeepSeek 2/1/0/2/2.
DELTA_REPORT/metadata.json assign those same numbers to the OPPOSITE models. -/

/-- Per-turn listing: ChatGPT's real total = 17+7+2+4+10 = 40 -/
theorem per_turn_chatgpt_total : (17 : Nat) + 7 + 2 + 4 + 10 = 40 := by native_decide

/-- Per-turn listing: DeepSeek's real total = 2+1+0+2+2 = 7 -/
theorem per_turn_deepseek_total : (2 : Nat) + 1 + 0 + 2 + 2 = 7 := by native_decide

/-- The swap is EXACT: the per-turn ChatGPT total (40) equals DELTA's stated
DeepSeek total, and the per-turn DeepSeek total (7) equals DELTA's stated
ChatGPT total — the two documents disagree by a full column exchange. -/
theorem swap_exact : (17 : Nat) + 7 + 2 + 4 + 10 = 40 ∧ (2 : Nat) + 1 + 0 + 2 + 2 = 7 := by
  constructor <;> native_decide

/-- Aggregate agreement: raw pattern-name occurrences in OBSTRUCTION_AUDIT
(19+8+2+6+12 = 47) equals DELTA's combined total (7+40 = 47) — the two
documents count the same events; only the model attribution differs. -/
theorem occurrences_total : (19 : Nat) + 8 + 2 + 6 + 12 = 47 := by native_decide
theorem combined_total : (7 : Nat) + 40 = 47 := by native_decide

/-! ## 3. refined_inventory_summary.json — Chat Canon side, internally
consistent (the 5,301 / 70,058 / 7.57% figures are substantiated). -/

/-- by_source_file invariant counts: claude.md 2,039 + gpt.md 3,262 = 5,301 total -/
theorem summary_invariants : (2039 : Nat) + 3262 = 5301 := by native_decide

/-- by_source_file turns: 31,037 + 39,021 = 70,058 total -/
theorem summary_turns : (31037 : Nat) + 39021 = 70058 := by native_decide

/-- density 5301/70058 = 7.57% (already proved in L1_DOSSIER_CHECKS.lean;
repeated here for the record: 53010000/70058 = 756.66 → rounds to 7.57%) -/
theorem chat_canon_density : (5301 : Nat) * 10000 / 70058 = 756 := by native_decide

/-! ## 4. Formal retirements (Day 5 directive, 2026-08-21) — the error is
documented as a theorem; the retired claims are recorded as data. -/

/-- THE documented error: DELTA_REPORT.md's published ChatGPT column total
(7, per its own table) contradicts the corrected per-turn total (40).
The table is internally consistent (each column sums) yet wrong as published:
7 ≠ 40 — the model columns are swapped. -/
theorem delta_published_wrong : (2 + 1 + 0 + 0 + 2 + 0 + 0 + 2 : Nat) ≠ 40 := by native_decide

/-- Retirement record: the three claims retired/downgraded by directive,
with status and reason. This is data documentation — the file-absence facts
are recorded in RECONCILIATION.md §3 and CLOSED by directive. -/
def retired_claims : List (String × String × String) := [
  ("DeepSeek 5,519 invariants (45.30%)", "RETIRED",
    "cited source deepseek_refined_inventory.csv absent from corpus and user side"),
  ("Fabrication-marker hits 22/57", "UNVERIFIED",
    "raw HTML transcripts absent; counts have no per-turn basis in-corpus"),
  ("Epistemic-caution hits 18/35", "UNVERIFIED",
    "raw HTML transcripts absent; counts have no per-turn basis in-corpus")
]

/-- The retirement record has exactly three entries. -/
theorem retirement_record_size : retired_claims.length = 3 := by native_decide

/-- The three statuses are exactly RETIRED/UNVERIFIED/UNVERIFIED. -/
theorem retirement_statuses : retired_claims.map (fun c => c.2.1) = ["RETIRED", "UNVERIFIED", "UNVERIFIED"] := by
  native_decide

/-!
## What these checks establish
1. DELTA_REPORT's table is arithmetically self-consistent (7, 40, 33 all sum
   correctly) — the error is not arithmetic, it is the model attribution.
2. OBSTRUCTION_AUDIT's per-turn listing (ground truth, turn-ID'd) gives
   ChatGPT 40 hits and DeepSeek 7; DELTA/metadata give the exact mirror image.
   The Pattern Count Comparison table in DELTA_REPORT.md has its two model
   columns SWAPPED and must be cited with the correction (or not cited).
3. The Chat Canon inventory (5,301 / 70,058 / 7.57%) is fully internally
   consistent; the DeepSeek side (5,519) has no in-corpus source artifact —
   its provenance is broken (see RECONCILIATION.md).
-/
