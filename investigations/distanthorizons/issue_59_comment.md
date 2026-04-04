Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH's LOD transparency pass only renders blocks flagged as transparent in the DH config's transparency mode; colored/tinted glass blocks (GT glass variants and vanilla stained glass) use custom render types and are not in DH's transparency block list, so they render as opaque in LODs.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/render/renderer/LodRenderer.java`
- `src/main/java/com/seibel/distanthorizons/core/dataObjects`

## The Fix

During LOD data collection, check Block.isOpaqueCube() and Block.renderAsNormalBlock(); blocks returning false from either should be stored with the transparent flag set and rendered in the transparency pass.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #42

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
