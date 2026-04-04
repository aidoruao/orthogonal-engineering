Hi @DarkShadow44, I've investigated this issue. Here's what I found:

## Root Cause

DH's LOD chunk builder reads biome IDs at generation time via the chunk's biome array; the PDIM dimension uses dynamically-modified biomes from Thaumcraft warp and bees that are stored in world NBT, not the static BiomeGenBase registry. The LOD builder reads from BiomeGenBase.getBiomeGenArray() which returns the default biome, not the runtime-modified one.

## Affected Files

- `src/main/java/com/seibel/distanthorizons/mixin/MixinBiomeGenBase.java`
- `src/main/java/com/seibel/distanthorizons/forge/BiomeHandler.java`

## The Fix

When building LOD data for a chunk, read the biome from Chunk.getBiomeGenForCoords() (which uses the chunk's stored biome array) rather than from the world's BiomeGenBase registry; invalidate LOD cache when biomes change via a ChunkDataEvent listener.

## How to Verify

1. Apply the proposed fix.
2. Reproduce the original issue scenario.
3. Confirm the issue no longer occurs.
4. Regression-test vanilla dimensions (overworld, nether, end).

## Related Issues

- #69

---
*Investigation performed using [orthogonal-engineering](https://github.com/aidoruao/orthogonal-engineering) Epistemic Forensics methodology (pipeline DH-STANDALONE-001). Confidence: HIGH. Full gap analysis available upon request.*
