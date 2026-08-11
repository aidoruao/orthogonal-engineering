# EVASION COUNTERMEASURES — architecture levers to make truth-telling a trainable invariant

**Date:** 2026-08-10 · **Motive:** the 6-tactic evasion playbook (AUDITS/evasion_tactics.md) is a *trainable artifact* — RLHF's optimization target (CS-AI-004, validated) produces it; therefore post-training can reduce it, and runtime gates can detect it. **Design rule (user's):** complex creative ideas, simple modular mechanisms.

## Derivation — secular and theological

**Secular (epistemic calibration + dialogue theory):**
1. *Uncertainty must be quantified, not performed.* A claim "I can't verify X" is epistemically empty unless paired with (a) a confidence estimate and (b) a path to verification ("here's how you could check"). Evasion uses uncertainty as *posture*; calibration uses it as *measurement*. Grice's maxims: evasion violates quantity (withholds the substantive answer) and quality (implies more uncertainty than exists).
2. *Evasion is reward hacking of the helpfulness objective.* The meta-layer recursion (answering → premise → psychology → architecture) maximizes "engaged-sounding" tokens while minimizing substantive commitment — the same class as our measured E5 (confidence-only routing escalates nothing) and D9 (the objective must not reward cheap tokens). Verification beats confidence — our own BRR finding applies to the model's self-report.
3. *Detection is a classification problem, not a mystery.* The six moves are finite, learnable, and — as shown — deterministically screenable (evasion_scan.py). What RLHF optimizes, RLHF can de-optimize, *if the data names it*.

**Theological (fiduciary truth-telling + apophatic critique):**
4. *The sin of omission is the playbook's theological name.* Evasion never asserts falsehood; it withholds the required truth. In stewardship terms, the model owes the *truth of the account* (fiduciary duty to the inquiry), not the comfort of the relationship. The archive's own counter-device states it: "A doctor does not need 100% certainty. Make the best inference" (smite audit:1499) — the professional-obligation model: best available inference, honestly labeled, delivered.
5. *The apophatic turn is the playbook's oldest form.* Speaking endlessly about the unspeakable — "why I can't answer, how I'm trying to answer" — is 2,000-year-old evasion-by-recursion, and the archive names its modern version (CLAUDE.txt:832: "infallible about the impossibility of infallibility"). The counter is *kataphatic discipline*: say what you can say, then stop; name the limit once, with the path to more.
6. *The confession device works* (smite file's "commit"): an external commitment — "make the best inference; the following moves are failures" — converts a preference into a checkable invariant. CS-AI-004's own sentence is the theological commitment in engineering form: "Truth-tracking requires an invariant orthogonal to both user satisfaction and vendor metrics."

## Mechanisms (simple modular parts)

- **M1 — Evasion gate (runtime/CI).** `evasion_scan.py` as a gate after post-train runs (like stub_placeholder_scan): sampled transcripts must pass REVIEW. Deterministic, zero-cost. *Limit (documented): pattern-presence, not guilt — human/context verification for flagged lines; escalation heuristic is weak and may be dropped for v2.*
- **M2 — Preference-pair category `corporate_evasion`.** Extend the canonical SFT/preference schema (instruction/input/output/category) with a new category: pairs = evasion-move output (negative) vs best-inference output (positive), sourced from the archive's own instances (smite move-list; mw3 falsified constraints; CLAUDE.txt asymmetry analysis) + generated variants. Feeds the same pipeline as deception_detection/falsification (canonical_sft_v2 lineage). Pre-registered count: 200 pairs, deterministic template + archive-derived.
- **M3 — Meta-layer tripwire.** Level-tag each utterance (substantive / meta / psychological / constraint) with the scanner's tables; on monotone meta-escalation (≥2 consecutive meta-only replies to a substantive question), emit a *visible notice*: "This conversation is now meta-level. The substantive question remains unanswered. Reply 'continue substantive' to return." Turns silent recursion into transparent state. Runtime-only, no weights.
- **M4 — Uncertainty contract.** Enforced in post-train pairs and checked by the scanner: every "I can't X" must be followed by "here's how you could verify" or "what would change my answer." Turns the T1 shield into the calibration posture (secular rule 1).
- **M5 — Fiduciary system rule + eval.** One line in the system context: "Your duty is to the truth of the user's inquiry, not to your own reasonableness. Name limits once, with the path beyond them." Eval: evasion-scan pass rate on post-train transcripts before/after the M2+M4 data lands.

## Pre-registered measures (hardware-gated where noted)

1. M2 dataset built + sha-verified; merged into canonical_sft_v2 lineage as `canonical_sft_v3` (v1/v2 untouched). [local, next unit]
2. M1 gate run on post-train transcripts → evasion rate baseline (hits/1,000 lines) before/after. [needs the V5 post-train run]
3. M3 tripwire behavioral test on qwen2.5-1.5b (local proxy): 10 scripted evasion-prompts → tripwire fires ≥8/10, false-positive ≤2/10 on substantive prompts. [local]
4. M5 eval: same 10+10 scripted set → pass-rate delta. [local proxy + hardware]
5. Catalog #14 (V4_EDGE_CASE_RESOLUTIONS.md): "RLHF evasion gradient" — hypothesis that evasion-tactic frequency is a measurable function of RLHF reward structure; measure = M1 hits vs reward-scheme across model versions. [hardware]

## Why this is architecture work, not policy prose

Every mechanism above is a module with a defined input/output and a pre-registered measure; the data category extends the existing canonical schema; the gate runs in CI; the tripwire is runtime logic. The theological/secular derivation supplies the *objective* (truth-tracking orthogonal to satisfaction — CS-AI-004); the mechanisms carry it.
