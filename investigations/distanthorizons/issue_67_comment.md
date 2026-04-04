Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

Mineshot overrides the camera/projection matrix for large screenshots; DH's RenderHelper caches modelViewMatrix and projectionMatrix set during the normal render frame. When Mineshot swaps the camera, DH renders LODs with the old matrices, causing depth-buffer mismatch and terrain clip.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/RenderHelper.java`
- `src/main/java/com/seibel/distanthorizons/mixin/MixinRenderGlobal.java`

## The Fix

Hook into Mineshot's screenshot begin/end events to suppress DH LOD rendering during large screenshot capture, or re-fetch the current GL modelview/projection matrices at render time rather than caching them.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #64
- #66

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: LOW. Full gap analysis available upon request.*
