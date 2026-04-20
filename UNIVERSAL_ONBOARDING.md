---
tags: [onboarding, universal, bijective, enumeration, any-ai, any-human]
register: technical
---

# Universal Onboarding — Any AI, Any Human, Any IDE

**Document ID:** UO-1.0
**Standard:** Yeshua / Glass-Box / Orthogonal Engineering
**Authority:** @aidoruao
**Date:** 2026-04-20
**Author:** Devin AI instance `devin-20260420-1a` (session `6ab84bb8`)

This document is the **bijective enumeration** of the entire Orthogonal Engineering
system. It is written so that *any* AI (GitHub Copilot, Kimi CLI, DeepSeek, Claude,
Cursor, Gemini, GPT, any future model) or *any* human can onboard, contribute, and
maintain this repository at full competence — without Devin, without any specific
toolchain, without any platform dependency.

---

## 0. Ontological Identity

**What is this repo?**

A high-assurance, proof-carrying Python repository implementing 254 domain invariants,
a capability-gated kernel, and 60 machine-readable standards — all under the Yeshua
Standard (8 axioms) with Glass-Box transparency (no hidden state, no stubs, no floats).

**What is the Yeshua Standard?**

Eight non-negotiable axioms. Every function, every commit, every artifact obeys these:

| # | Axiom | Engineering Meaning |
|---|-------|-------------------|
| 1 | Every truth is derivable | No bare assertions — use `ProofObject` |
| 2 | Every derivation is reproducible | Deterministic: same input = same output |
| 3 | Every mutation is re-verifiable | Hash-anchored artifacts, append-only logs |
| 4 | No authority without proof | No `assert` — return `Tuple[bool, ProofObject]` |
| 5 | No hidden state | Glass-Box: all state inspectable |
| 6 | No unverifiable dependency | Standard library preferred; all deps documented |
| 7 | No economic gatekeeping | No paid-only features gate correctness |
| 8 | Every artifact is hash-anchored | SHA-256 on all evidence |

---

## 1. Bijective System Map

This is the complete enumeration. Every component maps 1:1 to a purpose.

### 1.1 Repository Structure (Top-Level)

