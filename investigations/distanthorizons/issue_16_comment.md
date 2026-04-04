Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH writes to the DH depth texture (separate from vanilla framebuffer depth); entity rendering uses the vanilla depth buffer. Since DH depth is not composited back into the vanilla depth buffer before entity rendering, entities appear in front of LOD geometry.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeClientProxy.java`
- `src/main/java/com/seibel/distanthorizons/mixin/MixinFramebuffer.java`

## The Fix

After DH renders LODs and calls metaRenderer.applyToMcTexture(), also blit the DH depth texture into the vanilla framebuffer's depth attachment so entity rendering respects LOD occlusion.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

None identified.

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
