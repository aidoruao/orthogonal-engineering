---
tags: [agents, capabilities, matrix]
register: technical
---

# AGENT CAPABILITIES MATRIX

This matrix documents the capabilities, constraints, and onboarding files for every AI agent integrated with this repository. Use it to select the appropriate agent for a task, understand context window limits, and configure multi-agent workflows. All agents operate under the Yeshua Standard; warden-mode agents are read-only by definition.

| Agent | Access | Shell | Web | Context Window | Write to Repo | Platform File | Known Limitations |
|---|---|---|---|---|---|---|---|
| GitHub Copilot | read+write | no shell | no web | ~128k tokens | via PR + report_progress (cannot push directly) | `.github/copilot-instructions.md` | Cannot push directly to main; must use PR workflow; no shell execution |
| GPT-5.3-Codex | read+write | sandboxed shell | no web | ~192k tokens | yes (in Codespace) | runs in Codespace | Sandboxed shell limits filesystem access; no live web search |
| Claude (GitHub App) | read+write | no shell | no web | ~200k tokens | yes (via PR) | `CLAUDE.md` | No shell access; relies on tool calls for file operations |
| Devin AI | read+write | full shell | web search | ~128k tokens | yes | `DEVIN.md` | Sessions can die mid-task; 128k context may truncate large domain sweeps |
| Kimi Code CLI | read+write | full local shell | no web | ~220k tokens | yes | `docs/KIMI_ONBOARDING.md` | 220k context halt rule enforced; no web access; local filesystem only |
| Gemini (GitHub Actions) | read-only warden | no shell | no web | ~1M tokens | no (warden mode only) | `GEMINI.md` | Warden mode only; cannot write, commit, or mutate any repository state |
| NotebookLM | read-only | no shell | no web | external memory layer | no | N/A | External memory layer only; cannot execute code or commit changes |
| DeepSeek | read-only analysis | no shell | no web | ~64k tokens | no | N/A | Read-only mathematical analysis; limited context window; no code execution |
| Cursor AI | read+write | local shell | no web | ~200k tokens | yes | `.cursorrules` | Local IDE only; no CI integration; changes must be pushed manually |
| Windsurf AI | read+write | local shell | no web | ~128k tokens | yes | `.windsurfrules` | Local IDE only; limited cross-file context for very large repos |
| Aider CLI | read+write | local shell | no web | model-dependent | yes | `.aider.conf.yml` | Context window depends on backend model; may split large refactors across sessions |
| Cline | read+write | local shell | no web | ~200k tokens | yes | `cline_docs/` | Local VS Code only; tool-call latency on large directory reads |
| Continue.dev | read+write | no shell | no web | model-dependent | yes (via edits) | `.continue/config.json` | No shell access; context window depends on configured model backend |
| Master Questioner | read-only orchestrator | no shell | no web | 1M tokens | no code write | `MASTER_QUESTIONER.md` | Routes inquiry to specialized agents; synthesizes multi-agent outputs into coherent resolution |

## Multi-Agent Workflow Triangle

The recommended multi-agent workflow uses four roles:

**Devin AI — Planning and Orchestration**
Devin handles task decomposition, PR creation, and cross-session coordination. Its web search capability allows it to fetch external documentation. Use Devin when a task requires breaking work into subtasks across multiple sessions or when coordination between agents is needed.

**Kimi Code CLI — Execution**
Kimi handles long-running implementation tasks that require reading many files. Its 220k token context window is the largest available for local execution. The 220k context halt rule (stop reading when 80% of context is consumed) prevents truncation errors. Use Kimi for domain sweeps, large refactors, and multi-file implementation.

**GitHub Copilot — Code Review and CI Fix**
Copilot handles PR-level code review, CI failure diagnosis, and targeted fixes to failing checks. Its PR workflow integration makes it the preferred agent for responding to CI feedback. Use Copilot when a PR needs review comments addressed or a workflow is failing.

**NotebookLM — External Memory Layer**
NotebookLM serves as a persistent external memory layer for conversation history, architectural decisions, and session summaries. It has no write access but can be queried to reconstruct context when returning to a task after a long gap. Use NotebookLM to load context before beginning a new Devin or Kimi session.

## Context Window Planning

Before reading large directories, use `tools/context_window_estimator.py` to estimate token consumption:

```bash
# Estimate tokens for a directory
python tools/context_window_estimator.py --path src/domains/ --json

# Estimate tokens for specific files
python tools/context_window_estimator.py --path src/domains/d_aerospace/invariants.py --json

# Check against a specific agent's context limit
python tools/context_window_estimator.py --path src/domains/ --agent kimi --json
```

The estimator returns a JSON object with `total_tokens`, `file_count`, and `budget_remaining` for the specified agent. If `budget_remaining` is negative, split the read across multiple sessions or use targeted grep patterns instead of directory reads.

**Planning rules by agent:**
- Kimi: halt reading at 80% of 220k (176k tokens consumed)
- Devin: halt reading at 80% of 128k (102k tokens consumed)
- Copilot: target single-PR scope; keep context under 64k for reliable review
- Claude: up to 160k tokens before degradation risk

## Onboarding Commands

Run the onboarding command before making any changes in a new session. The command loads applicable standards, checks environment health, and prints a session summary.

```bash
# GitHub Copilot
python tools/onboard_agent.py --agent copilot

# GPT-5.3-Codex
python tools/onboard_agent.py --agent codex

# Claude
python tools/onboard_agent.py --agent claude

# Devin AI
python tools/onboard_agent.py --agent devin

# Kimi Code CLI
python tools/onboard_agent.py --agent kimi

# Gemini (warden mode — read-only)
python tools/onboard_agent.py --agent gemini

# Cursor AI
python tools/onboard_agent.py --agent cursor

# Windsurf AI
python tools/onboard_agent.py --agent windsurf

# Aider CLI
python tools/onboard_agent.py --agent aider

# Cline
python tools/onboard_agent.py --agent cline

# Continue.dev
python tools/onboard_agent.py --agent continue

# DeepSeek (analysis mode)
python tools/onboard_agent.py --agent deepseek

# NotebookLM (memory layer — no code changes)
python tools/onboard_agent.py --agent notebooklm
```

Each onboarding command validates the environment, loads the agent's platform file, and prints the applicable standards from `STANDARDS_REGISTRY.json`. Use `--skip-env-check` in CI environments where the full environment check is not available. Use `--json` for machine-readable output.
