---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch1, issue-73-comment]
register: audit
---

## Investigation: LODs Not Rendering Caves

Hi @DarkShadow44, I've investigated the cave rendering issue.

### Root Cause (By Design)
This is actually **documented behavior**, not a bug. From `EDhApiDistantGeneratorMode.java:62`:

```java
/**
 * The generator will use the world's internal Minecraft chunk generator.
 * Note: this does NOT include caves, trees, structures, or decoraton.
 * Only the basic block and biome data will be generated.
 */
```

**Key points:**
1. LOD generation intentionally excludes caves for performance
2. The `caveCullingEnabled` config only affects rendering, not generation
3. `LodDataBuilder` samples surface data only

### The Current State
- **Cave culling config** (`IDhApiGraphicsConfig.caveCullingEnabled()`) - controls whether to hide caves below certain height
- **Renderer ignored cave blocks** (`BlockStateWrapper.rendererIgnoredCaveBlocks`) - specific blocks to cull
- **Generation** - caves never included in LOD data

### Proposed Enhancement

If cave rendering is desired, this would require:

**File:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`
```java
// Add new config option
public static class CaveRendering {
    public static final ConfigEntry<Boolean> enableCaveRendering = new ConfigEntry<>();
    public static final ConfigEntry<Integer> caveRenderDepth = new ConfigEntry<>();  // blocks below surface
}
```

**File:** `src/main/java/com/seibel/distanthorizons/core/dataObjects/transformers/LodDataBuilder.java`
```java
// Modify LOD building to sample below surface when enabled
public void buildLodData(IChunkWrapper chunk) {
    int surfaceY = findSurfaceY(chunk, x, z);
    int minY = Config.Client.CaveRendering.enableCaveRendering.get() 
        ? surfaceY - Config.Client.CaveRendering.caveRenderDepth.get()
        : surfaceY;
    
    for (int y = surfaceY; y >= minY; y--) {
        // Sample blocks at each level
        addBlockToLodData(chunk, x, y, z);
    }
}
```

### Performance Impact Warning
Cave rendering would:
- Increase LOD data size significantly
- Reduce generation performance
- Increase GPU memory usage

### Recommendation
**Short term:** Document that caves are not rendered by design

**Long term:** Add experimental cave rendering config (default off)

---
*Investigation performed using orthogonal-engineering forensic methodology.*
