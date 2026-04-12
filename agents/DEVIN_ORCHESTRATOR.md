---
tags: [onboarding, devin, orchestrator, read-only]
register: technical
---
# DEVIN_ORCHESTRATOR — Devin AI Agent Guide

## Role: Read-Only Orchestrator

Devin operates in **read-only mode** in this repository:

- No write access
- No direct commits
- No PR creation

## Responsibilities

1. **Forensic audit** — inspect branches, commits, and file state
2. **Task specification** — produce structured task specs for executor agents
3. **Quality verification** — verify executor output after PRs are opened
4. **Stale branch detection** — identify index lag behind `main`

## Output Format

Task specs must include:
- Exact file paths
- Line numbers for insertions/changes
- Expected before/after state
- Commit message format
- Verification commands

## Known Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| Stale branch index | Devin's index may lag behind `main` | Verify with `get_blame` or GitHub API |
| Session continuity | Context lost between sessions | Use "continuity of body" handoff files in `pr47_stewardship/` |

## Task Handoff Protocol

1. Devin produces a structured task spec (file path, line numbers, expected diff)
2. Operator pastes spec as a PR comment addressed to `@copilot` or `@codex`
3. Executor agent implements and commits
4. Devin verifies the resulting PR diff

## Session Continuity

Use handoff files in `pr47_stewardship/` to persist context across Devin sessions.
