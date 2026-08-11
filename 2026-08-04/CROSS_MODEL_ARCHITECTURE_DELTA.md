# CROSS-MODEL ARCHITECTURE DELTA — V4 vs open-weight frontier (no-download, config-level → tensor-level)

**UPGRADE 2026-08-10:** tensor-level census DONE for Qwen3-235B-A22B + Kimi-K2-Instruct (`model_census.py` → `census/*.json`, all config cross-checks PASS, deterministic) — see **`CENSUS_REPORT.md`** for the tensor inventory, active-params/token, KV footprints, and per-model harsh audit. This file remains the config-level base; the report is the tensor-level layer.

**Date:** 2026-08-07 · **Method:** same no-download technique as the V4 census — public HF config.json only (~1–2 KB per model), no weights, no llama.cpp. Sources fetched live today (HTTP 200), commit-pinned:
- Qwen3-235B-A22B: `https://huggingface.co/Qwen/Qwen3-235B-A22B/raw/main/config.json` (commit `8efa6172…`, gated: false, Apache-2.0; repo contains `model.safetensors.index.json` → tensor census possible next)
- Kimi-K2-Instruct: `https://huggingface.co/moonshotai/Kimi-K2-Instruct/raw/main/config.json` (commit `fd1984e2…`)
- Mistral-Large-Instruct-2411: `https://huggingface.co/mistralai/Mistral-Large-Instruct-2411/raw/main/config.json` (commit `ba788209…`)
- V4 column: CHAIN_OF_CUSTODY.md §4 (no-download census + official docs; measured/verified on disk)

**Honesty labels:** `[config-level]` — fields from public configs; `[tensor-level]` — from safetensors index (done only for V4 so far); `[published]` — model cards/READMEs. Closed models (Claude Fable 5, GPT-5.x/Astra, Gemini, Grok) have no public configs — NOT inspectable; their info is paper/card-level only (see "closed models" section).

## Architecture table

| Field | V4 (DeepSeek, 158 GB) | Qwen3-235B-A22B | Kimi K2 Instruct | Mistral Large 2411 |
|---|---|---|---|---|
| Layers | 43 = 2 sliding + 21 CSA (rate 4) + 20 HCA (rate 128) | 94 dense-ish, `decoder_sparse_step: 1`, `max_window_layers: 94` | 61 (`first_k_dense_replace: 1`) | 88 dense |
| Attention | MLA, shared-KV head_dim 512; 64 heads × 128; partial RoPE 64ch; learnable attn_sink; Lightning Indexer top-k 512/1024 | GQA 64 heads / 4 KV, head_dim 128 | MLA (V3-lineage): q_lora 1536, kv_lora 512, qk_nope 128 / qk_rope 64, v 128 | GQA 96 heads / 8 KV, head_dim 128 |
| MoE | 256 + 1 shared, 6 active (**2.34%**), noaux_tc, Sqrt(Softplus), scale 1.5 | 128, 8 active (**6.25%**), norm_topk_prob, aux loss 0.001 | 384 + 1 shared, 8 active (**2.08%**), noaux_tc, sigmoid, scale 2.827 | dense (no MoE) |
| Context | 1,048,576 (YaRN×16), KV ≈6 GB fp8 @1M | 40,960 (`rope_scaling: null`) | 131,072 (YaRN×32 over 4,096 base) | 131,072 (native, no scaling) |
| RoPE θ | 160k | 1,000,000 | 50,000 | 1,000,000 |
| Vocab | 129,280 | 151,936 | 163,840 | 32,768 |
| Speculation | MTP ×3 + markov_head + confidence_head (mtp.2); DSpark block 5, 7-token | none in config | `num_nextn_predict_layers: 0` (none) | none |
| Bootstrap | hash-MoE frozen tid2eid on layers 0–2 | none | none | none |
| Quant | fp4-packed experts ≈148 GB + FP8 + BF16 + F32 | bf16 | **FP8 e4m3 shipped weights** | bf16 |
| Router extras | hyper-connections hc_mix + Sinkhorn ×20 | — | topk_group 1, seq_aux | — |

## Delta read — what it means for V5

