# 🧭 LEVEL 2: 5-MINUTE PROJECT ORIENTATION

## ⏱️ **READ TIME:** 5 minutes maximum
## ✅ **PREREQUISITE:** You MUST have read LEVEL1.md first
## 🎯 **PURPOSE:** Understand project structure and current focus

---

## 📊 PROJECT AT A GLANCE

**Repository:** `orthogonal-engineering-clean`  
**Files:** 3,001 files (27MB)  
**Core Concept:** Glass-Box Boundary enforcement  
**Current Version:** v0.2.0 (mathematically formalized)  
**Status:** Ready for GitHub deployment

**Key Insight:** This is NOT a typical codebase. It's a **methodology framework** with enforcement mechanisms.

---

## 🏗️ PROJECT STRUCTURE (5 MAIN DIRECTORIES)

### 1. **`automation/`** - ACTIVE ENFORCEMENT
```
automation/
├── run_full_audit_with_trace.py    # ⭐ MAIN ENFORCEMENT SCRIPT
├── generate_sha256_manifest.py     # Artifact validation
└── zed_incremental_hook.py         # IDE integration
```
**Purpose:** Glass-Box Boundary enforcement scripts  
**Current Focus:** Exit code 2 on boundary violations

### 2. **`documentation/`** - AUTHORITY SOURCES
```
documentation/
├── GLASS_BOX_BOUNDARY_v1.11.html   # ⭐ BLUEPRINT AUTHORITY
├── FORMAL_FOUNDATIONS.md           # Mathematical proofs
└── EPISTEMIC_CLOSURE.json          # Validation manifests
```
**Purpose:** Single source of truth for all rules  
**Rule:** HTML file is authoritative, code implements it

### 3. **`toolkit/`** - REUSABLE COMPONENTS
```
toolkit/
├── oe/                             # Orthogonal Engineering core
│   ├── evidence_store.py           # Trace storage
│   └── boundary_enforcer.py        # Decorator factory
└── workflows/                      # Predefined workflows
```
**Purpose:** Reusable enforcement components  
**Usage:** Import and extend for new projects

### 4. **`analysis/`** - VALIDATION & TESTING
```
analysis/
├── canonical_processor.py          # Chat analysis
├── failure_analyzer.py             # Breakdown analysis
└── correspondence_validator.py     # Cross-validation
```
**Purpose:** Validate methodology against real data  
**Data:** 600+ conversations, 233GB processed

### 5. **`onboarding/`** - YOU ARE HERE
```
onboarding/
├── LEVEL1.md                       # ✅ You read this
├── LEVEL2.md                       # ⭐ You are here
├── LEVEL3.md                       (Context navigation)
└── LEVEL4.md                       (Deep dive - optional)
```
**Purpose:** Prevent AI information overload  
**Rule:** Always follow hierarchical onboarding

---

## 🎯 CURRENT ACTIVE FOCUS

### **Glass-Box Boundary v1.11**
- **Authority:** `documentation/GLASS_BOX_BOUNDARY_v1.11.html`
- **Enforcement:** `automation/run_full_audit_with_trace.py`
- **Goal:** Exit code 2 on any boundary violation
- **Status:** Active development and refinement

### **Key Enforcement Mechanisms:**
1. **`@glass_box_boundary` decorator** - Wraps all Python functions
2. **Input/output validation schemas** - JSON schema validation
3. **Side effect gateways** - Confined external access
4. **Trace generation** - Complete audit trail
5. **Fail-fast architecture** - Exit code 2 on violations

---

## 🔄 WORKFLOW PROTOCOL

### **Standard Development Flow:**
```
1. Check HTML blueprint (documentation/GLASS_BOX_BOUNDARY_v1.11.html)
2. Update Python enforcer (automation/run_full_audit_with_trace.py)
3. Run validation: python automation/run_full_audit_with_trace.py
4. Check exit code: 0 = success, 2 = boundary violation
5. Fix violations, repeat from step 3
```

### **Git Protocol:**
- **Branch:** `main` only (simplicity over complexity)
- **Commits:** Descriptive, trace-linked messages
- **Push:** After validation passes (exit code 0)
- **Never:** Commit with boundary violations (exit code 2)

---

## 🚨 CRITICAL PATHS TO KNOW

### **UI → Database Detection:**
```
# BAD (boundary violation):
ui_button.click() → database.insert()

# GOOD (boundary compliant):
ui_button.click() → gateway.validate() → repository.insert()
```

