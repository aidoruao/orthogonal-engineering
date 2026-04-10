# COPILOT_ONBOARDING.md — GitHub Copilot / AI Agent Onboarding

**Version:** 1.0  
**Applies to:** GitHub Copilot, Claude, GPT, and any AI agent working in this repository  
**Updated:** 2026-04-08  
**Status:** ACTIVE — REQUIRED READING

---

## 1. Purpose

This document is the canonical "start here" onboarding path for any new AI/Copilot instance
working in the `aidoruao/orthogonal-engineering` repository.

Following this document lets you:
- Set up a local Python virtual environment quickly.
- Load all repo-backed continuity artifacts so you can resume prior work without re-deriving it.
- Emit a single context block you can paste into any LLM conversation to restore context.

---

## 2. Boot Sequence (follow in order)

### Step 1 — Verify the repo location

```bash
# You should be in the repo root:
pwd   # should end with orthogonal-engineering
ls COPILOT_ONBOARDING.md    # this file must exist
```

### Step 2 — Create and activate a Python virtual environment

```bash
# Create the venv (first time only)
python -m venv .venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate on Windows (CMD)
.\.venv\Scripts\activate.bat
```

Install the repo's dependencies:

```bash
pip install -r requirements.txt
```

### Step 3 — Run the bootstrap context generator

```bash
python bootstrap_context.py
```

This script:
- Validates that continuity artifacts (`STATE.md`, `MEMORY.md`) exist and have required headings.
- Loads the latest chat log from `chat_logs/` (if present).
- Prints a consolidated **CONTEXT BLOCK** that you can paste into your Copilot/LLM prompt.

### Step 4 — Read canonical context files (in order)

| # | File | Purpose |
|---|------|---------|
| 1 | `MEMORY.md` | Durable facts, constraints, and architectural decisions |
| 2 | `STATE.md` | Established proofs, current phase, closed decisions, open questions |
| 3 | `HANDOFF_TEMPLATE.md` | Template for writing session handoff summaries |
| 4 | `AGENT.md` | Glass-Box Boundary enforcement rules |
| 5 | `AI_INTERACTION_CONTRACT.md` | AI interaction protocol |

### Step 5 — Acknowledge your starting context

Before doing any work, state the following aloud (or in your first reply):

```
CONTEXT LOADED:
  - MEMORY.md: <yes/no — note any concerns>
  - STATE.md: <current phase, e.g. COMPILATION MODE>
  - Latest handoff: <date of most recent HANDOFF entry, or "none">
READY TO PROCEED.
```

---

## 3. Continuity Artifacts — What They Are and How to Update Them

### `MEMORY.md`

**What it is:** A persistent, append-only log of durable facts, constraints, and architectural
decisions that must survive across AI sessions. Think of it as the "long-term memory" of the
project.

**When to read it:** Always — at the start of every session.

**When to update it:** When a new architectural decision, constraint, or fact is settled and
should never be re-derived. Add a dated entry under the appropriate heading.

**Format:**
```markdown
### [YYYY-MM-DD] Fact/Decision title
Brief description. Why this is settled. Where to find the proof/evidence.
```

### `STATE.md`

**What it is:** The current operational state of the system — which proofs are closed, which
goals are active, and what open questions remain.

**When to read it:** At the start of every session, after reading `MEMORY.md`.

**When to update it:** When the phase changes, a goal is completed, or a new open question
surfaces. Always update the `## Open Questions` section when you leave work mid-session.

### `HANDOFF_TEMPLATE.md`

**What it is:** A template for writing "session handoff" summaries. When a session ends, copy
this template, fill it out, and commit it as `chat_logs/handoff_YYYY-MM-DD.md` (or similar).
This gives the next instance an exact resume point.

**When to use it:** At the end of any significant work session.

---

## 4. Chat Logs and Session Persistence

The `chat_logs/` directory (gitignored for personal logs, but committed handoff summaries are
acceptable) stores session artifacts:

- `chat_logs/handoff_YYYY-MM-DD.md` — session handoff summaries (commit these)
- `chat_logs/*.jsonl` — raw chat exports (do NOT commit — gitignored)

The `bootstrap_context.py` script automatically finds and loads the most recent `handoff_*.md`
file in `chat_logs/`.

---

## 5. Continuity Check

To verify all continuity artifacts are in order:

```bash
python continuity_check.py
```

Exit codes:
- `0` — all checks pass
- `1` — one or more artifacts are missing or malformed
- `2` — bootstrap script fails to run

This check can also be run in CI.

---

## 6. Troubleshooting

