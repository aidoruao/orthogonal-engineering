# NotebookLM Integration Guide

## Purpose

Google NotebookLM serves as an external memory layer that persists
across AI sessions (Devin, Kimi CLI, Copilot). It provides:

- Conversation continuity when sessions die
- Audio overviews (podcast format) of repo state
- Cross-session question answering
- Onboarding acceleration for new AI instances

## Setup

1. Go to https://notebooklm.google.com
2. Create notebook: "Orthogonal Engineering Master"
3. Upload these sources (max 50):

### Priority 1 (Always upload)
- `DOMAIN_INVARIANT_STATUS.md`
- `SOP_AI_HANDSHAKE.md`
- `DEVIN_ONBOARDING.md`
- `eschaton/omega.md`
- `src/sal/SAL_SPECIFICATION.md`

### Priority 2 (Upload latest)
- Latest Devin AI task file (e.g., `4-8-26 3a...`)
- Latest Kimi CLI session transcript
- `case_studies/youtuber_audits/framework.py`
- `axioms/type_registry.py`

### Priority 3 (Upload as needed)
- Any specific axiom module being discussed
- Any specific domain implementation
- Saved Devin chat HTML files

## Workflow: Devin Dies Mid-Session

1. Save Devin chat: Ctrl+A → Ctrl+C → paste into `devin_session_[date].md`
2. Upload to NotebookLM
3. Ask NotebookLM: "Summarize the last task Devin was working on
   and what remains to be done"
4. Start new Devin session with NotebookLM's summary as context

## Workflow: Kimi CLI Onboarding

1. Ask NotebookLM: "Generate a 500-word briefing for a new Kimi CLI
   session that needs to continue domain deepening"
2. Paste the briefing into Kimi CLI as the opening prompt
3. Kimi CLI now has full context without reading 50 files

## Workflow: Audio Overview

1. Click "Generate Audio Overview" in NotebookLM
2. Select sources: DOMAIN_INVARIANT_STATUS.md + omega.md
3. NotebookLM generates a ~10 minute podcast summarizing progress
4. Listen while doing other work — passive consumption of repo state

## Reproducibility for Others

Anyone can replicate this setup:
1. Clone the repo
2. Upload the Priority 1 files to their own NotebookLM
3. They now have a queryable, audio-capable interface to the repo

No API keys required. No self-hosting required. Free tier sufficient.
