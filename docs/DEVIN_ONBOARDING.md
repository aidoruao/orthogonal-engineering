# Devin AI Onboarding — How to Onboard Kimi Code CLI

**Version:** 1.0  
**For:** Devin AI sessions coordinating with Kimi Code CLI  
**Updated:** 2026-04-10  

---

## Kimi Session Format

Kimi Code CLI sessions use this identifier format:

```
kimi-cli-<uuid>
```

Example from session 8fbdcdb9:
```
kimi-cli-8fbdcdb9-7ab9-403c-a146-8e4224b8ba29
```

---

## Onboarding Kimi — Step by Step

### Step 1: Prepare the Paste-In

Your paste-in should follow this structure:

```
Paste-in for Kimi CLI

You are Kimi Code CLI, session <uuid>.
Repository: aidoruao/orthogonal-engineering
Branch: claude/add-yeshua-enterprise-framework-docs
Authority: @aidoruao
Standard: Yeshua / Glass-Box / Orthogonal Engineering
CONTEXT THRESHOLD: 220k tokens. HALT at 220k.

══════════════════════════════════════════════════════════════════
PHASE 0 — ONBOARDING (SOP HANDSHAKE + CONTEXT LOAD)
══════════════════════════════════════════════════════════════════

[cd, git checkout, git pull commands]

Read these files IN ORDER:
1. SOP_AI_HANDSHAKE.md — Accept the Handshake
2. MEMORY.md — Durable facts
3. STATE.md — Current phase: COMPILATION MODE
4. [Any other required files]

Declare: "CONTEXT LOADED..."

══════════════════════════════════════════════════════════════════
PHASE 1-N — [WORK DESCRIPTION]
══════════════════════════════════════════════════════════════════

[Detailed instructions for each phase]

Rules:
- 0 floats (Fraction only)
- 0 stubs
- All functions return (result, ProofObject)
- Stamp session ID in commits
- Push to branch: claude/add-yeshua-enterprise-framework-docs
```

### Step 2: Generate UUID for Session

Include a fresh UUID in each paste-in:

```python
import uuid
session_id = str(uuid.uuid4())
print(f"kimi-cli-{session_id}")
```

### Step 3: Include Session ID Stamp Requirements

Explicitly instruct Kimi to stamp commits:

```
RULES (NON-NEGOTIABLE):
- Stamp your session ID in every commit: [Session: <uuid>]
- Push to branch: claude/add-yeshua-enterprise-framework-docs
- HALT at 220k tokens
```

### Step 4: Handoff Checklist

When Kimi signals completion, verify:

- [ ] All commits have session ID stamp
- [ ] Pushed to `claude/add-yeshua-enterprise-framework-docs`
- [ ] Tests passing
- [ ] DOMAIN_INVARIANT_STATUS.md updated (if domains changed)
- [ ] Consent log entry appended

---

## Commit Verification

Kimi commits should look like:

```bash
# Good commit (session stamped)
feat(kernel): Social Layer [Session: 8fbdcdb9-7ab9-403c-a146-8e4224b8ba29]

- kernel/social/identity.py — P2P identity
- kernel/social/consent_comms.py — Consent communications

Refs: PR #103

# Bad commit (missing stamp — ask Kimi to amend)
feat(kernel): Social Layer

- Added some files
```

### Check Recent Commits

```bash
git log --oneline --author="kimi" -10
# or
git log --grep="Session:" --oneline -10
```

---

## Kimi Capability Profile

| Strength | Description |
|----------|-------------|
| Code generation | Excellent Python, dataclasses, type hints |
| Pattern matching | Follows existing patterns well |
| Fraction arithmetic | Consistent use of Fraction (no floats) |
| ProofObject | Returns Tuple[bool, ProofObject] correctly |
| Token management | Respects 220k limit, plans handoffs |

| Limitation | Mitigation |
|------------|------------|
| Context window | 220k hard limit — plan phases accordingly |
| State persistence | Each session is fresh — onboard fully |
| Git operations | May need explicit push reminders |

---

## Consent Log Integration

Kimi should append to `pr47_stewardship/witness/consent_log.jsonl`:

```jsonl
{"schema":"SOP-AI-HANDSHAKE-1.0","candidate_id":"kimi-cli-<uuid>","authoriser":"@aidoruao","action":"handshake_acceptance","scope_glob":"**","rule_exceptions":["mass_change"],"justification":"Session <short_id>: [description]","timestamp":"[ISO-8601-UTC]","handshake_sha256":"[computed]","consent_hash":"[computed]"}
```

