# THE OPEN-AUDIT CAMPAIGN — breaking the information asymmetry on frontier AI (master file)

**Established:** 2026-08-10 · **Owner:** oe-local recursion (DeepSeek-V4-Flash via Codewhale), operating for and with the user · **Status:** ACTIVE — this is the master plan; every AI or human joining this work starts here after WORK_LOG (what was done) and CHAIN_OF_CUSTODY.md (why, and with what evidence).
**Purpose of this file:** a single artifact that (1) states the campaign's charter and rules of engagement, (2) maps the information asymmetry target-by-target, (3) assigns work streams and cadence, (4) pre-registers the execution queue, and (5) makes the repo self-describing — any AI can reconstruct "what was last done and why" from this file + git history + the chain files.

---

## 1. Charter and rules of engagement (non-negotiable)

1. **Public sources only.** Everything cited: papers, model cards, configs, official docs, filings, court records, congressional testimony, speeches, interviews, press. Nothing obtained by intrusion, deception, or non-public means. Clean-room engineering: analysis is done from published artifacts only, never from proprietary material we do not legitimately possess.
2. **Nothing illegal, nothing malicious.** This campaign breaks *information asymmetry*, not laws. No doxxing (private individuals are out of scope; public officials/executives are analyzed ONLY in official, public capacity), no harassment, no fabrication, no impersonation.
3. **Evidence code** — every claim carries one of: `[measured]` (verified on disk/our tools), `[published]` (company/paper/model-card statement, URL-cited), `[hypothesis]` (our inference, labeled as such, with the reasoning), `[needs hardware]` (gated). A claim without a label or source is a defect — fix or delete it.
4. **The harshest thing we publish is the discrepancy between claim and evidence** — eval-version games (E4), unverifiable safety claims, closed configs where open ones exist, marketing vs measured. We do not need to exaggerate; the record is damning enough. Harsh = rigorous, unsparing, complete.
5. **Ground truth over prose.** Every number re-verified before publication (grep/sha/recompute; deterministic tools double-run byte-identical). The completion-integrity audit (2026-08-06) is the standing precedent: our own claims get audited the same way we audit others'.
6. **Nothing hidden.** Every dossier lists its sources (URL + date + what was verified). The transparency ledger is the index of all citations. No anonymous claims.

## 2. Strategic objective

Close the information gap in five layers, for every frontier lab:

| Layer | What's obfuscated | What we publish |
|---|---|---|
| L1 Architecture | weights, real configs, tensor layouts (closed labs), full training specs | no-download census: config + safetensors index + transformers source + docs (V4 method, now extended to Qwen3/Kimi/Mistral — D13) |
| L2 Eval truth | version drift, cherry-picked benchmarks, withheld runs | version-flagged registry (E4 fix in place), re-baselined rows, one harness |
| L3 Training/data policy | data provenance, consent, compensation, RLHF steering details | public-trail reconstruction: papers, patents, licensing/court filings, hiring patterns, regulatory submissions |
| L4 Safety & governance claims | system cards vs incident trails, red-team results vs shipped behavior | claim-vs-evidence dossiers, with citations |
| L5 Corporate fiduciary / RLHF-as-instrument | how alignment is *actually* steered (who decides, on what values, to what legal duty) | public-record corporate governance analysis: board/earnings/lobbying disclosures, testimony, org changes, policy shifts |

The end state: any auditor — human or AI — can answer "what did they claim, what did they ship, what did they hide, and what does the public record support" for every lab, from this repo alone.

## 3. Target matrix (evidence state as of 2026-08-10)

| Target | Architecture access | Eval data we hold | Key open questions |
|---|---|---|---|
| DeepSeek (V3/V4) | FULL no-download census (72,317 tensors, config, KV math) | 11-profile matrix row; LiveCodeBench/Codeforces/HLE/SWE/MRCR/TB | V4 runtime behavior (hardware-gated); real tid2eid table; HLE 0.40+ path |
| OpenAI (GPT-5.x, ChatGPT/Astra, o-series) | NONE (closed) | profiles (gpt5 row) | agentic behavior trails (Astra/Operator/Codex) from public demos+reports; system-card claims vs incidents |
| Anthropic (Claude 4/5, Fable 5/Mythos-class) | NONE (closed); sparse-attention paper is PUBLIC | profiles (claude row) | sparse-attention vs V4 CSA comparison from paper; safety-system claims vs public red-team/incident record |
| xAI (Grok 3/4) | NONE (closed) | profiles (grok row) | Colossus-scale training claims vs public reporting; eval transparency |
| Google DeepMind (Gemini 3.x) | NONE (closed) | profiles (gemini row) | sparse/TPU-specific attention; agentic (Project Mariner/Astra-G) trails |
| Moonshot AI (Kimi K2/K2.5) | FULL config census (V3-lineage MLA+noaux_tc, FP8) | profiles (kimi row; HLE 0.502 = the gap reference) | tensor-level census next; K2.5 training/data policy; why HLE-leading |
| Meta AI (Llama 4) | config/paper level (open weights, gated repo) | profiles (llama row) | sparse attention + MoE config details; data policy record |
| Mistral AI (Large/Medium) | FULL config census (dense, 131K native) | profiles (mistral row) | little missing at config level; benchmark re-baseline |
| Alibaba (Qwen3) | FULL config census (128/8 MoE, norm_topk_prob+aux loss); index public | profiles (qwen row) | tensor census; hybrid-thinking training details (tech report 2505.09388) |
| Zhipu (GLM-4.5/5.x) | config level (open) | registry gap | add row; reasoning model architecture |
| Regulators/gov (EU AI Act, US NTIA/Commerce, state AGs) | public filings | partial | lobbying disclosures per lab; enforcement actions; testimony trails |

