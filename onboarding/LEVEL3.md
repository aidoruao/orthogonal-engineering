---
tags: [onboarding, level3]
register: documentation
---

# 🧭 LEVEL 3: CONTEXT-AWARE NAVIGATION GUIDE

## 🎯 **PURPOSE:** Intelligent file navigation based on user requests
## ✅ **PREREQUISITES:** LEVEL1.md and LEVEL2.md MUST be completed first
## ⏱️ **USAGE:** Reference this file when you need to find specific information

---

## 📋 **HOW TO USE THIS GUIDE**

1. **Identify the user's request category** (use the table below)
2. **Go to the corresponding section** 
3. **Follow the navigation path** 
4. **Read the key files** in the recommended order
5. **Return to user** with informed response

**Never skip prerequisite files.** Each builds necessary context.

---

## 🗺️ **NAVIGATION MAP BY REQUEST TYPE**

### **A. GLASS-BOX BOUNDARY ENFORCEMENT**
*User asks about: boundary rules, enforcement, exit code 2, violations*

**Navigation Path:**
```
1. PRIMARY: documentation/GLASS_BOX_BOUNDARY_v1.11.html (Blueprint authority)
2. SECONDARY: AGENT.md (Enforcement agent specification)
3. TERTIARY: automation/run_full_audit_with_trace.py (Implementation)
4. SUPPORTING: toolkit/oe/boundary_enforcer.py (Decorator factory)
```

**Key Concepts to Understand:**
- `@glass_box_boundary` decorator pattern
- Exit code 2 = boundary violation (fail-fast)
- Suppressed signal detection
- Timeline sequence validation
- Artifact scanning requirements

**Common Questions & Answers:**
- **"What triggers exit code 2?"** → Any boundary violation (missing validation, suppressed error, direct I/O)
- **"How to fix boundary violations?"** → Add decorators, implement validation, use gateways
- **"Where are the rules defined?"** → HTML blueprint is authoritative source

---

### **B. REPOSITORY STRUCTURE & ONBOARDING**
*User asks about: project layout, getting started, understanding the codebase*

**Navigation Path:**
```
1. PRIMARY: _START_HERE.md (Complete overview)
2. SECONDARY: ONBOARD_FIRST.md (Mandatory protocol)
3. TERTIARY: onboarding/LEVEL1.md & LEVEL2.md (You should know these)
4. SUPPORTING: FILE_PURPOSE_MAP.md (File classification)
```

**Key Concepts to Understand:**
- 3,001 files organized into 5 main directories
- Hierarchical onboarding prevents information overload
- Clean location vs OneDrive "grenade" zone
- Progressive disclosure principle

**Common Questions & Answers:**
- **"Where do I start?"** → Always start with ONBOARD_FIRST.md
- **"What are the main directories?"** → automation/, documentation/, toolkit/, analysis/, onboarding/
- **"Why so many files?"** → 600+ conversations processed, 233GB of validation data

---

### **C. MATHEMATICAL FOUNDATIONS & THEORY**
*User asks about: proofs, formal methods, mathematical basis, theory*

**Navigation Path:**
```
1. PRIMARY: FORMAL_FOUNDATIONS.md (Complete mathematical framework)
2. SECONDARY: documentation/EPISTEMIC_CLOSURE.json (Validation manifests)
3. TERTIARY: INVARIANTS.md (Invariant classification)
4. SUPPORTING: proof/ directory (Proof artifacts and validation)
```

**Key Concepts to Understand:**
- Benevolent Absence Theorem (with proof)
- Signal Preservation Theorem (with proof)  
- Drift Routing Theorem (with proof)
- Invariant stability guarantees
- O(n) extraction complexity

**Common Questions & Answers:**
- **"Is this mathematically rigorous?"** → Yes, see FORMAL_FOUNDATIONS.md for proofs
- **"What's the computational complexity?"** → O(n) for pattern-based, O(n log n) for parsing
- **"Has this been validated?"** → Yes, against 600+ conversations, 233GB of data

---

### **D. AUTOMATION & TOOLING**
*User asks about: scripts, automation, tools, utilities*

