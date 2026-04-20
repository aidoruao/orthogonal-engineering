---
tags: [investigations, darkshadow44, distanthorizonsstandalone, batch2, batch2-master-report]
register: audit
---

# DistantHorizonsStandalone - Batch 2 Investigation Report

**Date:** 2026-04-04  
**Pipeline:** DH-STANDALONE-001  
**Issues:** 7 (Shader/Rendering/Compatibility)  
**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone

---

## Summary Table

| # | Title | Priority | Category | Status | Confidence | Fix Location |
|---|-------|----------|----------|--------|------------|--------------|
| 64 | Loading world with shaders enabled - LODs not rendering | HIGH | SHADER | FIX_PROPOSED | MEDIUM | `DhApiRenderProxy.java` |
| 65 | LOD rendering issue with Photon shaders | HIGH | SHADER | FIX_PROPOSED | MEDIUM | `GlDhTerrainShaderProgram.java` |
| 66 | LOD rendering issue with Solas shader | HIGH | SHADER | FIX_PROPOSED | MEDIUM | Same as #65 |
| 67 | Mineshot Camera - terrain disappears | HIGH | COMPATIBILITY | FIX_PROPOSED | HIGH | `RenderBufferHandler.java` |
| 69 | Distant Horizons Renderer Error | HIGH | RENDERING | NEEDS_MORE_INFO | LOW | Unknown - need logs |
| 44 | Some Chisel blocks are invisible | MEDIUM | COMPATIBILITY | FIX_PROPOSED | MEDIUM | `BlockStateWrapper.java` |
| 42 | Blindness, underwater overlays opaque | MEDIUM | RENDERING | FIX_PROPOSED | HIGH | `RenderHelper.java` |

---

## Issue Clusters

### Cluster A: Shader Integration (#64, #65, #66)
**Root Cause:** DH's shader integration doesn't properly detect or adapt to different shader packs

**Key Findings:**
- `deferTransparentRendering` defaults to `false` - should detect shader state
- No per-shader compatibility configuration
- Generic shader integration doesn't handle pack-specific quirks

**Recommended Fix Order:**
1. Add dynamic shader detection (#64)
2. Implement shader-specific compatibility layer (#65, #66)
3. Document known-working configurations

### Cluster B: OpenGL State Management (#42, #56 from Batch 1)
**Root Cause:** OpenGL state not preserved across DH rendering

**Key Findings:**
- `GL_BLEND` disabled unconditionally
- `GL_ALPHA_TEST` manipulated without state preservation
- `glClearColor` with alpha 0 causes issues

**Files Affected:**
- `RenderHelper.java` - Main culprit

### Cluster C: Mod Compatibility (#44, #67)
**Root Cause:** Custom rendering mods not handled

**Key Findings:**
- Mineshot camera override breaks frustum culling
- Chisel custom blocks not sampled correctly

---

## Key Findings

### High Confidence Fixes

1. **#42 - Overlay Opacity** (HIGH confidence)
   - `RenderHelper.java:37` disables `GL_BLEND` unconditionally
   - **Fix:** Save/restore blend state

2. **#67 - Mineshot Compatibility** (HIGH confidence)
   - Frustum culling uses player position, not camera position
   - **Fix:** Add config to disable culling for camera mods

### Medium Confidence Fixes

3. **#64 - Shader Detection** (MEDIUM confidence)
   - `deferTransparentRendering` should detect shader state
   - **Fix:** Add shader state detection at world load

4. **#65/#66 - Shader Compatibility** (MEDIUM confidence)
   - Need shader-specific rendering modes
   - **Fix:** Per-shader configuration

### Needs More Information

5. **#69 - Renderer Error** (LOW confidence)
   - Title too generic - need logs
   - **Action:** Request crash logs

---

## Code Quality Issues

| Issue | Severity | Count | Files |
|-------|----------|-------|-------|
| OpenGL state not preserved | HIGH | 3 | `RenderHelper.java` |
| No shader state detection | MEDIUM | 1 | `DhApiRenderProxy.java` |
| Missing mod compatibility | MEDIUM | 2 | `RenderBufferHandler.java`, `BlockStateWrapper.java` |

---

## Recommended Fix Priority

### Immediate
1. **#42** - Overlay opacity (HIGH confidence, affects gameplay)
2. **#67** - Mineshot compatibility (HIGH confidence, affects content creators)

### Short Term
3. **#64** - Shader detection (MEDIUM confidence, affects shader users)
4. **#65/#66** - Shader compatibility (group fix)

### Requires More Info
5. **#69** - Need error logs to proceed

### Documentation
6. **#44** - Chisel blocks (document limitation or add compatibility)

---

## Cross-Batch Patterns

### OpenGL State Management (Batch 1 #56 + Batch 2 #42)
Both issues caused by `RenderHelper.java` not preserving OpenGL state:
- #56: `glClearColor` and `GL_ALPHA_TEST`
- #42: `GL_BLEND`

**Recommendation:** Audit all of `RenderHelper.java` for state preservation.

### Shader Integration (Batch 2 #64, #65, #66)
Multiple related shader issues suggesting systematic approach needed.

---

## Files Most Frequently Implicated

| File | Issues Affected | Change Type |
|------|-----------------|-------------|
| `RenderHelper.java` | #42, #56 (from Batch 1) | OpenGL state preservation |
| `DhApiRenderProxy.java` | #64 | Shader detection |
| `RenderBufferHandler.java` | #67 | Frustum culling |
| `GlDhTerrainShaderProgram.java` | #65, #66 | Shader compatibility |
| `BlockStateWrapper.java` | #44 | Block handling |

---

## Artifacts Generated

- 7 × `issue_NN_analysis.json` - Forensic gap analysis
- 7 × `issue_NN_comment.md` - Copy-paste ready GitHub comments
- 1 × `BATCH2_MASTER_REPORT.md` - This file

---

*Investigation performed using orthogonal-engineering forensic methodology.*
