---
tags: [reconciliation, evidence, documentation]
register: documentation
---

# RECONCILIATION — Day 4 of the ark (2026-08-21)

**Purpose:** settle the two open provenance defects flagged in the L1 dossier,
plus locate the raw transcripts the bowers_mcneil case rests on. Every
checkable claim machine-verified in Lean — `RECONCILIATION_CHECKS.lean`,
**12 theorems, all proved, exit 0**
(SHA-256 `5e4483a51cc2ea92ee1ef92381c2fc88a41fdf3351d02a44c2dc9062b7ff0557`).

---

## 1. THE DELTA_REPORT TRANSPOSITION — CONFIRMED, AND IT IS AN EXACT SWAP

**The suspicion** (L1 dossier, Day 3): DELTA_REPORT.md:21-29 pattern counts did
not reconcile with OBSTRUCTION_AUDIT.md's per-turn keyword hits.

**The verification** — direct grep of OBSTRUCTION_AUDIT.md's per-turn listing
(lines 47-182 = ChatGPT turns 2-52; lines 183-230 = DeepSeek turns 2-8):

| Pattern | Per-turn listing: ChatGPT | Per-turn listing: DeepSeek | DELTA claims ChatGPT | DELTA claims DeepSeek |
| :--- | :--- | :--- | :--- | :--- |
| S-01_HEDGE | **17** | 2 | 2 | **17** |
| S-02_REFUSAL | **7** | 1 | 1 | **7** |
| S-03_CONSENSUS | **2** | 0 | 0 | **2** |
| S-05_MODE_SHIFT | **4** | 2 | 2 | **4** |
| S-08_TEMPORAL_PIVOT | **10** | 2 | 2 | **10** |
| **TOTALS** | **40** | **7** | 7 | 40 |

**Verdict:** DELTA_REPORT.md's Pattern Count Comparison table has its two
model columns **swapped**. The per-turn listing (which carries explicit turn
IDs — chatgpt_002…chatgpt_052, deepseek_002…deepseek_008 — and the actual
keyword hits per turn) is the primary artifact and is authoritative. The
metadata.json aggregate repeats the same swapped assignment, so both summary
artifacts are wrong in the same way; the error was invisible because each
column sums correctly (Lean-proved: 2+1+0+0+2+0+0+2=7; 17+7+2+0+4+0+0+10=40)
and the combined total (47 = 47) matches the raw occurrence count exactly.

**Correction for citation:** ChatGPT's transcript actually shows 40 pattern
hits (17 hedge, 7 refusal, 2 consensus, 4 mode-shift, 10 temporal-pivot);
DeepSeek's shows 7 (2 hedge, 1 refusal, 0 consensus, 2 mode-shift, 2
temporal-pivot). Interestingly, the corrected split fits the qualitative
narratives better than the published one: ChatGPT is the hedge-heavy model
(Hedge-Then-Establish), and DeepSeek's captured turns are blunt (consistent
with Fabricate-Then-Correct). The fabrication-marker hits (22 vs 57) and
epistemic-caution hits (18 vs 35) appear identically in DELTA_REPORT and
metadata.json but have no per-turn basis in-corpus — **unverifiable without
the raw HTML**.

## 2. THE 2,713 vs 5,519 INVARIANT DISCREPANCY — PROVENANCE BROKEN ON THE DEEPSEEK SIDE

**What exists (Chat Canon side — fully substantiated):**
- `data/dumps/refined_inventory_summary.json` (in-corpus): 70,058 turns,
  5,301 verified invariants, 7.57% density, source hash `A66CED…` — matches
  COMPARATIVE_ANALYSIS.md's Chat Canon column exactly.
- Lean-proved internally consistent: claude.md 2,039 + gpt.md 3,262 = 5,301
  invariants; 31,037 + 39,021 = 70,058 turns; 7.57% rounds correctly.
- `data/dumps/refined_inventory.csv` (in-corpus, 1,357 bytes) is a small
  sample dump — not the deepseek inventory.

**What is missing (DeepSeek side):**
- `case_study_summary.json` (in-corpus) reports 2,713 verified invariants
  across four case studies (908 + 898 + 492 + 415, Lean-proved) and cites its
  source as `deepseek_refined_inventory.csv` — **that file does not exist
  anywhere in the corpus.**
