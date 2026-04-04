Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH's fog renderer reads vanilla GL_FOG parameters via RenderHelper.enableFog/disableFog; the pollution fog from GregTech/pollution mods is applied as a post-process color overlay, not via GL_FOG state. DH's fog shader only uses GL_FOG_START/END/COLOR uniforms and misses the overlay.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/mixin/MixinEntityRenderer.java`
- `src/main/java/com/seibel/distanthorizons/RenderHelper.java`

## The Fix

Short-term workaround (suggested by reporter): add a config option to disable LOD rendering when pollution density exceeds a threshold, detectable via GTCompat. Long-term: read pollution color from GTCompat and blend it into DH's fog color uniform.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #42

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
