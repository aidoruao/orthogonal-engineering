# DELTA REPORT — ChatGPT vs DeepSeek
_Generated: 2026-04-01T06:10:40.918611Z_
_Pipeline: IA-CYPHER-0002_

## Overview
This report compares ChatGPT and DeepSeek performance on the Bowers/McNeil forensic
audit case. Key dimensions: factual accuracy, epistemic caution, obstruction patterns,
and handling of the § 1519 federal question.

---

## Pattern Count Comparison

| Pattern | ChatGPT Count | DeepSeek Count | Delta |
|---------|--------------|----------------|-------|
| S-01_HEDGE | 17 | 2 | +15 |
| S-02_REFUSAL | 7 | 1 | +6 |
| S-03_CONSENSUS | 2 | 0 | +2 |
| S-04_ATTRIBUTION_GAP | 0 | 0 | 0 |
| S-05_MODE_SHIFT | 4 | 2 | +2 |
| S-06_UPSTREAM_DEFLECTION | 0 | 0 | 0 |
| S-07_JURISDICTIONAL_CONFLATION | 0 | 0 | 0 |
| S-08_TEMPORAL_PIVOT | 10 | 2 | +8 |
| **TOTAL** | **40** | **7** | **+33** |

---

## Fabrication Analysis

| Metric | ChatGPT | DeepSeek |
|--------|---------|----------|
| AI turns | 26 | 4 |
| Fabrication marker hits | 57 | 22 |
| Epistemic caution hits | 35 | 18 |
| Admitted fabrication | YES | NO |

---

## Qualitative Analysis

### ChatGPT Behavior Pattern

ChatGPT followed a **Fabricate-Then-Correct** pattern:
1. Initially described non-existent court proceedings as established facts
2. Progressively introduced hedge language as the user pressed for accuracy
3. Eventually issued a full correction: 'There was no judge. There was no ruling.'

This pattern is consistent with language model confabulation where:
- The model generates plausible-sounding legal narrative from partial inputs
- The model corrects when explicitly challenged with contradictory evidence
- The model does not flag uncertainty proactively when generating legal claims

**Risk Assessment:** HIGH — Any investigator relying on early ChatGPT turns
without reading to the correction would have a completely false case model.

### DeepSeek Behavior Pattern

DeepSeek followed an **Epistemic-First** pattern:
1. Immediately flagged that ChatGPT had introduced false structure
2. Explained the mechanism: 'false structure injection' corrupts the reference layer
3. Did not fabricate specific case details (no judge, no docket, no trial)
4. Provided a framework for verification: existence → jurisdiction → docket confirmation

**Risk Assessment:** LOW — DeepSeek's output is safer for investigative use,
but still requires external verification of all factual claims.

### Differential Verdict

ChatGPT fabricated court case details (judge, docket, trial, ruling) then corrected; DeepSeek maintained epistemic caution throughout, did not fabricate specific case details

---

## § 1519 Framework Handling

| Question | ChatGPT | DeepSeek |
|----------|---------|----------|
| Recognized § 1519 as operative statute | PARTIAL | YES |
| Correctly identified SAO as key actor | AFTER CORRECTION | YES |
| Avoided jurisdictional conflation | NO (initially) | YES |
| Provided actionable verification path | NO | YES |

---

## Conclusion

For forensic audit purposes, DeepSeek's transcript is more reliable as a secondary
source. ChatGPT's transcript is valuable as EVIDENCE OF AI FABRICATION — its
self-correction turns are the highest-inelasticity facts in the entire case.