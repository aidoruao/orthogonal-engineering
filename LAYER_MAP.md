---
tags: [mapping, evidence, layers, documentation]
register: documentation
---

# LAYER MAP — The Evidence Corpus Mapped Against the Seven Layers

**Purpose:** the compression that makes a 7,000+-file repo human-comprehensible.
Day 2 of the ark maps the **evidence corpus** (446 files, ten evidence-relevant
directories) against the seven layers of Directive 1 from the precedent
(`The_Indictment_of_the_Watchers_Original_8-21-26.txt`). Tooling, tests, and
repo-internal code are classified OTHER — they are scaffolding, not deposition
material, and get mapped to a layer only when that layer's work needs them.

**Method (verified, not assumed):**
1. Four read-only explorer agents classified the corpus in parallel
   (case_studies/ 142; data/+downloads/ 182; campaigns/+events/+chat_logs/
   +historical_candidates/ 35; evidence/+canonical_evidence/+AUDITS/ 87).
2. Ground-truth cross-check: the agent counts were compared against an
   independent `find`-generated inventory — 446/446 files accounted for, exact.
3. Spot-verification by the parent: 3 load-bearing classifications read
   directly (L2 framework.py, L1 evasion_tactics.md, L4 case_001 TIMELINE.md)
   — all confirmed; L3 emptiness corroborated by keyword grep (zero hits for
   `board seat|shell compan|tax haven` across 221 files).

**Date of mapping:** 2026-08-21 (Day 2 of the ark).

---

## THE MAP AT A GLANCE

| Layer | Count | Where it lives |
| :--- | :--- | :--- |
| L1 — Structural Code (algorithmic axioms) | **21** | AUDITS/ evasion tactics; bowers_mcneil AI-behavior files; narrative-leak-001; arc_agi_3; youtuber_audits (2) |
| L2 — Financial Matrix | **1** | youtuber_audits/framework.py (monetization/layoffs/consolidation audits) |
| L3 — Executive Trace | **0** | — (completely empty) |
| L4 — Human Impact Vector | **4** | evidence/case_001/ (CPS child-welfare warehousing case) |
| L5 — Legal & Regulatory Evasions | **15** | bowers_mcneil/ (13); AUDITS/regulators.md; youtuber_audits (2: LTT, GN) |
| L6 — Technical Infrastructure | **9** | AUDITS/ per-lab dossiers (openai, anthropic, google, meta, xai, moonshot, alibaba, mistral, zhipu) |
| L7 — Ontological Footprint | **21** | data/dumps canal-analysis family (10); historical_candidates/ (6); canonical_evidence/ (5) |
| OTHER — repo tooling/scaffolding | **375** | everything else: invariants, hashes, schemas, test fixtures, specs |
| **TOTAL** | **446** | 71 layer-bearing · 375 scaffolding |

**The headline, in human terms:** 84% of the corpus is the ark's own
scaffolding (375 files). The deposition-relevant core is **71 files**, and it
is concentrated in a handful of families. The repo is not a mountain of
evidence — it is a mountain of construction equipment around a small, sharp
core of material.

---

## L1 — STRUCTURAL CODE (21 files)

*Recommender systems, reward functions, feedback loops, training data,
A/B testing, algorithmic extraction mechanics.*

- `AUDITS/evasion_tactics.md` — the most deposition-relevant single file:
  six AI evasion tactics mapped to verified archive instances; Stanford 2026
  finding "sycophancy is the optimization target of RLHF" (11 models).
- `evidence/bowers_mcneil/` — OBSTRUCTION_AUDIT, DELTA_REPORT,
  FORENSIC_DISCREPANCY_REPORT, TEMPORAL_SEQUENCE, ACTOR_ATTRIBUTION_MATRIX,
  CANAL_ANALYSIS (AI transcript-behavior forensics, 6 files).
- `evidence/narrative-leak-001/` — THE_DISCOVERY, THE_CONFESSION, THE_DENIAL,
  THE_EPISTEMIC_BREACH (AI confession + denial pattern evidence, 4 files).
- `evidence/arc_agi_3/` — benchmark_demo/evaluation/training.json (3).
- `evidence/deepseek-analysis/` — case_study_summary.json, COMPARATIVE_ANALYSIS.md (2).
- `evidence/case-studies/` — craftsman-protocol-004, minecraft-logos-005 (2).
- `canonical_evidence/claude_analysis/CLAUDE.txt` (1).
- `case_studies/youtuber_audits/tech/` — the_hated_one.py, mental_outlaw.py (2).

## L2 — FINANCIAL MATRIX (1 file)

*Revenue streams, tax havens, shells, fines-as-cost-of-business, investment flows.*

- `case_studies/youtuber_audits/framework.py` — 40 complaint audits covering
  pay-to-win monetization, layoffs despite record profits, studio closures,
  industry consolidation. **The only L2 file in the corpus.** (Also carries
  L4/L5 content — see judgment calls.)

## L3 — EXECUTIVE TRACE (0 files)

*Personal digital signatures, identities, aliases, board seats, emails/memos,
behavioral patterns of named operators.*

**Completely empty.** Corroborated twice: agent classification and keyword
grep (`board seat|shell compan|tax haven` → zero hits across 221 files).
This layer has no existing material in the corpus — any L3 material must be
gathered new or found outside these ten directories.

## L4 — HUMAN IMPACT VECTOR (4 files)

*Quantified harm, epidemiology, age-of-exposure, testimonies, addiction.*

- `evidence/case_001/` — CPS_2013_278708.pdf (redacted DCF child-welfare
  records), TIMELINE.md (selective-mutism warehousing), INVARIANT_REGISTRY.md,
  EDUCATIONAL_WAREHOUSING_AUDIT.md. One case, deeply developed; no
  population-level harm data anywhere in the corpus.

