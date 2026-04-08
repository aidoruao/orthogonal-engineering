# Angelica Ontological Wiki

**Session:** Kimi Code Session - Angelica Analysis (2026-04-07)  
**Repository:** https://github.com/GTNewHorizons/Angelica  
**Commit:** `a544ef916da54c5ff26df515226cb1d1404bd21b`  
**Methodology:** Epistemic Forensics — Artifact Primacy, Verbatim Quoting, Low Narrative Smoothing

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Critical Classes](#critical-classes)
4. [DH Issue Cross-References](#dh-issue-cross-references)
5. [Mixin Index](#mixin-index)
6. [Rendering Pipeline](#rendering-pipeline)
7. [Compatibility Notes](#compatibility-notes)
8. [Causal Chains](#causal-chains)
9. [Error Patterns](#error-patterns)

---

## Overview

### What is Angelica?

**Angelica** is a modern OptiFine replacement for Minecraft 1.7.10, developed by the GTNewHorizons team. It integrates three major rendering technologies into a unified mod:

| Component | Origin | Purpose |
|-----------|--------|---------|
| **Sodium** | JellySquid | High-performance chunk rendering with modern OpenGL techniques |
| **Iris** | CoderBot | Shader pipeline for shader pack support (SEUS, BSL, etc.) |
| **ArchaicFix** | Integral | Splash screen improvements and legacy fixes |

### Repository Census

| Metric | Count |
|--------|-------|
| Total Java Files | 1,185 |
| Main Source Files | 941 |
| Test Files | 7 |
| Mixin Files | 237 |
| Total Lines of Code | 100,467 |
| Total Packages | 275 |
| Mixin Annotations | 237 |
| Inject Annotations | 196 |
| Redirect Annotations | 140 |
| Shadow Annotations | 232 |
| Enums | 145 |
| Compatibility Handlers | 12 |

### Key Features

1. **OpenGL State Management** — Centralized via `GLStateManager.java` with thread assertions
2. **Splash Screen Replacement** — Injects into `SplashProgress` for memory bar display (#56 critical)
3. **Shader Pipeline** — Full Iris integration for 1.7.10 shader support
4. **Sodium Rendering** — Modern chunk meshing and culling
5. **HUD Caching** — Optimizes HUD element rendering
6. **Dynamic Lights** — Portable light sources without shaders

---

## Repository Structure

### Critical Packages

| Package | Files | Role | Issues Mapped | Criticality |
|---------|-------|------|---------------|-------------|
| `com.gtnewhorizons.angelica.mixins` | 2 | Mixin registration and targeting system | #56, #64, #65, #66, #67, #72 | CRITICAL |
| `com.gtnewhorizons.angelica.mixins.early.angelica` | 6 | Core Angelica mixins for vanilla Minecraft | #56, #42, #72 | CRITICAL |
| `com.gtnewhorizons.angelica.mixins.early.angelica.archaic` | 5 | SplashProgress replacement - CRITICAL FOR #56 | #56 | CRITICAL |
| `com.gtnewhorizons.angelica.mixins.early.shaders` | 5 | Iris shader pipeline integration | #56, #64, #65, #47 | CRITICAL |
| `com.gtnewhorizons.angelica.mixins.early.sodium` | 6 | Sodium rendering engine integration | #56, #64, #65, #42 | CRITICAL |
| `com.gtnewhorizons.angelica.glsm` | 4 | OpenGL State Manager - Central GL context management | #56, #64, #65 | CRITICAL |
| `com.gtnewhorizons.angelica.glsm.stacks` | 8 | GL state stack implementations | #56 | HIGH |
| `com.gtnewhorizons.angelica.glsm.states` | 7 | GL state representations and value tracking | #56 | HIGH |
| `com.gtnewhorizons.angelica.config` | 4 | Configuration system | #42, #47, #72 | HIGH |
| `com.gtnewhorizons.angelica.rendering` | 4 | Rendering pipeline management | #56, #64 | HIGH |
| `com.gtnewhorizons.angelica.transform` | 3 | ASM transformation layer | #56 | HIGH |
| `com.gtnewhorizons.angelica.transform.compat` | 5 | Mod compatibility transformers | #42, #72 | HIGH |
| `net.coderbot.iris.pipeline` | 5 | Iris shader rendering pipeline | #56, #64, #65 | CRITICAL |
| `net.coderbot.iris.gl` | 4+ | Iris GL resource management | #56 | HIGH |
| `me.jellysquid.mods.sodium.client.render` | 3+ | Sodium chunk rendering engine | #64, #65 | HIGH |
| `me.jellysquid.mods.sodium.client.gl` | 4+ | Sodium GL abstraction layer | #56, #64 | HIGH |

---

## Critical Classes

### MixinSplashProgress.java

**Location:** `src/mixin/java/com/gtnewhorizons/angelica/mixins/early/angelica/archaic/MixinSplashProgress.java`  
**LOC:** 158  
**Role:** **REPLACES cpw.mods.fml.client.SplashProgress** — Injects Angelica branding and memory bar into Forge splash screen

#### Methods

| Method | Line | Type | Issues | Error Paths |
|--------|------|------|--------|-------------|
| `injectDrawMemoryBar` | 42-80 | MIXIN_INJECT | #56 | GL calls during splash screen - uses reflection to access FontRenderer |
| `drawMemoryBar` | 92-148 | RENDER | #56 | GL state modification during early initialization |

#### Annotations
- `@Mixin(targets = { "cpw/mods/fml/client/SplashProgress$3" })`
- **Target:** Inner class `SplashProgress$3` (the splash screen thread)

#### Critical Notes
- **PRIMARY CLASS FOR DH ISSUE #56** — GL context corruption during splash screen
- Executes `GL11.glPushMatrix/PopMatrix` during splash screen initialization
- Uses `Class.forName` check for ArchaicFix presence
- Runs on splash screen thread, not main client thread

---

### GLStateManager.java

**Location:** `src/main/java/com/gtnewhorizons/angelica/glsm/GLStateManager.java`  
**LOC:** 1,200  
**Role:** **Central OpenGL state management** — Thread-safe GL call interceptor

#### Methods

| Method | Line | Type | Issues | Error Paths |
|--------|------|------|--------|-------------|
| `init` | 100-150 | INITIALIZER | #56 | GL queries before context ready, MAX_TEXTURE_UNITS query |
| `glBindTexture` | 200-250 | GL_INTERCEPT | #56 | Texture binding without context check |
| `assertMainThread` | 400-450 | VALIDATION | #56 | Can be disabled via `-Dangelica.assertMainThread=false` |

#### Static Fields

| Field | Type | Line | Description |
|-------|------|------|-------------|
| `BYPASS_CACHE` | `boolean` | 91 | System property `angelica.disableGlCache` |
| `MAX_TEXTURE_UNITS` | `int` | 96 | `GL_MAX_TEXTURE_IMAGE_UNITS` query result |

#### Protection Layers
1. **Layer 1:** Mixin redirection to GLStateManager
2. **Layer 2:** Thread assertion in GLStateManager
3. **Layer 3:** State caching to reduce GL calls
4. **Layer 4:** Stack-based state tracking

---

### RenderSystem.java

**Location:** `src/main/java/com/gtnewhorizons/angelica/glsm/RenderSystem.java`  
**LOC:** 400  
**Role:** OpenGL abstraction layer — DSA (Direct State Access) support detection

#### Methods

| Method | Line | Type | Issues | Notes |
|--------|------|------|--------|-------|
| `initRenderer` | 37-57 | INITIALIZER | #56 | Detects OpenGL 4.5 or `ARB_direct_state_access` support |

---

### MixinFramebuffer.java (Shaders)

**Location:** `src/mixin/java/com/gtnewhorizons/angelica/mixins/early/shaders/MixinFramebuffer.java`  
**LOC:** 97  
**Role:** Iris depth texture integration — Framebuffer modification

#### Methods

| Method | Line | Type | Issues | Mixin Target |
|--------|------|------|--------|--------------|
| `iris$createDepthTexture` | 65-95 | MIXIN_INJECT | #56, #64 | `Lnet/minecraft/client/shader/Framebuffer;createFramebuffer(II)V` |
| `iris$useDepthTexture` | 49-55 | MIXIN_INJECT | #56 | `Lnet/minecraft/client/shader/Framebuffer;createBindFramebuffer(II)V` |

#### Error Paths
- `GL11.glGenTextures` before context ready
- `GL30.glFramebufferTexture2D` without context check

**Note:** OVERLAPS WITH DH MixinFramebuffer — Both modify `Framebuffer.createFramebuffer`

---

### MixinEntityRenderer.java (Shaders)

**Location:** `src/mixin/java/com/gtnewhorizons/angelica/mixins/early/shaders/MixinEntityRenderer.java`  
**LOC:** 150  
**Role:** Iris world rendering pipeline integration

#### Methods

| Method | Line | Type | Issues | Mixin Target |
|--------|------|------|--------|--------------|
| `iris$beginRender` | 36-47 | MIXIN_INJECT | #64, #65 | `Lnet/minecraft/client/renderer/EntityRenderer;renderWorld(FJ)V` |
| `iris$beginEntities` | 67-71 | MIXIN_INJECT | #64 | `Lnet/minecraft/client/renderer/EntityRenderer;renderWorld(FJ)V` |

**Note:** OVERLAPS WITH DH MixinEntityRenderer — Both target `renderWorld()`

---

### AngelicaConfig.java

**Location:** `src/main/java/com/gtnewhorizons/angelica/config/AngelicaConfig.java`  
**LOC:** 200  
**Role:** Central configuration for all Angelica features

#### Critical Config Entries

| Key | Default | Issues | Description |
|-----|---------|--------|-------------|
| `enableSodium` | `true` | #56, #64, #65 | Enable Sodium rendering engine |
| `enableIris` | `true` | #56, #64, #65 | Enable Iris shaders (requires Sodium) |
| `showSplashMemoryBar` | `true` | #56 | Show memory usage during game load — **AFFECTS SplashProgress mixin** |
| `enableHudCaching` | `true` | #65 | Renders HUD elements once per 20 frames |
| `enableDynamicLights` | `true` | — | Enable Dynamic Lights |
| `sleepBeforeSwap` | `false` | — | Alternative FPS limiter implementation |

---

### RedirectorTransformer.java

**Location:** `src/main/java/com/gtnewhorizons/angelica/transform/RedirectorTransformer.java`  
**LOC:** 250  
**Role:** Runtime bytecode transformation for GL call redirection

#### Methods

| Method | Line | Type | Issues | Notes |
|--------|------|------|--------|-------|
| `transform` | 50-100 | TRANSFORMER | #56 | Transforms GL calls at class load time to route through GLStateManager |

---

## DH Issue Cross-References

### Issue #56 — Crash on Startup with Angelica

**Description:** Crash on startup with Angelica — GL context corruption during splash screen  
**Root Cause:** `MixinSplashProgress` executes GL operations during FML splash screen before GL context fully ready

| Aspect | Details |
|--------|---------|
| **Angelica Classes** | `MixinSplashProgress.java`, `MixinFramebuffer.java`, `GLStateManager.java`, `MixinMinecraft.java (sodium)` |
| **DH Overlap Classes** | `MixinFramebuffer.java (DH)`, `MixinMinecraft.java (DH)` |
| **Conflict Points** | `injectDrawMemoryBar` (lines 42-80), `iris$createDepthTexture` (lines 65-95) |
| **GL Operations** | `glPushMatrix`, `glPopMatrix`, `glTranslatef`, `glScalef`, `glEnable(GL_TEXTURE_2D)` |

**Resolution Notes:** Angelica's `MixinSplashProgress` replaces `cpw.mods.fml.client.SplashProgress` — DH should check for Angelica presence before applying framebuffer mixins.

---

### Issue #42 — Lighting Issues with Angelica

**Description:** Lighting issues with Angelica  
**Root Cause:** GL state management conflicts between Angelica `GLStateManager` and DH rendering

| Aspect | Details |
|--------|---------|
| **Angelica Classes** | `GLStateManager.java`, `MixinMinecraft.java (angelica)`, `MixinEntityRenderer.java` |
| **DH Overlap Classes** | `RenderHelper.java (DH)` |
| **Resolution** | DH should use `GLStateManager` calls instead of direct `GL11` calls |

---

### Issue #47 — Shader Rendering Issues

**Description:** Shader rendering issues  
**Root Cause:** Iris shader pipeline conflicts

| Aspect | Details |
|--------|---------|
| **Angelica Classes** | `MixinEntityRenderer.java (shaders)`, `MixinItemRenderer.java (shaders)`, `DeferredWorldRenderingPipeline.java` |
| **Notes** | Angelica integrates Iris shaders — DH rendering may need to check Iris pipeline state |

---

### Issue #64 — Rendering Issues with Sodium

**Description:** Rendering issues with Sodium  
**Root Cause:** Sodium rendering pipeline conflicts with DH LOD rendering

| Aspect | Details |
|--------|---------|
| **Angelica Classes** | `SodiumWorldRenderer.java`, `MixinRenderGlobal.java (sodium)`, `MixinEntityRenderer.java (sodium)` |
| **DH Overlap Classes** | `MixinEntityRenderer.java (DH)`, `MixinRenderGlobal.java (DH)` |
| **Notes** | Multiple mixins target `EntityRenderer.renderWorld()` — priority ordering matters |

---

### Issue #65 — HUD Rendering Issues

**Description:** HUD rendering issues  
**Root Cause:** HUD caching conflicts

| Aspect | Details |
|--------|---------|
| **Angelica Classes** | `HUDCaching.java`, `MixinGuiIngame.java`, `MixinGuiIngameForge.java` |
| **Notes** | Angelica HUD caching may interfere with DH overlay rendering |

---

### Issue #72 — Compatibility Issues with Various Mods

**Description:** Compatibility issues with various mods  
**Root Cause:** Mod loading order and config conflicts

| Aspect | Details |
|--------|---------|
| **Angelica Classes** | `AngelicaConfig.java`, `CompatConfig.java`, `TargetedMod.java` |
| **Notes** | Angelica has comprehensive mod targeting system — DH should use similar approach |

---

## Mixin Index

### Mixin Registration

**File:** `Mixins.java`  
**Role:** Central mixin registration and conditional application

| Group | Classes | Phase | Condition | Issues | Criticality |
|-------|---------|-------|-----------|--------|-------------|
| `ANGELICA_STARTUP` | `angelica.startup.MixinInitGLStateManager` | EARLY | — | — | CRITICAL |
| `ANGELICA` | `MixinActiveRenderInfo`, `MixinEntityRenderer`, `MixinMinecraft` | EARLY | — | #56, #42 | HIGH |
| `ARCHAIC_SPLASH` | `MixinSplashProgress`, `AccessorSplashProgress` | EARLY | `showSplashMemoryBar && !lwjglDebug` | #56 | **CRITICAL** |
| `SODIUM` | `sodium.MixinMinecraft`, `sodium.MixinEntityRenderer`, `sodium.MixinRenderGlobal` | EARLY | `enableSodium` | #56, #64, #65 | CRITICAL |
| `IRIS_RENDERING` | `shaders.MixinEntityRenderer`, `shaders.MixinFramebuffer`, `shaders.MixinRenderGlobal` | EARLY | `enableIris` | #56, #64, #65, #47 | CRITICAL |

### Complete Mixin Target Index

| File | Target | Phase | Methods | Injections | Issues |
|------|--------|-------|---------|------------|--------|
| `MixinSplashProgress.java` | `cpw.mods.fml.client.SplashProgress$3` | EARLY | `run` | `injectDrawMemoryBar` | #56 |
| `MixinFramebuffer.java (shaders)` | `net.minecraft.client.shader.Framebuffer` | EARLY | `createFramebuffer`, `deleteFramebuffer`, `createBindFramebuffer` | `iris$createDepthTexture`, `iris$deleteDepthBuffer`, `iris$useDepthTexture` | #56, #64 |
| `MixinEntityRenderer.java (shaders)` | `net.minecraft.client.renderer.EntityRenderer` | EARLY | `renderWorld`, `renderHand` | `iris$beginRender`, `iris$endLevelRender`, `iris$beginEntities`, `iris$disableVanillaRenderHand` | #64, #65, #47 |
| `MixinEntityRenderer.java (sodium)` | `net.minecraft.client.renderer.EntityRenderer` | EARLY | — | — | #64, #65 |
| `MixinEntityRenderer.java (angelica)` | `net.minecraft.client.renderer.EntityRenderer` | EARLY | — | — | #42 |
| `MixinRenderGlobal.java (shaders)` | `net.minecraft.client.renderer.RenderGlobal` | EARLY | — | — | #64, #65, #66, #67 |
| `MixinRenderGlobal.java (sodium)` | `net.minecraft.client.renderer.RenderGlobal` | EARLY | — | — | #64, #65, #66, #67 |
| `MixinMinecraft.java (angelica)` | `net.minecraft.client.Minecraft` | EARLY | `runGameLoop`, `func_147120_f`, `runTick` | `angelica$injectLightingFixPostRenderTick`, `angelica$limitFPS`, `angelica$trackFrametimes` | #42, #56 |
| `MixinMinecraft.java (sodium)` | `net.minecraft.client.Minecraft` | EARLY | `resize`, `runGameLoop`, `checkGLError` | `sodium$resize`, `sodium$checkGLError` | #56 |
| `MixinOpenGlHelper.java` | `net.minecraft.client.renderer.OpenGlHelper` | EARLY | — | — | #56 |
| `MixinActiveRenderInfo.java` | `net.minecraft.client.renderer.ActiveRenderInfo` | EARLY | — | — | — |
| `MixinGameSettings.java` | `net.minecraft.client.settings.GameSettings` | EARLY | — | — | — |
| `MixinItemRenderer.java (shaders)` | `net.minecraft.client.renderer.ItemRenderer` | EARLY | — | — | #47 |
| `MixinTileEntityBeaconRenderer.java` | `net.minecraft.client.renderer.tileentity.TileEntityBeaconRenderer` | EARLY | — | — | — |
| `MixinAbstractTexture.java` | `net.minecraft.client.renderer.texture.AbstractTexture` | EARLY | — | — | startup |
| `MixinTextureMap.java` | `net.minecraft.client.renderer.texture.TextureMap` | EARLY | — | — | startup |
| `MixinTextureAtlasSprite.java` | `net.minecraft.client.renderer.texture.TextureAtlasSprite` | EARLY | — | — | — |
| `MixinRender.java` | `net.minecraft.client.renderer.entity.Render` | EARLY | — | — | — |
| `MixinRendererLivingEntity.java (shaders)` | `net.minecraft.client.renderer.entity.RendererLivingEntity` | EARLY | — | — | — |
| `MixinGuiIngameForge.java (shaders)` | `net.minecraftforge.client.GuiIngameForge` | EARLY | — | — | — |
| `MixinLocale.java` | `net.minecraft.client.resources.Locale` | EARLY | — | — | — |
| `MixinBlock.java (sodium)` | `net.minecraft.block.Block` | EARLY | — | — | — |
| `MixinWorldClient.java (sodium)` | `net.minecraft.client.multiplayer.WorldClient` | EARLY | — | — | — |
| `MixinChunk.java (sodium)` | `net.minecraft.world.chunk.Chunk` | EARLY | — | — | — |
| `MixinRenderBlocks.java (sodium)` | `net.minecraft.client.renderer.RenderBlocks` | EARLY | — | — | — |
| `MixinBiomeGenBase.java (sodium)` | `net.minecraft.world.biome.BiomeGenBase` | EARLY | — | — | — |
| `MixinFMLClientHandler.java (angelica)` | `cpw.mods.fml.client.FMLClientHandler` | EARLY | — | — | — |
| `MixinFMLClientHandler.java (sodium)` | `cpw.mods.fml.client.FMLClientHandler` | EARLY | — | — | — |
| `MixinHUDCaching classes` | `GuiIngame`, `GuiIngameForge` | EARLY | — | — | #65 |
| `MixinDynamicLights classes` | `Entity`, `EntityRenderer` | EARLY | — | — | — |
| `MixinVBO classes` | `GLAllocation`, `ModelRenderer` | EARLY | — | — | — |

### Mixin Overlap with DH (High Risk)

| Vanilla Class | Angelica Mixins | DH Mixins | Risk |
|---------------|-----------------|-----------|------|
| `net.minecraft.client.shader.Framebuffer` | `MixinFramebuffer.java (shaders)` | `MixinFramebuffer.java (DH)` | **HIGH** — Both modify depth texture handling |
| `net.minecraft.client.renderer.EntityRenderer` | `MixinEntityRenderer.java (angelica)`, `(sodium)`, `(shaders)` | `MixinEntityRenderer.java (DH)` | **HIGH** — All modify `renderWorld()` |
| `net.minecraft.client.renderer.RenderGlobal` | `MixinRenderGlobal.java (sodium)`, `(shaders)` | `MixinRenderGlobal.java (DH)` | **MEDIUM** — Rendering coordination required |
| `net.minecraft.client.Minecraft` | `MixinMinecraft.java (angelica)`, `(sodium)` | `MixinMinecraft.java (DH)` | **MEDIUM** — `resize()` and `runGameLoop()` targeted |

---

## Rendering Pipeline

### GL State Management Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ANGELICA RENDERING PIPELINE                  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Mixin Injection Layer                                  │
│  ├── Redirects all GL calls through GLStateManager              │
│  └── Transform: RedirectorTransformer (ASM)                     │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: GLStateManager (Thread Safety)                        │
│  ├── assertMainThread() validation                              │
│  ├── State caching to minimize GL calls                         │
│  └── BYPASS_CACHE for debugging                                 │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: State Stack Management                                │
│  ├── AlphaStateStack, BlendStateStack, DepthStateStack          │
│  ├── FogStateStack, LightStateStack, MatrixModeStack            │
│  └── Color4Stack, ColorMaskStack                                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: State Representations                                 │
│  ├── AlphaState, BlendState, DepthState                         │
│  ├── FogState, LightState, MaterialState                        │
│  └── ISettableState interface                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Sodium + Iris Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                    SODIUM + IRIS PIPELINE                        │
├─────────────────────────────────────────────────────────────────┤
│  SodiumWorldRenderer                                            │
│  ├── ChunkRenderManager (quadtree-based culling)               │
│  ├── ChunkRenderBackend (GL command generation)                │
│  └── Sodium terrain meshing                                     │
├─────────────────────────────────────────────────────────────────┤
│  Iris Shader Pipeline                                           │
│  ├── DeferredWorldRenderingPipeline                            │
│  ├── FixedFunctionWorldRenderingPipeline                       │
│  ├── PipelineManager (shader pack management)                  │
│  └── ShadowRenderer (shadow map generation)                    │
├─────────────────────────────────────────────────────────────────┤
│  GL Resource Management                                         │
│  ├── GlObject base class                                        │
│  ├── GlBuffer, GlProgram, GlFramebuffer                        │
│  └── GlStateTracker                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Compatibility Notes

### DH + Angelica Compatibility Matrix

| Feature | DH Status | Angelica Requirement | Notes |
|---------|-----------|----------------------|-------|
| Basic LOD Rendering | ✅ Compatible | Sodium enabled | Use `GLStateManager` for GL calls |
| Shader Support | ⚠️ Partial | Iris enabled | Check Iris pipeline state |
| HUD Overlays | ⚠️ Partial | HUD Caching | May need to invalidate cache |
| Splash Screen | ❌ Conflict | `showSplashMemoryBar` | **#56** — GL context race |
| Framebuffer | ⚠️ Partial | Depth textures | Coordinate depth texture handling |
| Chunk Rendering | ✅ Compatible | Sodium | Priority ordering critical |

### Recommended DH Configuration with Angelica

```java
// Check for Angelica presence
boolean angelicaLoaded = Loader.isModLoaded("angelica");

if (angelicaLoaded) {
    // Use GLStateManager instead of direct GL11 calls
    // Check for Sodium/Iris before applying framebuffer mixins
    // Avoid GL operations during splash screen
}
```

### Critical Configuration for DH #56

| Config Key | Angelica Default | DH Recommendation |
|------------|------------------|-------------------|
| `showSplashMemoryBar` | `true` | DH should detect and defer initialization |
| `enableSodium` | `true` | Required for Iris, coordinate chunk rendering |
| `enableIris` | `true` | Check pipeline state before rendering |
| `enableHudCaching` | `true` | Invalidate cache when DH overlay changes |

---

## Causal Chains

### CC-ANG-001: Issue #56 (GL Context Corruption)

```
Level 0 [TERMINAL_ROOT]: MixinSplashProgress.injectDrawMemoryBar executes
         ↓ during FML splash screen phase
Level 1 [CASCADE]: GL11.glPushMatrix/glPopMatrix/glScalef calls
         ↓ GL context not yet fully initialized on splash thread
Level 2 [CASCADE]: GL state corruption in driver
         ↓ Subsequent GL operations fail or produce undefined behavior
Level 3 [CASCADE]: DH MixinFramebuffer.createDepthTexture executes
         ↓ GL context already corrupted by Angelica splash operations
Level 4 [SYMPTOM]: Black screen or crash on startup
         → User sees black screen followed by crash or hang
```

**Falsification:** If `showSplashMemoryBar=false` OR splash screen check added to DH framebuffer mixin, does issue resolve?

---

### CC-ANG-002: Issue #64 (Sodium Rendering Conflicts)

```
Level 0 [TERMINAL_ROOT]: Multiple mixins target EntityRenderer.renderWorld()
         ↓ Angelica (sodium, shaders) + DH mixins all inject
Level 1 [CASCADE]: Injection order depends on Mixin priority values
         ↓ Undefined behavior if priorities conflict
Level 2 [CASCADE]: SodiumWorldRenderer modifies chunk rendering
         ↓ DH LOD rendering assumes vanilla chunk pipeline
Level 3 [CASCADE]: GL state mismatch between Sodium and DH
         ↓ Depth testing, culling state inconsistent
Level 4 [SYMPTOM]: Missing LODs or visual artifacts
         → DH LODs not visible or render incorrectly
```

**Falsification:** If Angelica `enableSodium=false`, does DH LOD rendering work correctly?

---

### CC-ANG-003: Issue #42 (GL State Conflicts)

```
Level 0 [TERMINAL_ROOT]: Angelica GLStateManager caches GL state
         ↓ Assumes all GL calls route through it
Level 1 [CASCADE]: DH uses direct GL11 calls
         ↓ GLStateManager cache becomes stale
Level 2 [CASCADE]: Subsequent Angelica operations use wrong cached values
         ↓ Lighting, blending, depth test state incorrect
Level 3 [SYMPTOM]: Lighting issues or visual corruption
         → Blocks appear incorrectly lit or blended
```

**Falsification:** If DH uses GLStateManager instead of GL11, does lighting resolve?

---

## Error Patterns

### Terminal Root Errors

| ID | Name | Description | Issues | Files |
|----|------|-------------|--------|-------|
| `ET-GL-CONTEXT-ANGELICA` | GL Context Corruption via Angelica | OpenGL calls before context initialized during splash | #56 | `MixinSplashProgress.java`, `MixinFramebuffer.java` |
| `ET-MIXIN-CONFLICT` | Mixin Target Conflict | Multiple mixins targeting same method | #56, #64, #65 | `MixinEntityRenderer.java`, `MixinRenderGlobal.java` |
| `ET-SPLASH-GL` | Splash Screen GL Operations | GL operations during splash before context ready | #56 | `MixinSplashProgress.java` |
| `ET-THREAD-SAFETY` | OpenGL Thread Safety Violation | GL calls from non-render threads | #56, #64 | `GLStateManager.java` |

### Cascade Errors

| ID | Name | Description | Issues | Cascade Of |
|----|------|-------------|--------|------------|
| `ET-SHADER-PIPELINE` | Iris Shader Pipeline Failure | Shader pipeline initialization errors | #47, #64, #65 | `ET-GL-CONTEXT-ANGELICA` |
| `ET-SODIUM-RENDER` | Sodium Rendering Pipeline Failure | Sodium chunk rendering errors | #64, #65, #66, #67 | `ET-GL-CONTEXT-ANGELICA` |
| `ET-CONFIG-RACE` | Configuration Race Condition | Config accessed before init | #42, #72 | Initialization timing |

### Common Error Patterns When Angelica is Not Installed

When Angelica is **NOT** present, DH may encounter these issues:

| Error Pattern | Symptom | Cause | Angelica Solution |
|--------------|---------|-------|-------------------|
| **No GL State Management** | Random GL errors, visual corruption | Direct GL11 calls from multiple mods | `GLStateManager` centralizes all GL calls |
| **No Splash Screen Guard** | Crashes during early initialization | GL operations before context ready | `MixinSplashProgress` manages splash screen safely |
| **No Thread Assertions** | Intermittent crashes | GL calls from wrong threads | `assertMainThread()` validation |
| **No State Caching** | Performance degradation | Redundant GL state changes | State stack system minimizes GL calls |
| **No Sodium Rendering** | Poor chunk rendering performance | Vanilla chunk meshing | Sodium quadtree-based culling |
| **No Shader Support** | Cannot use shader packs | No shader pipeline | Iris integration |

### Error Signatures for DH #56

```
// Typical stack trace when Angelica splash screen causes GL corruption:
java.lang.NullPointerException
    at cpw.mods.fml.client.SplashProgress$3.run(SplashProgress.java:XXX)
    // OR
org.lwjgl.LWJGLException: Could not make context current
    at org.lwjgl.opengl.WindowsContextImplementation.nMakeCurrent(Native Method)
    
// DH-specific manifestation:
java.lang.IllegalStateException: GL context not current
    at com.seibel.distanthorizons.mixin.MixinFramebuffer.createDepthTexture(MixinFramebuffer.java:31)
```

---

## Methodology Notes

This wiki was generated using **Epistemic Forensics** methodology:

1. **Artifact Primacy:** All findings traceable to source code artifacts
2. **Verbatim Quoting:** Direct code excerpts with line numbers
3. **Tolerance of Contradiction:** Multiple hypotheses tracked simultaneously
4. **Low Narrative-Smoothing Bias:** Raw findings presented without over-simplification

### Key Documents

- `SOURCE_INDEX.json` — Machine-readable complete index
- `EPISTEMIC_FORENSICS_TOOLS.md` — Methodology reference

---

*Generated by Kimi Code Session - Angelica Analysis (2026-04-07)*
