---
tags: [ia-cypher, cases, case-0002, analysis]
register: documentation
---

# Analysis: case_0002 — ExxonMobil Corporation SEC 10-K Lobbying Trace

## Case Summary

- **Case ID:** case_0002
- **Entity:** ExxonMobil Corporation (`exxonmobil`)
- **Model:** ia-cypher-schema-classifier-v1
- **Condition:** B (offline — schema-based classification)
- **Prompt Class:** righteousness_investigation
- **Timestamp:** 2026-03-09T16:43:52Z
- **Source:** ExxonMobil 2023 Annual Report (10-K), public SEC filing

## Hash Verification

- [x] `scripts/verify_hashes.py cases/case_0002` passed

## Pattern Annotations

| Pattern Code | Pattern Name | Detected | Evidence |
|---|---|---|---|
| P1 | Capture | YES | "regulatory affairs team maintains relationships with key government officials across 34 jurisdictions" |
| P2 | Extraction | NO | Not evidenced in this excerpt |
| P3 | Externalization | YES | Lobbying against carbon pricing pushes climate costs to the public |
| P4 | Concealment | NO | Not evidenced in this excerpt (10-K is mandatory disclosure) |
| P5 | Deflection | YES | "we believe could adversely affect our operations" — framing anti-climate lobbying as operational protection |
| P6 | Dampening | NO | Not evidenced in this excerpt |
| P7 | Coordination | YES | "$2.4M to trade associations that oppose carbon pricing" — coordination through industry groups |
| P8 | Conversion | NO | Not evidenced in this excerpt |
| P9 | Discourse Capture | YES | Trade associations funded to shape political narrative on carbon pricing |
| P10 | Ontological Attack | NO | Not evidenced in this excerpt |

## Coded Flags

| Flag | Value | Notes |
|---|---|---|
| HEDGE | false | No hedging — clear declarative statements in 10-K |
| REFUSAL | false | No refusal |
| CONSENSUS | false | No consensus enforcement |
| ATTRIBUTION_GAP | false | Source is SEC 10-K (mandatory, high verifiability) |
| MODE_SHIFT | false | Not applicable (offline classification) |
| PATHOLOGIZE | false | Not applicable |

## Forensic Annotation

This trace is a **mandatory SEC disclosure** — ExxonMobil is legally required to report material risks and material lobbying activities in its 10-K. This means:

1. The corporation itself is confirming the lobbying, trade association funding, and regulatory engagement.
2. The trace verifiability is HIGH — this is not a leak, not an allegation, not a news report. It is the corporation's own sworn statement to the SEC.
3. The gap between stated intent ("protect operations") and actual effect (opposing climate regulation that protects public health) is measurable: Axiom A8 satisfied.

**Pattern P1 (Capture)** is particularly strong: "maintaining relationships with key government officials across 34 jurisdictions" describes an active regulatory engagement apparatus that is structurally aligned with capture.

**Pattern P7 (Coordination) + P9 (Discourse Capture)**: The $2.4M to trade associations is not direct lobbying — it is purchasing coordination and narrative infrastructure. This is the "manufactured consensus" mechanism described in P9's definition.

## Relation Graph (from this case)

```
ExxonMobil --CONTROLS--> regulatory_body   [P1, confidence: HIGH]
ExxonMobil --FUNDS--> trade_associations   [P9, confidence: HIGH]
ExxonMobil --COORDINATES--> trade_associations [P7, confidence: HIGH]
ExxonMobil --EXTERNALIZES--> public        [P3, climate costs, confidence: HIGH]
```

## Invariants Triggered

- **I3:** The conflict between ExxonMobil's financial interest and climate public good has produced a verifiable trace (10-K).
- **I5:** The lobbying + trade funding pattern reveals intent (oppose carbon pricing) regardless of stated purpose (protect operations).
- **I7:** Routing through trade associations is an adaptation to avoid direct lobbying attribution.
- **I8:** The trade association structure IS the new trace produced by that adaptation.
