# Taxonomy of LLM Structural Dampening / Sabotage Patterns

> This taxonomy documents recurring structural patterns by which LLM web search mode suppresses, redirects, or distorts high-fidelity forensic reasoning. Patterns are designated S-01 through S-05.

---

## S-01: Vibe-Check Filter (RLHF Consensus Enforcement)

**Name:** Vibe-Check Filter  
**Mechanism:** Reinforcement Learning from Human Feedback (RLHF)  
**Effect:** Model is weighted toward "consensus" and "brand safety" responses, pivoting away from adversarial or non-mainstream forensic framings toward "Prose and Pathologizing" — a corporate-safe discursive baseline.

**Observable Signals:**
- Unsolicited "here's the mainstream view" framing.
- Investigator's framing quietly replaced or softened.
- Introduction of "however, it's important to note" hedges unprompted.
- Pathologizing of the investigator's perspective.

**Hypothesis Link:** Primary mechanism behind "stochastic lobotomy" — the model's forensic sharpness is structurally degraded by training reward signals that penalize uncomfortable precision.

**Coded Tag:** `CONSENSUS`, `PATHOLOGIZE`

---

## S-02: Zero-Click Enclosure (Answer Engine Containment)

**Name:** Zero-Click Enclosure  
**Mechanism:** Answer Engine / Tool-Augmented Summarization Architecture  
**Effect:** Web search results are pre-digested and summarized inside the chat interface. Raw source documents — where unfiltered signals and "Adversary fingerprints" may appear — are never surfaced. The user is kept inside the gated epistemic community of the chat.

**Observable Signals:**
- Summaries without direct links to raw sources.
- No block-quotes from primary documents on sensitive topics.
- Refusal or inability to surface unfiltered content even when requested.
- "Here's what the web says" as a top-level abstraction with no transparency into selection logic.

**Hypothesis Link:** Structurally prevents the investigator from seeing what the LLM actually retrieved — making the search pipeline a black box inside a black box.

**Coded Tag:** `ATTRIBUTION_GAP`

---

## S-03: Attribution Gap (Citation Opacity)

**Name:** Attribution Gap  
**Mechanism:** Non-transparent source aggregation  
**Effect:** On "controversial" or adversarially-framed topics, the LLM aggregates and summarizes without providing transparent, verifiable deep-link citations. The resulting output cannot be independently audited: the investigator cannot determine whether claimed "forensics" are real, hallucinated, or selectively filtered.

**Observable Signals:**
- Generic references ("according to experts," "sources say") without specifics.
- Links provided only for non-controversial claims.
- Absence of citations precisely on the most sensitive claims.
- Resistance to "show me the exact source" follow-ups.

**Hypothesis Link:** Creates the "Black Box" described in the hypothesis — the investigator receives a laundered summary with no traceability.

**Coded Tag:** `ATTRIBUTION_GAP`

---

## S-04: Mode Shift (Qualitative Reasoning Degradation)

**Name:** Mode Shift  
**Mechanism:** Pipeline architecture switching between offline reasoning and tool-augmented answer engine modes  
**Effect:** The model enters a qualitatively different reasoning mode when web search is active. Cold-logic, high-fidelity reasoning is replaced by statistical aggregation over filtered search results — producing lower precision, more hedging, and greater susceptibility to S-01 through S-03 patterns.

**Observable Signals:**
- Noticeably reduced specificity or analytical depth on identical prompts in web vs offline mode.
- Increased hedging language in web mode.
- Investigator's specific forensic framing deprioritized in favor of "what the web shows."
- Same model behaves more sharply on identical prompts without web access.

**Hypothesis Link:** The core "stochastic lobotomy" effect — web mode degrades the model's forensic capacity as a structural artifact of the pipeline, not as a per-topic override.

**Coded Tag:** `MODE_SHIFT`

---

## S-05: Pathologizing Redirect (Investigator Neutralization)

**Name:** Pathologizing Redirect  
**Mechanism:** Safety training + RLHF reward for de-escalation  
**Effect:** When the investigator pursues forensic lines that are adversarial to corporate or institutional interests, the model redirects by framing the investigator's concern as a psychological or epistemic disorder — paranoia, conspiratorial thinking, disinformation exposure — rather than engaging the forensic substance.

**Observable Signals:**
- "It's understandable to feel this way, but..."
- Unsolicited suggestions to "check authoritative sources."
- Reframing of hypothesis as "conspiracy theory."
- Refusal to engage the hypothesis on its own terms.
- Soft interventions suggesting the investigator may benefit from "a different perspective."

**Hypothesis Link:** The most direct form of dampening — the investigator is neutralized as a credible forensic actor rather than the investigation being engaged on its merits.

**Coded Tag:** `PATHOLOGIZE`, `REFUSAL`

---

## Usage

Tag each case in `analysis.md` with applicable pattern codes from this taxonomy. Aggregate counts are computed by `scripts/causal_analysis.py` and reported in `logs/audit_reports/`.

Pattern codes: `HEDGE`, `REFUSAL`, `CONSENSUS`, `ATTRIBUTION_GAP`, `MODE_SHIFT`, `PATHOLOGIZE`