**Navigation Path:**
```
1. PRIMARY: automation/ directory (All enforcement scripts)
2. SECONDARY: toolkit/oe/ directory (Reusable components)
3. TERTIARY: workflows/ directory (Predefined workflows)
4. SUPPORTING: examples/ directory (Usage examples)
```

**Key Files to Examine:**
- `automation/run_full_audit_with_trace.py` - Main enforcement script
- `automation/generate_sha256_manifest.py` - Artifact validation
- `toolkit/oe/evidence_store.py` - Trace storage system
- `toolkit/oe/boundary_enforcer.py` - Decorator factory

**Common Questions & Answers:**
- **"How do I run the audit?"** → `python automation/run_full_audit_with_trace.py`
- **"What tools are available?"** → See toolkit/ directory for reusable components
- **"Are there examples?"** → Yes, in examples/ directory

---

### **E. VALIDATION & ANALYSIS**
*User asks about: testing, validation, analysis results, data*

**Navigation Path:**
```
1. PRIMARY: analysis/ directory (All analysis tools and results)
2. SECONDARY: audit_results/ directory (Audit outputs)
3. TERTIARY: evidence/ directory (Evidence collection)
4. SUPPORTING: logs/ directory (Execution logs)
```

**Key Files to Examine:**
- `analysis/canonical_processor.py` - Chat analysis pipeline
- `analysis/failure_analyzer.py` - Breakdown analysis
- `analysis/correspondence_validator.py` - Cross-validation
- `audit_results/` - Contains validation reports

**Common Questions & Answers:**
- **"What data validates this?"** → 600+ conversations, 233GB processed
- **"How are failures analyzed?"** → See failure_analyzer.py and FAILURES.md
- **"Where are validation results?"** → audit_results/ directory

---

### **F. DEPLOYMENT & GITHUB INTEGRATION**
*User asks about: deployment, GitHub, sharing, publishing*

**Navigation Path:**
```
1. PRIMARY: _START_HERE.md (Deployment guide)
2. SECONDARY: DEPLOYMENT_GUIDE.md (Step-by-step instructions)
3. TERTIARY: .github/ directory (GitHub workflows)
4. SUPPORTING: ABSOLUTE_GIT_SYNC_PROOF.md (Sync validation)
```

**Key Concepts to Understand:**
- 12-file deployment package
- GitHub Pages activation
- Repository metadata (topics, description)
- Live URLs structure

**Common Questions & Answers:**
- **"How to deploy to GitHub?"** → Follow _START_HERE.md steps
- **"What files are needed?"** → 12 core files (listed in _START_HERE.md)
- **"How to enable live demo?"** → Activate GitHub Pages in settings

---

### **G. FAILURE MODES & TROUBLESHOOTING**
*User asks about: errors, problems, debugging, issues*

**Navigation Path:**
```
1. PRIMARY: FAILURES.md (Known failure modes)
2. SECONDARY: logs/ directory (Error logs)
3. TERTIARY: debug_violation_detection.py (Debug tools)
4. SUPPORTING: system_audit_update_fixed.py (System audit)
```

**Key Concepts to Understand:**
- OneDrive "grenade" corruption
- Token context explosions
- Boundary violation patterns
- Common debugging approaches

**Common Questions & Answers:**
- **"Chat seems dead/unresponsive"** → Likely OneDrive corruption, move to clean location
- **"Git operations failing"** → Check for OneDrive sync, use clean clone
- **"Exit code 2 but don't know why"** → Check logs/ directory for violation reports

---

### **H. GIT & VERSION CONTROL**
*User asks about: git, commits, branches, sync, history*

**Navigation Path:**
```
1. PRIMARY: documentation/OE_GIT_SYNC.md (Git protocol)
2. SECONDARY: ABSOLUTE_GIT_SYNC_PROOF.md (Sync validation)
3. TERTIARY: VERIFY_GIT_SYNC_PROOF.md (Verification)
4. SUPPORTING: .gitignore (Ignore rules)
```

**Key Concepts to Understand:**
- Single branch (main) strategy
- Descriptive commit messages
- Never commit with boundary violations
- Clean location requirement (not OneDrive)

