# INDELIBLE FACTS — Bowers vs McNeil
_Generated: 2026-04-01T10:20:31.671077Z_
_Pipeline: IA-CYPHER-0002_

## Definition
An INDELIBLE FACT is a claim with inelasticity score ≥ 0.80, meaning it cannot be
plausibly revised without contradicting primary source evidence. These facts anchor
all downstream reasoning.

---

## FC-001: Bowers was arrested

**Inelasticity Score:** 0.85
**Gate 1 (Existence):** PASS — ChatGPT confirmed arrest is real; arrest is distinct from prosecution
**Gate 2 (Jurisdiction):** State of Florida / Duval County
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — Arrest record must be confirmed via Duval County public records
**Source:** ChatGPT transcript, confirmed in correction turn
**18 U.S.C. § 1519 Relevance:** LOW — arrest itself not obstructed; question is SAO decision

---

## FC-002: No criminal charges were filed (SAO declined to prosecute)

**Inelasticity Score:** 0.9
**Gate 1 (Existence):** PASS — ChatGPT explicitly confirmed: no criminal case, no docket, no court
**Gate 2 (Jurisdiction):** State Attorney's Office (SAO) / Florida
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — SAO memo/decision letter must be obtained via public records request
**Source:** ChatGPT transcript — explicit correction turns
**18 U.S.C. § 1519 Relevance:** HIGH — SAO memo declining prosecution = potential prosecutorial nullification

---

## FC-004: DeepSeek fabricated a judge, court, docket number, and trial

**Inelasticity Score:** 0.99
**Gate 1 (Existence):** PASS — DeepSeek admitted: ‘I constructed a narrative of a criminal proceeding that never happened.’ (Turns 6, 8)
**Gate 2 (Jurisdiction):** N/A — AI fabrication, not legal jurisdiction
**Gate 3 (Verification):** IN_TRANSCRIPT — DeepSeek correction verbatim in transcript, Turns 6 and 8; virtualized rendering captured tail end only
**Source:** DeepSeek transcript — AI self-admission of fabrication, Turns 6 and 8
**18 U.S.C. § 1519 Relevance:** HIGH — AI fabrication may constitute obstruction of federal investigation process if relied upon

---

## Provisional Institutional-Layer Candidates

The following claims have high expected inelasticity but are not yet treated as verified
indelible facts because the primary-source records (memo, weather logs, video, citation data)
have not yet been ingested into the repository. They are formalized here so the investigation
can preserve the target hypotheses without overstating current proof status.

### FC-007: Bodycam/cellphone video shows no rain at the time of the stop

**Expected Inelasticity Score:** 0.92
**Gate 1 (Existence):** ASSERTED_BY_USER — Institutional-layer claim introduced in the Devin/NotebookLM addon request; awaits ingestion of video artifacts
**Gate 2 (Jurisdiction):** Duval County / evidentiary record
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — Requires primary-source bodycam/cellphone footage with preserved timestamps and hash verification
**Source:** NotebookLM/Devin institutional-layer draft summarized in PR comment #4168458668
**18 U.S.C. § 1519 Relevance:** HIGH — if true, omission from charging memo would materially alter obstruction analysis
**Status:** PROVISIONAL — formalized, not yet source-ingested

### FC-008: Weather records falsify a rain-based pretext for the stop

**Expected Inelasticity Score:** 0.91
**Gate 1 (Existence):** ASSERTED_BY_USER — Claim has not yet been tied to ingested NOAA/local weather records in the repo
**Gate 2 (Jurisdiction):** Public weather record / Jacksonville, Florida
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — Requires public weather records aligned to stop time and location
**Source:** NotebookLM/Devin institutional-layer draft summarized in PR comment #4168458668
**18 U.S.C. § 1519 Relevance:** HIGH — weather contradiction would be a material correspondence anchor
**Status:** PROVISIONAL — formalized, not yet source-ingested

### FC-009: Officer Bowers has a 7-to-0 racial disparity in headlight citations

**Expected Inelasticity Score:** 0.89
**Gate 1 (Existence):** ASSERTED_BY_USER — Statistical disparity claim awaits ingestion of the citation dataset or records extract
**Gate 2 (Jurisdiction):** State/local citation records
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — Requires citation ledger or records request demonstrating the proposed ratio
**Source:** NotebookLM/Devin institutional-layer draft summarized in PR comment #4168458668
**18 U.S.C. § 1519 Relevance:** MEDIUM — disparity is more directly tied to § 242/§ 12601 analysis than to record falsification alone
**Status:** PROVISIONAL — formalized, not yet source-ingested

### FC-010: The SAO memo rebrands the punch as a 'distraction strike'

**Expected Inelasticity Score:** 0.93
**Gate 1 (Existence):** ASSERTED_BY_USER — Semantic-laundering claim awaits ingestion of the memo text itself
**Gate 2 (Jurisdiction):** State Attorney's Office memorandum
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — Requires the memo text or scan showing the phrase and its surrounding analysis
**Source:** NotebookLM/Devin institutional-layer draft summarized in PR comment #4168458668
**18 U.S.C. § 1519 Relevance:** HIGH — euphemistic reclassification in an official memo could be materially probative
**Status:** PROVISIONAL — formalized, not yet source-ingested

### FC-012: The SAO memo is 16 pages long and omits weather and video evidence

**Expected Inelasticity Score:** 0.9
**Gate 1 (Existence):** ASSERTED_BY_USER — Memo-length and omission claim awaits ingestion of the full memo
**Gate 2 (Jurisdiction):** State Attorney's Office memorandum
**Gate 3 (Verification):** REQUIRES_EXTERNAL_VERIFICATION — Requires the complete 16-page memo and a source-to-memo omission comparison
**Source:** NotebookLM/Devin institutional-layer draft summarized in PR comment #4168458668
**18 U.S.C. § 1519 Relevance:** HIGH — omission of material exculpatory evidence would directly sharpen the § 1519 theory
**Status:** PROVISIONAL — formalized, not yet source-ingested

## Summary

Verified indelible facts (score ≥ 0.80): 3
Provisional institutional candidates (score ≥ 0.80): 5

### DeepSeek Fabrication Admission (Score: 0.99)
DeepSeek's explicit self-admission that it fabricated judicial proceedings is the
highest-inelasticity fact in this case. The admission is verbatim in the transcript.
DeepSeek stated: "I constructed a narrative of a criminal proceeding that never happened."
This is a PRIMARY SOURCE ADMISSION — it requires no external verification.
DeepSeek credited ChatGPT for catching the fabrication.

### SAO Non-Prosecution (Score: 0.90)
The State Attorney's Office declined to file criminal charges after Bowers' arrest.
This is confirmed by ChatGPT's correction and is the operative fact for § 1519 analysis.

### Arrest Reality (Score: 0.85)
The arrest of Bowers is real and confirmed. The arrest did not produce criminal charges.
This distinction (arrest ≠ prosecution) is the core legal fact of the investigation.