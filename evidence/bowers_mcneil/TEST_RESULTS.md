---
tags: [evidence, bowers-mcneil, test-results]
register: audit
---

# TEST RESULTS — Bowers vs McNeil
_Generated: PR #81 manufactured-correspondence addendum_
_Pipeline: IA-CYPHER-0002 / analysis/automated_test_suite.py framework_
_Standard: Yeshua / Orthogonal Engineering_

## Overview
This update re-validates the Bowers/McNeil corpus after adding the public-source registry layer, S-15 Manufactured Correspondence, and H-BM-019.

## Results
- `python3 evidence/bowers_mcneil/FALSIFICATION_TESTS.py` — **PASS** (19/19 hypotheses survive)
- `python3 scripts/forensic_audit_pipeline.py` — **PASS**
- `sha256_manifest.json` — regenerated after registry/matrix/manual-doc updates

## Corpus Status Checks
| Check | Status |
|------|--------|
| FC-007 / FC-008 upgraded to VERIFIED_BY_PUBLIC_SOURCE | PASS |
| FC-009 remains PARTIALLY_VERIFIED | PASS |
| FC-010 / FC-011 / FC-012 upgraded to VERIFIED_BY_PUBLIC_SOURCE | PASS |
| FC-013 added | PASS |
| INV-015 added | PASS |
| H-BM-019 added | PASS |
| P15 added | PASS |
| S-15 added | PASS |

## CodeQL Note
The required CodeQL run may still report "0 alerts" while skipping Python due to database size. That limitation does not change the corpus-level validation state.
