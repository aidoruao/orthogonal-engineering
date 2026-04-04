Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

LodRenderer.renderLodPass() checks `renderParams.vanillaFogEnabled` to decide whether to run the fog renderer; when the blindness effect or underwater overlay is active, vanilla sets fog to near-zero distance, but DH still renders LODs at full opacity on top, blocking the effect.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/render/renderer/LodRenderer.java`
- `src/main/java/com/seibel/distanthorizons/mixin/MixinEntityRenderer.java`

## The Fix

In RenderHelper or MixinEntityRenderer, detect active overlay effects (blindness: Potion.blindness, underwater: player in water biome) and set a flag to suppress LOD rendering or set LOD alpha to zero when these effects are active.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #52

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
