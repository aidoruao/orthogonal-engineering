Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH loads client-side rendering code (OpenGL/LWJGL3) unconditionally during FML mod init even on dedicated-server or headless contexts; on LWJGL3+Java 25 this triggers a GL context initialization before any display is created.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeMain.java`
- `src/main/java/com/seibel/distanthorizons/forge/ForgeClientProxy.java`

## The Fix

Guard all client-side GL/LWJGL3 initialization behind FMLCommonHandler.instance().getEffectiveSide().isClient() checks in ForgeMain.init(); verify AngelicaCompat and RPLECompat are never instantiated on server side.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #56
- #53

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