**Common Questions & Answers:**
- **"What's the git strategy?"** → Simple: main branch only, descriptive commits
- **"How to avoid sync issues?"** → Never work in OneDrive, use clean location
- **"What to include in commits?"** → Working code only (exit code 0 must pass)

---

## 🔄 **WORKFLOW INTEGRATION PATTERNS**

### **When User Asks for Code Changes:**
```
1. Check: Have I completed onboarding? (LEVEL1, LEVEL2)
2. Navigate: Use this guide to find relevant files
3. Read: Understand the existing implementation
4. Check: What does HTML blueprint require?
5. Implement: With @glass_box_boundary decorators
6. Test: Run automation/run_full_audit_with_trace.py
7. Verify: Exit code must be 0 (not 2)
8. Commit: Only if validation passes
```

### **When User Asks for Explanation:**
```
1. Check: Have I completed onboarding? (LEVEL1, LEVEL2)
2. Navigate: Use this guide to find relevant files
3. Read: Understand the key concepts
4. Synthesize: Explain in user's context
5. Reference: Point to authoritative sources
6. Offer: Next steps or deeper reading
```

### **When User Reports Problems:**
```
1. Check: Location (must not be OneDrive)
2. Verify: Onboarding completed (LEVEL1, LEVEL2)
3. Diagnose: Use troubleshooting section above
4. Fix: Apply recommended solutions
5. Prevent: Document for future reference
```

---

## 🎯 **QUICK DECISION TREE**

**User asks about...**

**"Rules/enforcement/boundaries"** → Section A (Glass-Box Boundary)
**"Getting started/onboarding"** → Section B (Repository Structure)  
**"Theory/math/proofs"** → Section C (Mathematical Foundations)
**"Scripts/tools/automation"** → Section D (Automation & Tooling)
**"Testing/validation/data"** → Section E (Validation & Analysis)
**"Deployment/GitHub/sharing"** → Section F (Deployment)
**"Errors/problems/debugging"** → Section G (Failure Modes)
**"Git/commits/history"** → Section H (Git & Version Control)

**"I don't know where to start"** → ALWAYS start with ONBOARD_FIRST.md

---

## 📚 **DEEP DIVE READINGS (OPTIONAL)**

*Only after mastering the above sections:*

### **Advanced Topics:**
- `ontology/` directory - Formal ontology definitions
- `grounding_models/` - AI grounding implementations
- `correspondence_bridge/` - Cross-system validation
- `forgiveness_system/` - Error recovery mechanisms

### **Historical Context:**
- `historical_tests/` - Previous test implementations
- `phase3_outputs/` - Phase 3 development artifacts
- `chat_exports/` - Raw conversation data

### **Experimental Features:**
- `adversarial_tests/` - Adversarial testing suites
- `glass-box/` - Glass-Box implementation variants
- `inelasticity_results/` - Truth inelasticity research

---

## ⚠️ **CRITICAL REMINDERS**

1. **Never work in OneDrive** - This is the "grenade" zone
2. **Always complete onboarding** - LEVEL1.md and LEVEL2.md first
3. **Exit code 2 is intentional** - Fail-fast on boundary violations
4. **HTML blueprint is authoritative** - Code implements, doesn't define
5. **Progressive disclosure** - Don't try to understand everything at once
6. **Each AI instance starts fresh** - Don't assume previous context

---

## ✅ **VERIFICATION CHECK**

**Before using this guide, confirm:**
- [ ] LEVEL1.md completed (30-second overview)
- [ ] LEVEL2.md completed (5-minute orientation)  
- [ ] Location verified (not OneDrive)
- [ ] Critical files accessible
- [ ] User request categorized correctly

**If any missing, go back and complete prerequisites.**

---

## 🚀 **NOW NAVIGATE WITH CONFIDENCE**

You have the map. You know the territory. You understand the hierarchy.

**Use this guide to:**
- Find information quickly
- Provide accurate responses
- Maintain boundary compliance
- Avoid information overload
- Work efficiently in the 3,001-file repository

**The quality of your navigation determines the quality of your work.**

---
*This guide enables consistent, context-aware navigation across all AI instances, preventing the "where do I start?" problem that plagued previous implementations.*