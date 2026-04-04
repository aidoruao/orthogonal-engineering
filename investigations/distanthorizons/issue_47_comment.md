Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

MixinFramebuffer replaces the vanilla depth renderbuffer with a depth texture (GL_DEPTH_COMPONENT24); this removes stencil buffer support. NPCDBC's outline effect uses the stencil buffer (GL_STENCIL_INDEX8) for masking, which is now unavailable.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/mixin/MixinFramebuffer.java`

## The Fix

Change MixinFramebuffer to use GL_DEPTH24_STENCIL8 (combined depth+stencil texture) instead of GL_DEPTH_COMPONENT24; attach it to both GL_DEPTH_ATTACHMENT and GL_STENCIL_ATTACHMENT via GL30.glFramebufferTexture2D.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

None identified.

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
