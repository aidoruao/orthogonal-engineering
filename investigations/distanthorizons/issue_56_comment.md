Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

AngelicaCompat.verifyAngelicaVersion() throws AngelicaVersionGuiException when Angelica is absent or below minimum version; the exception propagates uncaught to the FML init event, crashing before the splash screen completes.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/forge/ForgeMain.java`
- `src/main/java/com/seibel/distanthorizons/forge/AngelicaCompat.java`
- `src/main/java/com/seibel/distanthorizons/forge/AngelicaVersionGuiException.java`

## The Fix

Wrap AngelicaCompat instantiation in try-catch; on AngelicaVersionGuiException set angelicaCompat=null and disable shader-dependent paths rather than crashing; display an in-game warning instead.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #72

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
