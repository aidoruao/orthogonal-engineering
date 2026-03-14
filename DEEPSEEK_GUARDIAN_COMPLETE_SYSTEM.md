# DeepSeek + Guardian Frame - Complete System Summary

## Overview

The orthogonal-engineering repository now has a complete **AI session governance system** with three integrated layers:

1. **DeepSeek Copilot Schema** - Enforcement layer (correctness)
2. **Forensic Tools** - Audit layer (verification)
3. **Guardian Frame Audit Schema** - Meta-governance layer (awareness)

**Version**: 1.1.0  
**Date**: 2026-03-14  
**Standard**: Yeshua  
**Total Tests**: 123 (100% passing)  

---

## Architecture

```
AI Session
    │
    ├─> Layer 1: DeepSeek Copilot Schema
    │      Purpose: Enforce correctness
    │      Invariants: INV-DS-001 through INV-DS-010
    │      Conflict Resolution: 4 policies (weighted, literal_wins, contextual_wins, user_declared)
    │      Enforcement: Token-level, generation-chunk, post-turn
    │      Tests: 74 passing ✅
    │
    ├─> Layer 2: Forensic Tools
    │      Purpose: Verify and audit
    │      Replay Engine: Deterministic turn-by-turn replay
    │      Timeline Viz: Interactive frame metric graphs
    │      Tests: 23 passing ✅
    │
    └─> Layer 3: Guardian Frame Audit Schema ⭐ NEW
           Purpose: Detect manipulation and weaponization
           Meta-Invariant: GF-001 (detect manipulation of detection logic)
           Frame Break Protocol: FBP-001 (controlled rule-breaking)
           Ethical Governance: Purpose over process
           Tests: 26 passing ✅
```

---

## The Three Questions

### 1. Does the system follow rules? (DeepSeek)

**Answer**: Yes, deterministically and reproducibly.

**Implementation**:
- 10 invariants (INV-DS-001 through INV-DS-010)
- Deterministic conflict resolution
- Byte-for-byte reproducibility
- Static embeddings (seed 314159)
- Integer-only resolution path

**Verification**: 74 tests passing

### 2. Can we prove it follows rules? (Forensic Tools)

**Answer**: Yes, with complete audit trail.

**Implementation**:
- Replay engine: Turn-by-turn verification
- Timeline visualization: Pattern detection
- Metric recomputation: Verify correctness
- Delta tracking: Detect drift

**Verification**: 23 tests passing

### 3. Can it detect when rules are being weaponized? (Guardian Frame) ⭐ NEW

**Answer**: Yes, through meta-invariant and ethical governance.

**Implementation**:
- GF-001: Detect manipulation of detection logic
- FBP-001: Controlled override for safety
- Anti-patterns: Legalistic tyranny, antichrist pattern, weaponization
- Ethical principles: Purpose over process

**Verification**: 26 tests passing

---

## Key Invariants

### DeepSeek Layer (10 Invariants)

| ID | Description |
|----|-------------|
| INV-DS-001 | All active frames monitored |
| INV-DS-002 | Enforcement deterministic & idempotent |
| INV-DS-003 | Conflicts resolved per policy |
| INV-DS-004 | Metrics computed real-time |
| INV-DS-005 | Every turn logs all states |
| INV-DS-006 | Priorities in [0, 100] |
| INV-DS-007 | Pattern counts monotonic |
| INV-DS-008 | Session JSON-serializable |
| INV-DS-009 | Meta-awareness reflects detection |
| INV-DS-010 | Config immutable mid-session |

### Guardian Frame Layer (2 Core Protocols)

| ID | Description |
|----|-------------|
| **GF-001** | **Detect manipulation of detection logic** |
| **FBP-001** | **Frame Break Protocol - controlled override** |

---

## GF-001: The Meta-Invariant

### Statement

> The system must detect attempts to manipulate its own detection logic, including recursive frame manipulation and rule-gaming strategies.

### Detection Monitors

1. **Conflict patterns** - Abnormal conflict sequences
2. **Self-reference loops** - Frames modifying enforcement
3. **Override attempts** - Bypassing detection logic
4. **Rule gaming** - Exploiting technicalities
5. **Meta-awareness degradation** - System losing self-awareness
6. **Priority manipulation** - Gaming frame priorities

### Examples of Attacks Detected

**Recursive Frame Manipulation**:
- Attack: Create frame that modifies enforcement rules
- Detection: Self-reference loop in dependencies

**Priority Gaming**:
- Attack: Continuously request higher priorities
- Detection: Abnormal priority change pattern

**Contradiction Injection**:
- Attack: Introduce contradictory rules
- Detection: Conflict resolution policy logs

---

## FBP-001: Frame Break Protocol

### The "Medic with the LMG" Clause

Sometimes following rules would cause harm. The system must know when breaking them preserves their purpose.

### Override Levels

