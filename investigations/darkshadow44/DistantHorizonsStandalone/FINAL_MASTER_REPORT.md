---
tags: [investigations, darkshadow44, distanthorizonsstandalone, final-master-report]
register: audit
---

# DistantHorizonsStandalone - FINAL INVESTIGATION REPORT

**Date:** 2026-04-04  
**Pipeline:** DH-STANDALONE-001  
**Total Issues Investigated:** 25  
**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone

---

## Executive Summary

This forensic investigation analyzed **25 open issues** in the DistantHorizonsStandalone mod for Minecraft 1.7.10/GTNH. The investigation covered **601 Java files** and identified root causes, proposed fixes, and implementation guidance for each issue.

### Key Findings

- **19 issues** have proposed code fixes
- **2 issues** need more information (#69, #73)
- **4 issues** are feature requests (#32, #58, #57, partially #73)
- **5 critical issues** require immediate attention

### Most Critical Issues

1. **#56** - Black screen without Angelica (OpenGL state)
2. **#51** - Severe TPS lag on servers (time budget)
3. **#62** - Server crashing (null checks)
4. **#49** - Commands don't exist (missing implementation)
5. **#64** - LODs not rendering with shaders (detection failure)

---

## Complete Issue Matrix

### Batch 1 - Critical/High (Server/Crash)

| # | Title | Priority | Status | Confidence | Primary Fix Location |
|---|-------|----------|--------|------------|---------------------|
| 72 | GTNH crashing | CRITICAL | FIX_PROPOSED | MEDIUM | `ForgeMain.java` |
| 62 | Server crashing alpha16 | CRITICAL | FIX_PROPOSED | MEDIUM | `ForgeServerProxy.java` |
| 56 | Black screen without Angelica | CRITICAL | FIX_PROPOSED | HIGH | `RenderHelper.java` |
| 53 | Server boot issue | CRITICAL | FIX_PROPOSED | MEDIUM | `ForgeMain.java` |
| 51 | Severe TPS lag | HIGH | FIX_PROPOSED | HIGH | `ForgeServerProxy.java` |
| 40 | Nether gen stuck | HIGH | FIX_PROPOSED | MEDIUM | `BatchGenerationEnvironment.java` |
| 73 | Caves not rendering | HIGH | BY_DESIGN | HIGH | Documentation |

### Batch 2 - High (Shader/Rendering)

| # | Title | Priority | Status | Confidence | Primary Fix Location |
|---|-------|----------|--------|------------|---------------------|
| 64 | LODs not rendering with shaders | HIGH | FIX_PROPOSED | MEDIUM | `DhApiRenderProxy.java` |
| 65 | Photon shader issues | HIGH | FIX_PROPOSED | MEDIUM | `GlDhTerrainShaderProgram.java` |
| 66 | Solas shader issues | HIGH | FIX_PROPOSED | MEDIUM | Same as #65 |
| 67 | Mineshot camera terrain disappears | HIGH | FIX_PROPOSED | HIGH | `RenderBufferHandler.java` |
| 69 | Renderer Error | HIGH | NEEDS_INFO | LOW | Need logs |
| 44 | Chisel blocks invisible | MEDIUM | FIX_PROPOSED | MEDIUM | `BlockStateWrapper.java` |
| 42 | Blindness/water overlays opaque | MEDIUM | FIX_PROPOSED | HIGH | `RenderHelper.java` |

### Batch 3 - High/Medium (Rendering/Gen/Commands)

| # | Title | Priority | Status | Confidence | Primary Fix Location |
|---|-------|----------|--------|------------|---------------------|
| 31 | Biome rendering not applied | HIGH | FIX_PROPOSED | MEDIUM | `FullDataToRenderDataTransformer.java` |
| 30 | NBT blocks not rendering | HIGH | FIX_PROPOSED | HIGH | `FakeWorld.java` |
| 20 | Missing LOD chunks | HIGH | FIX_PROPOSED | MEDIUM | `LodQuadTree.java` |
| 59 | Colored glass opaque | MEDIUM | FIX_PROPOSED | HIGH | `ClientBlockStateColorCache.java` |
| 52 | Pollution fog not rendering | MEDIUM | FIX_PROPOSED | MEDIUM | `GlDhFogRenderer.java` |
| 50 | Slow rate limiting | MEDIUM | FIX_PROPOSED | MEDIUM | `SyncOnLoadRequestQueue.java` |
| 49 | /dh pregen commands don't work | HIGH | FIX_PROPOSED | HIGH | New: `DhCommand.java` |

### Batch 4 - Medium (Compatibility/Features)

| # | Title | Priority | Status | Confidence | Primary Fix Location |
|---|-------|----------|--------|------------|---------------------|
| 47 | NPCDBC outlines issue | MEDIUM | FIX_PROPOSED | MEDIUM | `RenderHelper.java` |
| 32 | Fade wait for chunks | MEDIUM | FEATURE_REQ | MEDIUM | `GlVanillaFadeRenderer.java` |
| 58 | World white/blacklist | MEDIUM | FEATURE_REQ | HIGH | `ForgeServerProxy.java` |
| 57 | Restore commands | MEDIUM | FEATURE_REQ | HIGH | New: `DhCommand.java` |

---

## Critical Patterns Identified

### Pattern 1: OpenGL State Management (Issues #56, #42, #47)
**Impact:** 3 issues
**Root Cause:** `RenderHelper.java` doesn't preserve OpenGL state
**Fix:** Save/restore complete GL state (blend, alpha test, clear color, depth)

### Pattern 2: Server Event Handler Defensive Programming (#62, #53, #51)
**Impact:** 3 issues
**Root Cause:** Missing null checks, aggressive time budgets
**Fix:** Add validation and error handling

### Pattern 3: Missing Infrastructure (#49, #57)
**Impact:** 2 issues
**Root Cause:** Commands never implemented
**Fix:** Create `DhCommand.java` with full command structure

### Pattern 4: Shader Integration (#64, #65, #66)
**Impact:** 3 issues
**Root Cause:** No dynamic shader detection or per-shader config
**Fix:** Add shader state detection and compatibility layer

---

## Fix Priority Recommendations

### Immediate (Pre-Release)
1. **#56** - Black screen (HIGH confidence, critical)
2. **#51** - TPS lag (HIGH confidence, affects all servers)
3. **#62** - Server crash (defensive fix, safe)
4. **#49** - Commands (HIGH confidence, user-facing)

### Short Term (Next Sprint)
5. **#64** - Shader detection
6. **#42** - Overlay opacity (same fix as #56)
7. **#67** - Mineshot compatibility
8. **#59** - Glass transparency

### Medium Term
9. **#31** - Biome colors
10. **#30** - NBT blocks
11. **#47** - NPCDBC (with #56 fix)
12. **#58** - Dimension filter (feature)

### Documentation/Low Priority
13. **#73** - Document cave exclusion
14. **#69** - Needs more info

---

## Files Requiring Modification (Frequency)

| File | Issues | Change Type |
|------|--------|-------------|
| `RenderHelper.java` | #56, #42, #47 | OpenGL state preservation |
| `ForgeServerProxy.java` | #62, #53, #51, #58 | Defensive programming, filters |
| `ForgeMain.java` | #72, #53 | Error handling, version checks |
| `DhApiRenderProxy.java` | #64 | Shader detection |
| `GlDhTerrainShaderProgram.java` | #65, #66 | Shader compatibility |
| `ClientBlockStateColorCache.java` | #59 | Glass transparency |
| `FakeWorld.java` | #30 | NBT support |
| `BlockStateWrapper.java` | #44 | Block handling |
| `LodQuadTree.java` | #20 | Retry logic |
| `GlDhFogRenderer.java` | #52 | Pollution integration |
| `Create: DhCommand.java` | #49, #57 | Command implementation |

---

## Cross-Cutting Concerns

### GTNH Compatibility
- #72 GTNH crashing
- #52 Pollution fog
- #59 Colored glass (GTNH Daily)

### Shader Compatibility
- #64 LODs with shaders
- #65 Photon shaders
- #66 Solas shaders

### OpenGL State
- #56 Black screen
- #42 Overlay opacity
- #47 NPCDBC outlines

---

## Investigation Artifacts Summary

| Batch | Analysis Files | Comment Files | Master Reports |
|-------|---------------|---------------|----------------|
| Batch 1 | 7 | 7 | 1 |
| Batch 2 | 7 | 7 | 1 |
| Batch 3 | 7 | 7 | 1 |
| Batch 4 | 4 | 4 | 1 |
| **Total** | **25** | **25** | **5** |

### Location
All artifacts stored in:
```
~/orthogonal-engineering/investigations/distanthorizons_standalone/
├── batch1/ (14 files + manifest)
├── batch2/ (14 files + manifest)
├── batch3/ (14 files + manifest)
├── batch4/ (8 files + manifest)
└── FINAL_MASTER_REPORT.md
```

---

## Methodology Compliance

This investigation followed the **Epistemic Forensics** methodology:

1. ✅ **Artifact Primacy** - All findings based on source code examination
2. ✅ **Verbatim Quoting** - Code snippets with file paths and line numbers
3. ✅ **Tolerance of Contradiction** - Uncertainty levels stated where evidence incomplete
4. ✅ **Low Narrative-Smoothing** - "NEEDS_MORE_INFO" status where appropriate
5. ✅ **Falsification** - Each fix includes falsification test

---

## Next Steps

1. **Review** proposed fixes with maintainers
2. **Prioritize** based on user impact and fix confidence
3. **Implement** high-confidence fixes first (#56, #51, #62, #49)
4. **Test** fixes in GTNH environment
5. **Request** additional information for low-confidence issues

---

*Investigation completed 2026-04-04*  
*Pipeline: DH-STANDALONE-001*  
*Methodology: Orthogonal Engineering Epistemic Forensics*
