Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

Architechturecraft stores shape and material in NBT; the block's metadata alone maps to the default stone texture. DH reads blockId+meta without NBT, so all ArchitectureCraft blocks fall back to their base material (stone).

## Affected Files

- `src/main/java/com/seibel/distanthorizons/common/wrappers`

## The Fix

For blocks implementing IArchitectureCraft's shape interface, read the material NBT tag during LOD data extraction to pick the correct texture/color.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #30
- #12

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
