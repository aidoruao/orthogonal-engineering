Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

Solas shader modifies the depth buffer format or uses a custom framebuffer attachment; DH's MixinFramebuffer creates a GL_DEPTH_COMPONENT24 depth texture, but Solas expects GL_DEPTH24_STENCIL8 or a different internal format, causing depth test failures in LOD geometry.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/mixin/MixinFramebuffer.java`
- `src/main/java/com/seibel/distanthorizons/MixinFlags.java`

## The Fix

Query the active shader's required depth format via AngelicaCompat/IrisAccessor before creating the depth texture in MixinFramebuffer; fall back to GL_DEPTH24_STENCIL8 when shaders are active.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #65
- #64

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
