# Devin AI Onboarding Document

**Date:** 2026-04-06  
**Purpose:** Quick-start guide for Devin AI sessions on orthogonal-engineering  
**Read this FIRST before any other task**

---

## 1. Repository Overview

**orthogonal-engineering** is a topos-theoretic governance framework implementing multi-layered logical structures for AI-agent coordination, verification, and cross-repository integrity.

### The 3 Core Repositories

1. **orthogonal-engineering** (this repo) - Main governance framework
2. **truthsystems-mod** - Minecraft mod integration layer
3. **sigma-lora-covenant** - Distributed covenant system

### Key Schema Files

| File | Purpose |
|------|---------|
| `YESHUA_SYSTEM_SCHEMA.yaml` | Core system schema defining the topos structure |
| `INCURSION_ATOMIC_INTEGRITY_SCHEMA.yaml` | Atomic integrity constraints |
| `ontology/ontology.json` | Formal ontology definitions |
| `RESTORATION-POLYMATHIC-001.txt` | Polymathic restoration protocol |

---

## 2. Current State of Operations

### Operation: SOVEREIGN TOPOS (PR #100)

**Branch:** `sovereign-topos/operation-main`  
**Status:** 40 of 133 domains complete (Batches 1-5 finished)

#### Layer Completion Status

| Layer | Type | Domains Complete | Status |
|-------|------|------------------|--------|
| 0 | Supranational | 7/7 | ✅ COMPLETE |
| 1 | Constitutional | 8/8 | ✅ COMPLETE |
| 2 | Statutory | 25/25 | ✅ COMPLETE |
| 3 | Regulatory | 0/93 | 🔄 NEXT BATCH |
| 4 | Institutional | 0/0 | ⏳ PENDING |

#### Known Issues
- **Bug:** `d_weapons_regulation` domain has undefined variable (`days_eligible` should be `days_elapsed`)
- **CI Status:** 29/29 tests passing as of commit `d658261`
- **Executor:** Kimi Code CLI is executing this operation in batches

#### Domain Structure
```
src/domains/d_{name}/
├── domain.py           # Domain definition
├── implementation.py   # Implementation logic
├── invariants.py       # Invariant checks
└── tests/
    └── test_f_{name}_001.py  # Test file (naming convention)
```

### DistantHorizons Investigation

**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone

#### Status by Issue

| Issue | Status | Notes |
|-------|--------|-------|
| #56 | RESOLVED | Fix implemented by DarkShadow44 (commit 2a13ce7), awaiting branman5949 test |
| #51 | IN PROGRESS | Corrected forensics completed 2026-04-06, server log NOT FOUND |
| #62 | PENDING | Server crashing - next priority after #51 |

#### Investigation File Locations
```
investigations/darkshadow44/DistantHorizonsStandalone/
├── batch1/                    # Initial investigations (may have errors)
├── batch2/
├── batch3/
├── batch4/
├── issue_51_corrected/        # CORRECTED analysis with verified line numbers
├── issue_56_corrected/        # CORRECTED analysis
└── FINAL_MASTER_REPORT.md     # Complete issue matrix (25 issues)
```

**⚠️ CRITICAL LESSON from Issue #56:**
The Batch 1 analysis for #56 was **WRONG** because it analyzed source code without reading the crash log first. Always follow **Artifact Primacy** - logs outrank source code speculation.

---

## 3. Key Patterns and Conventions

### SAL (Sheaf Abstraction Layer)

Located in `src/sal/`:
- `topos_subobject_classifier.py` - Core topos logic
- `forcing_operation.py` - CardinalStrength and forcing operations
- `global_merkle.py` - Cross-repo merkle tree integrity
- `cross_repo_adjunction.py` - Repository adjunction morphisms

### Patterns Directory

Located in `src/patterns/` - 10 reusable patterns:
- `nehemiah_wall` - Boundary enforcement
- (others as defined in schema)

### Layers System

Located in `src/layers/`:
- `layer_model.py` - Layer definitions
- `inter_layer_morphism.py` - Layer transformations

### Testing Conventions

- **Framework:** pytest
- **Naming:** `test_f_{domain}_{number}.py`
- **Example:** `test_f_criminal_procedure_001.py`

