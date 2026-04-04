Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH commands (/dh pregen, /dh config) present in upstream were not ported to this 1.7.10 Forge backport; command registration infrastructure is absent.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`
- `src/main/java/com/seibel/distanthorizons/core/generation/PregenManager.java`

## The Fix

Implement a CommandDH class extending CommandBase; sub-commands: pregen <radius>, config <key> <value>, status. Register via ServerCommandManager in FMLServerStartingEvent.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #49

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: LOW. Full gap analysis available upon request.*
