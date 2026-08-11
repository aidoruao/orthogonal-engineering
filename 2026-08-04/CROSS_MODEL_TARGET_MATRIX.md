# Cross-Model Target Matrix — where V4 stands vs the field, and what to target
**Date:** 2026-08-04 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Sources:** oe-local `benchmarks/model_profiles/` (11 profiles), V4-Flash-0731 + V4-Pro READMEs, this session's measurements.
**Caveat (honest):** the profiles registry and the V4 READMEs use *different benchmark versions* (SWE_Bench vs SWE Verified; LiveCodeBench_v6 vs LiveCodeBench; MMLU-Pro 0.606 vs 86.2; GPQA 0.5051 vs 88.1 — the same name, clearly different eval methodology). Comparisons below are **directional**, and the registry itself needs re-baselining on V4 with one consistent harness — that is part of the checklist.

## 1. Standings by category (V4 vs field, directional)

**HLE (hardest reasoning) — the single biggest measured gap:**
- Kimi K2.5 0.502 · Gemini 3 Pro 0.458 · GPT-5.2 0.455 · Claude Opus 4.5 0.382 · V3.2 0.351 · Grok 3 0.334
- **V4-Flash max 0.348 / Pro max 0.377 → behind Kimi by ~13–15 points.** Target: 0.40+ (between GPT and Claude) in the next cycle; HLE-with-tools: V4-Pro 0.482 vs Kimi-class ~0.5 — same gap.

**BrowseComp (web agentic):**
- Kimi 0.749 · Devin 0.73 · GPT 0.658 · Gemini 0.524
- **V4-Flash max 0.732 / Pro max 0.834 → Flash is ~2 pts behind Kimi; Pro is ahead of the entire field.** Keep Pro-class behavior in the Flash line.

**SWE (code agentic):**
- GPT 0.825 · Claude 0.793 · Devin 0.79 · Kimi 0.768 · Gemini 0.758 · V3.2 0.721
- V4: SWE Verified 0.790 (Flash max) / 0.806 (Pro max) — mid-pack, ~3.5 behind GPT. Target: 0.83+.

**LiveCodeBench:**
- GPT 0.882 · V3.2 0.833 · Kimi 0.850 · Gemini 0.841
- **V4-Flash 0.916 / Pro 0.935 — already the field leader** (directional: v6 vs current). Hold, don't regress.

**Knowledge (MMLU-family):** V3.2 0.871 vs GPT 0.902 / Gemini 0.891 / Claude 0.887 — ~3 pts behind; V4 numbers unpublished (registry update item). MMLU-Pro: V3.2 0.606 vs GPT 0.784 / Claude 0.752 — bigger gap, but V4 README shows 86.2/87.5 on its own version — re-baseline needed.

**Math:** AIME: GPT 1.0 / Kimi 0.961 / Gemini 0.935 vs V3.2 0.892 (V4 unpublished); HMMT: V4 94.8/95.2 (README) vs field 0.912–0.973 — near-top. Codeforces: V4 3052/3206 (README) — front-tier.

**ARC-AGI-3 — universal frontier, not a regression:** **0.0 for all 11 profiles** (only Devin 0.05); profile note: "LLM-only score pending official eval". **First team to publish a real V4 ARC-AGI-3 number sets the reference** — worth prioritizing on big hardware. oe-local's own **symbolic ARC solver** (`benchmarks/run_arc_benchmark.py` + `axioms/arc_solver.py`) is verified working this session (10/10 demo tasks, Merkle-anchored proofs) — the symbolic complement for hybrid eval (LLM proposes, solver verifies).

## 2. Headroom ranking (targets for the next cycle, biggest gap first)

1. **HLE 0.348 → 0.40+** (gap to Kimi ≈ 15 pts) — data: arxiv_vendor papers + canonical mathematical_proofs + combined_v4–v7 logic/math blocks (small — needs expansion); **now expanded: `arxiv_reasoning_pairs.py` materializes 1,146 deterministic claim-decomposition + falsification pairs (math 143 / logic 133 / science 78) from the on-disk corpus, sha-verified, merged into `canonical_sft_v2.jsonl` (7,373 rows, 0 dupes)**; eval: HLE harness on the registry.
2. **BrowseComp (Flash line) 0.732 → 0.75+** (Pro already 0.834 — distill the behavior down) — data: agentic web tasks; eval: BrowseComp.
3. **SWE 0.790 → 0.83+** — data: generator code corpora + SWE-bench; the census (`expert_census.py`) tells which experts carry code.
4. **MMLU-family re-baseline + 3-pt gain** — the registry's version mismatch must be resolved first (one harness for all).
5. **ARC-AGI-3: publish the first V4 number** — any positive result is a reference point; the symbolic solver gives verification-grade proofs.
6. **LiveCodeBench: hold 0.916+** (already leader) — regression gate for every training milestone.

## 3. What this means for the kit

- The profiles registry is a **target-setting asset, not yet a measurement asset** — the eval layer's first job is re-baselining V4 on the same harness (checklist item).
- Category coverage mirrors the post-training data gaps already measured: HLE-class reasoning and knowledge are where both the *data* (4–5 unique math/logic pairs) and the *model* (15-pt HLE gap) are thinnest — one coherent story: build the reasoning data with arxiv_vendor + generator-scale synthetic proof corpora.

## 4. Artifacts

- `extract_profiles.py` — matrix extractor (re-runnable as profiles update)
- `DEEPSEEK_V3_TO_V4_DELTA.md` — lineage
- `POST_TRAINING_PREP.md` — updated with this matrix + the verified ARC solver
