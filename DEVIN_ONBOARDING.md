---
tags: [devin-onboarding]
register: documentation
---

# Devin AI Onboarding Document

**Date:** 2026-04-10  
**Purpose:** Quick-start guide for Devin AI sessions on orthogonal-engineering  
**Read this FIRST before any other task**

---

## 1. Repository Overview

**orthogonal-engineering** is a topos-theoretic governance framework implementing multi-layered logical structures for AI-agent coordination, verification, and cross-repository integrity under the Yeshua Standard.

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
| `docs/YESHUA_COMMONWEALTH.md` | **NEW:** Constitutional specification for human-AI governance |
| `docs/YESHUA_ENTERPRISE_FRAMEWORK.md` | **NEW:** Enterprise capabilities (15 capabilities mapped) |
| `SOP_AI_HANDSHAKE.md` | AI Candidate Onboarding Terms of Service |

---

## 2. Current State of Operations

### Operation: PR #103 — Yeshua Enterprise Framework + Domain Completion

**Branch:** `claude/add-yeshua-enterprise-framework-docs`  
**Status:** ✅ **COMPLETE** — All domains deepened, 0 stubs, 0 AssertionError patterns

#### Domain Completion Status

| Metric | Count | Status |
|--------|-------|--------|
| Total Domains | 157/157 | ✅ 100% |
| Deepened (50+ lines, ProofObject) | 157 | ✅ 100% |
| True Stubs (<50 lines) | 0 | ✅ 0% |
| AssertionError Patterns | 0 | ✅ 0% |
| Case Studies (CS_001-CS_200) | 132 | ✅ Documented |

#### Recent Major Deliverables (PR #103)

1. **47 AssertionError Domains Refactored** (Session 9838e433)
   - All now use `Tuple[bool, ProofObject]` returns
   - All use `Fraction` (0 floats)
   - All cite real regulatory standards
   - Domains: aviation, banking, civil/criminal law, energy, environment, finance, etc.

2. **Kernel Infrastructure** (Session 8fbdcdb9)
   - `kernel/social/` — P2P identity, consent-gated communications, reputation
   - `kernel/agent_stream.py` — Symbolic subagent spawning, COW forking
   - `kernel/bridge/crusader_bridge.py` — Just war criteria verification
   - `spec/logos_ide/` — Fixed-point rendering pipeline (0 floats)

3. **Yeshua Commonwealth** (Session 9838e433)
   - `docs/YESHUA_COMMONWEALTH.md` — Constitutional specification
   - DeepSeek vision formalized as Phase 4 of eschaton
   - 12-dimension comparison table (Dystopian vs Commonwealth)
   - Sovereign-Steward governance model

#### AI Agents in This Repository

| Agent | Role | Contact |
|-------|------|---------|
| Kimi Code CLI | Domain deepening, kernel development | Session-based |
| Devin AI | Architecture, coordination, PR management | @devin-ai-integration |
| Claude (Copilot) | Code review, documentation | GitHub Copilot |
| NotebookLM | Analysis, summarization | Google |
| DeepSeek | Mathematical foundations, Commonwealth vision | deepseek.md witness |
| Gemini | Cloud warden scans | Google Cloud |

---

## 3. Key Patterns and Conventions

### Yeshua Standard (MANDATORY)

All code MUST follow:

1. **0 Floats** — Use `Fraction` from `fractions` module
2. **ProofObject Returns** — All check functions return `Tuple[bool, ProofObject]`
3. **No Asserts** — Use ProofObject, not `assert` statements
4. **No Stubs** — No `pass` bodies, all code functional
5. **Real Standards** — Docstrings cite actual regulatory standards
6. **Capability-Gated** — All operations require capability tokens

