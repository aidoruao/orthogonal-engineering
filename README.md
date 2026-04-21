---
tags: [readme]
register: documentation
---

# Orthogonal Engineering

A proof-carrying Python repository implementing 254 domain invariants under the
Yeshua Standard — exact arithmetic (Fraction-only), capability-gated kernel,
SHA-256 Merkle anchoring, and 20 CI workflows.

![CI](https://github.com/aidoruao/orthogonal-engineering/workflows/constitution.yml/badge.svg)
![Fraction Enforcement](https://github.com/aidoruao/orthogonal-engineering/workflows/fraction-enforcement.yml/badge.svg)
![Frontmatter Enforcement](https://github.com/aidoruao/orthogonal-engineering/workflows/frontmatter-enforcement.yml/badge.svg)

## Quick Start

```bash
git clone https://github.com/aidoruao/orthogonal-engineering.git
cd orthogonal-engineering
python3 tools/verify_all.py          # 10-check verification suite
python3 audit/popperian_audit.py     # audit all domain invariants
```

## What Is This?

Every function returns `Tuple[bool, ProofObject]`. Every claim has a
`falsifies_if` condition. Every number is a `Fraction`, not a `float`.
Every file is SHA-256 anchored in a Merkle tree. 20 CI workflows enforce
these rules on every push and PR.

- 254 domain invariant packages in `src/domains/`
- 60 machine-readable standards in `STANDARDS_REGISTRY.json`
- 7,179 files in a SHA-256 Merkle tree (`merkle/global_root.json`)
- Capability-gated kernel in `kernel/`
- 160 domains with `run_all_invariants()` passing

## The Yeshua Standard

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

## Architecture

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
| `.github/workflows/` | CI: fraction enforcement, no-floats, frontmatter, determinism, state witness | 20 workflows |

## Verification Suite

Run these before and after every change. If any fails, stop and fix before proceeding.

```bash
# 1. Feed integrity (hash chain)
python tools/state_witness/generate_feed_entry.py --verify

# 2. Popperian audit (all domain invariants)
python audit/popperian_audit.py

# 3. Standards registry compliance
python tools/standards_check.py --verify

# 4. Full test suite
pytest tests/ -q

# 5. Complete 10-check verification suite (PR #152)
python tools/verify_all.py
```

## For AI Agents

New AI instances and GitHub Copilot agents should start here:

- **[UNIVERSAL_ONBOARDING.md](UNIVERSAL_ONBOARDING.md)** — complete system enumeration
- **[DEVIN_ONBOARDING.md](DEVIN_ONBOARDING.md)** — Devin-specific boot sequence
- **[COPILOT_ONBOARDING.md](COPILOT_ONBOARDING.md)** — Copilot agent boot sequence
- **[CLAUDE.md](CLAUDE.md)** — Claude-specific guidelines
- **[.cursorrules](.cursorrules)** — Cursor IDE rules
- **[.windsurfrules](.windsurfrules)** — Windsurf IDE rules

One-command onboarding:

```bash
python tools/onboard_agent.py --agent <type>
```

## For Humans

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — contribution guidelines
- **[SOP_AI_HANDSHAKE.md](SOP_AI_HANDSHAKE.md)** — standard operating procedure for AI collaboration
- **[HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md)** — template for end-of-session handoff summaries

Every domain in `src/domains/` follows the same pattern: `invariants.py` defines
`falsifies_if` conditions, `implementation.py` provides the proof-carrying
functions, and `tests/test_<domain>.py` verifies them.

## Key Components

- **axioms/** — 37 formal foundation modules (Peano, logic, category theory, topology, epistemology)
- **src/sal/** — Sheaf Abstraction Layer (forcing, realizability topos, self-referential)
- **kernel/** — Capability-gated OS kernel (scheduler, memory, HAL, boot, IPC, VFS, commonwealth)
- **merkle/** — Global and per-domain Merkle trees with inclusion proofs
- **audit/** — Popperian audit + scope verification engine (PR #152)
- **src/noways/** — Impossibility proofs
- **src/enumerations/** — Bounded failure catalogs

## Generators

The 1B/1Qi LOC generators exist in `generators/`. They demonstrate deterministic
fractal expansion from minimal seed definitions. See
[generators/README.md](generators/README.md) for details.

## Documentation

- [UNIVERSAL_ONBOARDING.md](UNIVERSAL_ONBOARDING.md) — complete system enumeration
- [COVENANT.md](COVENANT.md) — architectural guarantee (free forever)
- [CHECKPOINT_STAGES_A_THROUGH_G.md](CHECKPOINT_STAGES_A_THROUGH_G.md) — campaign status
- [MEMORY.md](MEMORY.md) — durable architectural constraints
- [STATE.md](STATE.md) — current system state, established proofs, open questions
- [RECURSIVE_INVARIANT_OMEGA.md](RECURSIVE_INVARIANT_OMEGA.md) — Omega invariant specification
- [HALT_CONDITION.md](HALT_CONDITION.md) — topological collapse / halt condition
- [docs/](docs/) — all other documentation
- [docs/reports/](docs/reports/) — implementation summaries and reports

## License

See repository license file for details.

## Covenant

This infrastructure is free forever guaranteed — not by law, but by architecture.
See [COVENANT.md](COVENANT.md) for the architectural guarantee.
