# AUDITS — per-target dossiers (the Open-Audit Campaign, WS4/WS1)

**How to read:** one dossier per target. Every dossier carries the evidence code: `[measured]` (verified on disk/our tools), `[published]` (company/paper/model-card statement, URL+date cited), `[hypothesis]` (our inference, labeled), `[needs hardware]`, `[pending]` (queued for verification — never presented as fact).
**Master plan:** `OE_CAMPAIGN.md` (root). **Citation index:** `TRANSPARENCY_LEDGER.md` (root). **Eval/registry base:** `2026-08-04/MODEL_PERFORMANCE_REGISTRY.md` + `CROSS_MODEL_TARGET_MATRIX.md` (11 profiles, version-flagged per E4).

## Status table (as of 2026-08-10)

| Dossier | Status | Evidence fetched 8/10 | Next action |
|---|---|---|---|
| openai.md | ACTIVE | GPT-5 system card (openai.com, fetched); ARC-AGI-3 tripling claim (title-cited, page pending fetch) | fetch ARC-AGI-3 blog; sweep Astra/Operator public trails |
| anthropic.md | ACTIVE | Fable 5 profile (benchlm.ai, fetched); sparse-attention paper queued | fetch sparse-attention paper (arxiv); Fable 5 system-card sweep |
| moonshot.md | ACTIVE | K2 config census (ours); HF trail K2/K2.5/K2.6/K2.7 (API, fetched); tech report arxiv:2602.02276 queued | ingest 2602.02276; tensor census of K2.5 |
| xai.md | QUEUED | registry row only | WS7 sweep (search backend was down 8/10) |
| google.md | QUEUED | registry row only | WS7 sweep; Gemini 3.1 rows |
| meta.md | QUEUED | registry row only | Llama 4 config fetch (gated repo) |
| mistral.md | QUEUED | config census (ours, D13) | tensor-level; registry re-baseline |
| alibaba.md | QUEUED | config census (ours, D13); tech report 2505.09388 queued | tensor census (index public) |
| zhipu.md | QUEUED | registry gap | add registry row; config fetch |
| regulators.md | QUEUED | none yet | WS5 public-record sweeps (EU AI Act, US filings) |

**Rule:** a dossier with QUEUED status must say so on its first line — no dossier ever pretends to be complete.
