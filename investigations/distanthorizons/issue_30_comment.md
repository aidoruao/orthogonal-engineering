Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

LOD block data stores blockId+metadata but not NBT; blocks like podzol (minecraft:dirt meta=2) are visually distinguished by NBT tag 3 in some modpacks, so DH maps all to the same visual. More broadly, any block using TileEntity or NBT for visual differentiation (GT machines, colored cables) will not render correctly.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/core/dataObjects`
- `src/main/java/com/seibel/distanthorizons/common/wrappers`

## The Fix

For blocks that implement ITextureProvider or have a TileEntity, extract the visual color/texture at LOD-build time from the block renderer rather than from blockId+meta alone; cache the result keyed on blockId+meta+relevant NBT fields.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #44
- #11
- #12

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: MEDIUM. Full gap analysis available upon request.*
