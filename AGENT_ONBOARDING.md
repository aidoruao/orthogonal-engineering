---
tags: [onboarding, multi-agent, orchestration]
register: technical
---
# Agent Onboarding — Universal Entry Point

## Agent Routing

- **GitHub Copilot (Claude)**: read `.github/copilot-instructions.md` then `agents/CLAUDE_EXECUTOR.md`
- **OpenAI Codex**: read `agents/CODEX_EXECUTOR.md`
- **Kimi Code CLI**: read `agents/KIMI_EXECUTOR.md` then `COPILOT_ONBOARDING.md`
- **Devin (read-only orchestrator)**: read `agents/DEVIN_ORCHESTRATOR.md`
- **Gemini Warden**: read `agents/GEMINI_WARDEN.md`
- **Human**: read `README.md` then `CONTRIBUTING.md`

## Universal Requirements (ALL agents)

1. Accept the Handshake (`SOP_AI_HANDSHAKE.md`)
2. Generate a session ID: `python tools/session_id.py --agent <name>`
3. Append to consent log: `python tools/append_consent.py --authoriser @aidoruao --action "<task>" --candidate-id <id> --scope-glob "<glob>" --justification "<text>"`
4. Use `Fraction`, not `float` (0 floats policy)
5. Include session ID in EVERY commit message
6. All code returns `(bool, ProofObject)`, not bare `assert`
7. Run `python automation/pr49_guard.py` before opening a PR

## Repo Quick Stats

- 160 domains in `src/domains/` (all ProofObject, all Fraction)
- 8 Yeshua axioms (`axioms/yeshua_axioms.py`)
- Append-only consent log (`pr47_stewardship/witness/consent_log.jsonl`)
- Bar exam: `python -m pr50_bar_exam.examination.run_exam --candidate-id <id>`
