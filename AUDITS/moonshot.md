# AUDIT — Moonshot AI (Kimi K2 family)

**Current as of:** 2026-08-10 · **Status:** ACTIVE · **Architecture access:** FULL config-level (ours, D13); tensor census queued · **Our evidence:** K2-Instruct config census (2026-08-07), HF API trail (2026-08-10), registry (kimi row: HLE 0.502 = the field's biggest HLE number).

## Known facts (cited)

- **Kimi K2-Instruct config** `[measured, ours, HF commit fd1984e2…]`: 61 layers, 384 routed + 1 shared expert, 8 active (2.08%), V3-lineage MLA (q_lora 1536 / kv_lora 512 / qk_nope 128 / qk_rope 64 / v 128), noaux_tc + sigmoid scoring (routed_scaling_factor 2.827), 131,072 ctx via YaRN×32 over a 4,096 base, FP8 e4m3 shipped weights, `num_nextn_predict_layers: 0` (no MTP). **It is architecturally DeepSeek V3's lineage** — the field's reference for what V3-style MLA+MoE scales to.
- **Open-weight trail** `[published, HF API, fetched 2026-08-10]`: Kimi-K2-Instruct (Jul 2025) → Kimi-K2.5 (Jan 1 2026, 862K downloads, image-text-to-text, tech report **arxiv:2602.02276**) → Kimi-K2.6 (Apr 14 2026, 785K) → Kimi-K2.7-Code (Jun 11 2026, 650K). All ungated, license:other. NVIDIA ships FP4 (Kimi-K2-Thinking-NVFP4) and Eagle3 speculative-decoding builds (Kimi-K2.5-Thinking-Eagle3) — the density/speculation ecosystem around K2 is public.
- **HLE** `[measured, registry]`: Kimi K2.5 0.502 vs V4-Flash max 0.348 — the biggest measured gap in our matrix; HLE is the frontier surface Moonshot currently leads on.

## Discrepancies (claim vs evidence)

1. **HLE leadership vs K2's V3-lineage architecture** `[measured]`: the model with no MTP, no CSA, 2.08% active experts out-scores V4 on HLE by 15 pts. Either HLE rewards their training/data pipeline (reasoning post-training), not architecture — or our V4 HLE numbers are on a different eval version (E4 risk). Both are hypotheses to resolve: fetch K2.5 tech report 2602.02276 + re-baseline HLE on one harness.
2. **license:other** `[published]` — Moonshot's weights are open-download but not standard open-source license; the "open" claim needs license-level scrutiny for L3 (data policy) work.

## Open questions / next probes

- [ ] Ingest arxiv:2602.02276 (K2.5 tech report) via the existing arxiv pipeline → WS3 notes + reasoning pairs.
- [ ] Tensor census of K2.5 (index.json public) — expert/gate tensor shapes vs V4 census; upgrade CROSS_MODEL_ARCHITECTURE_DELTA.md (pre-registered queue item 1).
- [ ] HLE re-baseline on one harness (WS2) — the single most decision-relevant number in the field for DeepSeek's next cycle.
- [ ] License + training-data-policy sweep (K2 reports disclose data mixes? cite what they disclose).

## Bottom line

Moonshot is the campaign's best open target: full architecture access, an active open-weight cadence (K2.5/2.6/2.7 in 6 months), NVIDIA's FP4/Eagle3 ecosystem, and the HLE number DeepSeek must beat. Every V5 reasoning-data decision in our chain traces back to this gap.
