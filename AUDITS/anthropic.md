# AUDIT — Anthropic (Claude 4/5, Fable 5 / Mythos-class)

**Current as of:** 2026-08-10 · **Status:** ACTIVE · **Architecture access:** NONE (closed); **one exception: the sparse-attention paper is public** (fetch queued) · **Our evidence:** registry profiles (claude row), Fable 5 public profile (BenchLM, fetched).

## Known facts (cited)

- **Claude Fable 5** `[published, BenchLM profile, data as of Aug 10 2026, fetched 2026-08-10]`: released Jun 9 2026; proprietary reasoning model; **1M context**; BenchLM score 82.8/100, **rank #2 of 216**; coding category **#2/133** (79.5/100, 99th percentile); agentic **#3/133** (75.3/100, 98th percentile); pricing $10 input / $50 output per M tokens (cached $1). **34 source-displayable benchmark rows across 381 tracked slots** — i.e., the public evidence covers under 9% of tracked benchmarks.
- **Public-evidence gap** `[published, same profile]`: Reasoning, Math, Knowledge, Multilingual, Multimodal, Instruction-following are **NOT ranked** for Fable 5 — "the public category table does not assign it a rank there" (evidence threshold not met). The model marketed as "reasoning" has no ranked public math/reasoning rows in this tracker. That is the asymmetry in its purest form: flagship claim, thin public eval trail.
- **Sparse attention is public** `[hypothesis→pending]`: Anthropic published sparse-attention work (2025) — directly comparable to DeepSeek V4's CSA/HCA hybrid (custody §4). Fetch and diff: cost model, indexer analog, KV math vs our 6 GB @1M. This is the one architecture-level window into a closed lab.

## Discrepancies (claim vs evidence)

1. **"Reasoning" flagship with unranked reasoning/math public rows** — `[published profile]` vs the marketing category. Not a falsification (absence of evidence ≠ evidence of absence) — but the asymmetry is documented, which is the campaign's job.
2. **1M context vs our KV math** `[published] vs [measured, ours]`: V4 achieves 1M with ≈6 GB fp8 KV via CSA/HCA. Anthropic's 1M claim has no public KV/cost figures; if their sparse attention is comparable, the V5 comparison gets a real peer; if not, the claim is unquantifiable. Fetch the paper.
3. **Safety-system claims** (system cards, interpretability research) vs public incident/red-team record — WS4 sweep queued; nothing asserted until sources land.

## Open questions / next probes

- [ ] Locate + fetch sparse-attention paper (do NOT guess arxiv id; use search when backend is up or arxiv API by title) → add to WS3 pipeline + CROSS_MODEL_ARCHITECTURE_DELTA.md as the first closed-lab architecture datapoint.
- [ ] Fable 5 / Mythos-5 system card sweep (Anthropic site) — safety claims, eval methodology, context-window engineering.
- [ ] Registry: add Fable 5 row (version-flagged per E4) using the 11 published rows — do not import BenchLM aggregates as ground truth; store row-level with source URLs.
- [ ] WS5: Anthropic's corporate-fiduciary public record (benefit-corp status, public statements on AI governance, testimony).

## Bottom line

Anthropic is closed at L1 like OpenAI, but leaks more at L3/L4 (papers, interpretability, safety docs). The campaign's two highest-value targets: (a) the sparse-attention paper as a real architecture comparator for V5's CSA work, (b) the Fable-5 public-evidence gap as the ledger's cleanest "claim vs trail" example.