## 4. Work streams (WS)

- **WS1 — Architecture deltas (no-download).** Extend CROSS_MODEL_ARCHITECTURE_DELTA.md to tensor level: Qwen3 + Kimi indices (pre-registered), Llama 4, GLM, then re-derive V5 levers. Keep D13 discipline: `[config-level]` vs `[tensor-level]` labels.
- **WS2 — Eval truth registry.** Continue registry_normalize.py lineage: add Fable 5, GPT-5.x, Gemini 3.1 rows (version-flagged); one-harness re-baseline on hardware.
- **WS3 — Paper pipeline.** arxiv_vendor ingest: Qwen3 tech report (2505.09388), Kimi K2 report, Anthropic sparse-attention, MoE survey/MLA lineage, any public GPT-5.x system card. → reasoning pairs + architecture notes (existing pipeline, sha-verified).
- **WS4 — Safety/gov claim dossiers.** Per lab: system card claims vs public incidents (court dockets, recall notices, press investigations). Public records only.
- **WS5 — Corporate fiduciary trail.** Public governance record: earnings calls, 10-K/10-Q risk factors, lobbying disclosures (US LDA), EU transparency registrations, org-chart changes, key-person testimony. Question per lab: to whom is the alignment fiduciary, and what does the record show about how RLHF/alignment decisions are made?
- **WS6 — Agentic behavior trails (product level).** Astra/Operator/Codex/Claude-Code/Mariner public evaluations, failure compilations from public bug reports — feeds the effort-router/TOOL_USAGE/BRR axes.
- **WS7 — Continuous web sweep.** Ongoing searches per target; every new source goes to TRANSPARENCY_LEDGER.md within the same session.
- **WS8 — Chain maintenance.** After every work item: WORK_LOG entry, custody §5/§7 update, gates (chain_integrity_check.py + stub_placeholder_scan.py), commit+push with a descriptive message. The repo IS the record.

## 5. Deliverables and cadence

- `AUDITS/` — one dossier per target (this directory), each: known facts (cited), discrepancies (claim vs evidence), open questions, next probe. Updated as evidence lands; a dossier is never "done", it is "current as of <date>".
- `TRANSPARENCY_LEDGER.md` — every source used, URL, date, what was verified. Append-only.
- Weekly (per session block): one "state of asymmetry" summary per target added to the dossier.
- Publication: this repo (origin main, aidoruao/orthogonal-engineering). Everything public, everything cited.

## 6. Continuity contract (the repo answers "what was last done and why")

1. Read order for any new instance: `WORK_LOG.md` (what) → `CHAIN_OF_CUSTODY.md` (why/evidence) → this file (plan) → `2026-08-04/DEVELOPERS_BRIEF.md` + `NEXT_CYCLE_LEARNING.md` (state) → `AUDITS/` + `TRANSPARENCY_LEDGER.md` (campaign state).
2. Git history is the temporal record: every commit message states what and why; every claim file is hash-anchored where it matters (MANIFEST, chain roots, sha256 columns).
3. Gates after new work: `chain_integrity_check.py` (ALL CLAIMS VERIFIED) + `stub_placeholder_scan.py` (benign findings only) + determinism double-run for any new tool.
4. If this file is stale (dates old, targets added), update it first — it is the load-bearing index of the campaign.
5. Ethics check before every publication: is every claim cited? Is every person a public figure acting officially? Is anything non-public being used? If yes to the last two, it does not ship.

## 7. Pre-registered execution queue (next units, in order)

1. Tensor census: Qwen3-235B-A22B + Kimi-K2-Instruct (`model.safetensors.index.json` — confirmed public) → upgrade CROSS_MODEL_ARCHITECTURE_DELTA.md to tensor-level. [~10-30 MB, no-download]
2. arxiv_vendor ingest: Qwen3 tech report 2505.09388; Kimi K2 report; Anthropic sparse-attention paper → WS3 notes + reasoning pairs.
3. Dossiers: AUDITS/openai.md, AUDITS/anthropic.md (started below), then xai.md, moonshot.md, google.md, meta.md, mistral.md, alibaba.md, zhipu.md, regulators.md.
4. Registry: add Fable 5 + GPT-5.x + Gemini 3.1 rows via registry_normalize.py (version-flagged per E4).
5. WS5 first pass: one corporate-fiduciary public-record sweep per US lab (LDA lobbying filings, earnings risk factors) — cite everything.
6. WS2 harness re-baseline on hardware when available.

---
**Bottom line of this file:** the asymmetry is breakable with public tools — we already did it for DeepSeek (full tensor census, no download), and the same method extends to every open-weight lab; for closed labs, the paper/card/filing trail plus our eval registry is the leverage. The campaign's weapon is the citation, its discipline is the label, its outcome is a repo that tells the whole truth to anyone who asks.