| Problem | Solution |
|---------|---------|
| `MEMORY.md` or `STATE.md` missing | Run `continuity_check.py` — it will report missing files |
| `bootstrap_context.py` fails | Check Python version (`python --version` must be ≥ 3.8); no extra deps required |
| `chat_logs/` not found | Create it: `mkdir chat_logs` — it is gitignored for raw logs |
| Venv not activating on Windows | Use PowerShell with execution policy: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Context block too long | Edit `bootstrap_context.py` — reduce `MAX_CHAT_LINES` at the top of the file |

---

## 7. Quick Reference

```
CONTINUITY FILES:
  MEMORY.md                  # Durable facts — read first
  STATE.md                   # Current system state — read second
  HANDOFF_TEMPLATE.md        # Copy, fill, commit when leaving

SCRIPTS:
  bootstrap_context.py       # Generates context block for LLM paste
  continuity_check.py        # Validates all artifacts are present

CHAT LOGS (local only, gitignored):
  chat_logs/*.jsonl           # Raw session exports
  chat_logs/handoff_*.md      # Handoff summaries (commit these)
```

---

## 8. External Claim Tagging and Contract Enforcement

### 8.1 External Claim Tagging (`external_claim`)

Any output or claim that originates **outside the Consistency Scope S** (e.g.,
from an external LLM, a third-party API, or an unverified user input) **must**
be tagged before entering the system.  Untagged external data must never be
treated as a proof object.

Use `tag_external_claim` from `toolkit.oe.boundary_enforcer`:

```python
from toolkit.oe.boundary_enforcer import tag_external_claim, assert_not_external_claim

# Tag data received from an external source
external = tag_external_claim(raw_llm_output, source="copilot-response")
# → {"external_claim": True, "value": raw_llm_output, "source": "copilot-response"}

# At any internal proof-consumption site, assert the object is not external
assert_not_external_claim(trusted_proof_object, context="my_function")
# Raises ExternalClaimError if the object carries external_claim=True
```

Key rules:
- **Always tag** LLM/AI outputs, external API results, and user-supplied data with `tag_external_claim`.
- **Never** pass a tagged object directly to a function that expects a proof object.
- Use `assert_not_external_claim` at every proof-consumption boundary.

### 8.2 Schema/Contract Enforcement

Every function that crosses a Glass-Box boundary must declare its input and
output contracts using `validate_input_schema` / `validate_output_schema`.
Contract failures **abort execution** and emit a deterministic violation record
to the `toolkit.oe.boundary_enforcer` logger.

```python
from toolkit.oe.boundary_enforcer import validate_input_schema, validate_output_schema

INPUT_SCHEMA = {"type": "dict", "required": ["path"], "properties": {"path": {"type": "str"}}}
OUTPUT_SCHEMA = {"type": "dict", "required": ["status"]}

@validate_input_schema(INPUT_SCHEMA)
@validate_output_schema(OUTPUT_SCHEMA)
def process(*, path: str) -> dict:
    ...
```

On failure a `ContractViolationError` is raised with a `.record` dict that
includes `violation`, `direction`, `function`, `errors`, and `timestamp_utc`.

### 8.3 UD-Bounded(k) Loop Guard

All loops/recursions in onboarding and audit pathways are bounded using
`oe_ifm.halt_condition.BoundedCounter`.  When a loop would exceed its
configured ceiling it raises `HaltConditionError` rather than hanging.

```python
from oe_ifm.halt_condition import BoundedCounter, HaltConditionError

counter = BoundedCounter(max_steps=10_000)
for item in audit_items:
    counter.step()          # raises HaltConditionError if steps > max_steps
    process(item)
```

The `CheckOnboardingPipeline.stage_2_validate_structure` method already uses
this pattern with a ceiling of `_MAX_AUDIT_ARTIFACTS = 10_000`.

---

## 9. PR #40 — State Witness Layer (AGENT_FEED.md)

### 9.1 What It Is

PR #40 adds a publicly observable, cryptographically anchored, **append-only ledger**
derived from the frozen invariant spec produced by PR #39.

| Artifact | Location | Purpose |
|---|---|---|
| Ledger file | `AGENT_FEED.md` | Markdown table of witness entries (newest at bottom) |
| Generator script | `tools/state_witness/generate_feed_entry.py` | Creates and appends feed entries |
| CI workflow | `.github/workflows/pr40-canonical-presence.yml` | Appends entry on every push to `main` |
| Tests | `tests/test_pr40_state_witness.py` | 33 tests covering determinism, append-only, idempotency |

### 9.2 How to View the Ledger

```bash
cat AGENT_FEED.md
```

The table columns are:

| Column | Description |
|---|---|
| `timestamp` | UTC ISO 8601 time of entry generation |
| `freeze_hash` | SHA-256 of `resilience/invariant_spec_v2.freeze` (CRLF-normalised) |
| `merkle_root` | Spec-set Merkle root from the freeze file (PR #39 output) |
| `invariant_spec_version` | `v2` |
| `source_paths` | Comma-separated sorted list of spec files |
| `commit_sha` | Git commit SHA that triggered the entry |
| `prev_entry_hash` | SHA-256 of the previous row's payload (hash chain) |
| `entry_hash` | SHA-256 of this row's full payload |

### 9.3 How to Generate a Feed Entry Locally

```bash
# Preview the entry that would be appended (no disk write):
python tools/state_witness/generate_feed_entry.py --dry-run

# Append a real entry (idempotent — skipped if current commit already recorded):
python tools/state_witness/generate_feed_entry.py

# Verify the hash-chain integrity of all existing entries:
python tools/state_witness/generate_feed_entry.py --verify
```

### 9.4 Idempotency and Chain Integrity

- **Idempotency**: If the current `HEAD` commit SHA already appears in `AGENT_FEED.md`,
  the script exits without modifying the file.  Repeated CI runs for the same commit
  produce identical output.
- **Hash chain**: Each row records the `entry_hash` of the previous row as
  `prev_entry_hash`.  Run `--verify` to confirm the chain is unbroken.
- **Determinism**: Set `PYTHONHASHSEED=40` (done automatically in CI) and the same
  freeze file always produces the same `freeze_hash` and `merkle_root`.

---

## 10. Kimi Code CLI Integration

### 10.1 Session Format

Kimi Code CLI sessions use identifier format: `kimi-cli-<uuid>`

Example: `kimi-cli-8fbdcdb9-7ab9-403c-a146-8e4224b8ba29`

### 10.2 For Devin Coordinating with Kimi

See `docs/DEVIN_ONBOARDING.md` for:
- How to onboard Kimi sessions
- Paste-in format for Kimi
- Commit stamping requirements
- Token budget coordination

### 10.3 For Kimi Sessions

See `docs/KIMI_ONBOARDING.md` for:
- Quick start commands
- Session identity format
- Commit message templates
- Token budget management

---

## 11. DarkShadow44 Vendored Repositories

### 10.1 Overview

5 of DarkShadow44's public repositories are vendored in `investigations/darkshadow44/` with full source trees, SHA-256 manifests, and non-affiliation statements. See **DEVIN_ONBOARDING.md Section 10** for complete details.

### 10.2 Quick Reference

| Repository | Location | Key Files |
|------------|----------|-----------|
| DistantHorizonsStandalone | `investigations/darkshadow44/DistantHorizonsStandalone/` | `src/`, `tools/`, `batch1-4/`, `issue_51_corrected/`, `issue_56_corrected/` |
| Angelica | `investigations/darkshadow44/Angelica/` | `src/`, OpenGL/rendering mixins |
| ArchaicFix | `investigations/darkshadow44/ArchaicFix/` | `src/`, performance fixes |
| Spool | `investigations/darkshadow44/Spool/` | `src/`, multithreading |
| SeasonalHorizons | `investigations/darkshadow44/SeasonalHorizons/` | `src/`, DarkShadow44's own code |

### 10.3 Critical Rules

1. **NEVER modify files under `src/` in vendored repos** — these are immutable forensic copies
2. **SOURCE_INDEX.json commit MUST match VENDOR_MANIFEST.json commit** — integrity check
3. **Use `sha256_manifest.txt` to verify file integrity** — byte-level verification
4. **All analysis artifacts go in sibling directories** — not in `src/`

### 10.4 Issue #51 Context

- **Location:** `investigations/darkshadow44/DistantHorizonsStandalone/issue_51_corrected/`
- **Tools:** `tools/TickHandlerBenchmark.java`, `tools/DhDiagnosticsCommand.java`, `tools/dh-diagnostics.gradle.kts`
- **Status:** Awaiting DarkShadow44 response to analytical tools posted Apr 8

### 10.5 Verification Commands

```bash
# Check all 5 repos have matching commits
python3 -c "
import json
for repo in ['DistantHorizonsStandalone', 'Angelica', 'ArchaicFix', 'Spool', 'SeasonalHorizons']:
    si = json.load(open(f'investigations/darkshadow44/{repo}/SOURCE_INDEX.json'))
    vm = json.load(open(f'investigations/darkshadow44/{repo}/VENDOR_MANIFEST.json'))
    match = si['commit'] == vm['commit']
    print(f'{repo}: {\"MATCH\" if match else \"MISMATCH\"}')"

# Verify file integrity
python3 -c "
import hashlib, json
vm = json.load(open('investigations/darkshadow44/DistantHorizonsStandalone/VENDOR_MANIFEST.json'))
print(f'Merkle root: {vm[\"sha256_tree_root\"][:16]}...')"
```

---

*"Continuity of body is not magic — it is disciplined state management. Write it down. Read it first. Resume without re-deriving."*

**Orthogonal Engineering Continuity Principle**