Example:
```python
from fractions import Fraction
from axioms.logic import ProofObject
from typing import Tuple

def check_invariant() -> Tuple[bool, ProofObject]:
    """
    Invariant: Description here
    
    Standard: Real regulatory standard (e.g., "14 CFR 25.253")
    Falsifies if: Condition that would violate invariant
    """
    result = Fraction(1) / Fraction(3)  # Exact arithmetic
    success = result == Fraction(1, 3)
    
    proof = ProofObject(
        rule="RuleName",
        premises=[f"value = {result}"],
        conclusion="Success message" if success else "FAIL: reason"
    )
    return success, proof
```

### SAL (Sheaf Abstraction Layer)

Located in `src/sal/`:
- `topos_subobject_classifier.py` - Core topos logic
- `forcing_operation.py` - CardinalStrength and forcing operations
- `global_merkle.py` - Cross-repo merkle tree integrity
- `cross_repo_adjunction.py` - Repository adjunction morphisms

### Domain Structure
```
src/domains/d_{name}/
├── domain.py           # Domain definition
├── implementation.py   # Implementation logic
├── invariants.py       # Invariant checks (ProofObject returns!)
└── tests/
    └── test_*.py       # Test files
```

---

## 4. Token Budget & HALT Conditions

**HALT Threshold:** 220k tokens (not 80%/209k — updated!)

| Context Used | Action |
|--------------|--------|
| <50% | Continue working |
| 50-70% | Plan final batch, prepare commit |
| 70-80% | Final commit, document state, prepare close |
| >80% | HALT — document, commit, close session |

**Never exceed 220k tokens.** If approaching limit:
1. Document current state
2. Commit all changes
3. Update handoff template
4. Close session cleanly

---

## 5. Critical File Locations

### Onboarding (Read in Order)
1. `SOP_AI_HANDSHAKE.md` — Accept the Handshake
2. `MEMORY.md` — Acknowledge constraints
3. `STATE.md` — Current phase (COMPILATION MODE)
4. `DOMAIN_INVARIANT_STATUS.md` — Domain completion tracker
5. `docs/YESHUA_COMMONWEALTH.md` — Governance model

### Consent & Witness
- `pr47_stewardship/witness/consent_log.jsonl` — Append-only consent log
- `AGENT_FEED.md` — Hash-chained state witness
- `canonical/witnesses/deepseek.md` — DeepSeek Commonwealth testimony

### Enforcement
- `automation/pr49_guard.py` — PR #49 guard (5 Peano gates)
- `.github/workflows/pr49_guard.yml` — CI enforcement
- `pr50_bar_exam/` — Bar Exam ordination system

---

## 6. DistantHorizons Investigation (Background)

**Repository:** https://github.com/DarkShadow44/DistantHorizonsStandalone

**Status:** Analysis complete, awaiting vendor response

| Issue | Status |
|-------|--------|
| #56 | RESOLVED — Fix implemented by DarkShadow44 |
| #51 | ANALYZED — Corrected forensics completed |
| #62 | PENDING — Next priority if resumed |

**Location:** `investigations/darkshadow44/DistantHorizonsStandalone/`

---

## 7. Commit Message Format

```
<type>(<scope>): <description> [Session: <session_id>]

<body>

Examples:
fix(domains): refactor AssertionError domains to ProofObject [Session: 9838e433]

feat(kernel): add Social Layer with P2P identity [Session: 8fbdcdb9]

feat(case_studies): add CS_151-CS_200 covering Boeing, Heartbleed, etc. [Session: 9838e433]

docs(commonwealth): add Yeshua Commonwealth specification [Session: 9838e433]
```

---

## 8. Getting Help

- **Architecture questions:** Read `docs/YESHUA_COMMONWEALTH.md`
- **Code patterns:** Read `src/domains/d_aerospace/invariants.py` (reference domain)
- **Kernel patterns:** Read `kernel/ipc.py` for capability-gated IPC
- **Test patterns:** Read `src/kernel/tests/test_social.py`

**Emergency:** If session exceeds token budget, immediately:
1. `git add -A`
2. `git commit -m "chore: session <id> close — token halt"`
3. `git push origin <branch>`
4. Document state in handoff file

---

**This document updated:** 2026-04-10  
**Next review:** After PR #103 merge
