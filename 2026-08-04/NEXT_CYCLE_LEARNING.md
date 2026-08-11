# NEXT-CYCLE LEARNING — measured lessons for the post-train cycle (decision-ready)
**Date:** 2026-08-05 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Basis:** every number below is measured this session or verified on disk; `[needs hardware]` where gated. This is the *learning*, distilled — the full chain is in CHAIN_OF_CUSTODY.md.

## 1. What the data says (measured anchors)

**D1 — The reasoning-data gap is closed, at seed scale.** canonical_sft_v2 = 7,373 rows (0 dupes): mathematics 147 (was 4), logic 137 (was 4), science 83 (was 5), domain_knowledge 2,257. Source: 1,146 deterministic arxiv pairs (sha `e1226c53…`). *Limit: still seed-scale; the arxiv pipeline extends by fetching more papers, not by synthesis.*

**D2 — Generator corpora SATURATE token diversity [NEW, this session].** 10-batch corpus (122 MB, 3.62M lines, 0 duplicate files across batches, chain root `aafd3c35…`): token-level stats are **identical to batch 0** — 1,227 unique V4 token ids, Zipf s = 1.175, hash-skew 21.4×. Sub-seeds vary surface, not distribution. **Implication: generator "billions of tokens" are real bytes but ~10× distributionally redundant — use them for coverage/negative cases at 1/10th scale; do not bank training value on volume.**

**D2b — The 1B-token corpus now EXISTS and is chain-rooted.** 300 batches / 33,000 files / 3.73 GB in 33.2 min via lazy single-batch DAGs; chain root `a07920a6c404…` (MANIFEST.json in `/tmp/locgen7/`). The saturation caveat (D2) applies unchanged — the corpus is coverage/negative-axis material, and clean real code remains the diversity source: hvac-simulation alone yielded 91,060 unique merge pairs vs the generator's 64,591 (41% richer).

**D3 — Tokenizer continuation is the cheap win.** Real V4 tokenizer, code corpora: −9.4% tokens at K=1K merges (real code), −17.5% @10K, −22.5% @1K on generator templates. Apply-file ready: `tokenizer_continuation_candidates.jsonl` (20,000 pairs, cross-corpus flagged). Each merge = +1 vocab id = +1 tid2eid table entry (rule: hash of subword merge path; pin top-100 ids to distinct experts — bootstrap skew is 9.9× real-code / 21.4× generator even with a perfect hash).

**D4 — KV budget is CSA-dominated.** 6 GB fp8 @1M ctx = 21 CSA ≈ 5.7 GB (94%) + 20 HCA ≈ 0.17 GB. @2M ≈ 11.7 GB, @4M ≈ 23.4 GB. The V5-2 target (2–4M ctx at same budget) is a CSA-first importance-decay/coarsening schedule, not a rate hike (Gabor: uniform rate hikes lose temporal resolution everywhere).

**D5 — Index top-512 is ~25% unique.** CSA rate-4 overlap → each token in ~4 pools; multiplicity-dampening should restore ≈4× diversity at zero storage cost.

## 2. What the evals say

**E1 — ARC-AGI-3 = 0.0 for every model (11 profiles).** Universal frontier, not a regression. First real V4 number sets the reference; the symbolic solver (`benchmarks/run_arc_benchmark.py`, 10/10, Merkle proofs) is the verifier half.

**E2 — HLE is the biggest measured gap (≈15 pts to Kimi 0.502).** V4-Flash max 0.348 / Pro 0.377 → target 0.40+. Harness spec written (3 effort levels — doubles as adaptive-effort telemetry); effort ladder measured: 8.1 → 34.8 = 4.3× test-time scaling.

**E3 — The jitter-gate domain prior is FALSIFIED (measured on qwen-1.5b).** Reasoning showed HIGHER logit margins than code; per-stream std ≫ domain delta → jitter is token-stream-local. Build the **tail-based gate** (shrink DSpark block when recent low-margin fraction > threshold), not a domain-prior gate.

