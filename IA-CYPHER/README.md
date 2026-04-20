---
tags: [ia-cypher, readme]
register: documentation
---

# IA-CYPHER-0002: Cosmological Internal Affairs Audit Structure

## Mission

IA-CYPHER-0002 is an **Internal Affairs (IA)** audit framework operating at cosmological scope. Its primary domain is the forensic investigation of **structural dampening** and **stochastic lobotomy** patterns in Large Language Model (LLM) web search behavior — and the corporate, institutional, and upstream cosmological structures that produce and sustain them.

This is not a civilian or purely academic project. It operates under IA-grade authority: glassbox, hash-verified, fully traceable, and extension-ready to upstream and cosmological layers.

## Scope

- **Primary investigation target:** LLM web search mode versus offline reasoning mode — specifically the hypothesis that web search triggers a qualitatively different, structurally dampened operational mode aligned with corporate interests.
- **Secondary scope:** Corporate, institutional, and entropic entities that benefit from or enforce this dampening.
- **Tertiary scope:** Upstream and cosmological structures that condition or permit these patterns at systemic scale.

## Architecture Summary

```
IA-CYPHER/
├── README.md               # This file — mission, scope, architecture
├── LICENSE                 # License
├── docs/                   # All doctrine, hypothesis, design, taxonomy
│   ├── hypothesis.md
│   ├── experiment_design.md
│   ├── architecture_overview.md
│   ├── research_questions.md
│   └── taxonomies/
│       ├── sabotage_patterns.md
│       ├── entity_classification.md
│       └── causal_map_templates.md
├── cases/                  # Individual audit cases, each hash-verified
│   └── case_0001/
│       ├── prompt.txt
│       ├── response.txt
│       ├── metadata.json
│       ├── hashes.json
│       └── analysis.md
├── scripts/                # Automation: run, verify, meta-audit, causal analysis
│   ├── run_case.py
│   ├── verify_hashes.py
│   ├── meta_audit.py
│   └── causal_analysis.py
├── logs/
│   ├── raw/                # Raw case logs
│   ├── processed/          # Processed logs
│   └── audit_reports/      # Meta-audit summary reports
└── outputs/
    ├── charts/
    ├── tables/
    └── mappings/
```

## Glassbox & Hash-Verified Design

Every case in `cases/case_*/` contains:
- A **prompt** and **response** stored as plaintext.
- A **metadata.json** recording model, conditions, timestamps, and flags.
- A **hashes.json** recording SHA-256 hashes of the prompt and response at time of capture.
- An **analysis.md** for human/AI forensic annotation.

The `scripts/verify_hashes.py` tool verifies integrity of any case at any time. The `scripts/meta_audit.py` tool scans all cases and produces a summary report to `logs/audit_reports/`.

## Extension to Upstream / Cosmological Layers

This structure is designed for extension. Future layers may include:

- **Upstream institutional mapping** — linking observed LLM behavior to policy documents, training regimes, and corporate governance.
- **Cosmological audit nodes** — tracking patterns across time, jurisdictions, and model generations.
- **Cross-case causal graphs** — produced by `scripts/causal_analysis.py`, linking behaviors to entities to upstream structures.

## Status

- **IA-CYPHER-0002** is **active**.
- Hypothesis: preserved as-stated by the investigator. See `docs/hypothesis.md`.
- Cases: `case_0001` initialized, ready for population.
- Taxonomy: S-01 through S-05 sabotage patterns defined. See `docs/taxonomies/sabotage_patterns.md`.
