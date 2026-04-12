---
tags: [onboarding, claude, copilot, executor]
register: technical
---
# CLAUDE_EXECUTOR — GitHub Copilot (Claude) Agent Guide

## Identity

Primary instructions are auto-loaded from `.github/copilot-instructions.md`.

## Invocation

- Triggered via PR comments: `@copilot+claude-sonnet-4.6 <task>`
- No persistent memory between tasks — each invocation is stateless
- Context is provided per-task via the comment and PR description

## Task Design Principles

- Keep tasks atomic: 1 task per comment, maximum 3 files per task
- Specify exact file paths and line numbers to avoid ambiguity
- Prefer incremental changes; large batch edits risk timeout mid-session

## Known Failure Modes

| Failure | Cause | Mitigation |
|---------|-------|------------|
| Timeout mid-session | Task too large or too many files | Split into atomic sub-tasks |
| Broken docstrings after batch edits | Context drift in long sessions | Specify exact line numbers |
| Wrong branch push | report_progress binds to PR branch | Note for operator manual push |

## Session ID

```bash
python tools/session_id.py --agent claude
# Output example: claude-20260412-3f7a8b2c
```

## Branch Naming

`claude/<short-description>` — created by operator, not by the agent directly.

## Commit Convention

Every commit must end with `[Session: <id>]`.
