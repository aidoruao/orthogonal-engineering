Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

Chisel 'Technical block' variants use a custom ISmartBlockModel that returns null or empty quads for certain metadata values; DH's LOD data builder calls Block.getRenderType() and skips blocks returning -1, treating them as invisible.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/common/wrappers`
- `src/main/java/com/seibel/distanthorizons/core/dataObjects`

## The Fix

In the block-data extraction path, fall back to the block's color/material properties when getRenderType()==-1 rather than skipping the block entirely; use a solid color derived from the block's map color.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #30
- #12
- #11

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