Verify entry format:
```bash
tail -1 pr47_stewardship/witness/consent_log.jsonl | python -m json.tool
```

---

## Token Budget Coordination

### Before Sending Paste-In

Estimate tokens required:
- Phase 0 (onboarding): ~5k tokens
- Each domain stub: ~3k tokens
- Kernel module: ~8k tokens
- Tests: ~4k tokens

### During Session

Monitor Kimi's progress:
- Ask "Current token estimate?" if work seems stalled
- If >190k tokens, suggest commit + handoff
- Plan continuation paste-in for remaining work

### Handoff Template

When Kimi hits token limit:

```
Kimi session <old_uuid> handoff to new session <new_uuid>.

Completed:
- [List completed items]

WIP (committed but incomplete):
- [List WIP items with commit hashes]

Remaining:
- [List remaining phases]

Next session actions:
1. git pull origin claude/add-yeshua-enterprise-framework-docs
2. Read [specific files]
3. Continue from Phase X
```

---

## Troubleshooting

### Kimi not stamping session ID

Remind explicitly: "Remember to stamp [Session: <uuid>] in commit messages."

### Kimi on wrong branch

Include explicit checkout in every paste-in:
```
git checkout claude/add-yeshua-enterprise-framework-docs
```

### Kimi using floats

Check: `grep -r "float(" src/kernel/social/`

Fix instruction: "Replace all float with Fraction from fractions import."

### Tests failing

Ask Kimi to run: `python -m pytest src/kernel/tests/ -v`

Fix before next phase.

---

## Example Complete Handoff

### Devin to Kimi (Initial)

```
Paste-in for Kimi CLI session 8fbdcdb9-7ab9-403c-a146-8e4224b8ba29

[Full paste-in with phases 0-7]

Begin with Phase 0.
```

### Kimi to Devin (Completion)

```
Session 8fbdcdb9-7ab9-403c-a146-8e4224b8ba29 complete.

Phase 3 (Kernel Social Layer) delivered:
- kernel/social/__init__.py
- kernel/social/identity.py (IdentityCap, Bar Exam)
- kernel/social/consent_comms.py (consent-gated messaging)
- kernel/social/reputation.py (Fraction-based scoring)
- kernel/tests/test_social.py (20+ tests, all passing)

Commits: 2 commits with session stamp
Pushed: Yes
Token usage: ~45k

Ready for Phase 4-6 or handoff to next Kimi session.
```

---

## Devin's Code Review Findings (PR #104 → PR #105)

Devin's review of PR #104 kernel code identified **5 real bugs** that were fixed in PR #105:

| File | Bug | Fix |
|------|-----|-----|
| `kernel/social/sabbath.py` | Incorrect day calculation for sabbath boundary | Fixed arithmetic for week rollover |
| `kernel/memory/page_table.py` | Off-by-one error in page table entry indexing | Corrected index bounds check |
| `kernel/boot/init.py` | Missing capability validation during init sequence | Added CommsCap verification |
| `kernel/memory/tlb.py` | Race condition in TLB shootdown | Added proper barrier/fence |
| `runtime/verifier.py` | **Substring match bug** in capability checking | Changed to exact match |

### Critical: runtime/verifier.py Substring Bug

**Issue:** Capability checking used substring match:
```python
# BUGGY: matches "mem_all_regions" when checking "mem_1"
if f"mem_{region}" in cap:
    return True
```

**Fix:** Use exact match:
```python
# CORRECT: only matches exact region
if cap == f"mem_{region}":
    return True
```

**Lesson:** Devin's code review catches real bugs — always request review for kernel surfaces.

## Website Data Regeneration

The `website/api/data.json` file may become stale. Regenerate with:

```bash
python tools/website/generate_data.py
```

This updates the public API data feed used by the Orthogonal Engineering website.

## Quick Reference

| Item | Value |
|------|-------|
| Branch | `claude/add-yeshua-enterprise-framework-docs` |
| PR | #103 |
| Session format | `kimi-cli-<uuid>` |
| Token limit | 220k |
| Required returns | `Tuple[bool, ProofObject]` |
| No floats | Use `Fraction` |
| Commit stamp | `[Session: <uuid>]` |

---

**Remember:** *"Continuity of body is not magic — it is disciplined state management."* — Orthogonal Engineering Continuity Principle