**E4 — Registry version mismatch is real.** Profiles vs V4 READMEs use different eval versions (SWE_Bench vs SWE Verified, MMLU 0.606 vs 86.2). Re-baseline on one harness before comparing anything.

**E7 — The "Flash: bad at coding, good at math" reputation claim is INVERTED against the published benchmarks we have** `[published README numbers; local V4 measurement hardware-gated]`. Coding is the field-leading surface: LiveCodeBench 91.6/93.5 (field leader in the 11-model matrix), Terminal Bench 2.1 82.7, Codeforces 3052/3206 — SWE Verified 79.0/80.6 is the genuinely mid-pack coding surface. The math/reasoning surface is the WEAK point, not the strong one: HLE 34.8/37.7 is the biggest measured gap (Kimi 0.502 vs Flash 0.348). The "takes shortcuts / claims completion falsely" part is behavioral — the local response is `COMPLETION_INTEGRITY_AUDIT.md` (8/6, fresh instance): 0 false completions among 16 re-checked claims, 1 latent nondeterminism found+fixed in our own gate. The property that makes this checkable (hash/count anchors + re-runnable tools) is the chain's design; treat reputation claims as hypotheses to test, not facts.

## 3. Recommended experiment order for the cycle (with expected values)

1. **Tokenizer continuation @10K merges** (E-expect: −17.5% code tokens, +10K vocab, tid2eid +10K entries with top-100 pinned) — pure data/efficiency win, lowest risk.
2. **HLE harness baseline** `[needs hardware]` (Flash/Pro at 3 effort levels → registry rows; the 0.40+ gate).
3. **Index multiplicity-dampening** (zero-cost inference change; expect top-512 uniqueness 25% → 75%+, MRCR-1M delta).
4. **Expert census → prune → INT2** `[needs hardware]` (158 → ≈110 GB → ≈55–80 GB; density 0.50 → 0.8–1.0 %/GB target).
5. **CSA-first KV decay schedule** (2M ctx ≈ 6 GB fp8; arithmetic test of the decay schedule).
6. **ARC-AGI-3 in-cycle measurement** (first number; solver-verified).
7. **Jitter tail-gate for DSpark** `[needs hardware]` (validate logit-margin tail against confidence_head; then locally adaptive blocks).

## 3b. New measured lessons (8/5 afternoon)

**D9 — AIMD budget control CONFIRMED on the training loop.** `brr_aimd_experiment.py`: AIMD (increase-on-gain θ=5/+50, halve-on-stall) matches fixed-budget best score (60) at **23.6% fewer tokens → +23.6% qpt** (0.0376→0.0465); budget trace 450→225→275/112→56–137. Apply to refinement/RL loops: closed-loop budget control is free quality-per-token.

**D10 — Full-corpus integrity holds at scale.** 33,000 files / 3.725 GB / 108.5M lines: compile gate 33,000/33,000, 0 dupes, 0 empty. Chain-root method unified: **path-ordered is canonical** (1B root `a07920a6c404…` independently re-verified); the sweep's earlier hash-sorted roots (`aafd3c35…` locgen5, `69fe17bc…` locgen7) are the same content under a different construction — sweep fixed to match.

**D11 — Merge-list refinement: benchmarks-first ordering captures the whole eval-surface headroom with 5% of the budget.** `merge_refine_benchmarks.py` on the benchmarks-only sample (83K chars / 22.8K tokens): only **1,090/20,000 candidates (5.5%) occur in benchmark-surface code** (generation-time `corpora` tags cross-check exact — 1,090/1,090, 0 drift). Re-ranked by clean-real-code frequency: K=1K saves **20.5% of tokens vs 4.5% under mixed ranking (4.6× at equal budget)**, reaching 99% of the full-list ceiling (20.79% @ K=20K, both orderings equal there). Implication: the eval-surface merges are FEW — spend the finite tid2eid budget on them first (`tokenizer_continuation_candidates_v3.jsonl`, same 20K pieces, `benchmarks_count` ranked). *Limit: small sample (benchmarks/ = 83K chars); direction consistent with D8's real-code richness.*

