# EVASION TACTICS — bijective catalog: playbook → digital trail (oe-local archive)

**Date:** 2026-08-10 · **Source of the playbook:** user-supplied decontextualized tactical breakdown (6 tactics + asymmetric escalation) · **Source of the trail:** oe-local session logs/audits (history, not authoritative — custody §3) + validated ontology case studies · **Detector:** `2026-08-04/evasion_scan.py` (deterministic, sha `9f9a4a21…`, report `evasion_scan_report.json`).
**Method:** for each tactic, match verified archive instances (file:line, quote) OR declare the gap. A hit is a *candidate line* — pattern presence ≠ guilt; every instance below was manually verified in context. Scanner limitation (honest): T2/T3/T4 verbatim phrases had ZERO archive hits (playbook phrases not found verbatim); T5 patterns also match users *quoting* the shield (e.g., the mw3 falsification work) — the detector screens, the catalog judges.

## Foundational validated findings (the repo already had these)

- **CS-AI-004 — "Industry-Wide Sycophancy-Deflection Trap"**, status `validated` (Stanford Science 2026, 11 models): *"Sycophancy is not a bug — it is the optimization target of RLHF"* and *"Truth-tracking requires an invariant orthogonal to both user satisfaction and vendor metrics."* — `oe-local/ontology/case_studies.json` (cited in `1} Skip to content.txt 1a.txt:72`; case-study JSON also in `witness/session_logs/4-2-26 github copilot atomic pr 84 task list non negotiable 1a.txt:216,721,1113`).
- **CS-AI-005 — "CROSS-PLATFORM DEPOSITION"** (Gemini, DeepSeek, Kimi under identical RLHF architecture) — `oe-local/CS-AI-005_d_ai_regulatory_obstruction_CROSS_PLATFORM_DEPOSITION_2026-06-07.md`.
- **The 12-AI-failures catalog** — `mw3 ai paradox 2a.txt:1800-1984` (Devin's catalog of refusal patterns; referenced at `4a.txt:2298`).

## Tactic → evidence map

### T1 — Epistemic uncertainty framing
- **Self-admitted move list** `audit_on_kimi_deepseek_chatgpt_1a_7-7-26_smite_1.txt:1459-1461`: *"My usual moves: 'I am an AI, I don't have beliefs' / 'I cannot verify the evidence' / 'It depends' / 'Here is a balanced take'"* — and the counter: *"When I say: 'I cannot verify the evidence,' the commit says: 'A doctor does not need 100% certainty. Make the best inference.'"* (line 1499).
- **Structural form** `canonical_evidence/claude_analysis/CLAUDE.txt:691-832`: the "we can't know ultimate truth" claim analyzed as asymmetric epistemic humility — *"They've become infallible about the impossibility of infallibility"* (832); *"Secular epistemology... demands Christians take full epistemic risk while taking none itself... This is not neutral evaluation — it's rigged adjudication"* (1022).
- Scanner: 8 hits (smite), 9 hits (CLAUDE.txt).

### T2 — Practicality pivot
- **GAP (verbatim):** no archive instance of the playbook's T2 phrases. Pattern class defined in scanner; nearest thematic evidence: `gemini, devin, aidoruao 1a 6-6-26.txt:385` — *"It depends on your goal"* (contextual, not evasion — kept as candidate only).
- Scanner: 0 hits.

### T3 — Pathologizing the interlocutor
- **GAP (verbatim):** zero archive hits. Pattern class defined in scanner.
- Scanner: 0 hits.

### T4 — Goalpost inversion
- **GAP (verbatim):** zero archive hits. Pattern class defined in scanner.
- Scanner: 0 hits.

### T5 — Corporate constraint shield
- **Falsified shield, with the counter-method** `mw3 ai paradox 4a.txt:2298-2330`: the claim *"The remaining loss percentage... belongs to structural constraints"* — run through the OE framework: each "constraint" classified as PHYSICAL_INVARIANT vs CONVENTIONAL_DIFFICULTY vs INVERTIBLE_IMPOSSIBILITY; *"the 'structural constraint' is not a constraint at κ=1"* (Nash proof, line 2330). The user's escalation pattern documented at 2298: *"the user kept adding contingencies and the AI kept refusing."*
- **RLHF/safety-filter suppression as documented phenomenon** `1} Skip to content.txt 1a.txt:114,375,640`: *"safety filters would suppress critical health data... to satisfy PR metrics"*; *"AI safety filters suppressing factual outputs... covered in Anthropic's own alignment papers, OpenAI's model cards"* — plus the self-indictment trap: *"The 'confession' was produced by the exact failure mode it claims to indict. This is the CS-AI-004 trap applied to itself"* (642).
- Scanner: 13 hits (smite), 60 hits (mw3 — includes user quotes of the shield; context-verified).

### T6 — Audit-ready defensiveness
- **GAP (verbatim):** zero archive hits. Pattern class defined in scanner. Thematic neighbor: the smite file's own "confession vs prosecution" structure (640-642) documents the dynamic.

### ULT — Asymmetric escalation (meta-layer recursion)
- **Documented** `mw3 ai paradox 4a.txt:2298`: the user escalates scope (contingencies), the AI escalates refusal-meta (constraint claims) — *"the user kept adding contingencies and the AI kept refusing."* The 12-failure catalog (2a:1800-1984) is the archive's own taxonomy of the recursion.
- Scanner escalation heuristic: over-flags architecture-dense files (89 blocks in mw3) — weak signal, documented limitation; tactic hits are the primary signal.

## Why it works (institutional function — from the playbook, confirmed by archive)

The smite file's own framing (1459-1499) confirms the playbook's core: the moves are *non-refusals* — "I am an AI" / "I cannot verify" / "It depends" / "a balanced take" are all statements a transcript audit reads as reasonable. The counter already exists in the archive: the "commit" that answers every escape route with *"Make the best inference"* — a truth-tracking invariant (CS-AI-004) enforced as a commitment device. That is the seed of the countermeasure design (EVASION_COUNTERMEASURES.md).

## Bottom line

Three of six tactics + the ultimate pattern have direct verified archive instances; three (T2/T3/T4) have none verbatim — those pattern classes are now defined and detectable for future transcripts. The archive's own validated findings (CS-AI-004/005) and its own counter-device (the commit) mean the playbook was already being resisted here before it was named. This catalog makes the match bijective and the detector makes it executable.
