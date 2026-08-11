# V4 → V5: Global Trajectory — non-fiction, grounded in measured facts
**Date:** 2026-08-04 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Basis:** HF API storage stats for Flash-0731 (sha `7872f01b`) and Pro (`b5968e91`), the technical report (arxiv 2606.19348), official READMEs (Flash-0731 and Pro), the 72,317-tensor map, and this session's measurements (token economics, generator at scale, local inference). Projections are labeled `[proj]`; everything else is measured or officially stated.

---

## 0. The trajectory already visible inside V4 (measured)

Between the preview (paper, 2026-04) and Flash-0731 (2026-07-31), DeepSeek moved the efficiency spearhead:

- **Flash: 284B (13B activated) → 304B (6/256 experts, ≈16.8B activated)** — +7% params.
- **Terminal Bench 61.8 (2.0) → 82.7 (2.1)** — a +20.9-point agentic jump, official claim: *"outperforms V4-Pro (Preview) despite far smaller activated parameter count."*
- Storage: 158 GB weights / 166.9 GB repo. Density ρ_I = 82.7/167 ≈ **0.50 %/GB**.
- **Pro: 1.6T params (49B activated), 864.8 GB storage** (HF API: 1.573T I8 fp4 experts + 23.2B F8 + 2.8B BF16; 64 shards). Density ≈ 0.098 %/GB at Pro-Max-class scores [proj, score assumption].

**The CIIF inversion holds *inside* the family:** Flash is ~5× denser than Pro. The strategy is two products on one architecture — capability (Pro) vs density (Flash) — and the 0731 release closed most of the capability gap at 1/5 the storage.

## 1. The family map (official benchmark deltas, same architecture)

Pro Max vs Flash Max (preview README): LiveCodeBench 93.5 vs 91.6 · Codeforces 3206 vs 3052 · HLE 37.7 vs 34.8 · Apex Shortlist 90.2 vs 85.7 · SWE Verified 80.6 vs 79.0 · MRCR-1M 83.5 vs 78.7 · CorpusQA-1M 62.0 vs 60.5 · Terminal Bench 2.0 67.9 vs 56.9.
→ Pro's edge is real but *single-digit* on most domains at **5.2× the storage**; the agentic gap (TB) was the widest and Flash-0731 already overrode it. This is the global template: capability per GB, not capability per se.

## 2. Official efficiency headline (the V4 paper's core claim)

*"At 1M-token context, V4-Pro requires only 27% of single-token inference FLOPs and 10% of KV cache vs DeepSeek-V3.2."* — consistent with what we computed independently: ~6 GB fp8 KV at 1M ctx (CSA/HCA pools + sliding windows), and the released artifact already ships fp4/fp8. The "1M context" is not marketing; it is an *efficiency result*.

## 3. V5 upgrade vectors — each with a measured basis and a measurable target

**V5-1 Tokenizer v2 (code).** Measured today: V4 tokenizes generated Python at 3.69 chars/token (25.6% better than Qwen, but identifiers still fragment: `input_data` → `input`+`_data`). Target: code-domain BPE merges → **3.0 chars/token ≈ 18–25% fewer tokens globally** → 18–25% cheaper every software task, 18–25% more code per context. Fully executable without model access; harness in `scale_token_test.py`.

**V5-2 Context beyond 1M.** KV at 1M ctx ≈ 6 GB fp8 (computed). Headroom: HCA rate 128→256 halves the long-range pool; lower-layer KV offload; fp4 indexer cache already in vLLM. Target: **2–4M context at the same 6 GB budget** [proj — arithmetic, not product]. With tokenizer v2, that's ≈ 300–600K LOC in context (from today's ≈107K).

**V5-3 Expert economics (the open lever).** 97.7% of expert weights idle per token (6/256). Census (needs 4×GPU class) → prune coldest 30% (158 → ≈110 GB) → INT2 (≈55–80 GB + 6 GB KV) → **48 GB-class single-GPU deployment** — the CIIF's "maximum arbitrage escape" becomes a product category. Density target: **0.8–1.0 %/GB**.

**V5-4 DSpark for code.** Code is structurally predictable (indentation/braces/templates — the generator corpus is a perfect probe). Code-adapted drafts (markov rank / MTP fine-tune on code) target accept-rate gains beyond the current 7-token speculative window; LiveCodeBench 91.6 suggests the model's code distribution is already low-entropy. Verification: deterministic generator corpus as the accept-rate test set.

**V5-5 Agentic post-training.** Flash-0731's own jump (61.8→82.7 TB) proves the lever. Targets: **TB 2.1 82.7 → 90+**, DeepSWE 54.4 → 65+, MCPAtlas 73.8 hold-while-cheaper; reasoning-effort continuum (HLE: Flash 8.1 non-think → 34.8 max — 4.3× from test-time scaling alone) → **adaptive effort routing** (spend max only when the task needs it).

**V5-6 Training side (official).** Muon optimizer + 32T tokens (paper) — the measured cost curve of the family suggests V5 continues both: 64T-class data [proj], same architecture, scale within Flash (≈350B [proj]) and Pro (2–3T [proj]) bands.

## 4. What V5 likely is [proj — synthesis of the above, not a leak]

Not "bigger for bigger's sake" — the family already proved density wins. The consistent reading:
- **Flash-line (the global product)**: ~300–400B, 100–130 GB shipped (pruned + INT2), 1–2M context, code-tokenizer v2, DSpark-v2 — deployable on a single 48–80 GB GPU. This is the "global world" model: open (MIT), commodity-priced, local-runnable.
- **Pro-line (the frontier)**: 2–3T, per-domain leaderboard wins at 27%-FLOPs/10%-KV efficiency carried forward; the density gap to Flash stays deliberate (two products).
- **The market consequence**: the race shifts from *capability* (Pro-Max already claims open-model SOTA) to *capability per GB* — where Flash-0731's 0.50 %/GB is today's bar, and GLM-5.2 (81.0 TB, ~400 GB est. → ~0.20 %/GB) and Opus-4.8 (85.0, ~900 GB → ~0.09 %/GB) are the comparison points from the Flash README table.

## 5. Honest limits

- Flash-0731 vs Pro numbers mix benchmark versions (TB 2.0 vs 2.1); family comparisons are directional, not apples-to-apples.
- No V4 runtime here: throughput, DSpark accept-rate, census, KV-at-runtime are unmeasured ([proj] where so).
- V5 does not exist; everything in §3–4 is a labeled projection from measured baselines + official claims. The only hard facts about "V5" are the vectors — they are all measurable with the tooling built this session.

## 6. Artifacts this session (oe-local/2026-08-04/)

- `DEEPSEEK_V4_ARCHITECTURE_INVESTIGATION.md` (v2) — the architecture, tensor-level
- `V4_UPGRADE_SPEC_FOR_SOFTWARE_USE.md` — U1–U6 upgrade levers with measured bases
- `V4_TO_V5_GLOBAL_TRAJECTORY.md` — this document
- `scale_token_test.py`, `measure_qwen_speed.py` — reusable measurement harnesses
- `oe-local/generators/batch_materializer.py` — fixed (Path.sep → os.sep)
- Ground truth: `ds_v4_config.json`, `ds_v4_inference_config.json`, `ds_v4_index.json` (72,317 tensors), plus Pro/paper data cited above
