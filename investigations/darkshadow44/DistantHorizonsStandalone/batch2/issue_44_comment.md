---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch2, issue-44-comment]
register: audit
---

## Investigation: Chisel Block Invisibility

Hi @DarkShadow44, I've analyzed the Chisel compatibility issue.

### Root Cause
Chisel mod uses custom rendering (TESR/ISBRH) for its decorative blocks. DH's LOD generation samples block states but doesn't handle Chisel's complex rendering:

```java
// BlockStateWrapper.java has pattern for special blocks:
public static ObjectOpenHashSet<IBlockStateWrapper> rendererIgnoredCaveBlocks = null;

public static ObjectOpenHashSet<IBlockStateWrapper> getRendererIgnoredCaveBlocks(...) {
    // Special handling for certain blocks
    rendererIgnoredCaveBlocks = getBlockWrappers(
        Config.Client.Advanced.Graphics.Culling.ignoredRenderCaveBlockCsv,
        ...
    );
}
```

Chisel blocks need similar special handling.

### The Fix

**File:** `src/main/java/com/seibel/distanthorizons/common/wrappers/block/BlockStateWrapper.java`

Add Chisel block detection:

```java
public static boolean isChiselBlock(IBlockStateWrapper block) {
    // Check if block is from Chisel mod
    String blockId = block.getBlockId();
    return blockId != null && blockId.startsWith("chisel:");
}

public static Color getChiselBlockColor(IBlockStateWrapper block, ILevelWrapper level) {
    // Fallback: use stone color or block's base material color
    Block materialBlock = Blocks.stone; // Default fallback
    
    // Try to get color from block's material
    return getColorFromMaterial(block, level);
}
```

### Immediate Workaround

Add Chisel blocks to ignored render list in config:
```csv
# In DH config - ignoredRenderCaveBlockCsv
chisel:*
```

This will skip Chisel blocks instead of showing them as invisible.

### Long-term Solution

Full Chisel compatibility would require:
1. Detecting Chisel mod
2. Sampling actual rendered color (expensive)
3. Using base block texture as fallback

---
*Investigation performed using orthogonal-engineering forensic methodology.*