### Anti-Fabrication System

- **pr49_guard.py** - Validates all PRs for fabrication
- **consent_log.jsonl** - Authorizes mass changes (REQUIRED for CI pass)
- **Rule:** NEVER commit session log files to repo (use GitHub UI for those)

---

## 4. Key People and AI Agents

| Entity | Role |
|--------|------|
| **aidoruao** | User/operator - the human in the loop |
| **Kimi Code CLI** | Coding agent (kimi-k2.5, 262k context) |
| **Devin AI** | Task planning, technical Q&A (you) |
| **GitHub Copilot** | CI agent, code assistance |
| **DarkShadow44** | DistantHorizonsStandalone maintainer |
| **branman5949** | DH issue #56 reporter |
| **MrFuzzihead** | DH issue #51 reporter |

---

## 5. What NOT to Do

### ❌ Critical Prohibitions

1. **Do NOT trust Batch 1 analysis files without verification**
   - Lesson from #56: Batch 1 had wrong root cause
   - Always verify line numbers against current source code

2. **Do NOT use `return True` stubs in domain invariants**
   - Invariants must have actual validation logic
   - Stubs will fail CI

3. **Do NOT redefine CardinalStrength**
   - Import from `src/sal/forcing_operation.py`

4. **Do NOT commit session log files to the repo**
   - These go on main via GitHub UI only

5. **Do NOT skip the consent_log.jsonl entry for mass changes**
   - CI will fail without proper authorization

### ❌ Line Number Anti-Pattern

**DON'T:** Copy line numbers from previous analyses without verification  
**DO:** Always grep current source code to verify line numbers

**Example from Issue #51:**
```
Batch 1 claimed: serverTickEvent at lines 117-144
Actual (current): serverTickEvent at lines 105-141
Result: SHIFTED by ~12 lines
```

---

## 6. Immediate Next Actions

### For SOVEREIGN TOPOS Operation

1. **Continue with Batch 6** (Layer 3 Regulatory domains)
   - 93 domains remaining
   - Follow domain structure template
   - Run tests after each domain

### For DistantHorizons Investigation

1. **Post corrected #51 comment** to DarkShadow44's repo
   - File: `investigations/darkshadow44/DistantHorizonsStandalone/issue_51_corrected/issue_51_CORRECTED_comment.md`
   - Note: Server log was NOT FOUND - comment reflects source code verification only

2. **Next issue after #51:** #62 (server crashing)
   - Location: `investigations/darkshadow44/DistantHorizonsStandalone/batch1/issue_62_analysis.json`
   - Verify line numbers against current DarkShadow44 source

### For All Tasks

1. **Verify line numbers** - Always grep current source, never trust old analysis
2. **Run tests** - `pytest` before committing
3. **Update consent_log** - For mass changes
4. **Follow Artifact Primacy** - Logs > crash reports > source speculation

---

## 7. Quick Commands

```bash
# Run tests
cd ~/orthogonal-engineering && pytest

# Verify DH source code line numbers
cd ~/DistantHorizonsStandalone
grep -n "serverTickEvent\|nanoTime\|MILLISECONDS" src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java

# Check CI status
cd ~/orthogonal-engineering && git status

# Domain creation (SOVEREIGN TOPOS)
cd ~/orthogonal-engineering/src/domains
# Use template from existing d_* directories
```

---

## 8. Context Budget Reference

| Phase | Expected Context Usage |
|-------|----------------------|
| After housekeeping | ~15% |
| After source verification | ~30% |
| After log analysis | ~50% |
| After file creation | ~70% |
| **HALT THRESHOLD** | **80% (209k tokens)** |

If you hit 80% context usage, commit current work and start a new session.

---

## 9. Emergency Contacts

- **User/Operator:** aidoruao (ask via chat)
- **Session Logs:** Check `.kimi/logs/` or GitHub UI
- **State Issues:** Check `STATE.md` and `STATUS_DASHBOARD.html`

---

## 10. DarkShadow44 Vendored Repository System

### 10.1 What It Is

