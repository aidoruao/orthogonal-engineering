Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

PregenManager.startPregen() exists and is functional, but the /dh pregen command registration is absent from ForgeServerProxy or a dedicated command handler; the command was present in upstream DH but not ported to this 1.7.10 backport.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/generation/PregenManager.java`
- `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`

## The Fix

Register a Forge CommandBase subclass that calls PregenManager.startPregen() with parsed origin/radius arguments; register it in ForgeServerProxy or via FMLServerStartingEvent.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #57

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