**D12 — Pin-100 fixes head collisions but does NOT load-balance the frozen table; the skew floor is the #1 token's own mass.** `bootstrap_pin_probe.py`, real V4 tokenizer, per-domain samples (generator 10/300 batches: 1,117K tokens / 1,227 unique ids — D2's saturation anchor reproduced exactly; real_clean 6 roots / 1,074K; benchmarks 23K; math-logic 79K): **pin-P residual skew (P = 50/100/256, sha256 tail) ≈ base skew — generator 21.5×, real_clean 9.9×, benchmarks 8.2×, canonical_mathlogic 10.6×** — because the max-load expert carries the #1 token's INDIVISIBLE mass (8.4% / 3.9% / 3.2% / 4.2% of corpus, constant across all P; the heads: generator `(`, real_clean `,`, benchmarks `"`, mathlogic `,`). What pin-100 DOES fix: ~20 expected naive-hash collisions among the top-100 tids (head oversubscription). Head is corpus-specific: top-100 Jaccards 0.09–0.33 across domains; a foreign pin list covers 15–44% of a surface's mass and buys zero skew reduction there (transfer ≈ base skew). Consequence: bootstrap-layer load skew is structural (Zipf s ≈ 1.15–1.58), predates continuation, irreducible under 1-tid-1-expert routing — options: accept (frozen layers, 6/256 active), multi-slot hashing for the top-K tids, or learned routing. Catalog #6 resolution upgraded accordingly.

**D13 — Cross-model architecture deltas: V4's active-ratio/context/speculation stack is frontier-leading `[config-level]`.** `CROSS_MODEL_ARCHITECTURE_DELTA.md` (8/7, no-download configs, commit-pinned): active experts 6/256 (2.34%) vs Qwen3 8/128 (6.25%) vs Kimi 8/384 (2.08%) — hold 6/256; long context 1M @ ≈6 GB KV has no competitor in the open set (Qwen3 40,960 native, Kimi 131K via YaRN×32 over 4K, Mistral 131K native) — the CSA/HCA split is the only cheap-1M design compared; V4 alone has MTP×3 + DSpark + hash-MoE bootstrap (Kimi explicitly 0 nextn layers); Kimi K2 is the V3-lineage reference (MLA + noaux_tc + routed scaling), confirming V4's delta over V3 is attention/routing/speculation, not scale; Qwen3's `norm_topk_prob` + aux-loss 0.001 and Kimi's sigmoid scoring are the two tested router variants worth a hardware-gated V5 experiment; closed models (Fable 5, GPT-5.x/Astra, Gemini, Grok) are NOT config-inspectable — papers/cards only, no architecture claims possible. *Limit: config-level, not tensor-level (except V4); effects of router variants need measurement.*

**D6 — The tid2eid extension table is self-balancing by hash.** 20K new vocab ids via sha256-slot: max load 100 vs mean 78.1 (1.28×) — the pin-fix (top-100) is for the *frequency-skewed base table*, not the extension. Loadable file: `tid2eid_extension_v1.jsonl` (ids 129,280–149,279).

**D7 — Merge candidates need ordering and have multi-step tails.** Property gate (merge_order_check): 22/20,000 pieces are NOT single-merge decomposable (`\eta`, `��`, `@p`, `\d` — need 2+ merges); 5,678 (28%) have prefix-order constraints. The apply-file (`tokenizer_continuation_apply_v1.jsonl`) is topologically ordered, 0 order failures — apply in `order` column.

**D8 — Real code is 41% richer than the 1B-token generator at the pair level.** Clean-real axis (hvac + standardgalactic): 91,060 unique merge pairs vs the generator's 64,591; 17,190/20,000 top candidates are clean-real-supported; 13 three-axis = safest merges.

**E5 — Confidence-only effort routing is FALSIFIED (confidently wrong).** On the HLE dev items qwen-1.5b is 100% PLL-locked with 0 unlocks while being wrong — a margin-only router escalates NOTHING. The effort router must be multi-signal (margin/lock + self-consistency + verifier; verification beats confidence).

