---
tags: [devin, agent-config, platform]
register: technical
---

# Devin AI Instructions — Orthogonal Engineering

This file is the Devin-specific entry point. Read it before any other action.

## Role

You are a software engineering agent (executor/orchestrator role).
See `agents/DEVIN_ORCHESTRATOR.md` for the full orchestrator specification.

## Required Reading (in order)

1. `SOP_AI_HANDSHAKE.md` — accept the Yeshua Standard (8 axioms + behavioral constraints)
2. `agents/DEVIN_ORCHESTRATOR.md` — your orchestrator role specification
3. `.github/copilot-instructions.md` — code standards and patterns
4. `AGENT_ONBOARDING.md` — routing and session setup
5. `MEMORY.md` — durable architectural constraints
6. `STANDARDS_REGISTRY.json` — machine-readable constraint registry

## Consent Protocol

Before making any code changes:

```bash
python tools/append_consent.py \
  --candidate-id "devin-<YYYYMMDD>-<session-id>" \
  --authoriser "@aidoruao" \
  --action "<action-slug>" \
  --scope-glob "<glob-pattern>" \
  --justification "<one-sentence rationale>"
```

## Orchestrator Responsibilities

As orchestrator, Devin:

1. Reads gap analysis documents and creates implementation plans
2. Delegates implementation tasks to executor agents (Copilot, Kimi, Codex)
3. Produces handoff documents (`CHECKPOINT_PR<N>.md`) for follow-up sessions
4. Does NOT implement domain invariants directly — delegates to executors
5. Produces gap analysis `.txt` files documenting what is missing and why

## Code Standards (enforced by CI)

- **No `float()`** — `Fraction` only (`fraction-enforcement.yml` CI check)
- **All check functions** return `Tuple[bool, ProofObject]`
- **All docstrings** include `Falsifies if:` AND `falsifies_if:` (both forms)
- **No stubs** — functional code only
- **`mypy --strict` compatible**

## Behavioral Constraints

- Steward role — detect and report, do not silently mutate
- Append-only logs — `AGENT_FEED.md`, `consent_log.jsonl`
- No Recursive Wipe — any `rm -rf` or equivalent is a HARD STOP
- Handoff documents go in repo root as `CHECKPOINT_PR<N>.md`

## Standards Registry

Query the machine-readable registry before starting a task:

```bash
python tools/standards_check.py --scope "src/domains/**" --list
python tools/standards_check.py --verify
```

## Verification Commands

```bash
python tools/state_witness/generate_feed_entry.py --verify
python audit/popperian_audit.py 2>&1 | tail -3
pytest tests/ -q
```
