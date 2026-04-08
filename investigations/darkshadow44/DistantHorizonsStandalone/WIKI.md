# DistantHorizonsStandalone Ontological Wiki

**Session:** Kimi Code Session #2, 1a (2026-04-07)  
**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone  
**Commit:** `1abcd988fd4d350795f34dd2e9f678c14ba6162f`  
**Methodology:** Epistemic Forensics — Artifact Primacy, Verbatim Quoting, Low Narrative Smoothing

---

## Table of Contents

1. [Overview](#overview)
2. [Package Map](#package-map)
3. [Class Reference](#class-reference)
4. [Error Taxonomy](#error-taxonomy)
5. [Issue Type Matrix](#issue-type-matrix)
6. [Causal Chain Catalog](#causal-chain-catalog)
7. [Paradox Registry](#paradox-registry)
8. [Countermeasure Registry](#countermeasure-registry)
9. [Config Reference](#config-reference)
10. [Mixin Reference](#mixin-reference)
11. [Cross-Issue Patterns](#cross-issue-patterns)

---

## Overview

### Repository Census

| Metric | Count |
|--------|-------|
| Total Java Files | 601 |
| Total Lines of Code | 84,402 |
| Total Packages | 160 |
| Total Methods | 3,605 |
| Error Paths | 839 |
| Log Statements | 471 |
| Error Log Calls | 283 |
| Mixin Annotations | 42 |
| Mixin Files | 13 |
| Enums | 56 |
| Concurrency Primitives | 283 |
| Constants | 902 |

### Investigation Status

- **Total Issues Investigated:** 25 (across 4 batches)
- **Corrected Analyses:** #51, #56
- **Patches Generated:** #51 (tick handler fix), #56 (MixinFramebuffer splash guard)

---

## Package Map

### Critical Packages

| Package | Files | Role | Issues Mapped | Criticality |
|---------|-------|------|---------------|-------------|
| `com.seibel.distanthorizons.forge` | 11 | Forge mod entry point, proxy layer, mod compatibility | #51, #53, #56, #58, #62, #72 | HIGH |
| `com.seibel.distanthorizons.mixin` | 13 | Mixin injection layer for vanilla Minecraft hooks | #56, #64, #65, #66, #67 | CRITICAL |
| `com.seibel.distanthorizons.core.config` | 34 | Configuration system, validation, defaults | #51, #50, #40 | HIGH |
| `com.seibel.distanthorizons.core.generation` | 7 | World generation orchestration | #40, #51 | HIGH |
| `com.seibel.distanthorizons.common.wrappers.worldGeneration` | 7 | World generation implementation | #40, #51 | HIGH |
| `com.seibel.distanthorizons.core.render` | 17 | LOD rendering engine, quadtree management | #64, #65, #66, #67, #69 | HIGH |
| `com.seibel.distanthorizons.common.render` | 47 | OpenGL rendering, shader management | #56, #64-#67, #69, #20, #30, #31, #59 | CRITICAL |
| `com.seibel.distanthorizons.core.level` | 13 | Level/world management | #51, #53, #58 | HIGH |
| `com.seibel.distanthorizons.core.multiplayer` | 13 | Multiplayer networking, session management | #51, #53, #58 | HIGH |
| `com.seibel.distanthorizons.core.network` | 16 | Network protocol, message handling | #51, #53 | MEDIUM |

### Package Statistics

Top packages by file count:
- `com.seibel.distanthorizons.core.util` — 74 files
- `com.seibel.distanthorizons.common.render` — 47 files
- `com.seibel.distanthorizons.api.interfaces` — 41 files
- `com.seibel.distanthorizons.common.wrappers` — 41 files
- `com.seibel.distanthorizons.core.wrapperInterfaces` — 43 files

---

## Class Reference

### ForgeServerProxy.java

**Location:** `src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java`  
**LOC:** 306  
**Role:** Server-side event proxy handling all server events

#### Methods

| Method | Line | Type | Issues | Error Paths |
|--------|------|------|--------|-------------|
| `registerEvents()` | 54-63 | INITIALIZER | — | — |
| `serverTickEvent()` | 105-141 | EVENT_HANDLER | #51 | Unbounded queue, 15ms deadline, no count limit |
| `serverLevelLoadEvent()` | 144-150 | EVENT_HANDLER | #53 | WorldServer cast without null check |
| `serverChunkLoadEvent()` | 163-175 | EVENT_HANDLER | #51 | Queue growth unbounded |
| `clickBlockEvent()` | 238-251 | EVENT_HANDLER | #62 | Schedule task without timeout |
| `schedule()` | 255-260 | UTILITY | — | — |

#### Critical Fields

| Field | Type | Line | Concurrency |
|-------|------|------|-------------|
| `chunkLoadEvents` | `ConcurrentLinkedQueue<ChunkLoadEvent>` | 101 | Thread-safe queue |
| `taskQueue` | `ConcurrentLinkedQueue<ScheduledTask<?>>` | 253 | Thread-safe queue |
| `chunksPendingResetByWorld` | `IdentityHashMap<World, LongOpenHashSet>` | 102 | Requires synchronization |
| `MAX_CHUNK_EVENTS_PER_TICK` | `int` | 103 | Constant (added in patch) |

### ForgeMain.java

**Location:** `src/main/java/com/seibel/distanthorizons/forge/ForgeMain.java`  
**LOC:** 181  
**Role:** Main mod entry point and initializer

#### Static Fields

| Field | Type | Line | Notes |
|-------|------|------|-------|
| `isHodgePodgeInstalled` | `boolean` | 62 | Network check result |
| `angelicaCompat` | `AngelicaCompat` | 64 | Critical for rendering (#56) |
| `gtCompat` | `GTCompat` | 63 | GregTech compatibility |

### MixinFramebuffer.java

**Location:** `src/main/java/com/seibel/distanthorizons/mixin/MixinFramebuffer.java`  
**LOC:** 79  
**Role:** Framebuffer mixin for depth texture handling

#### Methods

| Method | Line | Type | Issues | Error Paths |
|--------|------|------|--------|-------------|
| `createDepthTexture()` | 31-52 | MIXIN_REDIRECT | #56 | GL calls during splash screen |
| `bindDepthTexture()` | 57-63 | MIXIN_REDIRECT | #56 | GL30 calls without context check |

#### Annotations
- `@Mixin(Framebuffer.class)`
- `@Shadow`
- `@Redirect`

### Config.java

**Location:** `src/main/java/com/seibel/distanthorizons/core/config/Config.java`  
**LOC:** ~2000  
**Role:** Central configuration definition

#### Critical Config Entries

| Key | Line | Default | Min | Max | Issues |
|-----|------|---------|-----|-----|--------|
| `Server.maxGenerationRequestDistance` | 1744 | 4096 | 256 | 4096 | #51 |
| `Common.WorldGenerator.generationMaxChunkRadius` | 1378 | 0 | 0 | INT_MAX | #40, #51 |
| `Server.clientConnectionTimeoutInSeconds` | 1732 | 120 | — | — | #53 |
| `Client.Advanced.Graphics.Quality.lodChunkRenderDistanceRadius` | 193 | 256 | 32 | 4096 | #64, #65 |

---

## Error Taxonomy

### Terminal Root Errors

Errors that, if removed, make other errors irrelevant.

| ID | Name | Description | Issues | Files |
|----|------|-------------|--------|-------|
| ET-GL-CONTEXT | GL Context Corruption | OpenGL calls on wrong thread or during splash screen | #56 | MixinFramebuffer.java |
| ET-TICK-BUDGET | Tick Budget Exhaustion | serverTickEvent exceeds 50ms tick budget | #51, #50 | ForgeServerProxy.java |
| ET-INIT-RACE | Initialization Race Condition | Component accessed before initialization complete | #53, #62, #72 | ForgeMain.java, ForgeServerProxy.java |
| ET-CONFIG-PARADOX | Configuration Value Paradox | Config allows values that guarantee degradation | #51, #40 | Config.java |

### Cascade Errors

Errors that are consequences of terminal root errors.

| ID | Name | Description | Issues | Cascade Of |
|----|------|-------------|--------|------------|
| ET-QUEUE-UNBOUNDED | Unbounded Queue Growth | Queue grows without limit | #51 | ET-TICK-BUDGET |
| ET-NULL-DEREF | Null Pointer in Event Handler | Missing null checks | #62, #53 | ET-INIT-RACE |
| ET-RENDER-FAILURE | Rendering Pipeline Failure | OpenGL state mismatch | #64-#69 | ET-GL-CONTEXT |
| ET-NETWORK-TIMEOUT | Network Timeout | Client-server timeout | #53, #58 | ET-TICK-BUDGET |

---

## Issue Type Matrix

| Type | Issues |
|------|--------|
| **CRASH** | #56, #62, #72 |
| **PERFORMANCE** | #51, #50 |
| **RENDERING** | #64, #65, #66, #67, #69, #31, #30, #20, #59, #52, #42, #47 |
| **SERVER** | #53, #58 |
| **COMMANDS** | #49, #57 |
| **GENERATION** | #40 |
| **BY_DESIGN** | #73 |
| **FEATURE_REQUEST** | #32, #58, #57 |

---

## Causal Chain Catalog

### CC-001: Issue #51 (TPS Degradation)

```
Level 0 [TERMINAL_ROOT]: config: maxGenerationRequestDistance=4096
         ↓ 52.7M blocks² per player - no upper bound validation
Level 1 [CASCADE]: ForgeServerProxy.serverTickEvent unbounded queue
         ↓ chunkLoadEvents fills faster than it drains
Level 2 [CASCADE]: 15ms time budget (line 124)
         ↓ 30% of 50ms tick consumed by DH processing alone
Level 3 [CASCADE]: taskQueue processing without count limit
         ↓ while(!taskQueue.isEmpty()) may never terminate
Level 4 [CASCADE]: Z_STD compression 15.13ms writes
         ↓ single write can exceed 15ms budget
Level 5 [SYMPTOM]: TPS drops below 20
         → user-visible lag, potential disconnects
```

**Falsification:** If queue is capped at 20 events AND budget reduced to 5ms, does TPS stabilize at 20 even with 4096-block config?

### CC-002: Issue #56 (Black Screen Crash)

```
Level 0 [TERMINAL_ROOT]: MixinFramebuffer.createDepthTexture during splash screen
         ↓ GL context may not be fully initialized during FML splash
Level 1 [CASCADE]: GL11.glBindTexture + GL11.glTexImage2D
         ↓ OpenGL calls without context readiness check
Level 2 [CASCADE]: GL state corruption
         ↓ Frame buffer initialization fails
Level 3 [SYMPTOM]: Black screen then crash
         → User sees black screen followed by crash
```

**Falsification:** If splash screen check is added, does black screen issue resolve on affected systems?

### CC-003: Issue #53 (Server Event Handler)

```
Level 0 [TERMINAL_ROOT]: Server initialization race condition
         ↓ Components accessed before full initialization
Level 1 [CASCADE]: serverLevelLoadEvent WorldServer cast
         ↓ Cast without instanceof validation
Level 2 [CASCADE]: NullPointerException or ClassCastException
         ↓ Exception in event handler
Level 3 [SYMPTOM]: Server crash or player disconnect
         → Visible server instability
```

### CC-004: Issue #40 (Unbounded Generation)

```
Level 0 [TERMINAL_ROOT]: generationMaxChunkRadius default 0 (unbounded)
         ↓ No generation bounds by default
Level 1 [CASCADE]: BatchGenerationEnvironment unbounded generation
         ↓ Generation continues indefinitely
Level 2 [CASCADE]: Disk and memory pressure
         ↓ Unbounded storage consumption
Level 3 [SYMPTOM]: Excessive world file size
         → User reports massive storage use
```

---

## Paradox Registry

| ID | Description | Issues | Type | Severity |
|----|-------------|--------|------|----------|
| PX-001 | DH config allows values (maxGenerationRequestDistance=4096) that mathematically guarantee TPS degradation, but provides no validation warning | #51 | DESIGN_PARADOX | HIGH |
| PX-002 | MixinFramebuffer executes GL operations during splash screen phase, but splash screen is not DH's responsibility and GL context may not be ready | #56 | BOUNDARY_PARADOX | CRITICAL |
| PX-003 | ForgeServerProxy.serverTickEvent uses time budget (15ms) instead of count limit, but time measurement doesn't account for system load variation | #51, #50 | ASSUMPTION_PARADOX | MEDIUM |
| PX-004 | RenderHelper.drawDeferredLods() returns early when Angelica absent, completely disabling deferred rendering without user notification | #56 | FEATURE_PARADOX | MEDIUM |

---

## Countermeasure Registry

| ID | For Error | Type | Description | File | Line | Status |
|----|-----------|------|-------------|------|------|--------|
| CM-001 | ET-TICK-BUDGET | BUDGET_REDUCTION | Reduce tick handler time budget from 15ms to 5ms | ForgeServerProxy.java | 129 | GENERATED |
| CM-002 | ET-GL-CONTEXT | SPLASH_GUARD | Check isSplashScreenActive() before GL operations | MixinFramebuffer.java | 31-52 | GENERATED |
| CM-003 | ET-QUEUE-UNBOUNDED | QUEUE_CAP | Cap chunk events processed per tick to 20 | ForgeServerProxy.java | 110-114 | GENERATED |
| CM-004 | ET-NULL-DEREF | VALIDATION | Add null checks in server event handlers | ForgeServerProxy.java | 144-175 | NOT_GENERATED |
| CM-005 | ET-CONFIG-PARADOX | VALIDATION | Add config validation warning for values >2048 | Config.java | 1744-1750 | NOT_GENERATED |

### Patch Files

| Issue | Patch File | Description |
|-------|------------|-------------|
| #51 | `0001-issue51-tick-handler-fix.patch` | Caps chunk events to 20/tick, reduces budget to 5ms |
| #56 | `0001-test.patch` | Adds splash screen guard to MixinFramebuffer |

---

## Config Reference

### Critical Config Values

| Key | Default | MrFuzzihead's Value | Recommended | Issues |
|-----|---------|---------------------|-------------|--------|
| `Server.maxGenerationRequestDistance` | 4096 | 4096 | 1024 | #51 |
| `Common.WorldGenerator.generationMaxChunkRadius` | 0 | — | 128 | #40, #51 |
| `Client.Advanced.Graphics.Quality.lodChunkRenderDistanceRadius` | 256 | — | 256 | #64, #65 |
| `Server.clientConnectionTimeoutInSeconds` | 120 | — | 120 | #53 |

### Config Validation Rules

1. **maxGenerationRequestDistance > 2048** should trigger WARNING log
2. **generationMaxChunkRadius = 0** should require explicit user confirmation
3. **lodChunkRenderDistanceRadius > 1024** should warn about GPU memory

---

## Mixin Reference

| File | Target | Methods | Injections | Issues |
|------|--------|---------|------------|--------|
| MixinFramebuffer.java | `net.minecraft.client.shader.Framebuffer` | createFramebuffer, deleteFramebuffer | createDepthTexture, bindDepthTexture, oldBindStuff, deleteDepthTexture | #56 |
| MixinEntityRenderer.java | `net.minecraft.client.renderer.EntityRenderer` | — | — | #64, #65 |
| MixinMinecraft.java | `net.minecraft.client.Minecraft` | — | — | #56 |
| MixinRenderGlobal.java | `net.minecraft.client.renderer.RenderGlobal` | — | — | #66, #67 |
| MixinActiveRenderInfo.java | `net.minecraft.client.renderer.ActiveRenderInfo` | — | — | — |
| MixinBiomeGenBase.java | `net.minecraft.world.biome.BiomeGenBase` | — | — | — |
| MixinBlock_SideFacingUnloadedChunk.java | `net.minecraft.block.Block` | — | — | — |
| MixinChunkCache_SideFacingUnloaded.java | `net.minecraft.world.ChunkCache` | — | — | — |
| MixinNetHandlerPlayClient.java | `net.minecraft.client.network.NetHandlerPlayClient` | — | — | #53 |
| MixinOptionsScreen.java | `net.minecraft.client.gui.screen.OptionsScreen` | — | — | — |
| MixinTesselator.java | `net.minecraft.client.renderer.Tessellator` | — | — | — |
| MixinTextureAtlasSprite.java | `net.minecraft.client.texture.TextureAtlasSprite` | — | — | — |
| MixinTextureMap.java | `net.minecraft.client.texture.TextureMap` | — | — | — |

---

## Cross-Issue Patterns

### PATTERN-1: Config Distance Cascade

**Description:** High distance config values cause cascading performance issues  
**Issues:** #40, #51, #50  
**Terminal Root:** Config distance validation

**Pattern:**
```
High distance config → Unbounded generation → Queue growth → Tick budget exhaustion → TPS drop
```

### PATTERN-2: GL Context Initialization Race

**Description:** OpenGL operations during early initialization cause crashes  
**Issues:** #56, #64, #65  
**Terminal Root:** Splash screen GL readiness

**Pattern:**
```
Mixin injection during splash → GL calls before context ready → GL state corruption → Crash/Black screen
```

### PATTERN-3: Server Event Handler Validation Gap

**Description:** Missing null/state validation in server event handlers  
**Issues:** #53, #58, #62  
**Terminal Root:** Event handler validation

**Pattern:**
```
Event handler assumptions → Missing validation → Null/cast exceptions → Server instability
```

### PATTERN-4: Unbounded Queue Growth

**Description:** ConcurrentLinkedQueue without size limits causes memory pressure  
**Issues:** #51  
**Terminal Root:** Queue size management

**Pattern:**
```
Unbounded ConcurrentLinkedQueue → Producer faster than consumer → Memory pressure → GC pressure → Tick time increase
```

---

## Falsification Test Status

| ID | Title | Status | Related Issue |
|----|-------|--------|---------------|
| F-DH-001 | serverTickEvent completes within 15ms | FAILED | #51 |
| F-DH-002 | No GL calls during splash screen | FAILED | #56 |
| F-DH-003 | Config values >2048 trigger warning | FAILED | #51 |
| F-DH-004 | Chunk event queue has bounded size | FAILED | #51 |
| F-DH-005 | Z_STD write off-thread | UNKNOWN | #51 |

---

## Methodology Notes

This wiki was generated using **Epistemic Forensics** methodology:

1. **Artifact Primacy:** All findings traceable to source code artifacts
2. **Verbatim Quoting:** Direct code excerpts with line numbers
3. **Tolerance of Contradiction:** Multiple hypotheses tracked simultaneously
4. **Low Narrative-Smoothing Bias:** Raw findings presented without over-simplification

### Key Documents

- `EPISTEMIC_FORENSICS_TOOLS.md` — Methodology reference
- `DH_SOURCE_INDEX.json` — Machine-readable complete index
- `FINAL_MASTER_REPORT.md` — Executive summary

---

*Generated by Kimi Code Session #2, 1a (2026-04-07)*