### **Suppressed Signal Detection:**
```python
# BAD (boundary violation):
try:
    risky_operation()
except Exception:
    pass  # ❌ Signal suppressed!

# GOOD (boundary compliant):
try:
    risky_operation()
except Exception as e:
    logger.error(f"Boundary violation: {e}")
    sys.exit(2)  # ✅ Fail-fast with exit code 2
```

### **Missing Artifact Detection:**
- Every operation must produce documented artifacts
- Missing artifacts = boundary violation
- Artifacts must be SHA256-hashed and logged

---

## 📋 QUICK VERIFICATION SCRIPT

**Run this to check basic health:**
```bash
cd /c/Users/Aidor/Documents/orthogonal-engineering-clean
python automation/run_full_audit_with_trace.py --quick-check
```

**Expected output:**
- Exit code 0: System healthy
- Exit code 2: Boundary violations found (check logs)
- Any other exit code: System error

---

## 🧩 CONTEXT AWARENESS PROTOCOL

**Based on user request, navigate appropriately:**

| User asks about... | Go to... | Key files |
|-------------------|----------|-----------|
| **Git/sync** | `documentation/OE_GIT_SYNC.md` | Also check `ABSOLUTE_GIT_SYNC_PROOF.md` |
| **Automation** | `automation/` directory | `run_full_audit_with_trace.py` is main |
| **Theory/math** | `FORMAL_FOUNDATIONS.md` | Complete mathematical proofs |
| **Deployment** | `_START_HERE.md` | GitHub deployment guide |
| **Failures** | `FAILURES.md` | Known failure modes |
| **Validation** | `analysis/` directory | Canonical processor, validators |
| **Boundary rules** | `AGENT.md` | Your enforcement authority |

**Use `onboarding/LEVEL3.md` for detailed navigation.**

---

## 🔍 TROUBLESHOOTING COMMON ISSUES

### **Issue: "Chat seems dead or unresponsive"**
- **Check:** Are we in OneDrive? (Should be in `C:\Users\Aidor\Documents\`)
- **Fix:** Use clean location: `orthogonal-engineering-clean`
- **Root cause:** OneDrive sync corruption (the "grenade")

### **Issue: "Git operations failing strangely"**
- **Check:** `git status` shows weird conflicts
- **Fix:** Ensure not in OneDrive, clone fresh if needed
- **Root cause:** OneDrive file locking

### **Issue: "Exit code 2 but don't know why"**
- **Check:** `logs/` directory for violation reports
- **Fix:** Read report, apply suggested fixes
- **Root cause:** Boundary violation (intentional fail-fast)

### **Issue: "Too many files, don't know where to start"**
- **Check:** You skipped onboarding levels
- **Fix:** Go back to LEVEL1.md, follow hierarchy
- **Root cause:** Information overload

---

## 📚 NEXT STEPS BASED ON YOUR ROLE

### **If you're here for general maintenance:**
1. Run verification script (above)
2. Check git status
3. Review recent commits
4. Ensure no boundary violations

### **If you're here for specific development:**
1. Identify which subsystem (use table above)
2. Go to relevant directory
3. Check HTML blueprint for requirements
4. Implement with boundary decorators

### **If you're here for methodology understanding:**
1. Read `FORMAL_FOUNDATIONS.md` (mathematics)
2. Read `_START_HERE.md` (overview)
3. Explore `analysis/` (validation data)
4. Check `FAILURES.md` (limitations)

### **If you're here for deployment:**
1. Read `_START_HERE.md` completely
2. Follow deployment steps
3. Verify all 12 core files exist
4. Activate GitHub Pages

---

## ✅ COMPLETION CHECKLIST

**You have completed Level 2 when:**
- [ ] You understand the 5 main directory purposes
- [ ] You know the current focus is Glass-Box Boundary v1.11
- [ ] You can run the verification script
- [ ] You know where to go based on user requests
- [ ] You understand exit code 2 is intentional fail-fast

**Time check:** 5 minutes should be up. If you rushed, go back and read properly.

---

## 🚀 PROCEED TO USER REQUEST

**You are now ready to:**  
1. **Check the user's actual request**  
2. **Use `onboarding/LEVEL3.md` for context-aware navigation**  
3. **Apply Glass-Box Boundary principles to all work**

**Remember:** Every file modification must comply with boundary rules.  
**Exit code 2 is your friend** - it catches violations early.

---

## 🔗 QUICK REFERENCE

```
AGENT.md                          # Your authority
_START_HERE.md                    # Project overview  
automation/run_full_audit_with_trace.py  # Main enforcement
documentation/GLASS_BOX_BOUNDARY_v1.11.html  # Blueprint
onboarding/LEVEL3.md              # Context navigation (next)
```

**Now proceed to handle the user's actual request.**