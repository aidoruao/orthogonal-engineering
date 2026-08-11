# AUDIT — Alibaba (Qwen3 family)

**Current as of:** 2026-08-10 · **Status:** QUEUED (architecturally measured — see below).
**Our evidence:** config census `[measured, 2026-08-07, commit 8efa6172…]`: 94 layers, 128 experts / 8 active (6.25%), hidden 4096, GQA 64/4 KV, 40,960 ctx native (no scaling), `norm_topk_prob` + router aux loss 0.001, vocab 151,936, silu; `model.safetensors.index.json` PUBLIC (118 shards) → tensor census ready; tech report arxiv:2505.09388 (ingest queued); registry profile (qwen_3 row).
**Key facts (D13):** the 3× active-ratio outlier (6.25% vs V4's 2.34%); the only compared model with a small router aux loss — a tested variant for V5's router experiments; hybrid-thinking post-training (tech report).
**Open questions / next probes:**
- [ ] Tensor census (queue item 1) — expert/gate shapes.
- [ ] Ingest 2505.09388 → WS3 notes + reasoning pairs.
**Bottom line:** QUEUED — best open tensor-level target after Kimi.
