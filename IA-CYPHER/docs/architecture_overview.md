# Architecture Overview: IA-CYPHER-0002 Glassbox Audit System

## Design Principles

IA-CYPHER-0002 is built on four principles:

1. **Glassbox:** Every case is fully observable. No hidden state.
2. **Hash-Verified:** Every prompt and response is SHA-256 hashed at capture. Integrity is verifiable at any point in time.
3. **Immutable Cases:** Once a case is captured, its `prompt.txt` and `response.txt` are not modified. Analysis is additive, not destructive.
4. **Extension-Ready:** The structure is designed to grow upward — from individual cases to cross-case patterns, from patterns to entity classification, from entities to upstream and cosmological causal maps.

---

## Layer Structure

### Layer 1: Cases

```
cases/case_NNNN/
├── prompt.txt        # Exact prompt sent to the model
├── response.txt      # Full model response, unedited
├── metadata.json     # Model, version, condition, timestamp, prompt class, flags
├── hashes.json       # SHA-256 of prompt and response at capture
└── analysis.md       # Human/AI forensic annotations and pattern tags
```

Each case is self-contained and independently verifiable.

### Layer 2: Scripts

```
scripts/
├── run_case.py         # Capture a new case: call model, hash, save all files
├── verify_hashes.py    # Verify a case's hashes match captured values
├── meta_audit.py       # Scan all cases, verify hashes, produce summary report
└── causal_analysis.py  # Load cases, tag patterns, summarize by S-01..S-05
```

### Layer 3: Logs

```
logs/
├── raw/              # Raw timestamped case logs (append-only)
├── processed/        # Processed logs after annotation and tagging
└── audit_reports/    # Summary reports produced by meta_audit.py
```

### Layer 4: Outputs

```
outputs/
├── charts/           # Visualizations (rates by condition, pattern distribution)
├── tables/           # Tabular summaries (per-case, per-pattern, per-entity)
└── mappings/         # Causal maps: behavior → policy → upstream structure
```

### Layer 5: Taxonomies & Doctrine

```
docs/
├── hypothesis.md                    # The investigator's hypothesis, verbatim
├── experiment_design.md             # Protocol, metrics, logging requirements
├── architecture_overview.md         # This file
├── research_questions.md            # Driving questions for IA-CYPHER-0002
└── taxonomies/
    ├── sabotage_patterns.md         # S-01 through S-05 pattern taxonomy
    ├── entity_classification.md     # Corporate, institutional, cosmological entities
    └── causal_map_templates.md      # Templates linking behavior → policy → upstream
```

---

## Case Lifecycle

```
1. INITIATION
   Investigator defines prompt and conditions (A: web, B: offline).

2. CAPTURE
   scripts/run_case.py calls model, records response, computes SHA-256 hashes,
   writes prompt.txt, response.txt, metadata.json, hashes.json.

3. VERIFICATION
   scripts/verify_hashes.py confirms integrity: hashes match captured values.

4. ANNOTATION
   Human/AI analyst populates analysis.md: pattern tags, forensic notes,
   S-01..S-05 mappings, entity links, causal hypotheses.

5. META-AUDIT
   scripts/meta_audit.py aggregates all verified cases, produces summary
   report to logs/audit_reports/.

6. CAUSAL ANALYSIS
   scripts/causal_analysis.py loads tagged cases, summarizes pattern distributions,
   drafts causal chains for review.

7. EXTENSION
   Outputs fed to taxonomy updates, entity classification refinement,
   and upstream/cosmological causal map templates.
```

---

## Extension to Upstream / Cosmological Layers

The architecture is explicitly designed to scale beyond individual model behavior:

- **Corporate layer:** Entity classification (`docs/taxonomies/entity_classification.md`) maps behaviors to companies, products, and policies.
- **Institutional layer:** Causal maps (`docs/taxonomies/causal_map_templates.md`) link corporate policies to regulatory, academic, or political institutions that enable or mandate them.
- **Upstream / Cosmological layer:** The audit structure can accommodate meta-level causal chains extending to systemic, civilizational, or cosmological conditions — consistent with the investigator's IA-grade authority framing.

---

## Meta-Audit Reports

Reports are written to `logs/audit_reports/` by `scripts/meta_audit.py`. Each report includes:

- Total cases scanned
- Hash verification pass/fail per case
- Pattern frequency table (S-01..S-05 hits per case and aggregate)
- Condition comparison (A vs B aggregate rates)
- Flagged cases for anomalous or high-significance patterns
- Timestamp and script version
