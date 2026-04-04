Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

Photon shader pipeline renders opaque terrain in a deferred pass; DH injects LOD rendering at sortAndRender renderPass==0 (opaque), but Photon's gbuffer pass has already cleared the depth buffer, causing LODs to overdraw vanilla terrain.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/mixin/MixinRenderGlobal.java`
- `src/main/java/com/seibel/distanthorizons/forge/AngelicaCompat.java`

## The Fix

When Angelica/Iris shaders are active (AngelicaConfig.enableIris), delay opaque LOD injection to after gbuffer pass completion by using the deferred renderDeferredLods path already present in RenderHelper.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #66
- #64

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
