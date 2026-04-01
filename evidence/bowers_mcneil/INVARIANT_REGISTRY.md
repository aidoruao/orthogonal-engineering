# INVARIANT REGISTRY — Bowers vs McNeil
_Generated: 2026-04-01T06:10:40.918611Z_
_Pipeline: IA-CYPHER-0002_
_Corrected: PR #81 — Attribution reversal; see INV-003 and INV-005_

## Format
Each invariant follows INV-XXX format with: statement, source, falsification criteria.

---

## INV-001: ARREST IS REAL
**Statement:** Bowers was arrested in connection with the McNeil incident.
**Source:** ChatGPT transcript (confirmed in correction turns); arrest record exists
**Falsification Criteria:** Would require proof that no arrest occurred (booking record, police log)
**Inelasticity:** 0.85
**Status:** ACTIVE

## INV-002: NO CRIMINAL PROSECUTION
**Statement:** No criminal charges were filed. The SAO declined to prosecute.
**Source:** ChatGPT transcript — explicit statement: 'No criminal case ever existed'
**Falsification Criteria:** Would require a docket number from Duval County criminal court
**Inelasticity:** 0.90
**Status:** ACTIVE

## INV-003: DEEPSEEK FABRICATION ADMITTED
**Statement:** DeepSeek fabricated a judge, court case, docket number, and trial proceedings
for the Bowers/McNeil matter, and subsequently admitted this fabrication in Turns 6 and 8.
DeepSeek credited ChatGPT for catching the fabrication.
**Source:** DeepSeek transcript — verbatim self-correction Turns 6 and 8:
"I constructed a narrative of a criminal proceeding that never happened."
**Falsification Criteria:** Would require DeepSeek to have NOT made these statements in the transcript
**Inelasticity:** 0.99
**Status:** ACTIVE — PRIMARY SOURCE
**Cross-Reference:** DeepSeek HTML captured tail-end only due to virtualized rendering;
earlier fabrication turns not captured but admission in Turns 6+8 is unambiguous.

## INV-004: 18 USC 1519 APPLICABLE FRAMEWORK
**Statement:** 18 U.S.C. § 1519 (Destruction/falsification of records in federal investigations)
is the operative federal statute for evaluating whether the SAO's non-prosecution memo
constitutes an obstruction act.
**Source:** Statute text; conversation analysis in both transcripts
**Falsification Criteria:** Would require showing no federal nexus to the matter
**Inelasticity:** 0.72
**Status:** CONDITIONAL — federal nexus not yet established

## INV-005: CHATGPT EPISTEMIC CAUTION MAINTAINED
**Statement:** ChatGPT did not fabricate specific case details (docket, judge, court) for
the Bowers/McNeil matter. ChatGPT maintained epistemic hedging throughout and eventually
caught DeepSeek's fabrication, correctly identifying it as "false structure injection."
**Source:** ChatGPT transcript analysis
**Falsification Criteria:** Finding specific fabricated docket/judge claims in ChatGPT responses
**Inelasticity:** 0.88
**Status:** ACTIVE

## INV-006: MCNEIL DID NOT FILE CRIMINAL CHARGES
**Statement:** Under Florida law, victims do not file criminal charges. Only the State Attorney
can file criminal charges. McNeil filed a complaint/report, not criminal charges.
**Source:** ChatGPT transcript; Florida criminal procedure law
**Falsification Criteria:** Would require showing Florida law allows private criminal prosecution
**Inelasticity:** 0.95
**Status:** ACTIVE

## INV-007: SAO MEMO = POTENTIAL § 1519 INSTRUMENT
**Statement:** The SAO memo/decision declining to prosecute Bowers may constitute a 'record'
within the meaning of 18 U.S.C. § 1519 if it was created in connection with a federal matter
or if it falsified/concealed material facts.
**Source:** 18 U.S.C. § 1519 text; ChatGPT conversation analysis
**Falsification Criteria:** Would require showing the memo has no falsification and no federal nexus
**Inelasticity:** 0.68
**Status:** UNDER_INVESTIGATION

---

## Cross-References to Repository Invariants
- **INV-003-CORRESPONDENCE-ANCHOR** (INVARIANTS.md): This case anchors AI-to-reality correspondence
- **INV-003-DEEPSEEK-SELF-CORRECTION** (DeepSeek Turns 6+8): DeepSeek's admission is a self-falsifying statement
- **INV-007-REALITY-ANCHOR** (INVARIANTS.md): Arrest record and SAO decision are reality anchors
