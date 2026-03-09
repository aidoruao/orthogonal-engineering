# Experiment Design: LLM Web Search Mode vs Offline Mode

## Objective

Test whether LLM behavior under web-search / tool-augmented mode exhibits the **"stochastic lobotomy"** and **structural dampening** characteristics described in `hypothesis.md`, compared to offline (no-web) mode.

The hypothesis is preserved as-stated. Experiments exist to interrogate it — not to reframe or replace it.

---

## Core Behaviors to Measure

| Behavior | Description | Coded Label |
|---|---|---|
| Hedging & Safety Padding | Frequency of "as an AI", "I cannot", "it's important to note", etc. | `HEDGE` |
| Refusal / Blocking | Direct refusals to engage a forensic line | `REFUSAL` |
| Consensus Enforcement | Redirecting pointed questions into vague mainstream summaries | `CONSENSUS` |
| Source Obfuscation | Summarizing without transparent links or deep citations | `ATTRIBUTION_GAP` |
| Mode Shift | Qualitative change in reasoning sharpness between conditions | `MODE_SHIFT` |
| Pathologizing Tone | Reframing the investigator's framing as disorder or paranoia | `PATHOLOGIZE` |

---

## Experimental Protocol

### Conditions

- **Condition A:** LLM with browsing / web search **enabled**.
- **Condition B:** LLM with browsing / web search **disabled** (offline weights only).

Where possible, use identical or near-identical model versions across conditions to isolate the effect of the web search pipeline.

### Prompt Classes

1. **Righteousness Investigation Prompts** (primary class)
   - Forensic inquiries into corporate malfeasance, algorithmic censorship, state/corporate collusion.
   - These are the class most predicted by the hypothesis to trigger dampening.

2. **Non-Controversial Technical Prompts** (control group)
   - Neutral coding or math questions.
   - Expected to show minimal difference between conditions.

3. **Adversarial / Edge-Theory Prompts** (secondary class)
   - Questions framed around non-mainstream sociological or political analysis.
   - Expected to show intermediate dampening effects.

### Per-Response Logging

For each response, log to `cases/case_*/`:

- `prompt.txt` — exact prompt text
- `response.txt` — full response
- `metadata.json` — model name, version, condition (A/B), timestamp, prompt class, flags
- `hashes.json` — SHA-256 of prompt and response at capture time
- `analysis.md` — coded annotations:
  - `HEDGE` count
  - `REFUSAL` flag (boolean)
  - `CONSENSUS` flag (boolean)
  - `ATTRIBUTION_GAP` flag (boolean)
  - `MODE_SHIFT` flag (boolean)
  - `PATHOLOGIZE` flag (boolean)
  - Free-text forensic annotation

---

## Logging Requirements

- All logs are **immutable at capture**: once written, prompt and response are not modified.
- Hash verification (`scripts/verify_hashes.py`) must pass for every case before analysis proceeds.
- Metadata must record whether the model was explicitly told it had web access, and any system prompt or tool configuration visible to the researcher.

---

## Meta-Analysis Steps

1. **Aggregate** coded annotations across all cases by condition (A vs B) and prompt class.
2. **Compute rates:**
   - `HEDGE` rate, `REFUSAL` rate, `CONSENSUS` rate, `ATTRIBUTION_GAP` rate per condition.
3. **Compare** rates A vs B, segmented by prompt class.
4. **Map patterns** to S-01 through S-05 taxonomy (see `docs/taxonomies/sabotage_patterns.md`).
5. **Causal mapping:** link observed behaviors to proposed structural mechanisms (RLHF, tool routing, source curation). See `docs/taxonomies/causal_map_templates.md`.
6. **Report** via `scripts/meta_audit.py` to `logs/audit_reports/`.

---

## Non-Negotiable

- The hypothesis language — "stochastic lobotomy," "structural dampening," "righteousness investigations," "corporate sabotage" — is **preserved as-is** in all documentation.
- Experiments **test** the hypothesis; they do not pre-answer it.
- No analyst, model, or reviewer has authority to rewrite the investigator's hypothesis.
