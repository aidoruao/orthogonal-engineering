Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

ForgeServerProxy registers on the FML and MinecraftForge event buses; the WorldEvent.Load handler calls ServerApi.serverLevelLoadEvent which attempts to initialize the DH level system; an ASM conflict with other mods (chylex.hee, forestry, botania) causes a class-loading failure during event dispatch.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`
- `src/main/java/com/seibel/distanthorizons/common/wrappers/world/ServerLevelWrapper.java`

## The Fix

Wrap serverLevelLoadEvent in try-catch in ForgeServerProxy; log the exception and skip DH initialization for that world rather than propagating. Also verify ForgeMain.onInitializeServer() does not reference any client-only classes.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #62

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
