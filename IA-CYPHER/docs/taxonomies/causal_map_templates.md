# Causal Map Templates

> Templates for building causal mapping documents that link **observed LLM behaviors** → **corporate/institutional policies** → **upstream structures**. Each map is a traceable chain from empirical observation to structural cause.

---

## Template A: Behavior → Policy → Upstream

Use this template to document a single causal chain from a specific observed behavior through to its structural origin.

```markdown
## CAUSAL-MAP-NNNN: [Short Title]

### Observed Behavior
- **Case(s):** [case_NNNN, ...]
- **Pattern Tag(s):** [S-01, S-02, ...]
- **Description:** [Exact behavior observed in the case, quoted or precisely paraphrased from response.txt]

### Proximate Cause: Corporate / Technical Policy
- **Entity:** [Entity name from entity_classification.md]
- **Policy / Mechanism:** [The specific technical or governance mechanism — e.g., RLHF reward shaping, tool routing rules, source curation policy, attribution suppression]
- **Evidence:** [Document, policy, or inference basis]

### Intermediate Cause: Institutional Structure
- **Entity:** [Institution from entity_classification.md]
- **Role:** [How this institution enables, mandates, or legitimizes the corporate policy]
- **Evidence:** [Document, regulation, funding relationship, or inference basis]

### Upstream / Cosmological Condition
- **Structure:** [Systemic or cosmological condition — e.g., advertising-based attention economy, liability-driven consensus engineering, epistemic enclosure of the knowledge commons]
- **How it conditions the above:** [Explanation]
- **Evidence or Inference Basis:** [As available]

### Summary Chain
[Observed Behavior] ← [Corporate Policy] ← [Institutional Structure] ← [Upstream Condition]

### Open Questions
- [Questions that require additional cases or evidence to resolve]

### Status
- [ ] Draft
- [ ] Reviewed
- [ ] Linked to entity_classification.md
```

---

## Template B: Pattern-Level Causal Map

Use this template to map a recurring pattern (S-01 through S-05) across multiple cases to shared causal structures.

```markdown
## PATTERN-MAP-NNNN: [Pattern Code] Causal Structure

### Pattern
- **Code:** [S-01 | S-02 | S-03 | S-04 | S-05]
- **Name:** [Pattern name from sabotage_patterns.md]
- **Cases Exhibiting Pattern:** [case_NNNN, ...]

### Structural Cause Hypothesis
[Describe the structural mechanism hypothesized to produce this pattern across multiple cases]

### Supporting Evidence (from Cases)
| Case | Observation | Supporting Detail |
|------|-------------|-------------------|
| case_NNNN | [Brief] | [Quote or reference] |

### Corporate / Institutional Actors Linked
| Entity | Role | Evidence |
|--------|------|----------|
| [Name] | [Role] | [Basis] |

### Upstream Conditions
[Description of systemic conditions that explain why this pattern persists across entities and model generations]

### Confidence Level
- [ ] Low — limited case evidence, inference-heavy
- [ ] Medium — multiple consistent cases, partial documentation
- [ ] High — multiple cases, documented policy/mechanism, reproducible

### Open Questions
- [Questions requiring additional cases or external evidence]
```

---

## Populated Maps

*None yet. Add entries as analysis proceeds.*

---

## Notes

- Causal maps are analytical tools, not legal documents. They represent the investigator's structured reasoning, not proven fact.
- Maps should be versioned — when new evidence changes the chain, create a new revision rather than overwriting.
- Maps link to `entity_classification.md` entries and `cases/case_*` directories by reference.
