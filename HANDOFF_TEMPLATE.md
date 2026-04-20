---
tags: [handoff-template]
register: documentation
---

# HANDOFF_TEMPLATE.md — Session Handoff Summary Template

**Instructions:** Copy this file, fill in every section, and save as
`chat_logs/handoff_YYYY-MM-DD.md` (or `handoff_YYYY-MM-DD_HH-MM.md` if multiple sessions per day).
Commit the filled handoff to the repo so the next instance can resume without re-deriving context.

---

## Handoff Summary

**Date:** YYYY-MM-DD  
**Session start:** HH:MM UTC  
**Session end:** HH:MM UTC  
**Agent/instance:** (e.g. GitHub Copilot, Claude 3.5, GPT-4o)  
**Branch:** (git branch name)  
**Last commit:** (git short SHA and message)

---

## What Was Done This Session

*(List completed tasks in plain language. Be specific — the next instance has no memory.)*

- [ ] Task 1: …
- [ ] Task 2: …

---

## What Is In Progress (incomplete)

*(List unfinished tasks with enough context to resume them.)*

- **Task:** …  
  **Status:** …  
  **Next action:** …  
  **Relevant files:** …

---

## Decisions Made

*(List any architectural decisions, constraints, or facts settled during this session.
Copy significant ones to `MEMORY.md` before closing.)*

| Decision | Rationale | Evidence/File |
|----------|-----------|---------------|
| … | … | … |

---

## Open Questions Left Unresolved

*(List questions the next instance should investigate first.)*

1. …
2. …

---

## Files Changed (key files only)

*(Git diff summary or list of important changed files — helps the next instance know where to look.)*

```
modified:   path/to/file1.py
added:      path/to/file2.md
```

---

## Context for Next Instance

*(Anything the next instance absolutely must know to avoid mistakes or re-work.)*

- …

---

## Commands to Resume

*(Copy-paste commands for the next instance to get back into the correct state.)*

```bash
# Activate venv
source .venv/bin/activate   # Linux/macOS
# .\.venv\Scripts\Activate.ps1  # Windows

# Load context
python bootstrap_context.py

# Continue from where we left off
# <add specific command here>
```

---

*This handoff was written using `HANDOFF_TEMPLATE.md`. If the template has changed since this
session, reconcile differences before relying on this handoff.*
