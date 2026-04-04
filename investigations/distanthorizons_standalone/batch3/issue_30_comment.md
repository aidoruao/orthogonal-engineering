## Investigation: NBT Blocks Not Rendering Correctly

Hi @DarkShadow44, I've identified the NBT block issue.

### Root Cause
`FakeWorld.java` returns null for TileEntities:

```java
// FakeWorld.java:42
@Override
public TileEntity getTileEntity(int x, int y, int z) {
    return null;  // No NBT data available
}
```

Blocks that rely on NBT data (chests, signs, banners, modded blocks) won't render correctly because DH only samples block states, not TileEntity data.

### Why This Happens
1. DH generates LODs from chunk data
2. For performance, it doesn't store full NBT data
3. `FakeWorld` is used to render blocks but lacks TileEntity support

### The Fix

**Option 1: Document Limitation** (Recommended)
Add to documentation: "Blocks with complex NBT data (chests, signs, banners) render as base block type"

**Option 2: Basic NBT Support**

**File:** `src/main/java/com/seibel/distanthorizons/common/wrappers/block/FakeWorld.java`

```java
// Add simple NBT cache for critical blocks
private final Map<BlockPos, TileEntity> tileEntityCache = new HashMap<>();

public void setTileEntity(BlockPos pos, TileEntity te) {
    if (te != null && isCriticalBlock(te)) {
        tileEntityCache.put(pos, te);
    }
}

@Override
public TileEntity getTileEntity(int x, int y, int z) {
    return tileEntityCache.get(new BlockPos(x, y, z));
}

private boolean isCriticalBlock(TileEntity te) {
    // Only store blocks that significantly affect appearance
    return te instanceof BannerTileEntity || 
           te instanceof SkullTileEntity;
}
```

### Recommendation
Implement Option 2 for critical blocks only (banners, skulls) that significantly affect appearance, document others as limitations.

---
*Investigation performed using orthogonal-engineering forensic methodology.*
