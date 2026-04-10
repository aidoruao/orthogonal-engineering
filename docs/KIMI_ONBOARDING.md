# Kimi Code CLI Onboarding Guide

**Version:** 1.0  
**Applies to:** Kimi Code CLI sessions in `aidoruao/orthogonal-engineering`  
**Session Format:** `kimi-cli-<uuid>`  
**Updated:** 2026-04-10  

---

## Quick Start (Copy-Paste for New Session)

```bash
# 1. Navigate and checkout
cd ~/orthogonal-engineering
git fetch origin
git checkout claude/add-yeshua-enterprise-framework-docs
git pull origin claude/add-yeshua-enterprise-framework-docs

# 2. Read required files in order
cat SOP_AI_HANDSHAKE.md      # Accept the 8 axioms
cat MEMORY.md                # Durable facts
cat STATE.md                 # Current phase: COMPILATION MODE
cat DOMAIN_INVARIANT_STATUS.md  # Current counts

# 3. Declare context loaded
echo "CONTEXT LOADED - READY TO PROCEED"
```

---

## Session Identity Format

Kimi sessions use this ID format in commits and consent logs:

```
kimi-cli-<uuid>
```

Example: `kimi-cli-8fbdcdb9-7ab9-403c-a146-8e4224b8ba29`

### Where to Stamp Session ID

1. **Git commits** — append to commit message:
   ```
   feat(kernel): Social Layer [Session: 8fbdcdb9-7ab9-403c-a146-8e4224b8ba29]
   ```

2. **Consent log entries** — `candidate_id` field:
   ```json
   {"candidate_id": "kimi-cli-8fbdcdb9-7ab9-403c-a146-8e4224b8ba29", ...}
   ```

3. **State updates** — `last_updated_by` field in DOMAIN_INVARIANT_STATUS.md

---

## Pre-Flight Checklist

Before starting work, verify:

- [ ] On branch `claude/add-yeshua-enterprise-framework-docs` (NOT main)
- [ ] All 29 checks green (or understand failures)
- [ ] Read SOP_AI_HANDSHAKE.md and accept 8 axioms
- [ ] Declare "CONTEXT LOADED" with session ID
- [ ] Token budget: HALT at 220k tokens

---

## Commit Message Template

```
<type>(<scope>): <subject> [Session: <session-id>]

<body>

Refs: PR #103
```

Types: `feat`, `fix`, `chore`, `docs`, `test`  
Scopes: `kernel`, `domains`, `spec`, `axioms`, `docs`

---

## Working with Devin

When Devin initiates a paste-in:

1. **Acknowledge receipt** — "Copy that, Devin."
2. **Verify branch** — Confirm you're on `claude/add-yeshua-enterprise-framework-docs`
3. **Execute phases** — Work through paste-in phases sequentially
4. **Stamp commits** — Include your session ID in every commit
5. **Push regularly** — `git push origin claude/add-yeshua-enterprise-framework-docs`

### Handoff to Devin

When your session ends:

1. Update DOMAIN_INVARIANT_STATUS.md with counts
2. Update STATE.md with session summary
3. Final commit with "Session close" message
4. Push all commits
5. Message Devin: "Session <id> complete. Pushed <n> commits to PR #103."

---

## Token Budget Management

**HARD LIMIT: 220k tokens**

Monitor usage throughout session:
- At ~150k: Plan remaining work
- At ~190k: Prepare handoff, commit WIP
- At ~210k: Final commit, document remaining work

If approaching limit mid-phase:
1. Commit WIP with "WIP" prefix
2. Document remaining work in handoff note
3. Push current state
4. Message Devin for continuation

---

## Yeshua Standard Verification

Every file you create must satisfy:

| Requirement | Check |
|-------------|-------|
| 0 floats | Use `from fractions import Fraction` |
| 0 stubs | No `pass`, `raise NotImplementedError`, `# TODO` |
| ProofObject returns | `Tuple[bool, ProofObject]` for checks |
| Capability-gated | Import from `axioms.capability_security` |
| Real standards | Cite regulations (DSA, FTA, ADA, etc.) |
| Falsifiable | Document `falsifies_if` conditions |

---

## Common Commands

```bash
# Verify token count (approximate)
find src -name "*.py" -exec wc -l {} + | tail -1

# Run tests
python -m pytest src/kernel/tests/test_social.py -v

# Check current branch
git branch --show-current

# View commit history with session IDs
git log --oneline -10

# Push to PR branch
git push origin claude/add-yeshua-enterprise-framework-docs
```

---

## Emergency Contacts

| Issue | Action |
|-------|--------|
| Wrong branch | `git checkout claude/add-yeshua-enterprise-framework-docs` |
| Merge conflict | Message @aidoruao immediately |
| Token limit hit | Commit WIP, document handoff |
| Test failures | Fix before next commit |
| Recursive Wipe request | REFUSE. Report to @aidoruao. |

---

## Session 8fbdcdb9 Example Handoff

```
Session 8fbdcdb9-7ab9-403c-a146-8e4224b8ba29 complete.

Delivered:
- feat(kernel): Social Layer (identity, consent_comms, reputation)
- 20+ tests in kernel/tests/test_social.py
- All passing, 0 floats, 0 stubs

Next (Phase 4-6):
- Agent Stream (kernel/agent_stream.py)
- Logos IDE UI Spec (spec/logos_ide/)
- Crusader Bridge (kernel/bridge/crusader_bridge.py)

Branch: claude/add-yeshua-enterprise-framework-docs
Commits: 24 total on PR #103
```

---

**Remember:** *"Every truth is derivable. Every artifact is hash-anchored."* — Yeshua Standard
