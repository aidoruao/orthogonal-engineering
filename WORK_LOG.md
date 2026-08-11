# WORK LOG — oe-local session timeline (the "commits history" — no git in this workspace)
**Purpose:** instant answer to "what was recently done?" — chronological, hash-anchored.
**Chain of custody:** every entry's origin derives from CHAIN_OF_CUSTODY.md §3 (CIIF original, corpus, session logs); scope/objectives are custody §1. Read order: this log → custody → prep kit.
**Git (as of 8/10):** this repo (oe-local) HAS git — origin main = github.com/aidoruao/orthogonal-engineering; commit + push after every work item; every commit message states what and why.

## 2026-08-10 (Open-Audit Campaign launch + git push)

- **Git milestone** — ALL accumulated work pushed to origin main (commit f5abf97e, 97 files): the full 2026-08-04..07 cycle (chain, learning D1–D13/E1–E7, prep, catalog, audits, probes, tools) + tss-project flattened from nested repo (its .git preserved at ~/.tss-project-git-backup). Zero divergence with origin; nothing remote-only existed to protect; no force-push, no deletions. **NOTE for the human: the GitHub token in .git/config is plaintext — rotate it (Settings → Developer settings → PAT).**
- **Open-Audit Campaign launched** — `OE_CAMPAIGN.md` (root): charter (public sources only, nothing illegal, evidence code [measured]/[published]/[hypothesis]/[pending], harsh = documented discrepancy), 5-layer asymmetry framework (L1 architecture → L5 corporate fiduciary), 11-target matrix, 8 work streams, continuity contract (repo answers "what was last done and why"), pre-registered queue (tensor censuses, arxiv ingestions, dossiers, registry rows).
- **AUDITS/ created** — 10 dossiers: openai/anthropic/moonshot ACTIVE (real fetched sources: GPT-5 system card from openai.com; Fable 5 profile from BenchLM; Kimi-K2 family via HF API — K2.5/K2.6/K2.7-Code public, tech report arxiv:2602.02276), xai/google/meta/mistral/alibaba/zhipu/regulators QUEUED (honest stubs with measured config/registry content).
- **TRANSPARENCY_LEDGER.md** — append-only source index (8 entries + pending list). KEY DISCREPANCY FOUND: OpenAI claims 3× on ARC-AGI-3 ("two settings", Jul 29 2026) vs our matrix's universal 0.0 — top re-baseline priority.

## 2026-08-07 (cross-model architecture comparison)

- **Cross-model architecture delta** — `CROSS_MODEL_ARCHITECTURE_DELTA.md` (new): no-download config-level comparison (same method as the V4 census, ~2 KB/model, commit-pinned) of Qwen3-235B-A22B, Kimi-K2-Instruct, Mistral-Large-2411 vs V4. Findings: V4's 6/256 active (2.34%) is the efficiency class with Kimi (2.08%); 1M ctx @ ≈6 GB KV has no competitor (Qwen3 40K, Kimi 131K YaRN×32, Mistral 131K); V4 alone has MTP×3+DSpark+hash-bootstrap; Kimi K2 = V3-lineage reference (MLA+noaux_tc) confirming V4's delta is attention/routing/speculation; Qwen3 norm_topk_prob+aux-loss 0.001 and Kimi sigmoid scoring = hardware-gated V5 experiment candidates; closed models (Fable 5, Astra, Gemini, Grok) not config-inspectable — papers/cards only. Learning: D13. Next: tensor census (Qwen3 index confirmed public), arxiv ingestion, Fable 5 registry row.

## 2026-08-06 (fresh instance — completion-integrity audit)

- **Completion-integrity audit** — `COMPLETION_INTEGRITY_AUDIT.md` (new): adversarial fresh-session re-verification of every recomputable chain claim — hashes (arxiv `e1226c53…` / hle `6eb5092c…` full-match), counts (7,373 / 20,000×4), manifest sum 3,725,220,653, **1B chain root independently recomputed from raw bytes = a07920a6c404… (full 64-hex match, `verify_chain_root.py` added)**; deterministic tools double-run byte-identical (merge_refine 9c474880…, affinity probe, effort_router; pin probe e3705076…); **FOUND + FIXED: `merge_order_check.py` nondeterminism (set iteration → sorted; now byte-identical 3d463510…)**; NOTED: D2 10-batch corpus partially evicted from /tmp (token claims re-derived on locgen7), 1B disk 7.59 GB incl. 33K .pyc compile artifacts. Verdict: **0 false completions**. D9 AIMD GPU re-run still running at close (sampling-labeled; stored values self-consistent). Gates below.

