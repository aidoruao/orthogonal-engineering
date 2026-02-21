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