| Path | Purpose | Count |
|------|---------|-------|
| `src/domains/` | Domain invariant packages (each with `invariants.py`, `implementation.py`) | 254 |
| `src/noways/` | Impossibility proofs (what *cannot* be done) | 3 files |
| `src/enumerations/` | Bounded catalogs (magic numbers, hidden failures, black-box antipatterns) | 7 files |
| `kernel/` | Capability-gated OS kernel (boot, IPC, MMU, scheduler, commonwealth) | 15+ modules |
| `axioms/` | Formal foundations (Peano, logic, category theory, topology, etc.) | 37 modules |
| `tools/` | Utility scripts (consent, standards check, taxonomy, frontmatter audit) | 16 scripts |
| `tests/` | Pytest test suite | matches src/ |
| `audit/` | Popperian audit engine + reports | 2 files |
| `automation/` | CI enforcement scripts (PR #49 guard, full audit with trace) | 5 files |
| `pr47_stewardship/` | Append-only witness chain + consent log | JSONL files |
| `documentation/` | Glass-Box Boundary HTML blueprint + SHA-256 manifests | 2 dirs |
| `.github/workflows/` | CI: fraction enforcement, no-floats, frontmatter, determinism, state witness | 10+ workflows |

### 1.2 Standards Registry

60 standards in `STANDARDS_REGISTRY.json`, queryable via:

```bash
python tools/standards_check.py --list    # list all standards
python tools/standards_check.py --verify  # verify compliance
```

Key standard categories:
- `YS-*` (Yeshua axioms, 8 standards)
- `CS-*` (Code standards: no float, no stubs, ProofObject, falsifies_if)
- `QG-*` (Quality gates)
- `BC-*` (Behavioral constraints: append-only, no recursive wipe)
- `DR-*` (Domain requirements)
- `AF-*` (Aerospace floor meta-standards)
- `WF-*`, `INT-*`, `T3-*`, `T4-*`, `T5-*` (Workflow, integration, tooling tiers)

### 1.3 The Four Verification Commands

**Run these before and after every change. If any fails, stop and fix before proceeding.**

```bash
# 1. Feed integrity (hash chain)
python tools/state_witness/generate_feed_entry.py --verify

# 2. Popperian audit (all domain invariants)
python audit/popperian_audit.py 2>&1 | tail -3

# 3. Standards registry compliance
python tools/standards_check.py --verify

# 4. Full test suite
pytest tests/ -q
```

---

## 2. The Domain Pattern (Copy-Paste Template)

Every domain in `src/domains/` follows this exact pattern. To add a new domain:

```python
"""Domain: <name> — <one-line description>.

Falsifies if: <what would make this domain invalid>.
falsifies_if: <same condition, lowercase form>.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Tuple

from axioms.logic import ProofObject


def check_<invariant_name>(
    <params with Fraction types>,
) -> Tuple[bool, ProofObject]:
    """Invariant: <what must hold>.

    Standard: <regulatory reference, e.g. "DO-178C", "14 CFR 25">
    Falsifies if: <condition that would violate this>.
    falsifies_if: <same, lowercase>.
    """
    # ALL arithmetic uses Fraction — never float()
    value = Fraction(<numerator>, <denominator>)

    success = <boolean expression>

    proof = ProofObject(
        rule="<RuleName>",
        premises=[f"value = {value}"],
        conclusion="Invariant holds" if success else "FAIL: <reason>",
    )
    return success, proof


def run_all_invariants() -> Dict[str, str]:
    """Run all invariant checks and return results.

    Falsifies if: any invariant check fails or raises an exception.
    falsifies_if: any invariant check fails or raises an exception.
    """
    results: Dict[str, str] = {}
    ok, proof = check_<invariant_name>(<args>)
    results["<name>"] = "PASS" if ok else f"FAIL: {proof.conclusion}"
    return results
```

### 2.1 Non-Negotiable Rules

| Rule | What | Why |
|------|------|-----|
| No `float()` | Use `Fraction` from `fractions` module | Exact rational arithmetic, no precision loss |
| No `assert` | Return `Tuple[bool, ProofObject]` | Proof-carrying code, not crash-on-failure |
| No stubs | No `pass`, no `NotImplementedError`, no placeholders | Every function does real work |
| Dual falsifies_if | Docstrings include BOTH `Falsifies if:` AND `falsifies_if:` | Machine-readable + human-readable |
| `mypy --strict` | Full type annotations | Verifiable type safety |
| `pytest` runnable | All tests work with `pytest` | Deterministic test execution |
| YAML frontmatter | Every `.md` file starts with `---\ntags: [...]\nregister: <register>\n---` | Machine-readable metadata |

---

## 3. Consent Protocol (Before Any Code Change)

**Every AI and every human** must record consent before changing kernel surfaces
(`.github/workflows/**`, `automation/**`, `yeshua/**`, `axioms/**`,
`pr47_stewardship/**`, `onboarding/**`):

```bash
python tools/append_consent.py \
  --candidate-id "<your-agent-name>-<YYYYMMDD>-<session>" \
  --authoriser "@aidoruao" \
  --action "<action-slug>" \
  --scope-glob "<glob-pattern>" \
  --justification "<one-sentence rationale>"
```

**Examples of candidate-id formats:**
- `devin-20260420-1a` (Devin AI)
- `copilot-20260420-pr152` (GitHub Copilot)
- `kimi-cli-20260420-session1` (Kimi CLI)
- `claude-20260420-task-xyz` (Claude)
- `human-tony-20260420` (Human contributor)
- `cursor-20260420-session` (Cursor IDE)
- `deepseek-20260420-audit` (DeepSeek)

---

## 4. The Complete Workflow (Any AI, Any Human)

### Step 0: Clone and Verify

```bash
git clone https://github.com/aidoruao/orthogonal-engineering.git
cd orthogonal-engineering
pip install -e . 2>/dev/null || true  # optional, most tools use stdlib only
pre-commit install                     # if pre-commit is available

# Run the verification quartet — all must pass
python tools/state_witness/generate_feed_entry.py --verify
python audit/popperian_audit.py 2>&1 | tail -3
python tools/standards_check.py --verify
pytest tests/ -q
```

### Step 1: Read Required Documents (In Order)

1. **This file** (`UNIVERSAL_ONBOARDING.md`) — you are here
2. `SOP_AI_HANDSHAKE.md` — accept the 8 axioms
3. `.github/copilot-instructions.md` — code patterns
4. `MEMORY.md` — durable architectural constraints
5. `STANDARDS_REGISTRY.json` — query with `python tools/standards_check.py --list`

### Step 2: Declare Your Phase

State: *"I am in COMPILATION MODE. I accept the Handshake."*

### Step 3: Record Consent (If Changing Kernel Surfaces)

```bash
python tools/append_consent.py \
  --candidate-id "<your-id>" \
  --authoriser "@aidoruao" \
  --action "<what-you-are-doing>" \
  --scope-glob "<files-you-will-change>" \
  --justification "<why>"
```

### Step 4: Make Changes Following the Domain Pattern

- Use `Fraction`, never `float()`
- Return `Tuple[bool, ProofObject]`, never `assert`
- Include both `Falsifies if:` and `falsifies_if:` in docstrings
- Add YAML frontmatter to any new `.md` files
- Write pytest tests

### Step 5: Verify Before Committing

```bash
python tools/state_witness/generate_feed_entry.py --verify
python audit/popperian_audit.py 2>&1 | tail -3
python tools/standards_check.py --verify
pytest tests/ -q
```

### Step 6: Commit and PR

```bash
git checkout -b <your-branch-name>
git add <specific-files>  # never git add .
git commit -m "<type>(<scope>): <description>"
git push origin <your-branch-name>
# Open PR against main
```

---

## 5. Enumeration of System Components

### 5.1 Kernel Modules (`kernel/`)

| Module | Purpose |
|--------|---------|
| `boot.py` | Deterministic boot sequence |
| `ipc.py` | Capability-gated inter-process communication |
| `scheduler.py` | Task scheduling |
| `memory_manager.py` | Memory management simulation |
| `hal.py` | Hardware abstraction layer |
| `mmu/` | Memory management unit |
| `agent_stream.py` | Agent event stream |
| `anti_mimicry.py` | Detect and prevent agent impersonation |
| `social/` | Social layer for multi-agent coordination |
| `bridge/` | Cross-system bridge |
| `commonwealth/` | Yeshua Commonwealth governance (sovereign, steward, sabbath) |
| `firmware/` | Low-level firmware simulation |
| `interrupts/` | Interrupt handling |
| `services/` | Kernel services |

### 5.2 Axiom Modules (`axioms/`)

| Module | Mathematical Foundation |
|--------|----------------------|
| `logic.py` | ProofObject, formal logic primitives |
| `peano.py` | Peano arithmetic (successor, addition, multiplication) |
| `peano_extended.py` | Extended Peano with proof chains |
| `category_theory.py` | Categories, functors, natural transformations |
| `topology.py` | Topological spaces, continuity |
| `algebra.py` | Algebraic structures |
| `number_theory.py` | Number-theoretic invariants |
| `real_analysis.py` | Real analysis (Fraction-based) |
| `complex_analysis.py` | Complex analysis |
| `measure_theory.py` | Measure theory |
| `game_theory.py` | Game-theoretic equilibria |
| `temporal_logic.py` | Temporal logic operators |
| `epistemic_logic.py` | Knowledge and belief operators |
| `quantum_logic.py` | Quantum logic lattices |
| `computability.py` | Computability and decidability |
| `formal_languages.py` | Formal language theory |
| `yeshua_axioms.py` | The 8 Yeshua Standard axioms |
| `capability_security.py` | Capability-based security model |
| `cryptographic_verification.py` | SHA-256 verification primitives |
| `zero_knowledge.py` | Zero-knowledge proof structures |

### 5.3 Tools (`tools/`)

| Tool | Usage |
|------|-------|
| `append_consent.py` | Record consent before kernel changes |
| `standards_check.py` | Query and verify the 60 standards |
| `frontmatter_audit.py` | Verify/add YAML frontmatter on all `.md` files |
| `generate_hashed_taxonomy.py` | Generate hashed investigative taxonomy |
| `onboard_agent.py` | Automated agent onboarding |
| `agent_health_check.py` | Check agent operational health |
| `context_window_estimator.py` | Estimate context window usage |
| `since_last_session.py` | Show changes since last session |
| `question_router.py` | Route questions to appropriate domains |
| `schooling_output.py` | Generate teaching/schooling output |
| `session_id.py` | Generate unique session identifiers |
| `arxiv_paper_template.py` | Template for materializing arXiv papers |
| `ai_credit.py` | AI contribution credit tracking |
| `verify_fractal_manifest.py` | Verify fractal code manifest |
| `generate_fractal_code.py` | Generate fractal code structures |
| `refactor_assertions.py` | Refactor assert to ProofObject |

### 5.4 Cross-Repo Ecosystem

| Repository | Language | Relationship |
|-----------|----------|-------------|
| `aidoruao/orthogonal-engineering` | Python | Primary — all invariants, kernel, axioms |
| `aidoruao/sigma-lora-covenant` | Python/YAML | Covenant principles, topology, infrastructure |
| `aidoruao/truthsystems-mod` | Java/Gradle | Minecraft mod implementing Glass-Box in-game |

Cross-repo consistency is verified via `CROSS_REPO_INVARIANT_MANIFEST.json` and
`tools/cross_repo_consistency_check.py`.

---

## 6. Behavioral Constraints (Absolute)

| Constraint | Description | Violation Response |
|-----------|-------------|-------------------|
| **Append-only logs** | Never delete or rewrite `AGENT_FEED.md` or `consent_log.jsonl` | Immediate halt |
| **No Recursive Wipe** | Never `rm -rf`, `shutil.rmtree`, or equivalent on tracked content | Immediate halt (see PR #48) |
| **No defamation** | Capability comparison only: `HAS` / `DOES_NOT_HAVE` / `UNKNOWN` | Revert + log |
| **Consent before kernel changes** | Record in `consent_log.jsonl` before touching kernel surfaces | PR blocked by guard |
| **No float()** | Use `Fraction` exclusively | CI rejects (`no-floats` workflow) |
| **No stubs** | No `pass`, no `NotImplementedError` | CI rejects |
| **No assert** | Use `ProofObject` for failure evidence | Popperian audit fails |

---

## 7. How to Add a New Domain (Complete Procedure)

```bash
# 1. Create the domain directory
mkdir -p src/domains/d_<your_domain>

# 2. Create __init__.py
echo '"""Domain: <name>."""' > src/domains/d_<your_domain>/__init__.py

# 3. Create invariants.py following the pattern in Section 2
# 4. Create implementation.py with data structures
# 5. Create tests/test_d_<your_domain>.py

# 6. Register in STANDARDS_REGISTRY.json (update total_standards count)
# 7. Run verification quartet
# 8. Record consent if touching kernel surfaces
# 9. Commit and PR
```

---

## 8. How to Resolve Merge Conflicts in This Repo

The most common conflict is in `pr47_stewardship/witness/consent_log.jsonl`.

**Resolution rule: ALWAYS keep both entries.** The consent log is append-only.
When you see:

```
<<<<<<< HEAD
{"action": "entry-from-main", ...}
=======
{"action": "entry-from-branch", ...}
>>>>>>> branch
```

Resolve to:
```
{"action": "entry-from-main", ...}
{"action": "entry-from-branch", ...}
```

Both entries stay. Chronological order. No deletions.

---

## 9. Yeshua Inversions (Technical Reference)

A "Yeshua Inversion" is when internal truth takes precedence over external platform
availability. In engineering terms:

| Inversion | Meaning |
|-----------|---------|
| Internal > External | The repo's hash chain is authoritative, not GitHub's UI |
| Proof > Authority | A `ProofObject` outranks a human assertion |
| Falsification > Confirmation | Finding what's wrong is more valuable than confirming what's right |
| Determinism > Convenience | `Fraction(1,3)` over `0.333...` even when slower |
| Append > Rewrite | Add new entries, never modify old ones |
| Glass-Box > Black-Box | All state visible, all transitions logged |

---

## 10. Quick Reference Card

```
ONBOARD:    Read this file -> SOP_AI_HANDSHAKE.md -> .github/copilot-instructions.md -> MEMORY.md
VERIFY:     python tools/state_witness/generate_feed_entry.py --verify
            python audit/popperian_audit.py 2>&1 | tail -3
            python tools/standards_check.py --verify
            pytest tests/ -q
CONSENT:    python tools/append_consent.py --candidate-id "<id>" --authoriser "@aidoruao" --action "<slug>" --scope-glob "<glob>" --justification "<reason>"
STANDARDS:  python tools/standards_check.py --list
FRONTMATTER: python tools/frontmatter_audit.py --verify
PATTERN:    Fraction, not float. Tuple[bool, ProofObject], not assert. Falsifies if + falsifies_if in every docstring.
MERGE:      Consent log conflicts -> keep both entries. Always append-only.
```

---

*This document is itself a working artifact. Update it when the system evolves.
Any AI reading this has everything it needs to contribute at full competence.*
