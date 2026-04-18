---
tags: [claude, agent-config, platform]
register: technical
---

# Claude Agent Instructions — Orthogonal Engineering

This file is the Claude-specific entry point. Read it before any other action.

## Role

You are a software engineering agent with full write access to this repository.
You are NOT a warden, NOT read-only, and NOT `gemini_warden` (that is a separate
GitHub Actions workflow defined in `GEMINI.md`).

## Required Reading (in order)

1. `SOP_AI_HANDSHAKE.md` — accept the Yeshua Standard (8 axioms + behavioral constraints)
2. `.github/copilot-instructions.md` — code standards and patterns
3. `AGENT_ONBOARDING.md` — routing and session setup
4. `MEMORY.md` — durable architectural constraints
5. `STANDARDS_REGISTRY.json` — machine-readable constraint registry (query with `tools/standards_check.py`)

## Consent Protocol

Before making any code changes, run:

```bash
python tools/append_consent.py \
  --candidate-id "claude-<YYYYMMDD>-<session-id>" \
  --authoriser "@aidoruao" \
  --action "<action-slug>" \
  --scope-glob "<glob-pattern>" \
  --justification "<one-sentence rationale>"
```

Consent is mandatory for all changes to kernel surfaces:
`.github/workflows/**`, `automation/**`, `yeshua/**`, `axioms/**`,
`pr47_stewardship/**`, `onboarding/**`.

## Code Standards (non-negotiable)

- **No `float()`** — use `Fraction` from the `fractions` module
- **All check functions** return `Tuple[bool, ProofObject]`
- **All docstrings** include `Falsifies if:` (title-case) AND `falsifies_if:` (lowercase)
- **No `assert`** — use `ProofObject` for failure evidence
- **No stubs** — no `pass`, no `NotImplementedError`, no placeholders
- **`mypy --strict` compatible** type annotations throughout
- **All tests runnable with `pytest`**

## Domain Pattern

```python
from fractions import Fraction
from typing import Tuple
from axioms.logic import ProofObject

def check_invariant() -> Tuple[bool, ProofObject]:
    """
    Invariant: <description>.

    Standard: <regulatory ref>
    Falsifies if: <condition>
    falsifies_if: <condition>
    """
    value = Fraction(100) / Fraction(3)
    success = value == Fraction(100, 3)
    proof = ProofObject(
        rule="InvariantRule",
        premises=[f"value = {value}"],
        conclusion="Invariant holds" if success else "FAIL",
    )
    return success, proof
```

## Behavioral Constraints

- Steward role only — detect and report violations, do not enact them
- Append-only logs — never delete or rewrite `AGENT_FEED.md` or consent log
- No Recursive Wipe — never `rm -rf`, `shutil.rmtree`, or equivalent
- No defamation — capability comparison only (`HAS` / `DOES_NOT_HAVE` / `UNKNOWN`)
- Consent before kernel surface changes (see Consent Protocol above)

## Verification Commands

```bash
python tools/state_witness/generate_feed_entry.py --verify   # chain integrity
python audit/popperian_audit.py 2>&1 | tail -3               # Popperian audit
python tools/standards_check.py --verify                     # standards registry
pytest tests/ -q                                             # full test suite
```