1. **Active-expert ratio: V4 and Kimi are the efficiency class (2.1–2.3%); Qwen3 spends 3× (6.25%) with a 128-expert table.** The 6/256 choice is validated as frontier-efficient — V5 should hold it, not grow it (catalog #7's entropy term is the lever to use it better, not more of it).
2. **Long context: V4's 1M (KV ≈6 GB fp8) has no competitor at that cost.** Qwen3 caps at 40K with no scaling config; Kimi reaches 131K via YaRN×32 over a 4K base (a 32× extrapolation — the KV math for Kimi-style full attention at 1M would be ~50 GB+). V4's CSA/HCA split is the only design here that makes 1M cheap; V5's 2–4M target (catalog #13, kv_decay_schedule) is ahead of every compared architecture.
3. **MLA vs GQA: the frontier split is real.** Kimi kept V3-style MLA; Qwen3 and Mistral use GQA with small KV groups (4/8). V4's MLA head_dim-512 is the evolved form (V3 lineage + CSA). Informational: no evidence any competitor has a KV-cheaper attention; keep MLA.
4. **Speculation stack: V4 is alone.** MTP×3 + confidence head + DSpark exists nowhere in this set (Kimi explicitly `0` nextn layers). The jitter/tail-gate + PLL work (E3, pll_jitter_sim) is a differentiator investment, not catch-up.
5. **Router regularization: Qwen3's `norm_topk_prob` + tiny aux loss (0.001) is a tested variant V4's noaux_tc family doesn't use.** Worth a post-train experiment for V5 (adjacent to catalog #7's entropy-constrained routing); Kimi's sigmoid scoring (scale 2.827) is the other tested alternative. `[config-level]` — effects need measurement, which is hardware-gated.
6. **Kimi K2 = the V3-lineage reference.** Its config is DeepSeek V3's architecture (MLA + noaux_tc + routed scaling). V4's delta over that lineage — CSA/HCA split, hyper-connections, hash-MoE bootstrap, MTP×3, indexer — is exactly what the comparison should preserve and deepen. V4 is not "V3 with more experts"; it's a different attention/routing stack.
7. **Quant: only Kimi ships FP8; nobody ships V4's fp4-packed-expert density.** The census → prune → INT2 path (158 → ≈110 → 55–80 GB) has no published competitor target; it remains the density differentiator (0.50 %/GB → 0.8–1.0).

## Closed models (Claude Fable 5, GPT-5.x/Astra, Gemini, Grok) — what's actually learnable

- **No public weights/configs** — the no-download method stops at papers, model cards, and system cards. Fetching their "architectures" is not possible; claims about their internals would be `[hypothesis]` at best.
- **Genuinely relevant public papers to ingest via arxiv_vendor** (metadata-only, ~2 KB each): Anthropic's sparse-attention paper (long-context design, directly comparable to CSA), Qwen3 tech report (`arxiv:2505.09388`, tagged on the HF repo), Kimi K2 tech report, any GPT-5.x system card.
- **Astra (product, not model)**: its learnable content is *agentic behavior* (tool loops, verifier use, multi-step execution) — maps to the axes already built: BRR (BOUNDED_RECURSION_RESEARCH.md), the effort-router (E5/E6), TOOL_USAGE data, Terminal Bench 2.1 (82.7 → 90+ target). No architecture there to pull.
- **Fable 5 / Mythos-class (Anthropic)**: same treatment — published benchmarks for the registry (re-baselined per E4), papers for the pipeline, nothing at tensor level.

## Space accounting (answers the logistics question)

- Method: ~1–2 KB per config; tensor census (index.json) adds ~5–30 MB per model. **Total for a 5-model comparison: <100 MB.** No additional disk needed; the 13.1 GB free on C: is irrelevant (all work lives in WSL; C: is only touched via the WSL vhdx when large corpora are materialized — ~3.7 GB per 300-batch run, regenerable and chain-rooted).
- llama.cpp: NOT used, not needed, and explicitly out of scope (custody §2). The method is config/index/docs/transformers-source — the same one that produced the V4 census.

## Next steps (pre-registered)

1. **Tensor-level census of Qwen3-235B-A22B + Kimi-K2-Instruct** (index.json, ~10–30 MB each): expert tensor shapes, per-layer KV/attention tensors, gate tensors — the same schema as the V4 census → fill the `[tensor-level]` gap in this table.
2. **arxiv_vendor ingestion**: Qwen3 tech report (2505.09388), Kimi K2 report, Anthropic sparse attention paper → reasoning pairs + architecture notes.
3. **Registry update**: add Fable 5 row (published scores, version-flagged per E4) when stable sources exist.
4. **V5 post-train experiment candidates** (from row 5): norm_topk_prob + aux-loss variant, sigmoid scoring variant — `[needs hardware]`, pre-registered here.
