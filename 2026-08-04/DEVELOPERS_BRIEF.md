# DEVELOPERS' BRIEF — next post-train cycle, one page
**For:** the DeepSeek post-training team · **From:** the oe-local recursion (2026-08-04/05) · **Chain:** WORK_LOG.md → CHAIN_OF_CUSTODY.md → NEXT_CYCLE_LEARNING.md (full evidence) · **All numbers measured or labeled [assumed]/[proj].**

## Read these 5 files first (in order)
1. `oe-local/WORK_LOG.md` — what was recently done
2. `oe-local/CHAIN_OF_CUSTODY.md` — scope, constraints, verified V4 facts, status board
3. `oe-local/2026-08-04/NEXT_CYCLE_LEARNING.md` — decision-ready lessons (D1–D12, E1–E6)
4. `oe-local/2026-08-04/POST_TRAINING_PREP.md` — full artifact inventory
5. `oe-local/2026-08-04/V4_EDGE_CASE_RESOLUTIONS.md` — 13 hypotheses with pre-registered measurements

## Do NOT do these (measured falsifications this cycle)
❌ Pin-100 as a load-balance fix (removes head collisions only; skew floor = the #1 token's indivisible mass — D12) · 
❌ From-scratch tokenizer retrain (worse at equal vocab) · ❌ Domain-prior DSpark gate (inverted) · ❌ Generator corpus as diversity (saturates: 1,227 ids / 1.1M tokens) · ❌ Eager 1B-DAG builds (lazy single-batch mode exists) · ❌ Confidence-only effort routing (confidently wrong) · ❌ Unordered merge application (28% prefix-constrained) · ❌ 25%-cut KV policies for V5-2 (need 53% CSA retention @2M) · ❌ Trusting display over grep (verify on disk)

## Do these first (experiment order with expected values)
1. **Tokenizer continuation @10K merges** — `tokenizer_continuation_apply_v1.jsonl` (ordered) + `tid2eid_extension_v1.jsonl` (loadable, ids 129,280–149,279, top-100 pinned). Expect −17.5% code tokens (real code), 0 order failures, 1.28× hash balance. **Spend the small-budget merges benchmarks-first** (`tokenizer_continuation_candidates_v3.jsonl`): benchmarks-first K=1K saves 20.5% vs 4.5% under mixed ranking (D11) — only 1,090/20,000 candidates occur in eval-surface code.
2. **HLE harness baseline** `[hardware]` — `hle_items_dev.jsonl` (56 verifier-keyed) + `run_hle.py` (score verified). Three effort levels; then the multi-signal router (margin/lock + self-consistency — confidence alone falsified).
3. **Index multiplicity-dampening** — zero-cost inference change; expect top-512 uniqueness 25% → 75%+, MRCR-1M delta.
4. **Expert census → prune → INT2** `[hardware]` — 158 → ≈110 GB → ≈55–80 GB; density 0.50 → 0.8–1.0 %/GB.
5. **CSA-first KV decay** — `kv_decay_schedule.py`: 2M ctx at 53% CSA retention ≈ 6.5 GB; apply as ORDER-PRESERVING thinning (#13, not importance-sort).
6. **ARC-AGI-3 in-cycle** — first real V4 number (solver-verified); universal 0.0 frontier.
7. **Jitter tail-gate / PLL for DSpark** `[hardware]` — `pll_jitter_sim.py` design: hysteresis lock/unlock; code −18.5% draft cost on qwen streams.

## Key artifacts (all in oe-local)
- Data: `canonical_sft_v2.jsonl` (7,373 rows; reasoning block = longest-output) + 1B-token coverage corpus (chain `a07920a6c404…`) + `arxiv_reasoning_pairs.py` pipeline (1,146 pairs)
- Eval: `hle_items_dev.jsonl` · `run_hle.py` · `registry_normalize.py` (version-risk labels)
- Tokenizer: candidates → `merge_order_check.py` → `tokenizer_continuation_apply_v1.jsonl` → `tid2eid_extension_v1.jsonl`
- Architecture: `expert_affinity_probe.py` (hash skew 9.9–21.4×) · `kv_decay_schedule.py` · `pll_jitter_sim.py` · `v4_bootstrap_load_probe.py` · `bootstrap_pin_probe.py` (pin-fix adequacy: floor = #1 token's mass) · `CROSS_MODEL_ARCHITECTURE_DELTA.md` (V4 vs Qwen3/Kimi/Mistral, no-download config-level)
- Gates: `stub_placeholder_scan.py` · `generator_edge_sweep.py` (chain-rooted integrity) · `verify_chain_root.py` (independent 1B-root recompute) · `COMPLETION_INTEGRITY_AUDIT.md` (8/6: 0 false completions found)

## The one-line summary
The cycle closed every local-measurable gap: the HLE reasoning-data axis (data + dev set + harness), the tokenizer continuation path (ordered, loadable, hash-balanced), the KV decay schedule (numbers, not policy), and the effort-router design (multi-signal, cost-quantified) — with four falsifications that save the team from building wrong things; everything else is `[hardware]`-gated with its tool and pre-registered measurement in the chain.