## 2026-08-05 (continuing session)

- **Bootstrap pin-fix adequacy + affinity telemetry** — `bootstrap_pin_probe.py` (new): pin-P (50/100/256) does NOT reduce base-table skew — generator 21.5× / real 9.9× / benchmarks 8.2× / mathlogic 10.6×; floor = #1 token's indivisible mass (8.4%/3.9%/3.2%/4.2%, constant across P); pin-100's real value = ~20 head collisions removed; heads are corpus-specific (Jaccard 0.09–0.33, foreign pin covers 15–44% of mass, transfer ≈ base). D2 anchor reproduced exactly (1,227 unique ids). Learning: D12; catalog #6 upgraded. Gate: chain_integrity_check ALL PASS + stub scan below.
- **Benchmarks-only merge refinement** — `merge_refine_benchmarks.py` (new): of the 20,000 continuation candidates, only 1,090 (5.5%) occur in benchmark-surface code (tags cross-check exact: 1,090/1,090, 0 drift); re-ranked benchmarks-first, K=1K saves 20.5% vs 4.5% mixed (4.6×), 99% of the 20.79% full-list ceiling; `tokenizer_continuation_candidates_v3.jsonl` (refined, same schema + `benchmarks_count`) + `merge_refine_benchmarks.json`. Learning: D11. Gate: chain_integrity_check ALL PASS + stub scan below.
- **Registry normalizer + catalog #13** — `registry_normalize.py` (E4 fix: version-risk-flagged cross-model matrix, 14 benchmarks × 11 models) · `V4_EDGE_CASE_RESOLUTIONS.md` → 13 hypotheses (#13 wave-order preservation, mem8-derived: decay = order-preserving thinning). Gate: 92 files / 6 benign.
- **Ordered apply-file + KV decay schedule** — `tokenizer_continuation_apply.py` → `tokenizer_continuation_apply_v1.jsonl` (20,000 rows topologically ordered, 22 multi-step flagged, 0 order failures) · `kv_decay_schedule.py` (2M→53% / 4M→25% CSA retention for 6.5 GB). Gate: 90 files / 6 benign.
- **Tool trio** (slash_agent handoff executed): `expert_affinity_probe.py` (extension-rule sim: hash self-balancing 1.28×, 100 max load) · `merge_order_check.py` (P1 22 multi-step, P2 20,000/20,000, P3 5,678 order constraints, P4 0) · `pll_jitter_sim.py` + `margin_stream_collector.py` (aerospace PLL gate: code 81.5% locked / −18.5% draft cost, reasoning 100% locked). Also: `locgen7_MANIFEST.json` → workspace; 17,190/20,000 + 13 three-axis re-verified. Gate: 86 files / 6 benign.
- **slash_agent round** — sub-agent launched (name slash_agent); completed read-order intake + read-only verification (13 three-axis, scan stats); execution blocked by child gating (no side effects — verified); §5 "71 files" → "72" corrected.

## 2026-08-05 (earlier)

- **HLE dev set + runner + quality probe** — `hle_item_synthesizer.py` → `hle_items_dev.jsonl` (56 verifier-keyed items, sha `6eb5092c…`, 0 failures; semantic fix: result-as-claim) · `run_hle.py` (score mode verified on mock 9/10) · `dataset_quality_probe.py` (v2: 62.8% template diversity, 0 empty outputs, 39.6% empty inputs).
- **1B-token scale run COMPLETED** — lazy single-batch DAGs (`--single-batch N`, byte-identical to full-DAG) · `seed_definition_30m.yaml` · `scale_run_300.py`: 300 batches / 33,000 files / 3.73 GB / 33.2 min / chain root `a07920a6c404…` (MANIFEST in `/tmp/locgen7/` + workspace copy).
- **Continuation candidates v2** — clean-real axes (hvac + standardgalactic; 91,060 pairs vs generator 64,591 — 41% richer); 17,190/20,000 clean-real supported; 13 three-axis.
- **Stub/placeholder audit** — `stub_placeholder_scan.py`: 1 real stub fixed (ai_invariant_tests.py), 5 benign; gate now runs after every work item.
- **NEXT_CYCLE_LEARNING.md** — decision-ready lessons (D1–D5, E1–E4, 7-item experiment order, 5 falsified paths); generator saturation found (10-batch ≡ batch 0 at token level: 1,227 ids).
- **Generator scale test** — 2 toolchain bugs fixed (max_depth str-vs-int; seed invariant off 10×); sweep 110/110 compile; lazy-DAG design note.

