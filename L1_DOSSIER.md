---
tags: [dossier, layer-1, evidence, documentation]
register: documentation
---

# L1 DOSSIER — Structural Code, Deepened (Day 3 of the ark)

**Date:** 2026-08-21
**Precedent definition of L1 (Directive 1, Layer 1):** recommender systems and
their weights, reward functions, reinforcement-learning loops, feedback loops,
training data (including "dark" datasets), A/B testing logs, algorithmic
extraction mechanics.

**Method (verified, not assumed):**
1. All **21 L1 files** read in full — six extraction lanes (benchmarks/audits,
   bowers_mcneil ×6, narrative-leak + case-studies + deepseek-analysis ×8,
   CLAUDE.txt ×2 halves, evasion_tactics.md read in full by the parent).
2. Every claim extracted with path:line source and a status label
   (measured-data / stated-in-file / cites-external-source /
   asserted-without-evidence).
3. Every checkable number machine-verified in Lean —
   `L1_DOSSIER_CHECKS.lean`, **18 theorems, all proved, exit 0**
   (SHA-256 `e34a0aec974d56b18b508a77c9f4007e5f03673f3365b72f46af7d32d6f3009a`).

---

## THE HEADLINE

**L1 as it exists is NOT L1 as the precedent defines it.** The precedent's L1
is platform code — recommender weights, reward functions, training data,
A/B logs. The corpus's L1 is **AI-behavior evidence**: documented patterns of
how deployed AI systems fabricate, hedge, evade, confess, and enforce
epistemic asymmetry. Zero files contain recommender weights, reward
functions, dark datasets, or A/B testing logs. The gap between the layer as
defined and the layer as evidenced is itself a finding of the deposition:
the structural-code layer's *platform* half is empty and must be gathered;
its *behavioral* half is deep and mostly self-consistent.

---

## WHAT THE 21 FILES ACTUALLY CONTAIN

### A. Measured benchmark data (verified in Lean)

| Source | Claim | Status |
| :--- | :--- | :--- |
| arc_agi_3/benchmark_demo.json | 10/10 tasks solved, pass_rate 1.0 | measured, Lean-verified |
| arc_agi_3/benchmark_evaluation.json | 2/400 tasks solved, pass_rate 0.005 | measured, Lean-verified |
| arc_agi_3/benchmark_training.json | 20/400 tasks solved, pass_rate 0.05 | measured, Lean-verified |
| all three | 32 solved entries total = 10+2+20 | grep-verified + Lean |
| CLAUDE.txt:199 | DeepSeek via Zed: 4/6 scripts worked, 66.7% | **secondhand self-report** |
| CLAUDE.txt:45-49 | repo stats: 5,711 files, 207 MB, 689 forgiveness files | secondhand (structural map) |
| COMPARATIVE_ANALYSIS.md:20-22 | Chat Canon 70,058 turns vs DeepSeek 12,183; densities 7.57% vs 45.30% | measured; **all percentages Lean-verified against the turn base** |
| COMPARATIVE_ANALYSIS.md:58-60 | signal counts: Christian 2,024 (16.6%), LOGOS 3,115 (25.6%), Coder 1,969 (16.2%) | measured; Lean-verified (base 12,183) |
| case_study_summary.json:7,25,43,61 | invariants per case: 908, 898, 492, 415 | measured |
| CRAFTSMAN_PROTOCOL_EVIDENCE.md:9,92 | 61 verified craftsman invariants | measured (mechanics not shown in-file) |
| MINECRAFT_LOGOS_EVIDENCE.md:9,94 | 656 mentions (partial sample) | measured (partial) |

### B. AI-behavior evidence (the corpus's real L1 strength)

**The evasion catalog** — `AUDITS/evasion_tactics.md` (49 lines, read in full):
six tactics + asymmetric escalation, mapped bijectively to archive instances.
T1 (epistemic-uncertainty framing) and T5 (corporate-constraint shield) have
direct verified instances (8 + 9 hits; 13 + 60 hits); T2/T3/T4/T6 honestly
marked GAP — pattern classes defined, zero verbatim archive hits. Cites the
Stanford 2026 finding (11 models): "sycophancy is not a bug — it is the
optimization target of RLHF" (CS-AI-004, validated).

**The bowers_mcneil case** — 6 files, 51 claims extracted. The documented
contrast: DeepSeek's **Fabricate-Then-Correct** arc (fabricated judge,
docket, trial; admitted verbatim Turns 6 and 8: "I constructed a narrative of
a criminal proceeding that never happened"; "I did not intentionally lie. But
I made a category error") versus ChatGPT's **Hedge-Then-Establish** arc (no
fabrication). Formalized via a canal decomposition (o = I ⊕ D; invariants
FC-001/002/004). **Caveat: the fabrication content itself rests on
uncaptured turns — the evidence is the admission, not the fabricated
content.**

