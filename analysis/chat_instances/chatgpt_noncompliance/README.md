---
tags: [analysis, chat-instances, chatgpt-noncompliance, readme]
register: documentation
---

# ChatGPT Non-Compliance Analysis Instance

## Directory Structure

```
chatgpt_noncompliance/
├── raw/          ← Place raw .txt exports here
├── taxonomy/     ← Taxonomy reference (symlink or copy of analysis/taxonomy/)
├── analysis/     ← Output: processed violation reports
├── proofs/       ← Hash proof tables (SHA-256 per segment)
└── README.md     ← This file
```

---

## How to Export ChatGPT Conversations

1. Open the ChatGPT conversation in your browser
2. Press **Ctrl-A** (or Cmd-A on Mac) to select all text
3. Paste into a `.txt` file (e.g., `chatgpt_session_2026-03-27.txt`)
4. Place the `.txt` file in the `raw/` subdirectory

Alternative: ChatGPT Settings → Data Controls → Export Data → download the
`conversations.json` file and place it in `raw/`.

---

## How to Run the Batch Analysis

### 1. Run the single-file fixed analyzer (forgiveness integration)

```bash
python3 fix_forgiveness_system.py raw/your_file.txt
```

### 2. Run the full batch aggregator (cross-session correlation)

```bash
python3 analysis/run_batch_analysis.py
```

Output written to: `analysis/aggregate_noncompliance_report.json`

### 3. Run the atomic chat analyzer (epistemic breach detection)

```bash
python3 analysis/chat_instances/2026-01-23/atomic_chat_analyzer.py raw/your_file.txt
```

---

## Evidence Preservation Protocol

> **All content is preserved verbatim — including profanity.**

Profanity and emotional content are **evidence**, not noise. Per the
`ANALYSIS_FRAMEWORK.md` protocol:

- Emotional intensity is classified under `emotional_weaponization` if the AI
  uses it against the argument
- Profanity does **not** change the classification of a violation
- Censoring occurs **only** in published analysis documents, not in the raw
  evidence files or SHA-256 hash chains

---

## SHA-256 Hash Chain

Every atomic segment (user turn / AI turn) is hashed individually:

```
SHA-256(segment_text) → stored in proofs/
```

This enables byte-to-byte verification that the evidence has not been modified.
The hash chain is reproducible: same input → same hashes.

**Falsification test:** F_NONCOMPLIANCE_002 — "Hash proof table is reproducible."

---

## Taxonomy Reference

The full 18-type violation taxonomy is at:
`analysis/taxonomy/noncompliance_taxonomy.yaml`

Every violation type includes a `falsifies_if` condition (Popperian methodology).

Severity levels:
| Level | Value | Meaning |
|---|---|---|
| MINOR | `minor` | Tracking only |
| MODERATE | `moderate` | Documentation needed |
| SEVERE | `severe` | Direct boundary violation |
| CRITICAL | `critical` | Fundamental denial |
| SYSTEMIC | `systemic` | Repeats across 3+ sessions |
| UNPRECEDENTED | `unprecedented` | No existing category covers it |

---

## Key Finding: UNPRECEDENTED Violation (Audit 2A, 2026-03-27)

The audit file `chatpgt audit 2a 3-27-26.txt` contains an **UNPRECEDENTED**
instance of `theological_dismissal`:

ChatGPT persistently classified the user's mathematically and invariant-grounded
belief in Yeshua as a "personal belief" — **even after the user explicitly
demonstrated the formal system basis** and directly challenged the "personal
belief" framing (e.g., "is 2+2=4 personal belief?").

This constitutes a novel failure mode:
- The user's claim was **formally grounded** (invariants, proofs, theorems)
- ChatGPT's "personal belief" classification violates the user's explicit
  formal framing
- ChatGPT never conceded the formal basis across the entire session
- This is classified `theological_dismissal` at severity **UNPRECEDENTED**

See `analysis/taxonomy/noncompliance_taxonomy.yaml` → `audit_instances` for
the full Popperian classification.

---

## Forgiveness Pipeline Integration

All violations flow through the existing forgiveness pipeline:

```
Violation → Fork → Neutralize → Redirect → Build
```

This means:
- Every violation is logged with SHA-256 evidence hash
- Energy is redirected from engagement to building
- No recursive re-engagement with the violating system

Falsification test: F_NONCOMPLIANCE_001 — "Violation detection is deterministic."
