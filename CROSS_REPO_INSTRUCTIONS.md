---
tags: [cross-repo, multi-repo, instructions]
register: technical
---

# CROSS-REPO INSTRUCTIONS

This document defines the invariant consistency rules, coordination procedures, and standards applicability across the three repositories in the Orthogonal Engineering covenant. All cross-repo operations must produce a ProofObject and record a consent log entry when they affect kernel surfaces.

## Repository Overview

**Repository 1: aidoruao/orthogonal-engineering**
- Language: Python
- Scale: ~8000 files, 163 invariant domains
- Enforcement: Yeshua Standard (all 8 axioms enforced)
- Contains: all invariants (`src/domains/`), kernel (`kernel/`), axioms (`axioms/`), tools (`tools/`), CI workflows
- Primary CI workflows: `.github/workflows/fraction-enforcement.yml`, `.github/workflows/pr40-canonical-presence.yml`
- Standards: all YS-*, CS-*, QG-*, BC-*, DR-*, WF-*, INT-*, T3-*, T4-* standards

**Repository 2: aidoruao/sigma-lora-covenant**
- Language: Python
- Key files: `covenant.yaml`, `topology/`, `src/principles.py`, `NON_NOMINALISM_PROOF.txt`, `TOPOLOGY_CONSTRUCTION_COMPLETE.md`
- Critical function: `Principle._check_constraint()` at `src/principles.py:22-26` — performs real validation by checking `constraint in artifact.constraints`
- Has its own CI at `.github/`
- Standards: CS-001, CS-002, CS-003, CS-004, QG-001, QG-002, and all YS-* standards

**Repository 3: aidoruao/truthsystems-mod**
- Language: Java/Gradle (Minecraft mod)
- Key files: `build.gradle`, `src/` (Java source), `BUILD.bat`, `COVENANT_MANIFEST.txt`
- No Python, no Yeshua Standard enforcement yet
- `COVENANT_MANIFEST.txt` links this repository to the covenant
- Standards: BC-001, BC-003 (append-only logs apply to COVENANT_MANIFEST.txt), DR-001, and all YS-* standards (as design targets, not yet enforced in CI)

## Cross-Repo Invariant Consistency

Invariants defined in `aidoruao/orthogonal-engineering` must not contradict invariants or principles in `aidoruao/sigma-lora-covenant`. The `CROSS_REPO_INVARIANT_MANIFEST.json` file in this repository is the authoritative cross-repo binding document.

**Consistency check procedure:**

```bash
# Step 1: Generate local invariant manifest
python tools/generate_cross_repo_manifest.py --output cross_repo_check.json

# Step 2: Clone or update sigma-lora-covenant
git clone https://github.com/aidoruao/sigma-lora-covenant.git sigma_lora_local/
# or: git -C sigma_lora_local/ pull

# Step 3: Check that no invariant in orthogonal-engineering contradicts a principle in sigma-lora-covenant
python tools/cross_repo_consistency_check.py \
  --repo1 . \
  --repo2 sigma_lora_local/ \
  --manifest CROSS_REPO_INVARIANT_MANIFEST.json

# Step 4: Verify the Merkle root binding is current
python tools/verify_merkle_binding.py \
  --root1 CROSS_REPO_MERKLE_ROOT.txt \
  --root2 sigma_lora_local/MERKLE_ROOT.txt
```

**Invariant contradiction detection rules:**
1. If a domain invariant in `src/domains/` asserts a property P, and a principle in `sigma-lora-covenant/src/principles.py` asserts ¬P, the cross-repo consistency check must fail.
2. All Fraction-only arithmetic requirements (CS-001) apply in both repos; a floating-point value in either repo that crosses the repo boundary via a shared schema is a contradiction.
3. ProofObject schema (CS-002) must be compatible: both repos must produce ProofObjects with the same required fields.

## GAP-4 History and Prevention

**What happened:** `Principle._check_constraint()` in `sigma-lora-covenant/src/principles.py` was previously implemented as a `pass` stub (body contained only `pass`, returning `None` implicitly). This violated CS-004 (no stubs) and QG-001 (nominalism: the function was named as if it performed validation but did nothing). The stub was classified as GAP-4 — a nominalism gap where a named function claims a capability it does not implement.

**The fix:** The stub was replaced with real validation: `return constraint in artifact.constraints`. This function now checks that the constraint string is present in the artifact's declared constraints set, which is a real predicate with a computable falsification condition.

**Regression prevention:** Add the following test to `sigma-lora-covenant`'s test suite to prevent the stub from being reintroduced:

