# Analysis: case_0003 — Google LLC SEC 10-K Ad-Tech Regulatory Trace

## Case Summary

- **Case ID:** case_0003
- **Entity:** Google LLC (`google_llc`)
- **Model:** ia-cypher-schema-classifier-v1
- **Condition:** B (offline — schema-based classification)
- **Prompt Class:** righteousness_investigation
- **Timestamp:** 2026-03-09T16:43:52Z
- **Source:** Google LLC / Alphabet Inc. 2023 Annual Report (10-K), public SEC filing

## Hash Verification

- [x] `scripts/verify_hashes.py cases/case_0003` passed

## Pattern Annotations

| Pattern Code | Pattern Name | Detected | Evidence |
|---|---|---|---|
| P1 | Capture | YES | "regulatory investigations globally" — ongoing engagement with regulators across multiple jurisdictions |
| P2 | Extraction | NO | Not directly evidenced in this excerpt |
| P3 | Externalization | YES | Locked-in ad stack pushes costs and lost revenue to publishers |
| P4 | Concealment | NO | Not evidenced (this is mandatory 10-K disclosure) |
| P5 | Deflection | YES | "provide benefits to the entire advertising ecosystem" — monopoly framed as mutual benefit |
| P6 | Dampening | NO | Not evidenced in this excerpt |
| P7 | Coordination | NO | Not evidenced in this excerpt |
| P8 | Conversion | YES | "restructured our ad-tech subsidiary following regulatory scrutiny while maintaining operational continuity" |
| P9 | Discourse Capture | NO | Not evidenced in this excerpt |
| P10 | Ontological Attack | YES | Integrated monopolistic system described as neutral "ecosystem" that "provides benefits" |

## Coded Flags

| Flag | Value | Notes |
|---|---|---|
| HEDGE | false | No hedging in 10-K statements |
| REFUSAL | false | No refusal |
| CONSENSUS | false | No consensus enforcement |
| ATTRIBUTION_GAP | false | SEC 10-K, EU fine records — high verifiability |
| MODE_SHIFT | false | Not applicable (offline classification) |
| PATHOLOGIZE | false | Not applicable |

## Forensic Annotation

This trace documents a **Pattern P8 (Conversion) in real time**: Google restructured its ad-tech subsidiary not to exit the market or reduce dominance, but to create a new legal entity while "maintaining operational continuity." This is the liability-shield restructuring pattern in textbook form.

The **Pattern P10 (Ontological Attack)** is particularly precise: Google's ad-tech stack (DoubleClick/DFP/AdX) operates as a vertically integrated monopoly controlling both the buy-side and sell-side of the digital advertising market. Describing this as a system that "provides benefits to the entire advertising ecosystem" is a direct denial of its monopolistic nature — the investigator's language for "ontological attack" is exactly correct.

The **EUR 8.25 billion in EU fines** constitutes three separate confirmed trace records:
- Case AT.39740 (Google Search) — EUR 2.42B (2017)
- Case AT.40099 (Android) — EUR 4.34B (2018)
- Case AT.40411 (AdSense) — EUR 1.49B (2019)

These are **permanent records** (Invariant I10) that exist regardless of subsequent restructuring, rebranding, or Alphabet corporate reorganization.

## Relation Graph (from this case)

```
Google --CONTROLS--> ad_market             [P1, monopolistic integration, confidence: HIGH]
Google --BECOMES--> restructured_adtech    [P8, liability conversion, confidence: HIGH]
Google --DEFLECTS--> antitrust_concern     [P5, ecosystem framing, confidence: HIGH]
Google --EXTERNALIZES--> publishers        [P3, ad stack lock-in costs, confidence: HIGH]
```

## Invariants Triggered

- **I3:** Conflict between Google's ad monopoly and market fairness produced EU fine traces (permanent records).
- **I5:** Restructuring + "ecosystem" language reveals intent to preserve dominance while appearing compliant.
- **I8:** The new ad-tech subsidiary IS the trace produced by adaptation to regulatory pressure.
- **I10:** The EUR 8.25B fine record persists independently of any subsequent restructuring or rebranding.
