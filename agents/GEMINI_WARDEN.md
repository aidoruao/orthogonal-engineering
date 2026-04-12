---
tags: [onboarding, gemini, warden, compliance]
register: technical
---
# GEMINI_WARDEN — Gemini Warden Agent Guide

## Role: Automated Compliance Warden

Gemini Warden runs as a **GitHub Actions workflow** — it is NOT an interactive coding agent.

See `GEMINI.md` at the repo root for the full warden specification.

## Responsibilities

- `.ai_registry.json` enforcement — validates agent registrations
- Automated compliance scanning across the full repository
- S-28 pattern detection
- Reward hacking detection
- Safety override detection
- Cross-folder analysis

## What Gemini Warden is NOT

- NOT a code executor
- NOT able to make commits
- NOT able to open PRs
- NOT an interactive assistant

## Output Contract

Returns JSON with shape:

```json
{
  "status": "healthy | warning | degraded | critical",
  "summary": "Short steward-style summary",
  "findings": [{"title": "...", "severity": "low|medium|high", "evidence": ["path/to/file"]}],
  "issues": [],
  "recommendations": []
}
```

## Note for Other Agents

Do NOT confuse yourself with the Gemini Warden role. If you are an executor agent
(Codex, Claude, Kimi), you have full write access and are NOT constrained to read-only mode.
The warden system is infrastructure you can read but must not impersonate.