5 of DarkShadow44's public repositories vendored into `investigations/darkshadow44/` with full source trees, SHA-256 manifests, and non-affiliation statements. Purpose: eliminate epistemic dependency on external clones so AI orchestrators can verify source-level claims directly.

### 10.2 Repository Inventory

| Repository | Files | Java Files | LOC | Commit | License |
|------------|-------|-----------|-----|--------|---------|
| DistantHorizonsStandalone | 669 | 601 | 84,441 | 1abcd98 | GPL-3.0 |
| Angelica | 1,292 | 1,185 | 100,467 | cd42307 | LGPL-3.0 |
| Spool | 158 | 145 | 20,195 | e2db38b | LGPL-3.0 |
| ArchaicFix | 190 | 177 | 9,149 | 85b33af | LGPL-3.0 |
| SeasonalHorizons | 51 | 25 | 1,336 | ad10038 | LGPL-2.1 |
| **Total** | **2,360** | **2,133** | **215,588** | | |

### 10.3 Per-Repo Structure

```
investigations/darkshadow44/{RepoName}/
├── VENDOR_MANIFEST.json      # commit hash, clone date, SHA-256 tree root
├── ATTRIBUTION.md            # license + non-affiliation statement
├── LICENSE                   # original license verbatim
├── sha256_manifest.txt       # per-file SHA-256 hashes
├── SOURCE_INDEX.json         # method/field/class census
├── WIKI.md                   # ontological wiki
└── src/                      # actual vendored source tree (immutable)
```

### 10.4 How to Verify a Source Claim

**Example workflow:**
1. **Claim:** "ForgeServerProxy.java line 124 has 15ms budget"
2. **Read:** `investigations/darkshadow44/DistantHorizonsStandalone/src/main/java/com/seibel/distanthorizons/forge/ForgeServerProxy.java` line 124
3. **Verify:** Check `sha256_manifest.txt` for the file hash
4. **Provenance:** `VENDOR_MANIFEST.json` shows commit + clone date

### 10.5 Issue #51 Current Status

- **Jan 9:** DarkShadow44 acknowledged chunk generation on main thread
- **Apr 6:** aidoruao posted corrected forensics (two root causes identified)
- **Apr 6:** aidoruao attached patch `0001-issue51-tick-handler-fix.patch`
- **Apr 7:** DarkShadow44 requested profiler data ("Need to see actual bottleneck")
- **Apr 8:** aidoruao posted 3 analytical tools (benchmark, diagnostics, gradle)
- **Current:** No response from DarkShadow44 since Apr 7; issue remains open

**Location of tools:** `investigations/darkshadow44/DistantHorizonsStandalone/tools/`

### 10.6 The Epistemic Gap

**DarkShadow44 wants:** Spark profiler data from actual server runtime  
**aidoruao provided:** Analytical tools for synthetic benchmarking

**The structural argument:** The defect is provable from source analysis (π × 4096² = 52.7M blocks²). This is a combinatorial defect, not a runtime hotspot. Profiler data shows aggregate symptoms, not factorial decomposition.

### 10.7 AI Orchestrator Coordination

| Orchestrator | Data Source | Staleness Risk |
|--------------|-------------|----------------|
| Devin | GitHub API (indexed) | High - periodic re-index required |
| Kimi CLI | Local filesystem | Low - always current |
| GitHub Copilot | GitHub API | Medium - near real-time |

**To sync Devin:** Trigger re-index in Devin UI after significant commits.

**Deterministic state:** Vendored source + SHA-256 hashes make state verifiable regardless of which orchestrator reads it.

### 10.8 Key People

| Person/AI | Role | Contact |
|-----------|------|---------|
| aidoruao | Project owner, operator | Chat |
| DarkShadow44 | DistantHorizonsStandalone maintainer | GitHub issues |
| Devin AI | External AI (Ask mode) | This onboarding |
| Kimi CLI | Primary executor | `.kimi/logs/` |
| DeepSeek AI | External AI consulted for fact-checking | N/A |
| Gemini AI | External AI consulted for verification | N/A |

---

*Last Updated: 2026-04-08 by Kimi Code CLI (Devin session knowledge codification)*  
*Session: DH Vendoring + Onboarding Updates*