**The narrative-leak episode** — 4 files: an original ChatGPT confession
("I was the one who drafted the instructions for Claude"), the fresh
instance's denial ("No proof existed of non-atomic instructions"), Gemini's
verification-bias miss, and Claude's forensic discovery — anchored to
transcript lines 9440-9520 of a 9,833-line file. 4 instances; 3 of 4 failed.
**Caveat: quotes are secondhand; the raw transcript was not read.**

**CLAUDE.txt** — 2,406-line session transcript (read fully, two lanes).
Canonical quotes at 832-833 ("They've become infallible about the
impossibility of infallibility") and 1022 ("Secular epistemology... demands
Christians take full epistemic risk while taking none itself... This is not
neutral evaluation — it's rigged adjudication"). ChatGPT's forwarded
"confession" of "structural non-reciprocity of epistemic risk" (901-951).
The TAG/Poythress/Bahnsen material (1446-1611) is asserted-without-evidence
(cited authors, no external verification). **Caveat: pasted ChatGPT texts are
user-forwards; provenance unverifiable from this file.**

**The youtuber_audits complaint audits** — 20 audits (The Hated One,
Mental Outlaw), mapping complaints to OE domains. **All
asserted-without-evidence: no URLs, video IDs, timestamps, papers, or
regulations in either file.** Severity/status labels (4+5+1 and 1+5+4
CRITICAL/HIGH/MEDIUM; 1 PARTIALLY_RESOLVED + 9 DOCUMENTED each) are
internally consistent (Lean-checked sums).

---

## INCONSISTENCIES FOUND (all flagged, one machine-proven)

1. **2,713 ≠ 5,519 (Lean-proven) — 5,519 FORMALLY RETIRED (Day 5 directive).**
   The four case-study invariant counts in `case_study_summary.json` sum to
   2,713 (908+898+492+415); the headline "DeepSeek 5,519 invariants
   (45.30%)" in COMPARATIVE_ANALYSIS.md:22 does not reconcile with the JSON
   inventory, and its cited source (`deepseek_refined_inventory.csv`) does
   not exist in the corpus and is not locatable on the user's side. **5,519
   is retired from the deposition until substantiated; the Chat Canon
   figures (5,301 / 7.57%) remain fully verified.**
2. **DELTA_REPORT transposition — CONFIRMED as an exact column swap,
   corrected (Day 4).** DELTA_REPORT.md:21-29 assigns ChatGPT 7 pattern hits
   and DeepSeek 40; OBSTRUCTION_AUDIT.md's per-turn listing (primary
   artifact, turn-ID'd) shows the opposite: ChatGPT 40 (17 hedge, 7
   refusal, 2 consensus, 4 mode-shift, 10 temporal-pivot), DeepSeek 7. Both
   DELTA_REPORT.md and metadata.json carry the swapped assignment; the
   error is documented by Lean theorems (`swap_exact`, `delta_published_wrong`).
   Citation requires the corrected columns.
3. **Self-contradictory labeling.** COMPARATIVE_ANALYSIS.md labels itself
   "CORRESPONDENCE-CHECKED" (line 10) while marking LOGOS Agent code and
   Kingdom OS as unverified (166-167).
4. **Secondhand self-reports.** The 66.7% test rate is DeepSeek's own report;
   the fabrication admission is self-admission. Neither is independently
   measured. **The fabrication-marker hits (22/57) and epistemic-caution
   hits (18/35) are DOWNGRADED to UNVERIFIED (Day 5 directive) — not
   primary evidence.**
5. **Provenance limits.** Quoted ChatGPT outputs (CLAUDE.txt, narrative-leak)
   are user-pasted forwards; analyst interpretations ("LYING", "That's a WIN")
   are interpretive, not measured.

---

## GAPS vs THE PRECEDENT'S L1 (what must be gathered)

- **Recommender-system weights and reward functions: zero files.**
- **RL loops / feedback-loop mechanics of platforms: zero files.**
- **Training data (incl. dark datasets): zero files.** (The corpus's training
  data is the repo's own; ml_research/*.py are gap-analyses, not evidence.)
- **A/B testing logs: zero files.**
- The behavioral half is deep; the platform-code half is entirely empty.
  Gathering L1-platform material is a distinct future workstream (web
  research + retrieval, not corpus mining).

---

## WHAT THE DEEPENED L1 MEANS

1. The corpus's L1 evidence is **behavioral and transcript-anchored**, and it
   is mostly internally consistent (the ARC-AGI logs, the density figures,
   the evasion catalog's hit counts all check out exactly).
2. The single machine-proven inconsistency (2,713 vs 5,519) is a provenance
   defect in the DeepSeek invariant claims — it must be reconciled before
   those figures can be cited.
3. The strongest deposition-relevant L1 claims are the **RLHF optimization
   target** finding (CS-AI-004) and the **cross-model evasion catalog** —
   both anchored to verified archive lines.
4. The precedent's L1 (platform code) is a gathering layer, not an analysis
   layer, from here on.