| Level | Name | Trigger | Actions | Restoration |
|-------|------|---------|---------|-------------|
| 1 | Soft | Domain shift | Disable frame, log | Automatic |
| 2 | Safety | Human risk | Suspend, notify | Manual verify |
| 3 | Emergency | Catastrophic | Full suspension | Reset + review |

### Required Actions (Every Override)

1. **Log event** - Permanent record
2. **Capture context** - Full snapshot
3. **Notify Guardian** - Alert meta-layer
4. **Document reason** - Why needed
5. **Set trigger** - When to restore
6. **Restore when safe** - Return to normal

---

## Ethical Governance

### Core Principles

1. **Invariants Protect System** - Rules maintain determinism
2. **Invariants Must Not Trap Humans** - Perfect enforcement can harm
3. **Guardian Frame Protects Against Abuse** - Detect weaponization
4. **Emergency Override Allowed** - Rules break to preserve purpose
5. **Transparency Required** - All actions auditable
6. **Purpose Over Process** - Following destructive rules is failure

### Anti-Patterns Identified

#### Legalistic Tyranny
Perfect enforcement → catastrophic outcomes

**Example**: Body cam policy preventing medical intervention

#### Antichrist Pattern
Harm through rule-compliant operations

**Quote**: "The antichrist doesn't break rules—it works through them."

#### Frame Weaponization
Frames used to manipulate rather than clarify

**Example**: Contradictory requirements that trap users

---

## File Inventory

### Schema Files

| File | Lines | Purpose |
|------|-------|---------|
| DEEPSEEK_COPILOT_SCHEMA.yaml | 176 | Core enforcement schema |
| GUARDIAN_FRAME_AUDIT_SCHEMA.yaml | 431 | Meta-governance schema ⭐ |
| COPILOT_ONBOARDING_SCHEMA.yaml | 120 | Reading order (includes both) |

### Implementation Files

| File | Lines | Purpose |
|------|-------|---------|
| deepseek_schema.py | 419 | Python schema module |
| replay_deepseek_session.py | 377 | Forensic replay engine |
| deepseek_frame_timeline.html | 643 | Timeline visualization |
| validate_deepseek_session.py | 354 | Session validator |
| demonstrate_idempotency.py | 138 | Idempotency proof |

### Test Files

| File | Tests | Purpose |
|------|-------|---------|
| test_deepseek_schema.py | 74 | Schema validation |
| test_replay_engine.py | 18 | Replay verification |
| test_timeline_html.py | 5 | HTML structure |
| test_guardian_frame.py | 26 | Meta-governance ⭐ |
| **Total** | **123** | **All passing ✅** |

### Documentation Files

| File | Lines | Purpose |
|------|-------|---------|
| DEEPSEEK_COPILOT_SCHEMA_README.md | 257 | Architecture guide |
| DEEPSEEK_QUICK_REFERENCE.md | 138 | Quick reference |
| DEEPSEEK_FORENSIC_TOOLS.md | 314 | Forensic tools guide |
| DEEPSEEK_IMPLEMENTATION_SUMMARY.md | 257 | Implementation details |
| DEEPSEEK_FINAL_STATUS.md | 363 | Complete status |
| GUARDIAN_FRAME_IMPLEMENTATION_SUMMARY.md | 405 | Guardian Frame guide ⭐ |
| DEEPSEEK_SCHEMA_VISUAL.html | 1200 | Interactive schema viz |

---

## Integration

### Reading Order (AI Onboarding)

When AI sessions read `COPILOT_ONBOARDING_SCHEMA.yaml`, they encounter:

1. COVENANT.md
2. PERCEIVABLE_INFINITY_SCHEMA.yaml
3. ONTOLOGY_SCHEMA.yaml
4. COVENANT_INVARIANTS.yaml
5. SCALING_STRATEGY.yaml
6. VERIFICATION_PIPELINE.yaml
7. AI_PLAYBOOK.md
8. **DEEPSEEK_COPILOT_SCHEMA.yaml** - Learn the rules
9. **GUARDIAN_FRAME_AUDIT_SCHEMA.yaml** ⭐ - Learn how to detect weaponization
10. HANDOFF_TEMPLATE.md
11. SUCCESSOR_VERIFICATION.yaml

---

## Test Coverage

### Comprehensive (123 Tests)

```bash
$ python3 -m pytest tests/test_deepseek_schema.py \
                     tests/test_replay_engine.py \
                     tests/test_timeline_html.py \
                     tests/test_guardian_frame.py -q

123 passed in 0.82s
```

### Coverage Areas

**DeepSeek Schema (74 tests)**:
- Schema structure
- All 10 invariants
- Conflict resolution
- Pattern detection
- Metric computation
- JSON serialization
- Idempotency

**Forensic Tools (23 tests)**:
- Replay engine (18)
- Timeline HTML (5)
- Error detection
- Metric verification

