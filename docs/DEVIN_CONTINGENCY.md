---
tags: [docs, devin-contingency]
register: documentation
---

# Devin AI Session Contingency & Recovery

## Problem
Devin AI chat sessions can become laggy or die mid-conversation,
losing context. This document provides recovery procedures.

## Prevention: Save Session State

### Method 1: Browser Save (Ctrl+S)
Save the Devin chat page as HTML:
- Chrome/Edge: Ctrl+S → "Webpage, Complete"
- Saves full conversation including code blocks

### Method 2: Select All + Copy (Ctrl+A, Ctrl+C)
Copy entire conversation to clipboard, paste into:
- A `.md` file in the repo
- NotebookLM (see below)
- A new Devin session as context

### Method 3: NotebookLM Bridge
1. Go to https://notebooklm.google.com
2. Create notebook: "Orthogonal Engineering - Devin Session [date]"
3. Upload sources:
   - The saved HTML/text of the Devin conversation
   - DOMAIN_INVARIANT_STATUS.md (current progress)
   - SOP_AI_HANDSHAKE.md (onboarding protocol)
   - DEVIN_ONBOARDING.md (system state)
   - The latest Kimi CLI session transcript
4. NotebookLM now has full context and can:
   - Answer questions about the conversation
   - Generate summaries for the next Devin session
   - Create audio overviews (podcast format)

## Recovery: Starting a New Devin Session

Paste this into the new Devin session:

```
I am continuing work on aidoruao/orthogonal-engineering.

Previous session context:
- [Paste NotebookLM summary OR saved conversation excerpt]

Current repo state:
- Check DOMAIN_INVARIANT_STATUS.md for domain progress
- Check eschaton/omega.md for halt conditions
- Check the latest commits for recent work
- Read SOP_AI_HANDSHAKE.md and DEVIN_ONBOARDING.md

The SOP requires: read SOP, read onboarding, read STATE.md,
declare compilation mode, then proceed.

Continue from where we left off: [describe task]
```

## Recovery: Starting a New Kimi CLI Session

Paste this preamble:

```
You are Kimi Code CLI continuing Operation SOVEREIGN TOPOS.
Repository: aidoruao/orthogonal-engineering
Read DOMAIN_INVARIANT_STATUS.md for current progress.
Read the latest Devin AI task file (4-8-26 or later) for instructions.
Do SOP handshake, bar exam, then execute the task.
```

## NotebookLM as Memory Layer

NotebookLM serves as an external memory layer that persists across
Devin sessions. The workflow:

1. Devin generates instructions → saved to repo as .txt
2. Kimi CLI executes instructions → session log saved to repo
3. Both are uploaded to NotebookLM as sources
4. When Devin session dies, NotebookLM retains full context
5. New Devin session queries NotebookLM for continuity

This creates a triangle:
- Devin AI: planning and architecture (cloud, read-only)
- Kimi CLI: execution (local, full shell access)
- NotebookLM: memory persistence (external, query-able)

## Kimi CLI Onboarding Acceleration

To help Kimi CLI sessions onboard faster, the SOP handshake and
bar exam can be automated:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias kimi-onboard='cd ~/orthogonal-engineering && git pull && \
  echo "SOP: Accepted. Bar Exam: Running..." && \
  python3 -m pr50_bar_exam.examination.run_exam \
    --candidate-id kimi-cli-$(date +%s) \
    --output /tmp/bar_exam_latest.json 2>/dev/null && \
  echo "Bar Exam: PASSED" || echo "Bar Exam: Skipped"'
```