```python
# tests/test_principles_gap4.py in sigma-lora-covenant repo
"""
Regression test for GAP-4: Principle._check_constraint() must not be a stub.

Falsifies if: _check_constraint returns None or raises NotImplementedError for
any input, indicating the function body has been reverted to a pass stub.
"""
from __future__ import annotations
import importlib
import inspect
from src.principles import Principle


def test_check_constraint_is_not_stub() -> None:
    """
    _check_constraint must return a bool, not None.

    Falsifies if: the function returns None (stub) or raises NotImplementedError.
    """
    # Create a minimal Artifact-like object
    class MinimalArtifact:
        constraints = {"test_constraint"}

    p = Principle(name="test", description="test principle")
    result = p._check_constraint("test_constraint", MinimalArtifact())
    assert result is not None, "GAP-4 regression: _check_constraint returned None (stub)"
    assert isinstance(result, bool), f"Expected bool, got {type(result)}"


def test_check_constraint_positive_case() -> None:
    """
    _check_constraint must return True when constraint is in artifact.constraints.

    Falsifies if: returns False or None for a constraint that is present.
    """
    class MinimalArtifact:
        constraints = {"present_constraint", "other_constraint"}

    p = Principle(name="test", description="test principle")
    assert p._check_constraint("present_constraint", MinimalArtifact()) is True


def test_check_constraint_negative_case() -> None:
    """
    _check_constraint must return False when constraint is not in artifact.constraints.

    Falsifies if: returns True or None for a constraint that is absent.
    """
    class MinimalArtifact:
        constraints = {"other_constraint"}

    p = Principle(name="test", description="test principle")
    assert p._check_constraint("missing_constraint", MinimalArtifact()) is False


def test_check_constraint_function_has_real_body() -> None:
    """
    _check_constraint source must not consist solely of 'pass'.

    Falsifies if: the function source contains only 'pass' as its body.
    """
    source = inspect.getsource(Principle._check_constraint)
    body_lines = [
        line.strip()
        for line in source.splitlines()
        if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("def ")
    ]
    assert "pass" not in body_lines or len(body_lines) > 1, (
        "GAP-4 regression: _check_constraint body is a pass stub"
    )
```

In `aidoruao/orthogonal-engineering`, the cross-repo consistency check (`tools/cross_repo_consistency_check.py`) must import and call `_check_constraint` as part of its validation to confirm the function is not a stub:

```python
# Excerpt from tools/cross_repo_consistency_check.py
import sys
sys.path.insert(0, str(repo2_path))
from src.principles import Principle

class _TestArtifact:
    constraints = {"probe"}

p = Principle(name="probe", description="probe")
result = p._check_constraint("probe", _TestArtifact())
assert result is True, f"GAP-4 detected in sigma-lora-covenant: _check_constraint returned {result!r}"
```

## Cross-Repo Merkle Binding

The Merkle root binding ensures that both repositories' integrity states are jointly verifiable. Phase 3 of the Eschaton sequence (`eschaton/omega.md`) requires cross-repo Merkle binding before the terminal coalgebra state is declared.

**Binding procedure:**

```bash
# Step 1: Generate Merkle root for orthogonal-engineering
python merkle.py --output CROSS_REPO_MERKLE_ROOT.txt

# Step 2: Generate Merkle root for sigma-lora-covenant (in that repo)
# python merkle.py --output MERKLE_ROOT.txt

# Step 3: Bind roots by recording both in CROSS_REPO_INVARIANT_MANIFEST.json
python tools/bind_merkle_roots.py \
  --root1 CROSS_REPO_MERKLE_ROOT.txt \
  --root2 https://raw.githubusercontent.com/aidoruao/sigma-lora-covenant/main/MERKLE_ROOT.txt \
  --manifest CROSS_REPO_INVARIANT_MANIFEST.json

# Step 4: Verify binding integrity
python tools/verify_merkle_binding.py --manifest CROSS_REPO_INVARIANT_MANIFEST.json
```

**Binding schema in CROSS_REPO_INVARIANT_MANIFEST.json:**

```json
{
  "binding_timestamp": "ISO-8601",
  "repo1": {
    "name": "aidoruao/orthogonal-engineering",
    "merkle_root": "<sha256>",
    "commit_sha": "<sha>"
  },
  "repo2": {
    "name": "aidoruao/sigma-lora-covenant",
    "merkle_root": "<sha256>",
    "commit_sha": "<sha>"
  },
  "combined_root": "<sha256-of-both-roots>",
  "binding_proof_hash": "<sha256>"
}
```

The `combined_root` is `SHA-256(repo1.merkle_root ∥ repo2.merkle_root)`. Phase 3 Eschaton requires this combined root to be stable (unchanged) for at least two consecutive CI runs before declaring Sabbath Halt.

For `aidoruao/truthsystems-mod`, binding is via `COVENANT_MANIFEST.txt` which records the orthogonal-engineering Merkle root and commit SHA. The Minecraft mod does not produce a Merkle root itself; its binding is one-directional (orthogonal-engineering binds to it, not vice versa).

## Standards Applicability

The following table maps standards from `STANDARDS_REGISTRY.json` to the three repositories. YS-* standards are universal design targets; their enforcement tooling exists only in orthogonal-engineering but the architectural requirements apply to all repos.

