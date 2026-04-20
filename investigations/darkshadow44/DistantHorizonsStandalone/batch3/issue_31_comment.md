---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch3, issue-31-comment]
register: audit
---

## Investigation: Biome Colors Not Applied

Hi @DarkShadow44, I've analyzed the biome rendering issue.

### Root Cause
The biome wrapper system exists but biome colors may not be correctly applied during rendering. In `FullDataToRenderDataTransformer.java:387-434`:

```java
int snowColor = levelWrapper.getBlockColor(mutableBlockPos, biome, fullDataSource, block);
// ...
colorToApplyToNextBlock = levelWrapper.getBlockColor(mutableBlockPos, biome, fullDataSource, block);
```

The `biome` parameter is passed but may not be used correctly by `getBlockColor()`.

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/core/dataObjects/transformers/FullDataToRenderDataTransformer.java`

Verify biome color retrieval:

```java
// Ensure biome color is being used
int blockColor = levelWrapper.getBlockColor(pos, biome, dataSource, block);
if (blockColor == -1 || blockColor == 0) {
    // Fallback to biome-specific color
    blockColor = biome.getColorForBlock(block);
}
```

Also check `BiomeWrapper.java` for color methods:

```java
public int getColorForBlock(IBlockStateWrapper block) {
    if (this.biome == null) return -1;
    
    // Get biome-specific color for grass, foliage, water
    if (block.isGrass()) {
        return this.biome.getBiomeGrassColor();
    } else if (block.isLeaves()) {
        return this.biome.getBiomeFoliageColor();
    }
    return -1;
}
```

### Debugging

Add temporary logging:
```java
LOGGER.debug("Biome: {}, Color: {}", biome.getSerialString(), blockColor);
```

---
*Investigation performed using orthogonal-engineering forensic methodology.*