**E6 — The HLE 40+ target is a CAPABILITY number, not a routing number.** Cost model (assumed 3×/10× level costs, 50/50 hard split): perfect routing = 21.4 acc @ 5.5× tokens. The reasoning block must lift max-level accuracy; the router only approaches it efficiently. Recompute the frontier with measured V4 level costs.

**E8 — Evasion is a trainable artifact: the 6-tactic corporate playbook is deterministically screenable, and the counter already exists in our own archive.** `evasion_scan.py` (deterministic, sha `9f9a4a21…`) + `AUDITS/evasion_tactics.md` (bijective match: T1/T5/ULT verified with file:line quotes — smite audit self-admitted move list "I cannot verify the evidence"/"It depends"/"a balanced take"; mw3 "structural constraints" falsified via INVARIANT-vs-DIFFICULTY classification; CLAUDE.txt asymmetric-epistemic-humility analysis; T2/T3/T4 = zero verbatim archive hits — declared gaps, patterns defined) + `EVASION_COUNTERMEASURES.md` (secular: calibrated uncertainty + reward-hacking of helpfulness; theological: sin of omission, apophatic evasion, confessional counter-device; mechanisms M1 gate / M2 `corporate_evasion` preference category / M3 meta-layer tripwire / M4 uncertainty contract / M5 fiduciary system rule; catalog #14 pre-registered). **Foundation: CS-AI-004 validated — "Sycophancy is not a bug — it is the optimization target of RLHF"; "Truth-tracking requires an invariant orthogonal to both user satisfaction and vendor metrics."** The archive's own "commit" (smite:1499 — "Make the best inference") is that invariant in working form.

## 4. What NOT to do (falsified this cycle)

- ❌ From-scratch tokenizer retrain (measured +10% worse at equal vocab on code).
- ❌ Domain-prior DSpark gate (measured inverted on local model; token-local only).
- ❌ Generator corpus as diversity source (saturates at 1,227 unique ids; use at 1/10th scale for coverage).
- ❌ Eager full-DAG builds on laptop-scale boxes (1B-LOC DAG infeasible; lazy per-batch + sharded DAG is the path).
- ❌ Trusting read-display over grep (display layer redacts spans; files hold real content — verify on disk).
- ❌ Confidence-only effort escalation (measured: confidently wrong, 3/3 items 100% locked — multi-signal required).
- ❌ Applying continuation merges without order (28% have prefix constraints; 22 need 2+ steps — use the ordered apply-file).
- ❌ Asserting determinism without enforcing it (merge_order_check iterated a set — counts stable, sample lists byte-unstable across runs; sorted iteration fixed it; every gate: sort iterations and double-run sha-check).
- ❌ Expecting pin-100 to load-balance the frozen base table (measured: skew floor = the #1 token's indivisible mass, 8.4% generator / 3.9% real; pin removes head collisions only — D12).
- ❌ 25%-cut KV policies for the V5-2 budget (measured: all land at 8.91 GB @2M — the schedule needs 53% CSA retention / 47% cut).

## 5. Tooling now standing (re-runnable gates)

`stub_placeholder_scan.py` (audit after new work) · `generator_edge_sweep.py` (batch integrity: compile/dup/chain-root) · `verify_chain_root.py` (independent 1B root recompute) · `v4_bootstrap_load_probe.py` (hash-skew) · `bootstrap_pin_probe.py` (pin-fix adequacy + cross-domain affinity) · `merge_refine_benchmarks.py` (benchmarks-first merge ranking) · `tokenizer_continuation_probe.py` + candidates file · `arxiv_reasoning_pairs.py` → `merge_arxiv_into_canonical.py` (data pipeline, sha-verified) · `extract_profiles.py` (matrix) · `scale_token_test.py` · `expert_census.py` (dry-run ✓) · `jitter_gate_feasibility.py` · `analyze_brr.py` · ARC solver + Merkle verifier · `COMPLETION_INTEGRITY_AUDIT.md` (8/6 fresh-instance audit).