## 2026-08-04

- **Edge-case catalog** — `V4_EDGE_CASE_RESOLUTIONS.md` (11 hypotheses from admissibility/mem8/Ortyx; #6 hash-skew MEASURED 9.9×/21.4×, #12 jitter-gated speculation, #2 index ≈25% unique, #4 KV arithmetic).
- **Jitter-gate feasibility** — `jitter_gate_feasibility.py`: domain prior FALSIFIED/inverted on qwen-1.5b → tail-based gate design.
- **Cross-model matrix** — `extract_profiles.py` → `CROSS_MODEL_TARGET_MATRIX.md` (HLE biggest gap: Kimi 0.502 vs Flash 0.348; ARC-AGI-3 = 0.0 universal).
- **Reasoning-data pipeline** — `arxiv_reasoning_pairs.py` (1,146 deterministic pairs, sha `e1226c53…`) → `merge_arxiv_into_canonical.py` → `canonical_sft_v2.jsonl` (7,373 rows, 0 dupes; math 147 / logic 137 / science 83).
- **ARC solver verified** — `benchmarks/run_arc_benchmark.py`: symbolic solver, 10/10 demos, Merkle proofs.
- **Tokenizer continuation measured** — headroom −9.4% @1K / −17.5% @10K merges on real code; candidates files emitted.
- **Foundation** — CIIF verification (ρ_I = 0.50 %/GB), no-download census (72,317 tensors), BRR, V4_TO_V5 trajectory, `CHAIN_OF_CUSTODY.md` created.

## How to use
- "What was recently done?" → read this log top-down.
- "Where does the chain derive from?" → CHAIN_OF_CUSTODY.md §3 (CIIF original at `oe-local/2026-08-04/THE COMPRESSION-INTELLIGENCE INVERSION FORMULA.txt`, corpus `8b-public-documents/`, session logs).
- "Recently worked files" → `ls -lt /home/idor/oe-local/2026-08-04/ | head -20` (raw mtime view) + this log's file lists.
- Each entry's claims were verified at the time (sha256/grep); re-verify before relying on stale copies.
- **Learning update (8/5 evening)** — NEXT_CYCLE_LEARNING.md current: D6 (extension table self-balancing 1.28×), D7 (merge ordering: 22 multi-step / 5,678 prefix-constrained, apply-file ordered), D8 (real code 41% richer at pair level), E5 (confidence-only routing falsified — confidently wrong), E6 (HLE 40+ is a capability number, not routing; frontier 21.4 @ 5.5×); falsified list now 8 items.
- **Developers' brief (8/5 evening)** — DEVELOPERS_BRIEF.md: one-page decision sheet (5 files to read, 8 falsified paths, 7-item experiment order with expected values, artifact map) — the team's first stop.
- **Chain integrity audit (8/5 evening)** — chain_integrity_check.py: ALL 14 CLAIMS VERIFIED (exit 0) — rows, roots, existence across the whole chain; the closing gate over the gates.
- **Massive tests (8/5 evening)** — full-corpus sweep: 33,000/33,000 compile pass, 0 dupes, 3.725 GB, chain-root method unified (path-ordered canonical; 1B root a07920a6c404 independently re-verified) · AIMD training campaign: F4 CONFIRMED (+23.6% qpt vs fixed budget at equal best).
- **Session close (8/5)** — chain integrity re-verified (ALL CLAIMS PASS), stub gate 103 files / 6 benign; context ~70% — full handoff via WORK_LOG/custody/learning/prep/brief. Next session: read WORK_LOG step 0.
