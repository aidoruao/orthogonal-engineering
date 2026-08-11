# GENERATOR SCALE TEST — 1Qi-generator edge cases, fixes, and billion-token arithmetic
**Date:** 2026-08-05 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Machine:** RTX 4050 laptop, 6 GB VRAM, 7.6 GB RAM

## 1. Toolchain edge cases found & FIXED this session (all verified)

**BUG-1 — `max_depth` string TypeError (both generators).** `seed_definition_omega.yaml` sets `max_depth: "infinity"` (quoted); `fractal_expander.py:76` and `dag_generator.py:264` compared `int >= str` → `TypeError` on any recursion path. Fixed with a module-level `_coerce_max_depth()` in both files (`"infinity"/"inf"/"unbounded"/"∞"` → 10¹⁸; numeric strings → int; junk → loud ValueError). Verified: both files parse, class methods intact (`_can_spawn_sub_universe`, `compute_sub_dag_hashes`), coercion returns 10¹⁸ for `"infinity"`, and the previously-failing materialization now succeeds. **Lesson for the pipeline: YAML numbers must be typed; add a config-schema lint to the materializer.**
*(Note: an intermediate edit misplaced the helper inside the class, silently swallowing a method — caught by structure assert, not by parsing. Added the hasattr checks to the verify step.)*

**BUG-2 — seed product invariant mismatch.** `seed_definition.yaml` claims 1B lines but its level product was 100×10×100×10×100 = 10⁸ (off 10×); `dag_generator_omega.py`'s invariant check correctly rejected it (`ValueError`). The comment's arithmetic was also wrong. Fixed: `function: 10 → 100` → product 10⁹ ✓, and per-batch 10×100×100×100 = 10⁶ ×10 = 10M lines = `batch_size` ✓ consistent. The test seed (`seed_definition_test.yaml`) was already correct (10×10×10×100×10 = 10⁶) — the 1B seed now matches its geometry.

**DESIGN-NOTE — eager DAG build is the scaling ceiling.** Both DAG generators materialize the full node tree in memory: the 1M-LOC test DAG = 1,102,001 nodes → 672 MB JSON in 12s; a 1B-LOC DAG (10⁹ line nodes) is infeasible on this machine (RAM/time). The materialization path (`--batch N` → modules → files) is lazy per batch and fast — the intended scale path is: build the DAG once on a big box (or shard per batch), then materialize batches in parallel. The 1Qi design's "minimal storage: seed + generators + manifests (~500 MB)" is the right pattern; the eager DAG build should be made lazy/sharded as the next toolchain improvement.

## 2. Measured batch + edge sweep (1M-LOC test seed, batch 0)

- **Batch 0:** 110 files, 12,417,326 bytes (12.4 MB), 361,720 lines, materialized in **4.0 s** (≈3.1 MB/s).
- Line count 361K vs 100K nominal: templates add boilerplate (~3.6× header/blank lines per function) — the "LOC" accounting is template-inflated; **token count is the honest unit**, not LOC.
- **Sweep (classic tooling: cksum chain, sort|uniq dedup, py_compile gate, byte coverage):**
  - compile gate: **110/110 files valid Python** ✓
  - duplicate files (sha256): **0** ✓ · empty files: 0 ✓
  - max line 77 chars, mean 33.3 · byte-variety 62/256 (ASCII-code subset — expected for templates; flagged as an edge: generated corpora lack byte diversity by design)
  - integrity chain root (sha256 over sorted file hashes): `9f191ebfccc8b6971ce25e5aea496cb82b4af78d2caae200d9f2f1a352c30c65`
- **Determinism:** same seed + DAG → same content (batch hash printed per run); the chain root is the re-verification handle (re-run sweep → same root).

## 3. Token economics + billion-token arithmetic [proj — measured rates, projected totals]

- V4 tokenizer on the batch sample: **~685,600 tok/s** tokenize throughput on this laptop; generator code ≈ 3.75 chars/token.
- Materialization ≈ 3.1 MB/s ≈ ~830K tokens/s of *generated* text.
- **1B tokens ≈ 20–25 min wall, ≈ 3.75 GB disk on this laptop** · 10B tokens ≈ 4 h ≈ 37.5 GB · 100M tokens ≈ 2.5 min.
- 1B-LOC layer-0 universe: ≈ 124 GB materialized · 1Qi: minimal-storage design (~500 MB) with lazy materialization is the only sane path.
- **Implication for the post-train cycle:** billion-token-scale *generated-code* corpora are locally producible and verifiable (chain-rooted); the honest caveat from the probes stands — generator corpora are template-skewed (1,227 unique V4 token ids in 1.1M tokens), so they are the *negative/coverage* axis of training data, not a substitute for real code (the continuation candidates file already flags this).

## 3b. DESIGN-NOTE RESOLVED — lazy single-batch DAG mode (verified, in use)
- `dag_generator.py --single-batch N` (new) builds only the requested batch's subtree: 110,112 nodes vs 1,102,001 full — **1.0 s vs 12 s, ~67 MB vs 672 MB**.
- **Consistency verified:** lazy-DAG batch 0 materializes **byte-identical** to full-DAG batch 0 (same 110 files, same 12,417,326 bytes; diff clean except __pycache__ residue).
- `seed_definition_30m.yaml` (new): 300 batches × 100K lines = 30M LOC, same geometry as the test seed — the scale-run seed.
- **Scale run COMPLETED (`scale_run_300.py`):** 300 batches / 33,000 files / 3,725,220,653 bytes (3.73 GB) / 33.2 min / **≈1B tokens** (3.36M tokens/batch measured) — **chain root `a07920a6c404…`, MANIFEST.json in `/tmp/locgen7/`**. The eager-DAG ceiling (§1 DESIGN-NOTE) is a solved problem: any batch count is reachable on this laptop, resumable via DONE markers.

## 4. Artifacts
- Fixes: `generators/fractal_expander.py`, `generators/dag_generator.py` (`_coerce_max_depth`, `--single-batch`), `generators/seed_definition.yaml` (function 100), `generators/seed_definition_30m.yaml` (new).
- `generator_edge_sweep.py` + `generator_edge_sweep.json` (re-runnable on any batch dir).
- `scale_run_300.py` + run log `/tmp/locgen7_run.log`; corpus `/tmp/locgen7/` (MANIFEST.json with chain root on completion).
- Test corpus: `/tmp/locgen4/batch_0` (12.4 MB, chain root above); DAG `/tmp/locgen4_dag.json` (672 MB — delete after use).
