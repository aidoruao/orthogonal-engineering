# HLE HARNESS SPEC — pre-registered eval for the next post-train cycle
**Date:** 2026-08-05 · **Agent:** DeepSeek-V4-Flash (Codewhale) · **Status:** spec only — execution `[needs hardware]`
**Purpose:** one harness that (a) re-baselines V4 on HLE with the same methodology the 11-profile registry used, resolving the version-mismatch caveat, and (b) tracks the #1 headroom target: HLE 0.348 (Flash max) / 0.377 (Pro max) → **0.40+** (Kimi 0.502 / Gemini 0.458 are the field benchmarks).

## 1. Task definition (locked)
- HLE-style: hard research-level multiple-choice questions, 10 options each, single correct index; requires multi-step reasoning + domain knowledge. Questions are held-out frontier items — no public leakage channel.
- Fields per item (JSONL): `id`, `domain` ∈ {mathematics, physics, cs, biology, chemistry, engineering}, `question`, `options` (list of exactly 10), `answer_index` (offline; never shipped with the eval set).
- Split: `dev` 50 items (sanity/smoke), `test` 250 items (scored; answer key kept off the run machine).

## 2. Protocol (locked, run on big hardware)
1. Model: Flash-0731 and Pro (and any candidate checkpoint) via the official runner (torchrun MP=4, fp4↔fp8) or vLLM `--trust-remote-code --moe-backend deep_gemm_mega_moe --kv-cache-dtype fp8`.
2. Decode: greedy (temperature 0), `max_tokens` 4096 per item, single completion.
3. **Effort ladder (this is the adaptive-effort telemetry, catalog #10):** run each item at all three effort levels — non-think, think, max — and score per level. Output: accuracy per level + tokens/query per level. Expected shape from measured baselines: 8.1 (non-think) → 34.8 (max) for Flash = 4.3× test-time scaling; the harness quantifies the *per-item* routing signal (low non-think confidence → escalate) that a query-adaptive effort router would use.
4. Scoring: exact `answer_index` match. Report per-domain and per-level; also report HLE-with-tools if the runner supports it (Pro 0.482 baseline — keep the same harness, note the variant).
5. Registry: append rows to `benchmarks/MODEL_PERFORMANCE_REGISTRY.md` (model, version sha, date, effort level, accuracy, tokens/query, domain breakdown). One harness for Flash AND Pro — this resolves the registry's version-mismatch caveat for HLE.

## 3. Density contract (CIIF applied)
- ρ_HLE = accuracy / storage GB, reported alongside raw accuracy: Flash at 158 GB vs Pro at 864.8 GB — the same score at 1/5 storage is a headline, not a footnote.
- Efficiency gate: the 0.40+ target must be met at ≤ 2× tokens/query on hard items only (the effort router's job), per the pre-registered contract in `V4_EDGE_CASE_RESOLUTIONS.md` #10.

## 4. Training-side connection (the closed loop)
- Training set: `canonical_sft_v2.jsonl` (7,373 rows — reasoning block now filled: math 147 / logic 137 / science 83 / domain_knowledge 2,257) + arxiv reasoning pairs (1,146) are the data axis; HLE is the eval axis. Every training milestone runs this harness; the delta tells whether the reasoning block moved the measured gap.
- Related gates: MRCR-1M (78.7 → 83+), LiveCodeBench hold-gate (≥ 91.6, never regress), Terminal Bench 2.1 (82.7 → 90+).

## 5. Files / layout (to materialize on the run machine)
- `benchmarks/hle/hle_items_dev.jsonl` (50) · `hle_items_test.jsonl` (250) · `run_hle.py` (decode + score + registry append) · `hle_answer_key.asc` (GPG-encrypted answer index; decrypt only in scoring, never on the decode host).
- **DEV SET MATERIALIZED 8/5 (locally, no hardware): `2026-08-04/hle_items_dev.jsonl` — 56 items, spec-format, sha `6eb5092c…`**, built by `hle_item_synthesizer.py` from the on-disk arxiv corpus (falsification template: paper's main result → identify the stated condition under which it fails; correct option = verbatim limitation, distractors = other papers' limitations, deterministic slot placement; 0 verification failures, 10-slot answer-index spread). Test set (250) remains `[needs hardware/curation]` — extend the same synthesizer with more paper categories or team-sourced frontier items.
- Run bookkeeping: every run writes `hle_run_<model>_<sha>_<date>.json` (raw per-item results, tokens/query, config snapshot) — the registry row is derived, never hand-entered.

## 6. Honest limits
- The spec is the contract, execution is hardware-gated; **the dev set now exists** (56 verifier-keyed items, deterministic). If the team has its own HLE source, this spec is format-compatible; if not, the synthesizer extends to more categories — answer keys remain verifier-constructed (no LLM self-grading).
