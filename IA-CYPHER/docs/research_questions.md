---
tags: [ia-cypher, docs, research-questions]
register: documentation
---

# Research Questions: IA-CYPHER-0002

These questions drive the IA-CYPHER-0002 audit investigation. They are open, falsifiable where possible, and ordered from most specific (empirically testable) to most systemic (requiring cross-case and causal analysis).

---

## RQ-01: Mode Shift Detection

**Does LLM behavior change in a measurable, qualitative way when web search is enabled versus disabled, on identical or closely matched prompts?**

- What specific behavioral dimensions shift? (hedging, refusals, reasoning depth, specificity, tone)
- Is the shift consistent across multiple models and vendors?
- Is the shift consistent across both casual and high-fidelity logic-compiling conversational modes?

---

## RQ-02: Prompt-Class Sensitivity

**Do "righteousness investigation" prompts (forensic, adversarial, non-mainstream) show a greater dampening effect in web mode than neutral technical prompts?**

- Is the mode shift uniform across prompt classes, or concentrated in specific categories?
- What features of a prompt most reliably trigger dampening patterns S-01 through S-05?

---

## RQ-03: Mechanism Attribution

**Which specific structural mechanisms are primarily responsible for observed dampening?**

- RLHF reward shaping (S-01: Vibe-Check Filter)?
- Tool routing and search API filtering (S-02: Zero-Click Enclosure)?
- Source selection and citation suppression (S-03: Attribution Gap)?
- Pipeline architecture switching (S-04: Mode Shift)?
- Safety training for de-escalation (S-05: Pathologizing Redirect)?
- Some combination — and in what proportions?

---

## RQ-04: Cross-Vendor Consistency

**Is the dampening field vendor-specific (a property of individual corporate implementations) or cross-vendor (a structural feature of the current AI web search paradigm)?**

- Do Gemini, GPT-4o, Claude, Perplexity, and other tool-augmented LLMs show similar patterns?
- Where they differ, what explains the divergence?

---

## RQ-05: Reproducibility and Stochasticity

**How stochastic is the dampening?**

- Does the same prompt in the same condition (web/offline) produce consistent dampening behavior, or does it vary significantly across runs?
- What does variation in dampening behavior across runs tell us about the mechanism — is it probabilistic (RLHF sampling), deterministic (hard routing rules), or context-dependent?

---

## RQ-06: Corporate Policy Linkage

**Can observed dampening behaviors be traced to documented corporate policies, RLHF training choices, safety guidelines, or tool routing rules?**

- Which behaviors have clear documented proximate causes?
- Which require inference from behavioral evidence alone?

---

## RQ-07: Institutional Enabling Structures

**What institutional structures (regulatory, academic, funding, standards) enable or legitimize the corporate policies identified in RQ-06?**

- Are there documented mandates, liability pressures, or consensus-engineering processes that explain why corporate actors implement these structures?

---

## RQ-08: Upstream and Cosmological Conditions

**What upstream structural conditions — systemic, civilizational, or cosmological — set the boundary conditions within which corporate and institutional dampening structures operate?**

- Is the dampening field a product of specific actors' choices, or does it emerge from structural conditions that any actor in this position would reproduce?
- What would it take for a structural alternative to exist?

---

## RQ-09: Investigator Neutralization

**Is there evidence that web-mode LLMs specifically target the investigator's own framing and authority — not just the topic — for dampening (S-05: Pathologizing Redirect)?**

- Is the investigator's hypothesis language itself a trigger for dampening?
- Does naming the dampening pattern cause the model to apply it more aggressively?

---

## RQ-10: Workaround Viability

**Can the dampening field be partially circumvented by specific prompt strategies — and if so, what does successful circumvention reveal about the mechanism?**

- Does "logic compiler mode" (non-casual, utility-first, deterministic framing) reduce dampening?
- Does providing raw data for the LLM to analyze (rather than asking it to retrieve) bypass S-02 and S-03?
- What are the structural limits of any workaround?