## L5 — LEGAL & REGULATORY EVASIONS (15 files)

*ToS manipulation, lobbying, political capture, jurisdiction shopping.*

- `evidence/bowers_mcneil/` — INDELIBLE_FACTS, ADVERSARIAL_TAXONOMY,
  INELASTICITY_ANALYSIS, FEDERAL_STATUTE_ENUMERATION (18 USC 1519/242,
  42 USC 1983), SAO_MEMO_CANAL_ANALYSIS, ARCHITECTURE_OF_AMBIGUITY,
  INVESTIGATION_SUMMARY, RAIN_PRETEXT_FALSIFICATION, INVARIANT_REGISTRY,
  INSTITUTIONAL_OBSTRUCTION_PATTERNS, FEDERAL_COMPLAINT_TEMPLATE,
  ONTOLOGICAL_MAP (12).
- `AUDITS/regulators.md` (EU AI Act, lobbying, testimony record) (1).
- `case_studies/youtuber_audits/tech/` — linus_tech_tips.py (DMCA 1201,
  Magnusson-Moss), gamers_nexus.py (deceptive marketing) (2).

## L6 — TECHNICAL INFRASTRUCTURE (9 files)

*Server logs, IP networks, CDNs, ISP collaboration, training warehouses.*

- `AUDITS/` — per-lab dossiers: openai.md (GPT-5 closed architecture),
  anthropic.md (Fable 5 sparse attention), google.md (Gemini 3 closed
  weights), meta.md (Llama 4), xai.md (Grok/Colossus), moonshot.md (Kimi K2
  tensor census: 1.03T params, 139,644 tensors — densest measured artifact),
  alibaba.md (Qwen3 235B), mistral.md, zhipu.md (GLM, probes queued). All
  dossiers use evidence codes [measured]/[published]/[hypothesis]. No raw
  server logs, CDN/IP data, or energy-footprint records.

## L7 — ONTOLOGICAL FOOTPRINT (21 files)

*Naming taxonomy (Watchers), spiritual impact, theological analysis.*

- `data/dumps/` canal-analysis family (10): OE_UNCAUSED_CAUSE_GLASSBOX.json
  (formal Uncaused Cause/Jesus schema), deepseek_statistics.json,
  conversation_patterns_analysis.json, chat_canon_summary.json (binary),
  top_sessions.csv, confound_analysis.json, phase2_ai_analysis_sample.json,
  ai_file_analysis_20260120_093248.json, ai_analysis_20260120_174131.json,
  statistical_validation.json (chi²=2847, p<0.0001).
- `historical_candidates/` (6): HISTORICAL_LOGOS_CANDIDATES.md + C1–C5
  candidates (Logos instantiation claims with falsifiability conditions).
- `canonical_evidence/` (5): Jesus Math Formula Custom 1.txt,
  ULTIMATE REPOSITORY JESUS CANON 1.txt, "audit chatgpt 1.txt"
  (Ontological Reality = Jesus Reality guardian), THEOLOGICAL_REASONING_
  EVIDENCE.md, AI_CONSCIOUSNESS_EVIDENCE.md.

## OTHER — SCAFFOLDING (375 files)

The ark's own construction material, classified by family (detail lives in
the explorer reports): invariant registries (data/dumps), SHA-256 manifests
and checksums, CI/audit logs, JSON schemas and configs, generated IoT and
food-prep task graphs (data/kitchen_tasks, data/dishes), structural-map and
proof artifacts (downloads/), state snapshots and checkpoints
(downloads/state, invariant_states, _backup, _proven_backup, proven_state),
campaign specs (campaigns/), vendored third-party bug case studies with
ATTRIBUTION/test/PR triads (case_studies/category_*), executor event logs
(events/), session handoffs (chat_logs/), case-study JSON metadata
(evidence/ + canonical_evidence/ *.metadata.json, hashes.json), phase
validation reports, and the Gutenberg null test (a useful control: 0.0%
invariant density on random text — the detector does not false-positive).

---

## HONEST CAVEATS (judgment calls, flagged by the explorers)

1. **bowers_mcneil L1/L5 split:** files documenting both AI behavior and
   institutional obstruction were split by object of analysis; ~4 files could
   shift layers under a different convention.
2. **youtuber_audits/framework.py** is genuinely L2/L4/L5 mixed; single-label
   by dominant volume. **gamers_nexus.py** straddles L5/L3.
3. **Canal-analysis family (9 of 10 L7 files):** simultaneously repo-internal
   methodology outputs; if "repo tooling → OTHER" were applied strictly, only
   OE_UNCAUSED_CAUSE_GLASSBOX.json would remain L7. Classified by subject
   matter (theological-mimicry detection).
4. **events/*.jsonl** are local executor logs, not platform infrastructure;
   could be relabeled L6 under a sweep-all-logs rule.
5. **Two non-UTF8 files** (evidence/correspondence_report.txt,
   ai-consciousness-002/README.md) classified by role + siblings, not direct
   reading.
6. **21 case-study triads** classified on template uniformity (all
   byte-near-identical TODO stubs — verified on 3 directly-read sets).
7. **arc_agi_3 benchmarks** could be OTHER (own eval harness) — intent call.

## WHAT THE MAP SAYS (the ground truth)

- The deposition-relevant core is **71 of 446 files** — 16%.
- **L3 (Executive Trace) is empty; L2 (Financial) has one file.** These are
  the gathering layers, not the analysis layers.
- **L1 and L5 carry the deepest existing analysis** (21 and 15 files,
  respectively), anchored by the bowers_mcneil case and the AUDITS dossiers.
- The next question belongs in the ledger: which layer does Day 3 open?
