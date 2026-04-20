---
tags: [investigations, darkshadow44, archaicfix, wiki]
register: audit
---

# ArchaicFix - Technical Documentation

## Overview

ArchaicFix is a "Swiss army knife of bugfixes" for Minecraft 1.7.10, targeting performance improvements, bug fixes, and mod compatibility. This document serves as a technical reference for understanding what ArchaicFix does so that **Distant Horizons (DH) does not need to duplicate these fixes**.

> **Repository**: https://github.com/DarkShadow44/ArchaicFix  
> **Forked From**: embeddedt/ArchaicFix  
> **Commit**: `85b33afdd7f08b0842d944b198b0de966a72d778`  
> **License**: LGPL-3.0 (with caveats, see [Licensing](#licensing))

---

## Table of Contents

1. [Architecture](#architecture)
2. [Key Subsystems](#key-subsystems)
3. [Performance Fixes](#performance-fixes)
4. [Bug Fixes](#bug-fixes)
5. [Mod Compatibility](#mod-compatibility)
6. [DH Overlap Analysis](#dh-overlap-analysis)
7. [Configuration Reference](#configuration-reference)
8. [Licensing](#licensing)

---

## Architecture

```
ArchaicFix/
├── Core (ArchaicFix.java, ArchaicConfig.java)
├── ASM Layer (ArchaicTransformer.java, LateMixinPlugin.java)
├── Lighting Engine (lighting/ - Phosphor backport)
├── Mixins/
│   ├── client/core/     # Client-side vanilla fixes
│   ├── client/lighting/ # Client lighting hooks
│   ├── common/core/     # Server-side vanilla fixes
│   ├── common/lighting/ # Server lighting integration
│   └── common/<mods>/   # Mod-specific fixes
├── Helpers/             # Utility classes
├── Recipe/              # Recipe caching system
└── LoliASM API/         # Memory optimization (zone.rong.loliasm)
```

---

## Key Subsystems

### 1. Phosphor Lighting Engine

**Location**: `org.embeddedt.archaicfix.lighting`

A backport of the Phosphor lighting engine (originally by Angeline for 1.12+). This is one of the most significant performance improvements in ArchaicFix.

**Key Components**:
- `LightingEngine.java` (608 LOC) - Main lighting calculation engine
- `PooledLongQueue.java` - Memory-efficient queue for light updates
- Mixin integration in `mixins/common/lighting/`

**How It Works**:
1. Queues light updates instead of processing immediately
2. Processes updates in batches using breadth-first propagation
3. Uses bit-packed coordinates for memory efficiency
4. Thread-safe with ReentrantLock and ownership validation

**DH Implications**: DH should **not** implement its own lighting engine. Rely on Phosphor/ArchaicFix for block lighting. DH LOD lighting should be calculated separately.

---

### 2. Recipe Caching System

**Location**: `org.embeddedt.archaicfix.recipe`

Guava Cache-based recipe lookup to reduce crafting lag in large modpacks.

**Key Components**:
- `MixinCraftingManager.java` - Intercepts recipe lookups
- `RecipeCacheLoader.java` - Cache population logic
- `LastMatchedInfo.java` - Last-match optimization

**How It Works**:
1. Creates a cache key from items in crafting grid
2. Uses Guava LoadingCache with 500k entry weight limit
3. Falls back to linear scan only on cache miss
4. Last-match optimization for repeated crafts

**Config**: `cacheRecipes` (default: false, EXPERIMENTAL)

**DH Implications**: DH has no crafting system - no overlap.

---

### 3. Cascading Worldgen Detection

**Location**: `org.embeddedt.archaicfix.helpers.CascadeDetectionHelper`

Detects and logs when chunk population causes cascading worldgen (chunks loading other chunks during generation).

**How It Works**:
1. ThreadLocal stack tracks currently populating chunks
2. Wraps chunk population with detection logic
3. Logs mod responsible for cascading generation
4. Optional stacktrace logging for debugging

**Config**: 
- `logCascadingWorldgen` (default: true)
- `logCascadingWorldgenStacktrace` (default: false)

**DH Implications**: DH's chunk generation should be checked against this detection. Cascading worldgen from DH would be logged.

---

### 4. Entity Ticking Optimization

**Location**: `MixinWorld.java` (`skipUpdateIfOptimizing`)

Skips entity AI/ticking for entities outside configured player distance.

**How It Works**:
1. Configures squared distance threshold (default: 4096 = 64 blocks)
2. For each entity update, checks distance to all players
3. Skips ticking if beyond threshold (unless forced chunk or special entity)
4. Allows despawn check even when skipping

**Config**:
- `optimizeEntityTicking` (default: false)
- `optimizeEntityTickingDistance` (default: 4096)
- `optimizeEntityTickingIgnoreList` (default: ["Wither", "EnderDragon"])

**DH Implications**: DH does not modify entity ticking - these are complementary.

---

## Performance Fixes

### Summary Table

| ID | Fix | Config | Default | DH Overlap Risk |
|----|-----|--------|---------|-----------------|
| PERF-001 | Phosphor Lighting Engine | `enablePhosphor` | true | MEDIUM |
| PERF-002 | Entity Ticking Optimization | `optimizeEntityTicking` | false | LOW |
| PERF-003 | Recipe Caching | `cacheRecipes` | false | NONE |
| PERF-004 | Spawn Chunk Disabling | `disableSpawnChunks` | false | LOW |
| PERF-005 | Block Update Limit (65k) | `increaseBlockUpdateLimit` | true | MEDIUM |
| PERF-006 | Remove System.gc() | N/A (always) | - | NONE |
| PERF-007 | GL Error Check Skip | N/A (always) | - | MEDIUM |
| PERF-008 | Async Creative Search | `asyncCreativeSearch` | true | NONE |
| PERF-009 | LongHashMap Better Hash | N/A (always) | - | LOW |
| PERF-010 | Item Lag Reduction | `itemLagReduction` | true | LOW |

### Detailed Descriptions

#### PERF-001: Phosphor Lighting Engine

**Impact**: Major (can reduce lighting lag by 80%+)

**Technical Details**:
- Replaces vanilla's immediate light updates with batched processing
- Uses neighbor-aware propagation to minimize recalculation
- Handles both sky and block light
- Thread-safe with main thread validation

**Files**:
- `lighting/world/lighting/LightingEngine.java`
- `mixins/common/lighting/MixinWorld_Lighting.java`
- `mixins/common/lighting/MixinChunk.java`

**Why DH Shouldn't Duplicate**: Lighting calculation is complex and Phosphor is well-tested. DH should use vanilla/Phosphor lighting data for LODs rather than implementing parallel lighting.

---

#### PERF-005: Block Update Limit Increase

**Impact**: Medium (prevents update queue overflow)

**Technical Details**:
- Vanilla limits block updates to 1000 per tick
- ArchaicFix increases this to 65000
- Prevents "Update queue overflow" issues in redstone-heavy worlds

**Why DH Shouldn't Duplicate**: DH should work within vanilla's update system. If DH needs block updates, it should respect the configured limit.

---

## Bug Fixes

### Summary Table

| ID | Bug | Vanilla Issue | Config | Default |
|----|-----|---------------|--------|---------|
| BUG-001 | Tick List Synchronization | MC-Unknown | `fixTickListSynchronization` | true |
| BUG-002 | Fullscreen Resize | MC-68754 | Always | - |
| BUG-003 | Camera Clip Through Blocks | MC-30845 | Always | - |
| BUG-004 | Fall Distance Calculation | MC-Unknown | Always | - |
| BUG-005 | Skin Memory Leak | MC-Unknown | `fixSkinMemoryLeak` | true |
| BUG-006 | TileEntity Unload Lag | MC-Unknown | `fixTEUnloadLag` | true |
| BUG-007 | Login Race Condition | MC-Unknown | `fixLoginRaceCondition` | true |
| BUG-008 | Structure Entity Persistence | MC-108664 | `fixEntityStructurePersistence` | true |

### Detailed Descriptions

#### BUG-001: Tick List Synchronization

**Problem**: "TickNextTick list out of synch" crash/exception

**Solution**: Fixes synchronization in scheduled tick processing

**File**: `mixins/common/core/MixinWorldServer.java`

**Why DH Should Care**: DH has its own tick handling (`ForgeServerProxy.serverTickEvent`). Verify DH doesn't introduce similar synchronization issues.

---

#### BUG-006: TileEntity Unload Lag

**Problem**: Lag spikes when TileEntities unload (saves to disk)

**Solution**: Optimizes TE unloading to reduce stutter

**File**: `mixins/common/core/MixinWorld_UpdateEntities.java`

**Why DH Shouldn't Duplicate**: DH should not modify TE unloading behavior. This is a vanilla optimization.

---

## Mod Compatibility

ArchaicFix includes specific fixes for 25+ mods:

### High-Priority Compatibility

| Mod | Fix | File |
|-----|-----|------|
| OptiFine | Disable version checker | `MixinVersionCheckThread.java` |
| ChickenChunks | Optimize chunk viewer | `MixinPlayerChunkViewerManager.java` |
| AE2 | Fix duplicate stack rendering with NEI | `MixinNEIItemRender.java` |
| GregTech6 | Tooltip optimization, crafting optimization | `MixinGT_API_Proxy_Client.java`, `MixinAdvancedCraftingXToY.java` |
| Botania | Fix cascading worldgen | `MixinBlockSpecialFlower.java` |
| Mekanism | Fix cascading worldgen | `MixinGenHandler.java` |
| Thaumcraft | Better hashing (EXPERIMENTAL) | `betterThaumcraftHashing` |

### Compatibility Philosophy

ArchaicFix uses Mixin's priority system and conditional injection to avoid conflicts:
- `@Mixin(priority = 999)` - runs late to allow other mods to inject first
- `expect = 0` - allows injection to fail silently if target not found
- Mod detection via `Loader.isModLoaded()`

---

## DH Overlap Analysis

### High-Risk Overlap Areas

#### 1. Chunk Loading

**ArchaicFix**:
- `MixinChunkProviderServer.neverLoadSpawn()` - disables spawn chunks
- `CascadeDetectionHelper` - logs cascading worldgen
- Phosphor lighting hooks in chunk loading

**Distant Horizons**:
- `ForgeServerProxy.chunkLoadEvents` - queues chunk load events
- `ForgeServerProxy.serverChunkLoadEvent` - processes chunk loads

**Analysis**: 
- ArchaicFix's spawn chunk disabling operates at chunk provider level
- DH's chunk events are higher-level
- **Risk**: LOW - different layers of the system
- **Action**: Verify DH chunk processing works with spawn chunks disabled

#### 2. Tick Handling

**ArchaicFix**:
- `MixinWorld.skipUpdateIfOptimizing()` - entity ticking optimization
- `MixinWorldServer` - tick list synchronization

**Distant Horizons**:
- `ForgeServerProxy.serverTickEvent()` - 15ms tick budget for DH processing
- Task queue processing

**Analysis**:
- ArchaicFix optimizes entity ticking; DH processes chunk/LOD tasks
- **Risk**: LOW - different tick subsystems
- **Action**: Monitor TPS when both are active; entity optimization reduces load, giving DH more budget

#### 3. GL Context / Rendering

**ArchaicFix**:
- `MixinMinecraft.skipErrorCheck()` - disables GL error checking
- Client lighting mixins

**Distant Horizons**:
- `RenderHelper.drawLods()` - LOD rendering
- `MixinFramebuffer` - depth texture handling

**Analysis**:
- ArchaicFix reduces GL validation overhead
- DH does its own GL state management
- **Risk**: MEDIUM - both touch GL state
- **Action**: Verify no rendering artifacts when both mods present

#### 4. Lighting Engine

**ArchaicFix**:
- Full Phosphor lighting engine replacement
- Block and sky light calculation

**Distant Horizons**:
- LOD lighting calculations (independent of block lighting)

**Analysis**:
- Phosphor optimizes vanilla lighting updates
- DH LODs use their own simplified lighting
- **Risk**: MEDIUM - lighting should be complementary
- **Action**: Verify DH LODs render correctly with Phosphor enabled

### Complementary Fixes (No Overlap)

These ArchaicFix fixes have **no overlap** with DH and should be used together:

1. **PERF-002 Entity Ticking Optimization** - DH doesn't touch entities
2. **PERF-003 Recipe Caching** - DH has no crafting system
3. **PERF-004 Spawn Chunk Disabling** - DH uses different chunk management
4. **PERF-008 Async Creative Search** - DH has no GUI search
5. **GEN-001 Cascading Worldgen Detection** - Helps debug DH worldgen too

### Fixes DH Should NOT Duplicate

These are core fixes that DH should not reimplement:

1. **Phosphor Lighting Engine** - Use ArchaicFix/Phosphor
2. **Tick List Synchronization** - Verify DH doesn't break this
3. **TileEntity Unload Lag** - Vanilla optimization
4. **Block Update Limit** - Work within vanilla constraints

---

## Configuration Reference

### Critical Configs for DH Users

```java
// Recommended settings for DH compatibility:

enablePhosphor = true              // Keep enabled for lighting performance
optimizeEntityTicking = false      // Can enable for extra TPS, but test first
cacheRecipes = false               // Safe to enable, but experimental
disableSpawnChunks = false         // Test with DH - may affect LOD generation
fixTickListSynchronization = true  // Keep enabled
fixTEUnloadLag = true              // Keep enabled
increaseBlockUpdateLimit = true    // Safe to keep enabled
logCascadingWorldgen = true        // Useful for debugging DH worldgen
```

### Config Categories

| Category | Options | Purpose |
|----------|---------|---------|
| **Performance** | 10+ options | Entity ticking, spawn chunks, block updates |
| **Lighting** | `enablePhosphor` | Phosphor lighting engine |
| **Rendering** | Fancy items, texture modernization | Client visual improvements |
| **Bugfixes** | 15+ options | Various vanilla bug fixes |
| **Mod Compat** | Thaumcraft, OptiFine, etc. | Per-mod compatibility |
| **Worldgen** | Cascading detection/fixes | World generation optimization |

---

## Licensing

### Primary License

ArchaicFix is licensed under **LGPL-3.0**.

### Special Licensing Notes

1. **Occlusion Culling Module** (not present in current commit)
   - Derived from CoFHTweaks (Minecraft 1.8 derived)
   - **NOT under LGPL-3.0**
   - See `src/main/java/org/embeddedt/archaicfix/occlusion/LICENSE` (if present)

2. **LoliASM Components** (`zone.rong.loliasm`)
   - From LoliASM
   - Licensed under **LGPL-2.1**

3. **MemoryLeakFix Components** (`ca.fxco.memoryleakfix`)
   - From MemoryLeakFix
   - Licensed under **LGPL-2.1**

4. **Phosphor Lighting Engine**
   - Derived from Phosphor by Angeline
   - LGPL-3.0 compatible

### DH Integration Guidelines

- DH can safely depend on ArchaicFix being present
- DH should not redistribute ArchaicFix code
- DH should recommend ArchaicFix as a companion mod
- For occlusion culling (if ever needed), check license separately

---

## Threading Analysis

### Thread-Safe Components

| Component | Thread Safety | Notes |
|-----------|---------------|-------|
| LightingEngine | ReentrantLock | Validates thread ownership |
| CascadeDetectionHelper | ThreadLocal | Per-thread population stacks |
| Recipe Cache | Guava LoadingCache | Thread-safe cache |

### Threading Fixes

- **MatterOverdrive**: Matter registration on separate thread
- **JourneyMap**: Debug feature removal for thread safety

---

## Summary for DH Developers

### What ArchaicFix Does That DH Should NOT Do

1. **Lighting Engine** - Let Phosphor handle block lighting
2. **Recipe System** - No need for crafting optimization
3. **Entity Ticking** - Don't modify entity update logic
4. **Vanilla Bugfixes** - Don't reimplement vanilla fixes

### What ArchaicFix Does That HELPS DH

1. **Chunk Loading Optimization** - Reduces server load, more resources for DH
2. **Entity Ticking Optimization** - More tick budget for DH processing
3. **Cascading Worldgen Detection** - Helps debug DH generation issues
4. **Tick List Synchronization** - Stable tick loop for DH integration

### Testing Checklist for DH + ArchaicFix

- [ ] Verify LODs generate correctly with Phosphor enabled
- [ ] Test chunk loading with spawn chunks disabled
- [ ] Monitor TPS with both entity optimization and DH active
- [ ] Check for rendering artifacts (GL state conflicts)
- [ ] Verify cascading worldgen detection doesn't flag DH falsely

---

## References

- **ArchaicFix Repository**: https://github.com/DarkShadow44/ArchaicFix
- **Phosphor (Original)**: https://github.com/jellysquid3/phosphor-forge
- **Mixin Documentation**: https://github.com/SpongePowered/Mixin/wiki
- **Forge 1.7.10 Docs**: https://mcforge.readthedocs.io/en/1.7.10/

---

*This documentation was generated for orthogonal-engineering investigation purposes. Last updated: 2026-04-07*
