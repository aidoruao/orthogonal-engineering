Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

BiomesOPlenty registers biomes with extreme fog/water color values (>1.0 or <0.0 as float components); AngelicaCompat.getFogColor() wraps GLStateManager.getFogColor() into a java.awt.Color constructor which requires [0.0,1.0] range and throws IllegalArgumentException on out-of-range values.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/AngelicaCompat.java`
- `src/main/java/com/seibel/distanthorizons/RenderHelper.java`

## The Fix

In AngelicaCompat.getFogColor(), clamp each color channel to [0.0, 1.0] before constructing java.awt.Color: `new Color(Math.max(0,Math.min(1,(float)color.x)), ...)`

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #31

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
