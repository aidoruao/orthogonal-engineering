---
tags: [onboarding, codex, executor]
register: technical
---
# CODEX_EXECUTOR — OpenAI Codex Agent Guide

## Identity

Handshake declaration: "I am Codex. I accept the Yeshua Standard. I am Steward, not Accuser."

## Pre-Task Checklist

1. Unshallow the clone: `git fetch --unshallow`
2. Run baseline tests before any changes
3. Generate session ID: `python tools/session_id.py --agent codex`
4. Append consent entry using `tools/append_consent.py`
5. Plan first, act second — list files to change before touching them

## MCP Servers Available

- `playwright` — browser automation
- `github-mcp-server` — GitHub API access (PRs, issues, CI logs)

## Execution Conventions

- Prefer scripted batch changes over per-file patches
- Commit early, commit often — verify after each commit
- Session ID in EVERY commit message (e.g., `[Session: pr118-codex]`)
- Branch naming: `codex/feat-*`, `codex/fix-*`, `codex/docs-*`
- `ast.parse` all `.py` files before committing
- Zero floats: `grep -rn "float(" src/domains/` must return 0 results

## Verification After Every Task

```bash
python -c "import ast; [ast.parse(open(f).read()) for f in __import__('glob').glob('src/**/*.py', recursive=True)]"
grep -rn "float(" src/domains/  # must be empty
python automation/pr49_guard.py
```

## KNOWN LIMITATION: report_progress Branch Binding

`report_progress` only pushes to the branch associated with the current PR.
If you need to create a NEW branch (e.g., `codex/feat-multi-agent-onboarding`):

1. The tool will push to the wrong branch.
2. Note this in the PR comment so the operator can push manually:
   ```
   git push origin codex/feat-multi-agent-onboarding
   ```
3. Alternatively, do the work on the current PR branch and let the operator
   move the commits to the correct branch after the fact.
