# DeepSeek-V4 Architecture Investigation — Offline Report (v2)
**Date:** 2026-08-04 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Method:** CIIF Phases 1–4, executed recursively — 100% no-download (metadata + source only)
**Ground truth sources:** real `config.json` (HF, sha `7872f01b`), official `inference/config.json`, `model.safetensors.index.json` (5.6 MB — full 72,317-tensor map, zero weights), HF API storage stats, official README benchmarks, transformers 5.8.1 `modeling_deepseek_v4.py` (reference implementation, 1498 lines), HF model_doc architecture page (with attention-mask diagrams), vLLM GitHub inventory + recipes, official `inference/` runner docs.

---

## 0. Ground Truth First

- **Params: 304.18B** — HF API `safetensors.parameters` (296.35B I8 + 6.30B F8_E4M3 + 1.48B BF16 + 37.7M F32 + 2.3M I64). The CIIF's "304B" ✓.
- **A_task = 82.7** — official README, Terminal Bench 2.1 ✓ (GLM-5.2 81.0, Opus-4.8 85.0 match the doc's table).
- **S_install = ~158 GB weights / 166.9 GB repo storage** (`usedStorage`). The doc's "~750 GB BF16" is the *uncompressed counterfactual* — the release already ships **fp4 experts (packed as I8) + FP8 attention (e4m3, 128×128 blocks, ue8m0, dynamic) + BF16 residual**, per `quantization_config`/`expert_dtype: fp4`.
- **Real density ρ_I = 82.7 / 167 ≈ 0.50 %/GB** — already beats the doc's own "INT4 → 0.436" row.

## 1. Structural Baseline

`DeepseekV4ForCausalLM`, context 1,048,576 (YaRN ×16 from 64K), hidden 4096, 43 layers, vocab 129280, untied embeddings (`embed.weight` + `head.weight`).

**Layer census — definitive, from the checkpoint's own tensors (72,317 tensors):**
- **2 sliding-window attention** layers (0, 1) — window 128, no compressor, no indexer (verified: zero `attn.compressor.*` / `attn.indexer.*` tensors).
- **21 Compressed Sparse Attention (CSA, "c4a")** layers — even 2..42: compressor (rate 4, overlapping windows) + **Lightning Indexer** (64 heads × 128 dims, top-k 512, own rotary θ=160k, ReLU-gated scores, paper §2.3.1 eqs. 13–17).
- **20 Heavily Compressed Attention (HCA, "c128a")** layers — odd 3..41: compressor only (rate 128, non-overlapping, no indexer; §2.3.2 eqs. 20–23).
- **Corrections to CIIF:** the doc's "30 c4a / 31 c128a" (61 layers) is wrong on both counts. Both published configs' `compress_ratios` (44 and 46 entries, tails of 0s) also disagree with the weights — the checkpoint carries compressor tensors on layers 41–42 and indexers on 42, so the effective map is 2/21/20, and the config arrays are stale in the tail (release inconsistency worth flagging).

**Attention core (all 43 layers):** MLA with **1 shared KV head** (shared-KV MQA, keys = values), head_dim 512, q_lora_rank 1024, o_lora_rank 1024 (grouped output projection: `o_groups=8` → `o_lora_rank` per group, `wo_a`+`wo_b`), partial RoPE on the trailing 64 channels (interleaved-pair, eq. 26), **per-head learnable attention sink** (`attn.attn_sink`, eq. 27). Quantized: every weight has a sibling `.scale` tensor (FP8 per-block scales).

**Hyper-connections (mHC, §2.2):** `hc_mult=4` parallel residual streams per block, `hc_attn/ffn_base/fn/scale` tensors per layer + `hc_head_*` at the top; Sinkhorn-Knopp doubly-stochastic mixing (`hc_sinkhorn_iters=20`), non-expansive signal propagation.

**MoE (all 43 layers):** 256 routed experts (w1/w2/w3 + scales) + 1 shared expert; 6 active per token (**2.34% — 97.7% idle**); `noaux_tc` top-k with `e_score_correction_bias` (`ffn.gate.bias`), Sqrt(Softplus) scoring, routed scale 1.5, clamped SwiGLU (limit 10). **Hash-MoE bootstrap:** `ffn.gate.tid2eid` (frozen token-id→expert-id table) on the **first 3 layers (0,1,2)** — my v1 report wrongly said "last 3"; the doc confirms "first few bootstrap layers". (DSpark's `target_layer_ids [40,41,42]` is the speculative module, unrelated.)

**MTP + DSpark (from tensors):** 3 full MTP blocks (`mtp.0..2`), each with its own attention + 256 experts; `markov_head` (markov_w1/w2 — markov_rank 256) and `confidence_head` only on `mtp.2`; `dspark_block_size=5`, noise token 128799. (transformers config says `num_nextn_predict_layers: 1`; inference config says `n_mtp_layers: 3` — another minor config inconsistency.)

## 2. Implementation Code (where it actually lives)

**Correction to CIIF's plan:** `git clone vllm && grep c4a vllm/.../models/deepseek_v4.py` finds **nothing** — vLLM has no native V4 file (404 + models-dir inventory: only `deepseek_v2.py`, `deepseek_vl2.py`, `deepseek_eagle3.py`). The real implementations:
1. **transformers 5.8.1** `models/deepseek_v4/modeling_deepseek_v4.py` — reference; classes verified: `DeepseekV4Indexer`, `CSA/HCACompressor`, `CSACache/HCACache`, `GroupedLinear`, `HyperConnection` (+`HyperHead`), `TopKRouter`/`HashRouter`, `SparseMoeBlock`, `DecoderLayer`, `Model`, `ForCausalLM`.
2. **HF repo's own `inference/` runner** — `convert.py`/`generate.py` (torchrun, MP=4, fp4↔fp8 switchable).
3. vLLM serves it via `--trust-remote-code` + `--moe-backend deep_gemm_mega_moe` + `--attention-config '{"use_fp4_indexer_cache": true}'` + `--kv-cache-dtype fp8`; SGLang via `flashinfer_mxfp4`.
4. HF model_doc page documents the full attention-mask layout per layer type (diagrams reproducible via `visualize_attention_masks.py`).

## 3. Recursive CIIF Math — where the GB actually go

**Weights ~157.6 GB** = fp4-packed experts ~148 GB + FP8 ~6.3 GB + BF16 ~3.0 GB + F32 ~0.15 GB.

**KV cache at 1M context (fp8, computed from real dims):** MLA latent = 1088 dims/token. Sliding layers keep only the 128-token window (negligible); CSA pools = seq/4 ≈ 250k entries/layer; HCA pools = seq/128 ≈ 7.8k entries/layer:
- 21 CSA ≈ 5.7 GB, 20 HCA ≈ 0.17 GB, sliding ≈ 0 → **total ≈ ~6 GB fp8 at 1M ctx** (before fp4 indexer-cache savings).
- **CIIF claims "140 GB / 70 GB FP8 / offload to 14 GB" — unsupported; native ≈ 6 GB.** The doc's Phase 3 is the architecture's native design. (v1 report said ~11 GB; corrected now that sliding layers provably don't store full sequences.)

**CIIF roadmap vs shipped reality:**
- "Compress to INT4 (188 GB)" → already shipped (fp4 experts, 158 GB).
- "90% idle experts" → actually 97.7% idle/token; cold-expert pruning remains the one real lever (needs a corpus census — requires 4×GPU hardware or API traces; un-runnable on this 6 GB laptop).
- "INT2 on pruned → ~78 GB, sub-100 GB total" → plausible trajectory from 158 GB (≈110 GB @30% prune, ≈55–80 GB + INT2), but unverifiable here.
- "Don't fork llama.cpp yet" ✓ agreed — nothing to fork; vLLM/SGLang already support it.

## 4. The No-Download Full-View Method (what was asked about)

The entirety of the architecture is inspectable with zero weight downloads:
1. **`config.json` (~2 KB)** — hyperparameters.
2. **`model.safetensors.index.json` (5.6 MB)** — **complete tensor map: all 72,317 tensor names + shard placement** (this report's census is derived from it: 43×256 experts + 3×256 MTP experts, compressors, indexers, sinks, hyper-connections, routers, heads).
3. **transformers modeling source** (installed locally) — full execution semantics.
4. **HF API** (`/api/models/...`) — per-dtype parameter counts + storage size.
5. **Official docs** — model_doc page + README + inference README.
6. **Paper** (arxiv 2606.19348 / `DeepSeek_V4.pdf` in the repo) — design rationale.
Only missing: per-tensor *shapes* (they live in each shard's safetensors header, ~200 KB per 3 GB shard — fetchable by range requests if needed) and behavioral verification (needs the weights).

## 5. Limits

- No weights local (Qwen-1.5B/TinyLlama only); all facts from metadata + source + docs, none from running the model.
- Per-tensor shapes not extracted (48 shard headers would add ~10 MB); config↔weights inconsistencies flagged above are real but impact-free for inference (extra weights go unused).

## 6. Verdict

CIIF direction confirmed; headline numbers (304B, 82.7, density inversion) real. The model already shipped the doc's compression roadmap (fp4/fp8, native sparse KV ≈ 6 GB at 1M ctx). The one remaining lever — cold-expert pruning — needs hardware this machine lacks. The "view the entire architecture without downloading" claim is **true and demonstrated**: config + safetensors index + source + docs cover the full structure.

## 7. Artifacts (in `oe-local/2026-08-04/`)

- `ds_v4_config.json` — transformers config (sha 7872f01b)
- `ds_v4_inference_config.json` — official runner config
- `ds_v4_index.json` — full 5.6 MB tensor index (72,317 tensors)
- `_ds_v4_math.py` — dims-based size/KV estimate (superseded by official 304.18B count + tensor census)
- `_ds_v4_index_layers.py` / `_cmp_ratios.py` — census + config-comparison scripts
- This report (v2 — corrected: hash-MoE on layers 0–2; census 2 sliding/21 CSA/20 HCA from tensors; KV ≈ 6 GB)