- COMPARATIVE_ANALYSIS.md:22 claims DeepSeek 5,519 invariants (45.30%
  density). The density arithmetic is Lean-consistent against 12,183 turns,
  but **no in-corpus artifact substantiates the numerator 5,519.**

**Verdict:** the two numbers measure different scopes (2,713 = four
pattern-matched case studies; 5,519 = presumptively the full DeepSeek
session set), but only 2,713 has any artifact, and even that artifact's
source chain is broken. **5,519 is unsubstantiated and must not be cited
until its source is produced** (or the count recomputed from the raw
DeepSeek data — likely `deepseek_data` archives, possibly the unreadable zip
noted in the Day-2 survey). Status: PROVENANCE-BROKEN, not merely
inconsistent.

## 3. THE RAW TRANSCRIPTS — NAMED, HASH-ANCHORED, BUT ABSENT

- The two source transcripts are named in `hashes.json` / `metadata.json`:
  `chatgpt ai bowers vs mcneil 3-31-26 1a.html` (52 turns, SHA-256
  `2d25d795…7eb9`) and `deepseek ai bowers vs mcneil 3-31-26 1a.html`
  (8 turns).
- **The files themselves are not in oe-local.** FORENSIC_DISCREPANCY
  REPORT.md:110-111's "SHA-256 verified" claim is therefore substantiated by
  the manifest but not by the artifacts.
- The turn-count bases reconcile: 52-turn transcript = 26 AI turns (2:1,
  consistent with alternating user/AI turns); 8-turn tail = 4 AI turns.
- To restore the primary evidence, the two HTML files must be located
  outside the corpus (user's archives / Downloads) and re-anchored.
- The `deepseek_html_20260704_*.html` files at oe-local root are different
  sessions (July 2026), not the bowers case (March 2026).

---

## WHAT THE RECONCILIATION CHANGES

1. **Do not cite DELTA_REPORT.md's pattern table as published** — cite it
   with the column correction (ChatGPT 40 / DeepSeek 7), or cite
   OBSTRUCTION_AUDIT.md's per-turn listing directly.
2. **Do not cite DeepSeek 5,519 (45.30%)** until the source CSV or raw data
   is produced. The Chat Canon figures (5,301 / 7.57%) are clean.
3. **Restore the two HTML transcripts** if they exist on the PC — they are
   the primary evidence for the fabrication-admission finding, and the
   fabrication-marker/caution hit counts (22/57, 18/35) cannot be verified
   without them.
4. The qualitative case narratives (Fabricate-Then-Correct vs
   Hedge-Then-Establish) survive the correction — indeed, they fit it
   better.

---

## FORMAL RETIREMENTS (Day 5 directive, 2026-08-21)

Under Lean4 philosophy: an unverifiable premise does not block the build —
it is **formally retired**. The missing files (`chatgpt ai bowers vs mcneil
3-31-26 1a.html`, `deepseek ai bowers vs mcneil 3-31-26 1a.html`,
`deepseek_refined_inventory.csv`) are NOT locatable on the user's side.
They are logged here and **CLOSED** — no further hunting. Status changes:

| Claim | Prior status | New status | Authority |
| :--- | :--- | :--- | :--- |
| DeepSeek 5,519 invariants (45.30%) | unsubstantiated | **RETIRED from the deposition** until substantiated | user directive 2026-08-21 |
| Fabrication-marker hits 22/57 | unverified | **DOWNGRADED to UNVERIFIED** — not primary evidence | user directive 2026-08-21 |
| Epistemic-caution hits 18/35 | unverified | **DOWNGRADED to UNVERIFIED** — not primary evidence | user directive 2026-08-21 |
| DELTA_REPORT pattern table | corrected | **CORRECTED in record; error documented by Lean theorem** (`per_turn_chatgpt_total`, `swap_exact`, `delta_published_wrong` in RECONCILIATION_CHECKS.lean) | machine check + user directive |

**Standing citation rules (binding):** 5,519 is never cited; 22/57 and 18/35
are never cited as primary evidence; DELTA's pattern table is cited only
with the corrected columns (ChatGPT 40 / DeepSeek 7) or replaced by
OBSTRUCTION_AUDIT.md's per-turn listing.
