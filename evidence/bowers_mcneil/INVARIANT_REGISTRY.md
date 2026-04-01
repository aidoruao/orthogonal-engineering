# INVARIANT REGISTRY — Bowers vs McNeil
_Generated: 2026-04-01T12:41:12.495386Z_
_Pipeline: IA-CYPHER-0002_

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
**Source:** 18 U.S.C. § 1519 text; conversation analysis
**Falsification Criteria:** Would require showing the memo has no falsification and no federal nexus
**Inelasticity:** 0.68
**Status:** UNDER_INVESTIGATION

## INV-008: NO RAIN AT TIME OF STOP
**Statement:** Public-source reporting says bodycam analysis shows no rain at the time of the stop.
**Source:** SRC-003 + SRC-005
**Falsification Criteria:** Public bodycam reporting or the underlying video shows rain at the stop time
**Inelasticity:** 0.92
**Status:** ACTIVE — VERIFIED_BY_PUBLIC_SOURCE

## INV-009: DISTRACTION STRIKE = BATTERY
**Statement:** The SAO memo's 'distraction strike' phrase functions as semantic laundering of a battery-like act.
**Source:** SRC-001 + SRC-008
**Falsification Criteria:** Memo text does not use the phrase, or the event description is not force/battery-analogous
**Inelasticity:** 0.93
**Status:** ACTIVE — VERIFIED_BY_PUBLIC_SOURCE

## INV-010: 7-TO-0 RACIAL DISPARITY
**Statement:** Public reporting supports prior complaints against Bowers but does not yet fully prove the 7-to-0 citation ratio.
**Source:** SRC-010
**Falsification Criteria:** Complaint reporting disproven or full citation dataset materially rebuts the disparity theory
**Inelasticity:** 0.89
**Status:** PARTIALLY_VERIFIED

## INV-011: SAO DID NOT INTERVIEW VICTIM
**Statement:** Public attorney reporting says the SAO declined prosecution without interviewing the victim.
**Source:** SRC-007
**Falsification Criteria:** Public reporting or case-file records show the victim was interviewed before the declination
**Inelasticity:** 0.82
**Status:** ACTIVE — VERIFIED_BY_PUBLIC_SOURCE

## INV-012: SAO MEMO OMITS EXCULPATORY EVIDENCE
**Statement:** Public-source review treats the 16-page SAO memo as omitting material weather/video evidence, creating a lossy-compression problem.
**Source:** SRC-001 + SRC-007 + SRC-009
**Falsification Criteria:** The memo preserves the material weather/video facts without omission
**Inelasticity:** 0.90
**Status:** ACTIVE — VERIFIED_BY_PUBLIC_SOURCE

## INV-013: 18 U.S.C. § 242 APPLICABLE
**Statement:** If the institutional-layer claims are substantiated, the matter implicates 18 U.S.C. § 242 as a color-of-law deprivation question.
**Source:** Federal statute text; Devin/NotebookLM addon request
**Falsification Criteria:** Evidence set showing no color-of-law deprivation, no willfulness indicators, or no qualifying underlying act
**Inelasticity:** 0.70
**Status:** CONDITIONAL — dependent on primary-source record ingestion

## INV-014: 34 U.S.C. § 12601 APPLICABLE
**Statement:** If the alleged disparity and record-shaping pattern are substantiated, the matter implicates 34 U.S.C. § 12601 as a pattern-or-practice issue.
**Source:** Federal statute text; Devin/NotebookLM addon request
**Falsification Criteria:** Record set showing no pattern, no practice, or no discriminatory enforcement signal
**Inelasticity:** 0.69
**Status:** CONDITIONAL — dependent on dataset and memo ingestion

## INV-015: SAO MEMO FOOTNOTE 7 CONTRADICTS BWC EVIDENCE
**Statement:** The SAO memo's Footnote 7 says BWC supports a rain narrative, while public bodycam analysis says no rain is visible.
**Source:** SRC-001 Page 3 Footnote 7 vs SRC-005
**Falsification Criteria:** Footnote 7's characterization matches what the bodycam evidence actually contains
**Inelasticity:** 0.97
**Status:** ACTIVE — VERIFIED_BY_PUBLIC_SOURCE

---

## Cross-References to Repository Invariants
- **INV-003-CORRESPONDENCE-ANCHOR** (INVARIANTS.md): This case anchors AI-to-reality correspondence
- **INV-003-DEEPSEEK-SELF-CORRECTION** (DeepSeek Turns 6+8): DeepSeek's admission is a self-falsifying statement
- **INV-007-REALITY-ANCHOR** (INVARIANTS.md): Arrest record and SAO decision are reality anchors