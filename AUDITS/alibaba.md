# AUDIT — Alibaba (Qwen3 family)

**Current as of:** 2026-08-10 · **Status:** QUEUED (architecturally measured — config + tensor).
**Our evidence:** config census `[measured, 2026-08-07, commit 8efa6172…]` + **tensor census `[measured, 2026-08-10, model_census.py, census/qwen3_235b_a22b.json, sha da5b0dde…]`**: 36,945 tensors, **470,187,269,120 B total (≈235.1B params bf16)**, 94 layers / 128 experts / 8 active (6.25%), GQA 64/4 KV, 40,960 ctx native (no scaling), `norm_topk_prob` + router aux loss 0.001, vocab 151,936, silu; **0 speculation tensors (no MTP)**; 94 router tensors; **active params/token ≈14.7B = 2.1× V4**; KV footprint 48,128 dims/token (2.2× V4); shipped density 0.50 B/GB (vs V4 1.93); tech report arxiv:2505.09388 (ingest queued); registry profile (qwen_3 row).
**Key facts (D13 + CENSUS_REPORT):** the 3× active-ratio outlier; the only compared model with a small router aux loss; does not attempt long context (`rope_scaling: null`).
**Open questions / next probes:**
- [ ] Ingest 2505.09388 → WS3 notes + reasoning pairs.
- [ ] HLE/reasoning eval rows for Qwen3 (registry re-baseline).
**Bottom line:** QUEUED — tensor census DONE (queue item 1 partially complete); eval rows next.
