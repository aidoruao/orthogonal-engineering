Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

On first world load with shaders active, AngelicaCompat is initialized and angelicaCompat!=null, so MixinFramebuffer's framebufferMixinEnabled flag controls depth texture creation; but the IrisAccessor.isShaderPackInUse() state is false until after the first render frame, causing DH to skip LOD setup.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/AngelicaCompat.java`
- `src/main/java/com/seibel/distanthorizons/MixinFlags.java`
- `src/main/java/com/seibel/distanthorizons/forge/IrisAccessor.java`

## The Fix

In RenderHelper.drawLods(), re-check IrisAccessor.isShaderPackInUse() each frame and invalidate/reinitialize DH render state when shader state transitions from disabled to enabled.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #65
- #66

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
