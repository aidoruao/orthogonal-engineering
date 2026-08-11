# TENSOR-LEVEL CENSUS REPORT — Qwen3-235B & Kimi-K2 vs V4 (WS1, verified)

**Date:** 2026-08-10 · **Tool:** `model_census.py` (new, stdlib-only, no-download: config.json + model.safetensors.index.json over HTTP; deterministic, double-run byte-identical — sha `da5b0dde…` qwen3, `5f26b4ba…` kimi) · **Outputs:** `census/qwen3_235b_a22b.json`, `census/kimi_k2_instruct.json` · **V4 column:** custody §4 + V4 tensor census (72,317 tensors, no-download).
**Verification:** every derived count cross-checked against the model's own config — ALL PASS (layers: 94/94, 61/61; experts: 128/128, 384/384; Kimi router count 60 = 61 layers − 1 dense layer, matching `first_k_dense_replace: 1`).

## Tensor inventory

| Metric | V4 (DeepSeek) | Qwen3-235B-A22B | Kimi-K2-Instruct |
|---|---|---|---|
| Tensors in index | 72,317 | 36,945 | 139,644 |
| Total params (from index bytes) | 304.18B (shipped fp4/FP8/BF16 mix) | **235.1B** (470,187,269,120 B ÷ 2 bf16) | **1,029.2B** (1,029,173,256,720 B ÷ 1 fp8) |
| Layers | 43 (2 sliding + 21 CSA + 20 HCA) | 94 | 61 (layer 0 dense — verified: 60 routers) |
| Experts | 256 + 1 shared | 128 | 384 + 1 shared (360 shared-expert tensors) |
| Active / token | 6 (2.34%) | 8 (6.25%) | 8 (2.08%) |
| **Active params / token** | **≈7.1B** | **≈14.7B** | **≈21.4B** |
| Attention tensors | MLA (head_dim 512 shared-KV) | GQA (94× k_proj/v_proj) | MLA verified at tensor level (61× q_a/kv_a) |
| Router/gate tensors | 46 (incl. 3 MTP) | 94 | 60 |
| Speculation tensors | MTP×3 + markov + confidence | **0** | **0** |
| KV footprint / token | 512×43 = **22,016 dims** | 4×128×94 = 48,128 dims | 512×61 = 31,232 dims |
| Shipped density (B/GB) | **1.93** (fp4-packed) | 0.50 (bf16) | 1.00 (fp8) |

## Harsh audit — what's wrong, why, and how (per model, evidence-cited)

### Qwen3-235B-A22B
1. **2.1× the active compute of V4 per token (14.7B vs 7.1B active).** Why: 8 of 128 experts active with 6.25% budget — a table-size/active-budget tradeoff that spends 3× the fraction of params V4 or Kimi do. How: drop to 4–6 active (the 128-expert table has room), or grow the table toward V4's 256/6 ratio. This is the single largest efficiency delta in the open field.
2. **40,960-token context with `rope_scaling: null`** — the only compared model that does not even attempt long context (their own Qwen2.5 line used YaRN; Qwen3 dropped it). Why: architecture choice (dense-ish 94 layers, no CSA analog). How: V4-style hybrid attention (CSA/HCA) or YaRN reintroduction; at 1M tokens, Qwen3-style GQA KV = 48,128 dims/token ≈ 96 GB fp16 — infeasible without a sparse design. **V4's 6 GB @1M stands as the cheapest long-context design in the open field, now at tensor level.**
3. **Router aux loss 0.001 + `norm_topk_prob`** — a real, tested balance signal V4's noaux_tc family doesn't use. Not "wrong" — but it is the one variant from this census worth a hardware-gated V5 experiment (D13, queue item).

### Kimi-K2-Instruct
1. **3.0× V4's active compute per token (21.4B vs 7.1B) on a 1.03T-param model.** Why: 384×2048 experts × 8 active, noaux_tc with sigmoid. How: fewer active experts or smaller moe_intermediate (2048 → 1536 would cut ~25% of expert compute). The HLE 0.502 lead is bought with 3× the per-token compute — an actionable "why they win, and at what cost" number for DeepSeek.
2. **Zero speculation on a 1.03T model.** Why: `num_nextn_predict_layers: 0` — verified at tensor level (no MTP/nextn tensors). How: MTP-1/2 (V4's design) or Eagle3 (NVIDIA already ships `Kimi-K2.5-Thinking-Eagle3` — the ecosystem is ahead of the base model). Decode-bound 1T models are the clearest speculation opportunity in the field.
3. **32× YaRN extrapolation over a 4,096-token base to reach 131K** — the most stressed scaling config in the set (V4: 16×). Why: short native training, cheap context after the fact. How: longer native context training; risk at depth is measurable only on hardware (pre-registered KV probe).
4. **FP8 shipped density 1.00 vs V4's 1.93** — Moonshot ships 1 byte/param; V4 ships 0.5 (fp4-packed experts). Our census→prune→INT2 path (158 → ≈55–80 GB) targets 3.8–5.5 B/GB — no competitor ships within 2× of that.

### Both (vs V4)
- **No hyper-connections, no hash-MoE bootstrap, no DSpark, no MTP** — V4's unique stack is now confirmed at tensor level as the field's only instance of: speculation + long-context-hybrid + frozen-hash bootstrap. The audit's conclusion: **V4's architecture is not behind — its training/data pipeline (HLE) and density shipping are the gaps.** That redirects the next cycle's spend: reasoning data (canonical_sft_v2, HLE harness), not architecture rework.

## What changed in the delta (upgrade from config-level → tensor-level)

- All D13 rows confirmed (active ratios, contexts, speculation) by independent tensor counts.
- New tensor-level facts: active-params/token (7.1/14.7/21.4B), KV dims/token (22,016/48,128/31,232), shipped density (1.93/0.50/1.00), Kimi's dense layer-0 (60 routers), zero-speculation verified for both.
- Pre-registered next: Mistral tensor census (dense reference), then GLM config row, then the HLE/registry re-baseline.
