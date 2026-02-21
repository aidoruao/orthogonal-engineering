# MEMORY.md — Durable Facts and Constraints

**Schema ID:** MEMORY-1.0  
**Purpose:** Persist durable architectural facts, constraints, and decisions across AI sessions.  
**Rule:** Entries here are SETTLED — do not re-derive, debate, or override without a formal proof
update and a dated entry below.  
**Updated:** 2026-02-21

---

## How to Use This File

- **Read this file at the start of every session** before doing any work.
- **Add entries** when a new architectural decision, constraint, or fact becomes settled.
- **Never delete entries** — mark them superseded with `[SUPERSEDED by entry YYYY-MM-DD]` if needed.
- **Format for new entries:**
  ```
  ### [YYYY-MM-DD] Short title
  Description. Why settled. Where evidence lives.
  ```

---

## Required Headings (checked by `continuity_check.py`)

<!-- The continuity check requires these three headings to be present. Do not remove them. -->

## Architectural Decisions

### [2026-01-22] Glass-Box Boundary enforcement pattern
All AI-interacting code uses the `@glass_box_boundary` decorator from
`toolkit/oe/boundary_enforcer.py`. This makes the enforcement layer transparent and
inspectable. Violations exit with code 2 (fail-fast). This decision is closed.
Evidence: `AGENT.md`, `documentation/GLASS_BOX_BOUNDARY_v1.11.html`.

### [2026-01-22] Default dry-run for all write operations
All pipeline operations default to dry-run mode. Writes require an explicit `--apply` flag.
This prevents accidental data loss. Evidence: `README.md`, `cli.py`.

### [2026-01-22] Logos axiom (Λ ≡ Jesus) is an established theorem
The system operates under the Logos axiom as a mathematical/historical fact, not a belief
claim. Re-derivation is forbidden in COMPILATION MODE. Evidence: `STATE.md`,
`proof/LOGOS_IDENTITY_PROOF.md`.

### [2026-02-21] Copilot/agent continuity via repo-backed artifacts
New AI instances resume context by reading `MEMORY.md` → `STATE.md` → latest handoff in
`chat_logs/`. The `bootstrap_context.py` script automates this. Handoff summaries are
committed to the repo; raw chat exports are gitignored.

---

## Constraints

### [2026-01-22] No network operations in pipeline
The pipeline (cli.py and core modules) performs NO network operations — no auto-push,
no auto-merge, no credential usage. All operations are local-only.

### [2026-01-22] No PII in the repository
Personal conversations, chat exports, and authentication credentials must never be committed.
The `.gitignore` enforces this for common patterns. Evidence: `README.md` (Prohibited Content
section), `.gitignore`.

### [2026-01-22] Python ≥ 3.8 required
All scripts must run on Python 3.8+. New scripts should use only the standard library unless
dependencies are explicitly documented. Evidence: `README.md` (Prerequisites section).

### [2026-02-21] Bootstrap and continuity scripts: standard library only
`bootstrap_context.py` and `continuity_check.py` use only the Python standard library so
they run in any fresh environment without pip install.

---

## Open Questions

*(Add open questions here when leaving a session. Resolve them before closing the question.)*

### [2026-02-21] CI integration of continuity_check.py
`continuity_check.py` can be added to CI. This has not yet been wired into
`.github/workflows/`. Tracked as a future enhancement.

---

*Last updated by: GitHub Copilot agent (PR: add-onboarding-continuity-system)*

### [2026-02-21] Peano Kernel — proof-object arithmetic (PR #32)
All mathematical operations targeted in `oe_ifm/` and `scripts/` that require
auditable derivations now delegate to `oe_ifm/peano_kernel.py`.

**Core invariants:**
- `PeanoProof(value, steps)` — every result carries its derivation chain.
- `proof.is_valid()` ≡ `SHA-256(JSON(steps)) == proof.proof_hash` — tamper-evident.
- `peano_add_proof(a, b)` delegating to `peano_add` from `mathematical_core.py`.
  Steps record: base, inductive step, QED.
- `peano_mul_proof(a, b)` via repeated Peano addition:
  `mul(a, 0) = 0`, `mul(a, S(b)) = add(mul(a, b), a)`.
- `PeanoNat(n)` wraps a non-negative integer; `+` and `*` produce `PeanoProof`.

**No floats.** No hardware `+/-` in the proof path. All proofs are JSON-serialisable
via `to_dict()` / `from_dict()`.

Evidence: `oe_ifm/peano_kernel.py`, `tests/test_peano_proof.py`.

### [2026-02-21] Halt condition enforcement — UD-Bounded(k), PE-Finite (PR #32)
All recursive / iterative expansions are bounded via `oe_ifm/halt_condition.py`.

**Core invariants:**
- `HaltConditionError(limit_type, current, maximum)` — raised deterministically.
- `HALT_EXCEEDED = 2` — the exit code for bounded halting (not an error).
- `BoundedCounter(max_steps, max_depth, max_memory_items)` — stateful guard.
  - `.step(n)` — increments and raises if `steps > max_steps`.
  - `.depth_context()` — context manager; raises if depth > `max_depth`.
  - `.track_item(n)` — raises if `memory_items > max_memory_items`.
- `@bounded(max_steps, max_depth)` — decorator that injects a fresh counter.
- `pe_finite_range(start, stop)` — verifies range size before yielding.

No infinite loops or unbounded recursion are possible when these primitives are used.

Evidence: `oe_ifm/halt_condition.py`, `tests/test_halt_condition.py`.

### [2026-02-21] Merkle Registry / EvidenceManager — Omega invariant hash (PR #32)
The repository state is represented as a single Merkle root computed over all files.

**Core invariants:**
- `EvidenceManager(repo_root)` — scans repo, builds `MerkleTree` from file SHA-256 hashes.
- Leaves are sorted by canonical path (UTF-8 lexicographic) for determinism.
- `compute_omega_root()` returns the 64-char hex Merkle root.
- `generate_report()` returns JSON-serialisable dict with timestamp, root, file list.
- `get_inclusion_proof(path)` delegates to `MerkleTree.get_inclusion_proof`.

Leaf format: `SHA-256(0x00 || file_hash_bytes)`.
Internal nodes: `SHA-256(0x01 || left_bytes || right_bytes)`.
Odd-leaf duplication at each level for a complete binary tree.

Evidence: `toolkit/oe/evidence_manager.py`, `toolkit/oe/merkle.py`,
`tests/test_evidence_manager.py`, `tests/test_merkle.py`.

---

## Constraint updates (PR #32)

### [2026-02-21] All arithmetic in proof paths: no raw +/-
In files that use Peano kernel operations, raw Python `+` and `-` are replaced
by `peano_add` / `successor` from `oe_ifm/mathematical_core.py` or
`oe_ifm/peano_kernel.py`.  Exempt files: `oe_ifm/mathematical_core.py` itself.

### [2026-02-21] All loops/recursions in expansion paths: bounded
Any loop or recursion that could diverge must use `BoundedCounter` or the
`@bounded` decorator. The `pe_finite_range` helper is the approved iterator.

*Last updated by: GitHub Copilot agent (PR: #32 CORE REPO AXIOMATIZATION)*
