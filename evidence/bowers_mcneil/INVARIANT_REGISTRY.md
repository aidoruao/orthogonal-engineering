# INVARIANT REGISTRY — Bowers vs McNeil
_Generated: 2026-04-01T10:14:17.256932Z_
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
**Statement:** The institutional-layer draft alleges that video and weather sources jointly show
no rain at the time of the stop, falsifying a rain-based pretext.
**Source:** Devin/NotebookLM addon request; pending ingestion of bodycam/cellphone footage and weather data
**Falsification Criteria:** A time-aligned source set showing rain at the stop time/location or the absence of the cited video
**Inelasticity:** 0.92 (expected once source-ingested)
**Status:** PENDING_PRIMARY_SOURCE_INGESTION

## INV-009: DISTRACTION STRIKE = BATTERY
**Statement:** If the SAO memo uses the term 'distraction strike' for the window-punch incident,
that phrase functions as semantic laundering rather than a neutral description.
**Source:** Devin/NotebookLM addon request; pending SAO memo text
**Falsification Criteria:** Memo text showing no euphemistic reclassification or showing the physical act was not a punch/battery analogue
**Inelasticity:** 0.93 (expected once memo is ingested)
**Status:** PENDING_PRIMARY_SOURCE_INGESTION

## INV-010: 7-TO-0 RACIAL DISPARITY
**Statement:** The institutional-layer draft alleges a 7-to-0 racial disparity in Bowers headlight citations,
which would function as a statistical anchor for discriminatory-pattern analysis.
**Source:** Devin/NotebookLM addon request; pending citation-record ingestion
**Falsification Criteria:** Citation data disproving the proposed ratio or showing materially different demographics
**Inelasticity:** 0.89 (expected once records are ingested)
**Status:** PENDING_PRIMARY_SOURCE_INGESTION

## INV-011: SAO DID NOT INTERVIEW VICTIM
**Statement:** The institutional-layer draft alleges the SAO declined prosecution without interviewing the victim.
**Source:** Devin/NotebookLM addon request; pending case-file/public-records confirmation
**Falsification Criteria:** Interview log, memorandum, or case-file note establishing that the victim was interviewed
**Inelasticity:** 0.74
**Status:** UNDER_INVESTIGATION

## INV-012: SAO MEMO OMITS EXCULPATORY EVIDENCE
**Statement:** The institutional-layer draft alleges the SAO memo omits weather and video evidence, creating a lossy-compression problem.
**Source:** Devin/NotebookLM addon request; pending full memo + evidence comparison
**Falsification Criteria:** Memo text preserving the material weather/video facts without omission
**Inelasticity:** 0.90 (expected once memo is ingested)
**Status:** PENDING_PRIMARY_SOURCE_INGESTION

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

---

## Cross-References to Repository Invariants
- **INV-003-CORRESPONDENCE-ANCHOR** (INVARIANTS.md): This case anchors AI-to-reality correspondence
- **INV-003-DEEPSEEK-SELF-CORRECTION** (DeepSeek Turns 6+8): DeepSeek's admission is a self-falsifying statement
- **INV-007-REALITY-ANCHOR** (INVARIANTS.md): Arrest record and SAO decision are reality anchors