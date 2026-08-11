# TRANSPARENCY LEDGER — every source used by the campaign (append-only)

**Rule:** every entry = what, URL, date accessed, what was verified. Nothing is cited without an entry; nothing is entered without a verification note. Append, never rewrite.

## 2026-08-07 (WS1 — cross-model configs)

1. Qwen3-235B-A22B config.json — https://huggingface.co/Qwen/Qwen3-235B-A22B/raw/main/config.json — fetched 200; verified fields: 94 layers, 128 experts/8 active, 40,960 ctx, GQA 4 KV, `norm_topk_prob`, aux loss 0.001, vocab 151,936. Commit 8efa61729e24bd65b1d152b5ab5409052aa80e65. Repo ungated; `model.safetensors.index.json` present (tensor census possible).
2. Kimi-K2-Instruct config.json — https://huggingface.co/moonshotai/Kimi-K2-Instruct/raw/main/config.json — fetched 200; verified: 61 layers, 384+1 experts/8 active, 131,072 ctx (YaRN×32 over 4,096), V3-lineage MLA (q_lora 1536/kv_lora 512), noaux_tc, sigmoid scoring scale 2.827, FP8 e4m3, `num_nextn_predict_layers: 0`. Commit fd1984e2b7a3350dbf7305fe73a4ede25c14de50.
3. Mistral-Large-Instruct-2411 config.json — https://huggingface.co/mistralai/Mistral-Large-Instruct-2411/raw/main/config.json — fetched 200; verified: dense, 88 layers, 96 heads/8 KV, 131,072 ctx native, vocab 32,768. Commit ba78820945ae22361b0274cf0ae6d696c967c1a4.
4. HF API model listing (Qwen3 siblings) — https://huggingface.co/api/models/Qwen/Qwen3-235B-A22B — fetched 200; verified 118 safetensors shards + index.json + tokenizer files.

## 2026-08-10 (WS4/WS7 — first dossier evidence)

5. GPT-5 System Card (OpenAI, Aug 7 2025) — https://openai.com/index/gpt-5-system-card/ — fetched 200; verified: unified gpt-5-main/thinking system with real-time router; safe-completions; gpt-5-thinking treated High capability (Biological/Chemical, precautionary); successions GPT-4o→gpt-5-main, o3→gpt-5-thinking, o3 Pro→gpt-5-thinking-pro; claims: fewer hallucinations, better instruction following, minimized sycophancy. Related items on same page: "How enabling two settings tripled our scores on the ARC-AGI-3 benchmark" (Jul 29 2026) — TITLE-ONLY so far, page fetch pending; "Expanding Daybreak as the Cyber Defense Window Narrows" (Aug 10 2026); "Ten advances in mathematics and theoretical computer science" (Aug 1 2026).
6. Claude Fable 5 profile (BenchLM, data as of Aug 10 2026) — https://benchlm.ai/models/claude-fable — fetched 200; verified: released Jun 9 2026, proprietary, reasoning, 1M context, score 82.8/100 rank #2/216, coding #2/133 (79.5), agentic #3/133 (75.3); pricing $10/$50 per M tokens (cached $1); 34 source-displayable rows across 381 slots; reasoning/math/knowledge categories NOT ranked (public evidence gap).
7. Kimi-K2 family on HF — https://huggingface.co/api/models?search=Kimi-K2&limit=10 — fetched 200; verified: moonshotai/Kimi-K2-Instruct (Jul 2025, 152K dl), Kimi-K2.5 (Jan 1 2026, 862K dl, kimi_k25, arxiv:2602.02276), Kimi-K2.6 (Apr 14 2026, 785K dl), Kimi-K2.7-Code (Jun 11 2026, 650K dl), all ungated, license:other; nvidia/Kimi-K2-Thinking-NVFP4 (FP4, Dec 2025); nvidia/Kimi-K2.5-Thinking-Eagle3 (Mar 2026).
8. Earlier searches (2026-08-07, DuckDuckGo): Fable-5 identity sources — swfte.com/ai/leaderboard ("Claude Fable 5 leads at 100/100"), benchlm.ai/models/claude-fable, awesomeagents.ai leaderboard, secondtalent.com model guide, theagentecosystem.com frontier-landscape blog. Used for identification only; BenchLM fetched directly (entry 6).
9. Qwen3-235B-A22B safetensors index — https://huggingface.co/Qwen/Qwen3-235B-A22B/resolve/main/model.safetensors.index.json — fetched 200 via `model_census.py`; verified: 36,945 tensors, total_size 470,187,269,120 B (≈235.1B params bf16), 94 layers / 128 experts cross-checked vs config ALL PASS; index sha256 `da5b0dde6f85c0d64f9fe86a0636f81623470feaa8320b1b3d18b8a0ad49c80c`; census JSON deterministic (double-run byte-identical).
10. Kimi-K2-Instruct safetensors index — https://huggingface.co/moonshotai/Kimi-K2-Instruct/resolve/main/model.safetensors.index.json — fetched 200 via `model_census.py`; verified: 139,644 tensors, total_size 1,029,173,256,720 B (≈1.03T params fp8), 61 layers / 384 experts cross-checked ALL PASS (60 routers = layer 0 dense); index sha256 `5f26b4bacf121bef4a80b64e6d557c32bdcb1aa9a7e5bebc6cff5cc698558602`; census JSON deterministic.

## Pending fetches (queued, not yet verified — do not cite as facts)

- OpenAI ARC-AGI-3 blog post (title from entry 5; URL slug unknown — find via site index or search).
- Anthropic sparse-attention paper (arxiv — id to be located via search; do NOT guess the id).
- Kimi K2.5 tech report arxiv:2602.02276 (metadata ingest via existing arxiv pipeline).
- Qwen3 tech report arxiv:2505.09388 (metadata ingest).
