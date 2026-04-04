Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH LOD generation samples the highest non-air block per column for height; underground cave chambers are never captured because the LOD data stores only surface-level geometry, so caves below appear as solid filled columns.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/generation/DhLightingEngine.java`
- `src/main/java/com/seibel/distanthorizons/core/dataObjects`

## The Fix

Extend LOD column data to include below-surface void spaces by sampling multiple vertical segments per column; or add a cave-detection pass that marks sky-exposed underground cells.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #20

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
