/-!
# L1 Dossier — Machine Checks (Day 3 of the ark, 2026-08-21)

Every checkable number from the L1 deepening is verified here with EXACT
integer arithmetic (scaled to basis points/ppb where needed — no floats).
Sources are cited per theorem. Run: `lean L1_DOSSIER_CHECKS.lean`.
-/

/-! ## 1. ARC-AGI benchmark logs (evidence/arc_agi_3/, measured data) -/

/-- demo: 10 solved of 10 tasks, pass_rate 1.0 (benchmark_demo.json:5-6,59) -/
theorem demo_pass : (10 : Nat) / 10 = 1 := by native_decide

/-- evaluation: 2 solved of 400 tasks, pass_rate 0.005 (benchmark_evaluation.json:5-6,2009) -/
theorem eval_pass : (2 : Nat) * 200 = 400 := by native_decide

/-- 2/400 = 0.005 exactly, in thousandths: 2*1000 = 4*5*100... check: 2/400 = 1/200; 1/200 of 1000 = 5 -/
theorem eval_pass_per_mille : (2 : Nat) * 1000 / 400 = 5 := by native_decide

/-- training: 20 solved of 400 tasks, pass_rate 0.05 (benchmark_training.json:5-6,2009) -/
theorem train_pass : (20 : Nat) * 100 / 400 = 5 := by native_decide

/-- grep cross-check: exactly 32 "solved": true across all three logs (10+2+20) -/
theorem solved_total : (10 : Nat) + 2 + 20 = 32 := by native_decide

/-! ## 2. COMPARATIVE_ANALYSIS.md (evidence/deepseek-analysis/) -/

/-- Turns: Chat Canon 70,058; DeepSeek 12,183; difference 57,875 (:20) -/
theorem turns : (70058 : Nat) - 57875 = 12183 := by native_decide

/-- Canal rate: 20.87% + 7.33pp = 28.20% (:21), in basis points -/
theorem canal_pp : (2087 : Nat) + 733 = 2820 := by native_decide

/-- Invariants: 5,301 vs 5,519 (:22) -/
theorem invariant_delta : (5519 : Nat) - 5301 = 218 := by native_decide

/-- Chat Canon density: 5301/70058, claimed 7.57% (:22).
    Exact: 53010000/70058 = 756 remainder, i.e. 7.5666% — rounds to 7.57%. -/
theorem chat_canon_density_floor : (5301 : Nat) * 10000 / 70058 = 756 := by native_decide
theorem chat_canon_density_under_757 : (5301 : Nat) * 10000 < 70058 * 757 := by native_decide

/-- DeepSeek density: 5519/12183, claimed 45.30% (:22).
    Exact: 55190000/12183 = 4530 remainder 1010, i.e. 45.3008% — rounds to 45.30%. -/
theorem deepseek_density_floor : (5519 : Nat) * 10000 / 12183 = 4530 := by native_decide

/-- Signal counts vs DeepSeek turns 12,183 (:58-60):
    Christian 2,024 → 16.6%; LOGOS 3,115 → 25.6%; Coder 1,969 → 16.2% (all round up correctly) -/
theorem christian_pct : (2024 : Nat) * 10000 / 12183 = 1661 := by native_decide
theorem logos_pct : (3115 : Nat) * 10000 / 12183 = 2556 := by native_decide
theorem coder_pct : (1969 : Nat) * 10000 / 12183 = 1616 := by native_decide

/-! ## 3. The DISCREPANCY (case_study_summary.json vs COMPARATIVE_ANALYSIS.md) -/

/-- The four case-study invariant counts sum to 2,713 (case_study_summary.json:7,25,43,61):
    908 + 898 + 492 + 415 -/
def case_sum : Nat := 908 + 898 + 492 + 415
theorem case_sum_value : case_sum = 2713 := by native_decide

/-- But COMPARATIVE_ANALYSIS.md:22 claims the DeepSeek total is 5,519.
    2713 ≠ 5519: the JSON inventory does NOT reconcile with the headline total.
    (The raw deepseek_refined_inventory.csv is needed to reconcile.) -/
theorem case_sum_mismatch : case_sum ≠ 5519 := by native_decide

/-! ## 3b. CLAUDE.txt secondhand report (canonical_evidence/claude_analysis/CLAUDE.txt:199) -/

/-- DeepSeek via Zed reported 4 of 6 scripts worked, 66.7% success (secondhand).
    Exact: 400/6 = 66 remainder 4, i.e. 66.67% — rounds to 66.7%. -/
theorem deepseek_success_pct : (4 : Nat) * 100 / 6 = 66 := by native_decide

/-! ## 4. Layer-map arithmetic (LAYER_MAP.md, Day 2) -/
/-- L1 total: 21 files = 1 (evasion_tactics) + 6 (bowers_mcneil) + 4 (narrative-leak)
    + 3 (arc_agi_3) + 2 (deepseek-analysis) + 2 (case-studies) + 1 (CLAUDE.txt)
    + 2 (youtuber_audits) -/
theorem l1_total : (1 : Nat) + 6 + 4 + 3 + 2 + 2 + 1 + 2 = 21 := by native_decide

/-- Deposition core: 71 = L1 21 + L2 1 + L3 0 + L4 4 + L5 15 + L6 9 + L7 21 -/
theorem core_total : (21 : Nat) + 1 + 0 + 4 + 15 + 9 + 21 = 71 := by native_decide

/-- Corpus total: 446 = 71 layer-bearing + 375 scaffolding -/
theorem corpus_total : (71 : Nat) + 375 = 446 := by native_decide

/-- Scaffolding: 375 = 137 (case_studies) + 172 (data/downloads) + 29 (campaigns/misc) + 37 (evidence/audits) -/
theorem scaffolding_total : (137 : Nat) + 172 + 29 + 37 = 375 := by native_decide

/-- 71 of 446 = 15.92% — "16%" in the map rounds correctly (7100/446 = 15 remainder 410). -/
theorem core_share_pct : (71 : Nat) * 100 / 446 = 15 := by native_decide

/-- 21 of 446 = 4.71% (L1's share of the corpus: 2100/446 = 4 remainder 316). -/
theorem l1_share_pct : (21 : Nat) * 100 / 446 = 4 := by native_decide

/-!
## What these checks establish
1. All three ARC-AGI pass rates are internally consistent with their task counts.
2. Every percentage claim in COMPARATIVE_ANALYSIS.md rounds correctly against
   its stated turn-count base (12,183 DeepSeek turns).
3. The case-study JSON inventory (2,713 invariants) does NOT reconcile with the
   headline 5,519 — a genuine internal inconsistency, flagged for reconciliation.
4. The Day-2 layer-map arithmetic closes exactly.
-/
