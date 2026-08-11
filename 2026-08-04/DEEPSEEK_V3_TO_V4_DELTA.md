# DeepSeek V3.2 → V4 Delta — the upgrade lineage, verified from real configs
**Date:** 2026-08-04 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Sources:** real config.json for V3.2 (`a7e62ac`), V4-Flash-0731 (`7872f01b`), V4-Pro (`b5968e91`); HF API storage stats; oe-local `benchmarks/model_profiles/deepseek_v3.json`; official READMEs; the V4 paper (arxiv 2606.19348).

## 1. Config delta (real numbers)

| Dimension | V3.2 | V4-Flash-0731 | V4-Pro |
|---|---|---|---|
| Params (HF API) | 685.4B | 304.2B | 1,598.8B |
| Activated | 37B (official profile) | ~13–16.8B | 49B (paper) |
| Storage | 689 GB (fp8 only) | 167 GB (fp4 experts + fp8) | 865 GB |
| Layers | 61 | 43 | 61 |
| Hidden | 7168 | 4096 | 7168 |
| Routed experts | 256 | 256 | 384 |
| Active/token | 8 (grouped: topk_group 4) | 6 | 6 |
| Scoring | Sigmoid | Sqrt(Softplus) | Sqrt(Softplus) |
| Attention | MLA + DSA indexer (top-k **2048**) | MLA + CSA/HCA, Lightning indexer top-k **512** | top-k **1024** |
| KV latent/token/layer | 576 | 1088 | 1600 |
| Context | 163,840 (YaRN ×40) | 1,048,576 (×16) | 1,048,576 |
| Dense FFN | intermediate 18432 (first 3 layers dense) | none | none |
| New in V4 | — | mHC hyper-connections (hc_mult 4, Sinkhorn), hash-MoE bootstrap (3 layers, tid2eid), DSpark+MTP, expert fp4, swiglu clamp, o_groups 8/16 | same |
| Attention layout | uniform | 2 sliding + 21 CSA + 20 HCA | 30 CSA + 30 HCA + 1 full (compress_ratios start 128,128 — **no sliding bootstrap; family members differ structurally**, not just in scale) |

Same vocab (129,280 — shared tokenizer), MIT, noaux_tc lineage, fp8 quantization config, YaRN.

## 2. The "10% KV" claim — verified, and NOT reproduced

Paper: *"at 1M tokens, V4-Pro needs 10% of V3.2's KV cache."* Computed from real dims (fp8, 1M ctx, sliding windows negligible):
- V3.2: 576 × 61 × 1M = **36.8 GB fp8 / 73.7 GB bf16**
- V4-Flash: 21×(1088/4×1M) + 20×(1088/128×1M) ≈ **6.2 GB** → **17% of fp8-V3.2, 8% of bf16-V3.2**
- V4-Pro: 30×(1600/4×1M) + 30×(1600/128×1M) + 1×1.6 GB ≈ **14.7 GB** → **40% of fp8-V3.2, 20% of bf16-V3.2**

**Finding:** the 10% figure does not reproduce under standard MLA-latent accounting (we bracket 8–40% depending on model + baseline dtype; Flash-vs-bf16-V3.2 = 8% is the closest to the claim). Possible causes (flagged, not resolved): the paper's V3.2 baseline may include its DSA branch storage or use a different context; or "10%" refers to the Flash line. The 27%-FLOPs claim is likewise not resolvable from configs alone (activated params: 37B vs 13–16.8B vs 49B — active-param ratio alone gives 35–45%, so the 27% must come from attention-cost accounting at 1M ctx). **Both headline efficiency claims should be re-derived from the paper's methodology before being quoted.**

## 3. Benchmark lineage (oe-local V3.2 profile vs V4 README; versions differ — directional)

From `benchmarks/model_profiles/deepseek_v3.json` (V3.2) vs Flash-0731/Pro README (max mode where noted):
- SWE_Bench 0.721 → **SWE Verified 79.0/80.6** — big gain
- BrowseComp 0.412 → **73.2/83.4** — the single largest relative gain (a known V3.2 failure mode fixed)
- HLE 0.351 → **34.8/37.7**
- LiveCodeBench_v6 0.833 → **91.6/93.5**
- GPQA_Diamond 0.505 → **88.1/90.1**
- **ARC_AGI_3: 0.0 (V3.2) — and no V4 number published. The biggest open gap → measure it in the next cycle.**
- MMLU 0.871 / GSM8K 0.917 / AIME 0.892 / HumanEval 0.656 — no direct V4 counterparts published (eval-registry update target).

**Failure modes in the oe-local profile → post-training targets:** ARC-AGI-3 0.0 (measure + target), BrowseComp (resolved, keep), confabulation incidents (court-case fabrication, file-count fabrication — PR #81) → alignment data targets (the canonical_evidence/boundary_enforcement sets + combined_v4–v7 falsification/deception blocks apply directly).

## 4. Structural lineage → what it means for the next training cycle

1. **Routing: 8/256 grouped → 6/256 free.** Fewer active experts (2.3% vs 3.1% of experts per token) + Sqrt(Softplus) scoring → the census tool (`expert_census.py`, dry-run ✓) answers whether code workloads concentrate even further; pruning headroom grew.
2. **Hash-MoE bootstrap** (first 3 layers, frozen tid2eid) — a training-time constraint: these layers' routing is fixed at checkpoint time; fine-tunes must keep the table consistent.
3. **mHC hyper-connections** — Sinkhorn-constrained mixing changes gradient paths vs residual nets; LoRA/instruction tuning should target the HC tensors (`hc_attn/ffn_base/fn/scale`) as an adapter surface — untested, defined experiment.
4. **Indexer economics: top-k 2048 (V3.2) → 512 (Flash) / 1024 (Pro)** — 4×/2× fewer index lookups; per-query KV gather shrinks; post-training should keep the indexer's own rotary (θ=160k) and position_bias stable (they gate long-context transfer).
5. **fp4 experts (V4) vs fp8-everything (V3.2)** — 4× expert storage cut; the INT2/prune path (§3 of the upgrade spec) continues from here.
6. **Context 160K → 1M** — training-data curricula must now exercise >160K spans; the arxiv_vendor + generator corpora are the available long-context sources.

## 5. Artifacts

- `verify_kv_claim.py` — the KV arithmetic (reproducible)
- `DEEPSEEK_V4_ARCHITECTURE_INVESTIGATION.md` (v2) — V4 tensor-level
- `POST_TRAINING_PREP.md` — data/eval/tool inventory incl. this delta
- oe-local asset discovered: `benchmarks/model_profiles/deepseek_v3.json` (+10 other model profiles: claude_opus_4_5, gemini_3_pro, gpt5, kimi_k2_5, llama_4, qwen_3, …) — a ready-made cross-model eval registry for target-setting.
