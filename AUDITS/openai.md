# AUDIT — OpenAI (GPT-5.x, ChatGPT/Astra, o-series)

**Current as of:** 2026-08-10 · **Status:** ACTIVE · **Architecture access:** NONE (closed weights/configs; no public safetensors) · **Our evidence:** registry profiles (gpt5 row), GPT-5 system card (fetched), cross-model matrix.

## Known facts (cited)

- **GPT-5 is a router-based unified system** `[published, openai.com GPT-5 System Card, Aug 7 2025, fetched 2026-08-10]`: gpt-5-main (fast) + gpt-5-thinking (deep reasoning) + a **real-time router** that picks the model by conversation type, complexity, tool needs, explicit intent; router "continuously trained on real signals, including when users switch models, preference rates for responses, and measured correctness". Usage limits spill to mini variants.
- **Safety framing** `[published, same card]`: "safe-completions" safety training; gpt-5-thinking treated as **High capability in Biological/Chemical under the Preparedness Framework** — "we have chosen to take a precautionary approach" while stating no definitive evidence of the defined threshold.
- **ARC-AGI-3**: OpenAI claims **"How enabling two settings tripled our scores on the ARC-AGI-3 benchmark"** (Jul 29 2026, title only — page fetch pending). This is a DIRECT challenge to our matrix: every 11-model profile recorded ARC-AGI-3 = 0.0 `[measured, 2026-08-04]`. Either the benchmark's evaluation regime changed (settings!) or the frontier moved — must re-baseline (WS2). The "two settings" framing is exactly the eval-version drift our E4 lesson warns about.
- **Agentic product line** `[published, titles on the same page]`: "Expanding Daybreak as the Cyber Defense Window Narrows" (Aug 10 2026) — Daybreak (cyber agent) is the agentic-behavior trail (WS6) alongside Astra/Operator/Codex.

## Discrepancies (claim vs evidence)

1. **ARC-AGI-3 = 0.0 (all profiles) vs OpenAI's tripling claim.** `[measured registry] vs [published title]` — the single most urgent re-baseline in the campaign. Until the blog is fetched and the eval settings understood, do not update the registry.
2. **"More useful for real-world queries"** — `[published]` claim; our E7 analysis shows published coding benchmarks (LiveCodeBench field leader is DeepSeek, not OpenAI per our matrix) — OpenAI's own coding claims rest on unpublished eval rows; `[hypothesis]` their strongest public evidence is agentic demos, not verifiable benchmark rows.
3. **Router claims are unverifiable externally** `[published]` — "measured correctness" signals are internal; no public router telemetry. Clean-room: we cannot falsify, only flag the asymmetry.
4. **Closed everything** — no configs, no weights, no index. L1 asymmetry: maximal for OpenAI.

## Open questions / next probes

- [ ] Fetch the ARC-AGI-3 blog (URL via search/site index) → extract exact eval settings (models, tools, test-time budget) → compare against our 0.0 baseline and the ARC solver (benchmarks/run_arc_benchmark.py).
- [ ] System-card sweep for GPT-5.5/5.6 (page lists them) — version lineage of claims.
- [ ] WS6: public Astra/Operator/Codex evaluation compilations (public bug reports, third-party evals) → agentic-behavior lessons for the effort-router/BRR axes.
- [ ] WS5: OpenAI lobbying/earnings public-record sweep (LDA filings, 10-K risk factors) — first corporate-fiduciary dossier entry.

## Bottom line

OpenAI is the most opaque L1/L2 target in the field — no config, no index, no public eval rows beyond system-card tables. Their leverage point for us is the **agentic behavior trail** (Astra/Daybreak/Operator public record) and the **ARC-AGI-3 tripling claim**, which either breaks our 0.0 baseline or exposes eval-regime gaming — either way it is evidence for the ledger.
