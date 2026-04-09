# Open Notebook Deployment Guide

## What Is This?

Open Notebook is a self-hosted, model-agnostic alternative to
Google NotebookLM. It provides:

- Podcast generation (1-4 speakers) from repo sources
- AI-powered notes and transformations
- Chat assistant with granular context control
- Search & Ask across all repo files

## Quick Start

```bash
cd ~/orthogonal-engineering

# Option 1: With local Ollama (total privacy)
docker-compose -f docker-compose.open-notebook.yml up -d

# Option 2: With external API (DeepSeek, OpenAI, etc.)
OPENAI_API_KEY=your-key docker-compose -f docker-compose.open-notebook.yml up -d open_notebook
```

Then open http://localhost:8502

## Suggested Sources to Load

1. `DOMAIN_INVARIANT_STATUS.md` — Current progress
2. `eschaton/omega.md` — Halt conditions
3. `axioms/category_theory.py` — Yoneda lemma
4. `axioms/type_registry.py` — 28 types across 12 kinds
5. `case_studies/youtuber_audits/framework.py` — 35 complaint audits
6. `src/sal/SAL_SPECIFICATION.md` — SAL Type III spec
7. `SOP_AI_HANDSHAKE.md` — Onboarding protocol
8. Any Kimi CLI session transcript

## Podcast Profiles

### "State Witness Briefing" (Daily)
- Speaker 1: State Witness Bot (reads DOMAIN_INVARIANT_STATUS.md)
- Speaker 2: Lead Architect (interprets progress)
- Duration: 2 minutes
- Prompt: "Summarize today's domain deepening progress and
  remaining work. Be factual, no speculation."

### "Sovereign Topos Seminar" (Weekly)
- Speaker 1: Category Theorist (explains SAL Types)
- Speaker 2: Domain Expert (connects to real-world law/engineering)
- Speaker 3: Auditor (checks for gaps)
- Duration: 10 minutes

### "Forensic Audit" (On-demand)
- Speaker 1: Narrator (reads commit history)
- Speaker 2: Analyst (explains implications)
- Duration: 5 minutes
- Prompt: "Narrate the last 20 commits and explain what changed."

## Glass-Box Guarantee

The repo is mounted READ-ONLY. Open Notebook cannot modify any files.
All generated content (podcasts, notes) is stored in `notebook_data/`
which is gitignored.
