---
tags: [onboarding, kimi, executor]
register: technical
---
# KIMI_EXECUTOR — Kimi Code CLI Agent Guide

## Capabilities

- **262k token context window** — largest of all agents in this repo
- Supports subagent spawning and parallel execution within a session
- Auto-generates session IDs: `kimi-cli-<uuid>`

## Best Use Cases

- Mass domain creation (10+ domains in a single session)
- Batch refactoring across many files
- Multi-file changes requiring large context

## Execution Conventions

- Session tracking via `tools/session_tracking/cli_usage_tracker.py`
- See `COPILOT_ONBOARDING.md` Section 10 for full Kimi-specific documentation
- Session ID format: `kimi-cli-<uuid4>`

## HALT Protocol

| Token Count | Action |
|-------------|--------|
| < 200k | Continue normally |
| 200k–220k | Commit all pending work, note remaining tasks in PR description |
| > 220k | HALT immediately — close session, open new session to continue |

Failure to HALT at 220k causes scrollback truncation and silent data loss.

## Verification After Every Task

```bash
python -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('src/**/*.py', recursive=True)]"
grep -rn "float(" src/domains/  # must be empty
```