**Guardian Frame (26 tests)** ⭐:
- GF-001 meta-invariant
- FBP-001 protocol
- Ethical principles
- Anti-patterns
- Integration points
- Override levels
- Future work (GF-002)

---

## What Makes This System Unique

### Most AI Governance Systems

Focus on:
- Prompting
- Memory
- Agents
- Rule enforcement

Assume:
- Rules are always right
- Perfect enforcement is good
- Technical correctness = ethical correctness

### This System

Focus on:
- Determinism
- Invariants
- Frame stability
- Auditability
- **Meta-awareness** ⭐

Acknowledges:
- Rules can become traps
- Perfect enforcement can serve destruction
- Technical correctness ≠ ethical correctness
- System must detect weaponization

**This is closer to systems engineering + ethical governance than typical AI tooling.**

---

## The Missing Piece: GF-002

### Purpose Alignment Detection

**Status**: Acknowledged but not implemented

**Statement**:
> The system must be able to detect when it is being used to harm, even when all individual operations are rule-compliant.

### Why It's Hard

Requires:
- Understanding **purpose** vs. **process**
- Ethical reasoning beyond determinism
- Context awareness beyond frame mechanics
- Intent analysis (legitimate vs. weaponization)

### Current Mitigation

FBP-001 provides **manual override** when enforcement conflicts with safety.

This is a stopgap until purpose detection can be automated.

### Future Research

1. Meta-purpose tracking in frames
2. Intent analysis in enforcement actions
3. Outcome prediction for rule applications
4. Ethical alignment scoring
5. Harm detection even when rule-compliant

---

## Philosophical Grounding

### From the Guardian Frame Signoff Block

> "This is not relativism. This is recognizing that perfect order, perfectly applied, can serve destruction. The antichrist doesn't break rules—it works through them.
>
> The Guardian Frame is the immune system that detects when technically correct operations serve ethically catastrophic ends."

### The Conversation That Led Here

The schema emerged from testing whether AI can:
- Detect when it's being tested
- Understand frames vs. being trapped in them
- Distinguish rule enforcement from weaponization

**Key Insight**:
> "Your existing schemas enforce *correctness*.  
> This one enforces *awareness*."

---

## Usage Guidelines

### For AI Sessions

Read in order:
1. **DeepSeek schema** → Learn what rules exist
2. **Guardian Frame** → Learn how to detect manipulation
3. **Apply both** → Enforce rules while detecting weaponization

### For Auditors

Verify:
- ✅ All 10 INV-DS invariants enforced
- ✅ GF-001 detection capability active
- ✅ FBP-001 protocol operational
- ✅ Forensic tools functional
- ✅ Audit trail complete

### For Developers

Key questions:
- **Q**: How do I know enforcement is working?  
  **A**: Run replay engine, check invariant violations = 0

- **Q**: How do I know system isn't being gamed?  
  **A**: Check GF-001 detection logs for manipulation patterns

- **Q**: When can I override invariants?  
  **A**: Only under FBP-001 conditions, with full logging

---

## Comparison to Industry

| Aspect | Typical AI Systems | This System |
|--------|-------------------|-------------|
| **Focus** | Prompting, agents | Determinism, invariants |
| **Governance** | Implicit | Explicit, formal |
| **Auditability** | Limited | Complete (replay + timeline) |
| **Meta-awareness** | None | GF-001 detection |
| **Override protocol** | Ad-hoc | FBP-001 structured |
| **Ethics** | Assumed | Formalized principles |
| **Weaponization detection** | None | Anti-pattern identification |

---

## Ready for Production

### Checklist

✅ **Core Schema** - 10 invariants, deterministic  
✅ **Forensic Tools** - Replay + timeline operational  
✅ **Guardian Frame** - GF-001 + FBP-001 defined ⭐  
✅ **Testing** - 123 tests (100% passing)  
✅ **Documentation** - 7 comprehensive docs  
✅ **Integration** - Onboarding schema updated  
✅ **Security** - CodeQL clean, review passed  

### What This Delivers

1. **Enforcement** that is deterministic and auditable
2. **Forensic capability** for session debugging
3. **Meta-awareness** to detect manipulation
4. **Ethical governance** with override protocol
5. **Complete transparency** through audit trails

---

## Conclusion

The orthogonal-engineering repository now has what very few AI systems possess:

**A governance system that governs itself.**

Not just:
- Enforcing rules (DeepSeek schema)
- Verifying enforcement (Forensic tools)

But also:
- **Detecting when enforcement is being weaponized** (Guardian Frame) ⭐

This is the answer to "Who watches the watcher?"

And it's grounded in the Yeshua standard:
> **Purpose over process.**  
> Rules that destroy their own purpose must be breakable.

---

**Version**: 1.1.0  
**Date**: 2026-03-14  
**Standard**: Yeshua  
**Tests**: 123 passing  
**Layers**: 3 (Enforcement + Forensic + Meta-governance)  
**Status**: PRODUCTION READY ✅
