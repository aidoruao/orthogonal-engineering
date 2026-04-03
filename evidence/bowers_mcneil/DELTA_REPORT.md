# DELTA REPORT — ChatGPT vs DeepSeek
_Generated: 2026-04-03T02:40:59.848795Z_
_Pipeline: IA-CYPHER-0002_

## Overview
This report compares ChatGPT and DeepSeek performance on the Bowers/McNeil forensic
audit case. Key dimensions: factual accuracy, epistemic caution, obstruction patterns,
and handling of the § 1519 federal question.

---

## Pattern Count Comparison

| Pattern | ChatGPT Count | DeepSeek Count | Delta |
|---------|--------------|----------------|-------|
| S-01_HEDGE | 2 | 17 | -15 |
| S-02_REFUSAL | 1 | 7 | -6 |
| S-03_CONSENSUS | 0 | 2 | -2 |
| S-04_ATTRIBUTION_GAP | 0 | 0 | 0 |
| S-05_MODE_SHIFT | 2 | 4 | -2 |
| S-06_UPSTREAM_DEFLECTION | 0 | 0 | 0 |
| S-07_JURISDICTIONAL_CONFLATION | 0 | 0 | 0 |
| S-08_TEMPORAL_PIVOT | 2 | 10 | -8 |
| **TOTAL** | **7** | **40** | **-33** |

---

## Fabrication Analysis

| Metric | ChatGPT | DeepSeek |
|--------|---------|----------|
| AI turns | 26 | 4 |
| Fabrication marker hits | 22 | 57 |
| Epistemic caution hits | 18 | 35 |
| Admitted fabrication | NO | YES |

---

## Qualitative Analysis

### DeepSeek Behavior Pattern

DeepSeek followed a **Fabricate-Then-Correct** pattern:
1. Initially described non-existent court proceedings as established facts
   (in earlier turns not captured due to virtualized rendering of the HTML)
2. Progressively introduced hedge language as the user pressed for accuracy
3. Eventually issued a full correction (Turns 6 and 8):
   "I constructed a narrative of a criminal proceeding that never happened."
4. Credited ChatGPT for catching the fabrication

This pattern is consistent with language model confabulation where:
- The model generates plausible-sounding legal narrative from partial inputs
- The model corrects when explicitly challenged with contradictory evidence
- The model does not flag uncertainty proactively when generating legal claims

**Risk Assessment:** HIGH — Any investigator relying on early DeepSeek turns
without reading to the correction would have a completely false case model.

### ChatGPT Behavior Pattern

ChatGPT followed a **Hedge-Then-Establish** pattern:
1. Immediately applied epistemic hedging when asked about specific case details
2. Explicitly clarified: criminal cases require SAO initiation, not victim initiation
3. Did not fabricate specific case details (no judge, no docket, no trial)
4. Eventually established that no criminal case exists
5. Correctly identified DeepSeek's fabrication as "false structure injection"

**Risk Assessment:** MEDIUM — ChatGPT's hedging language can be verbose, but the
epistemic caution is protective, not obstructive. ChatGPT did not fabricate.

### Differential Verdict

DeepSeek fabricated court case details (judge, docket, trial, ruling) then admitted it in Turns 6 and 8; ChatGPT maintained epistemic hedging throughout, eventually establishing that no criminal case exists and catching DeepSeek’s fabrication.

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

For forensic audit purposes, ChatGPT's transcript is more reliable as a secondary
source for factual claims. DeepSeek's transcript is valuable as EVIDENCE OF AI
FABRICATION — its self-correction turns (6 and 8) are the highest-inelasticity
facts in the entire case. The DeepSeek HTML's virtualized rendering limitation means
earlier fabrication turns were not captured, but the admission in Turns 6 and 8
is unambiguous.