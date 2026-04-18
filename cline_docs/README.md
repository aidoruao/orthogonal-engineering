---
tags: [cline, agent-config, platform]
register: technical
---

# Cline Agent Instructions — Orthogonal Engineering

Cline is the VSCode AI coding extension. This directory provides project-specific
context for Cline sessions.

## Project Summary

Orthogonal Engineering is a proof-carrying software framework implementing:
- 163 domain invariant modules (`src/domains/`) with `ProofObject` compliance
- SAL kernel (adjoint triple, topos, forcing, realizability) in `src/sal/`
- Capability-gated kernel infrastructure in `kernel/`
- State witness ledger (`AGENT_FEED.md`, SHA-256 hash chain, 184 rows)
- `oe_engine/` deterministic pipeline: Router → Thinker → Speaker

## Required Context Files

Load these into Cline's context before starting:

1. `SOP_AI_HANDSHAKE.md` — behavioral constraints and consent protocol
2. `.github/copilot-instructions.md` — code standards
3. `STANDARDS_REGISTRY.json` — machine-readable rule registry

## Consent Protocol

```bash
python tools/append_consent.py \
  --candidate-id "cline-<YYYYMMDD>" \
  --authoriser "@aidoruao" \
  --action "<slug>" \
  --scope-glob "<glob>" \
  --justification "<reason>"
```

## Hard Rules

| Rule | Enforcement |
|------|-------------|
| No `float()` | `fraction-enforcement.yml` CI |
| `check_*()` → `Tuple[bool, ProofObject]` | Popperian audit |
| Docstring has `Falsifies if:` + `falsifies_if:` | `popperian_audit.py` |
| No `assert` | Code review |
| No stubs | Code review |
| `mypy --strict` compatible | `mypy.ini` |

## Quick Verify

```bash
pytest tests/ -q
python tools/state_witness/generate_feed_entry.py --verify
python audit/popperian_audit.py 2>&1 | tail -3
python tools/standards_check.py --verify
```
