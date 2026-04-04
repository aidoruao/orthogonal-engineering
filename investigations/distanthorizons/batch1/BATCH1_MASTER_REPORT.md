# DistantHorizonsStandalone - Batch 1 Investigation Report

**Date:** 2026-04-04  
**Pipeline:** DH-STANDALONE-001  
**Issues:** 7 (Critical/High priority)  
**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone

---

## Summary Table

| # | Title | Priority | Category | Status | Confidence | Fix Location |
|---|-------|----------|----------|--------|------------|--------------|
| 72 | GTNH crashing when this mod is added | CRITICAL | CRASH | FIX_PROPOSED | MEDIUM | `ForgeMain.java`, `GTCompat.java` |
| 62 | Server crashing with the latest alpha16 | CRITICAL | CRASH | FIX_PROPOSED | MEDIUM | `ForgeServerProxy.java` |
| 56 | Screen is Black and then Crashes when Angelica isn't Present | CRITICAL | CRASH | FIX_PROPOSED | HIGH | `RenderHelper.java` |
| 53 | Server boot issue | CRITICAL | SERVER | FIX_PROPOSED | MEDIUM | `ForgeMain.java`, `ForgeServerProxy.java` |
| 51 | Getting pretty severe TPS when installed on server | HIGH | PERFORMANCE | FIX_PROPOSED | HIGH | `ForgeServerProxy.java` |
| 40 | Nether gets stuck on generating chunks | HIGH | WORLD_GENERATION | FIX_PROPOSED | MEDIUM | `BatchGenerationEnvironment.java` |
| 73 | LODs not rendering caves properly / at all | HIGH | RENDERING | GAP_IDENTIFIED* | HIGH | N/A - By Design |

*Issue #73 is documented behavior, not a bug. Would require feature enhancement.

---

## Issue Clusters

### Cluster A: Server Stability (#51, #53, #62)
**Root Cause:** Server event handlers lack defensive programming (null checks, time budgets, error handling)

**Files Affected:**
- `ForgeServerProxy.java` - Multiple event handlers
- `ForgeMain.java` - Server initialization

**Recommended Fix Order:**
1. Add null checks to event handlers (#62, #53)
2. Reduce time budget for tick processing (#51)
3. Add error handling around ServerApi calls

### Cluster B: Mod Compatibility (#56, #72)
**Root Cause:** Optional dependencies (Angelica, GTNH) not properly validated

**Files Affected:**
- `ForgeMain.java` - Compatibility class instantiation
- `RenderHelper.java` - Angelica null path rendering
- `GTCompat.java` - GTNH integration

**Recommended Fix Order:**
1. Add version checking for GTNH (#72)
2. Fix OpenGL state management without Angelica (#56)

### Cluster C: World Generation (#40)
**Root Cause:** Unbounded queue + no timeout for generation events

**Files Affected:**
- `BatchGenerationEnvironment.java` - Event queue management

---

## Key Findings

### Critical Issues

1. **RenderHelper OpenGL State (#56)**
   - `glClearColor(1, 1, 1, 0.0F)` clears to transparent
   - Alpha test disable/enable without state preservation
   - **Fix:** Save/restore complete GL state

2. **Server Tick Handler (#51)**
   - 15ms time budget too aggressive
   - Unbounded chunk event queue iteration
   - **Fix:** 5ms budget + limit events per tick

3. **ForgeServerProxy Null Safety (#62, #53)**
   - Multiple event handlers without null checks
   - No error handling around ServerApi calls
   - **Fix:** Defensive programming throughout

### Documentation Gap (#73)

Cave rendering is **explicitly excluded by design** (`EDhApiDistantGeneratorMode.java:62`). This should be:
- Better documented in user-facing materials
- Considered as potential enhancement (with performance warnings)

---

## Code Quality Issues Identified

| Issue | Severity | Count | Files |
|-------|----------|-------|-------|
| Missing null checks | HIGH | 5+ | `ForgeServerProxy.java` |
| Unbounded queue iteration | HIGH | 2 | `ForgeServerProxy.java`, `BatchGenerationEnvironment.java` |
| No error handling | MEDIUM | 3 | `ForgeMain.java`, `ForgeServerProxy.java` |
| Aggressive time budgets | MEDIUM | 1 | `ForgeServerProxy.java` |
| OpenGL state not preserved | MEDIUM | 1 | `RenderHelper.java` |

---

## Recommended Fix Priority

### Immediate (Before Next Release)
1. **#56** - Black screen without Angelica (HIGH confidence, clear fix)
2. **#51** - TPS lag (HIGH confidence, affects all servers)
3. **#62** - Server crash (MEDIUM confidence, defensive fix is safe)

### Short Term (Next Sprint)
4. **#53** - Server boot issue (same code path as #62)
5. **#40** - Nether generation stuck (add timeouts)
6. **#72** - GTNH crash (add version checking)

### Documentation
7. **#73** - Document that caves are not rendered; consider enhancement

---

## Files Most Frequently Implicated

| File | Issues Affected | Change Type |
|------|-----------------|-------------|
| `ForgeServerProxy.java` | #51, #53, #62 | Defensive programming |
| `ForgeMain.java` | #53, #72 | Error handling, version checks |
| `RenderHelper.java` | #56 | OpenGL state management |
| `BatchGenerationEnvironment.java` | #40, #51 | Queue management, timeouts |
| `GTCompat.java` | #72 | Version validation |

---

## Artifacts Generated

- `issue_72_analysis.json` + `issue_72_comment.md` - GTNH crash
- `issue_62_analysis.json` + `issue_62_comment.md` - Server crash
- `issue_56_analysis.json` + `issue_56_comment.md` - Black screen
- `issue_53_analysis.json` + `issue_53_comment.md` - Server boot
- `issue_51_analysis.json` + `issue_51_comment.md` - TPS lag
- `issue_40_analysis.json` + `issue_40_comment.md` - Nether generation
- `issue_73_analysis.json` + `issue_73_comment.md` - Cave rendering
- `BATCH1_MASTER_REPORT.md` - This file

---

*Investigation performed using orthogonal-engineering forensic methodology.*
*Total Java files in codebase: 601*