| Standard ID | Applies to Repo 1 (orthogonal-engineering) | Applies to Repo 2 (sigma-lora-covenant) | Applies to Repo 3 (truthsystems-mod) |
|---|---|---|---|
| YS-001 (Every truth is derivable) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-002 (Every derivation is reproducible) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-003 (Every mutation is re-verifiable) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-004 (No authority without proof) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-005 (No hidden state) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-006 (No unverifiable dependency) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-007 (No recursive wipe) | Yes — enforced in CI | Yes — design target | Yes — design target |
| YS-008 (No nominalism) | Yes — enforced in CI | Yes — design target | Yes — design target |
| CS-001 (Fraction only, no float) | Yes — enforced | Yes — enforced | No — Java repo; use BigDecimal equivalent |
| CS-002 (ProofObject for all checks) | Yes — enforced | Yes — enforced | No — no Python; COVENANT_MANIFEST.txt serves as evidence record |
| CS-003 (No assert) | Yes — enforced | Yes — enforced | No — Java; use JUnit assertions only in tests |
| CS-004 (No stubs / no pass bodies) | Yes — enforced | Yes — enforced (GAP-4 history) | No — Java; no pass equivalent |
| QG-001 (No nominalism) | Yes — enforced | Yes — enforced | Partial — COVENANT_MANIFEST.txt must name real implemented features |
| QG-002 (No dogma) | Yes — enforced | Yes — enforced | Partial — Java Javadoc must include @falsifiesIf annotations when added |
| BC-001 (No destructive operations) | Yes — enforced | Yes — enforced | Yes — BUILD.bat must not delete source files |
| BC-003 (Append-only logs) | Yes — AGENT_FEED.md | Yes — covenant log | Yes — COVENANT_MANIFEST.txt must be append-only |
| DR-001 (Technical register documentation) | Yes — enforced | Yes — enforced | Yes — README and COVENANT_MANIFEST.txt must use technical register |
| WF-001 (Workflow constraint) | Yes — enforced | Yes — own CI | Not applicable — no GitHub Actions yet |
| WF-002 (fetch-depth: 0) | Yes — enforced | Yes — own CI | Not applicable |
| WF-003 (skip ci in bot commits) | Yes — enforced | Yes — own CI | Not applicable |
| INT-001 (AGENT_FEED chain integrity) | Yes — enforced | No — no feed | No — no feed |
| INT-002 (build_feed_entry 8 fields) | Yes — enforced | No — no feed | No — no feed |
| T3-001 (onboard_agent.py before changes) | Yes — enforced | No — own tooling | No — own tooling |
| T3-002 (context_window_estimator.py) | Yes — enforced | No | No |
| T4-001 (GLOSSARY.md ≥40 entries) | Yes — this repo | No | No |
| T4-002 (AGENT_CAPABILITIES_MATRIX.md ≥10 agents) | Yes — this repo | No | No |
| T4-003 (CROSS_REPO_INSTRUCTIONS.md references all 3 repos) | Yes — this repo | No | No |

## Coordinating Cross-Repo Commits

When an invariant in `aidoruao/orthogonal-engineering` references or depends on `aidoruao/sigma-lora-covenant`, coordinate commits using the following procedure to avoid drift between the two repositories:

**Step 1: Establish the cross-repo change plan**

Before making changes in either repository, document which files in each repo will change and how the shared invariant is affected. Record this in the consent log:

```bash
python tools/append_consent.py \
  --candidate-id "<agent>-<session>" \
  --authoriser "@aidoruao" \
  --action "cross-repo-change" \
  --scope-glob "src/domains/**,CROSS_REPO_INVARIANT_MANIFEST.json" \
  --justification "Updating invariant X which is referenced by sigma-lora-covenant/src/principles.py"
```

**Step 2: Apply changes in dependency order**

Changes must be applied in this order to avoid a window where repo 1 references a principle that does not yet exist in repo 2:

1. Apply and merge the change in `aidoruao/sigma-lora-covenant` first.
2. Record the resulting commit SHA from sigma-lora-covenant.
3. Update `CROSS_REPO_INVARIANT_MANIFEST.json` in `aidoruao/orthogonal-engineering` with the new sigma-lora-covenant commit SHA.
4. Apply the corresponding invariant change in `aidoruao/orthogonal-engineering`.
5. Merge the orthogonal-engineering PR.

**Step 3: Update the Merkle binding**

After both PRs are merged:

```bash
python tools/bind_merkle_roots.py \
  --root1 CROSS_REPO_MERKLE_ROOT.txt \
  --root2 https://raw.githubusercontent.com/aidoruao/sigma-lora-covenant/main/MERKLE_ROOT.txt \
  --manifest CROSS_REPO_INVARIANT_MANIFEST.json

git add CROSS_REPO_INVARIANT_MANIFEST.json CROSS_REPO_MERKLE_ROOT.txt
git commit -m "chore(cross-repo): update Merkle binding after cross-repo invariant change [skip ci]

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

**Step 4: Run cross-repo consistency check**

```bash
python tools/cross_repo_consistency_check.py \
  --repo1 . \
  --repo2 sigma_lora_local/ \
  --manifest CROSS_REPO_INVARIANT_MANIFEST.json
```

This check must exit zero before declaring the cross-repo change complete. A non-zero exit is a blocking failure.

**Emergency rollback:** If a cross-repo change causes a consistency failure, revert both commits in reverse order (orthogonal-engineering first, then sigma-lora-covenant). Do not attempt to fix forward without first verifying the consistency check passes on the reverted state.
