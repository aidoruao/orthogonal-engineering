# DeepSeek Methodology Guide

This document explains how to use the DeepSeek-style methodology schemas
integrated into the orthogonal-engineering monorepo, and how this connects to
the UVM/axiomatic/Peano/witness architecture.

---

## Overview

The methodology acts as an **immune system** for the repository: it makes
architectural assumptions explicit, links them to real-world failure cases, and
enforces them via machine-readable falsification tests.

### Schema files (under `ontology/`)

| File | Purpose |
|---|---|
| `search_lens.json` | Domains, artifact types, and root-cause signals used to triage issues |
| `case_studies.json` | Real-world issues and CVEs linked to root causes and methodology components |
| `falsification_tests.json` | Falsification test registry (F-IDs, assumptions, strategies, test-file mappings) |
| `ontology.json` | Extended domain ontology and OI-XXX issue registry |
| `pr26_ontological_issues.json` | Legacy OI-001..OI-016 issues (cross-platform determinism) |

### Validation script

```bash
# Validate all schema cross-references:
python scripts/validate_methodology.py

# Also report F-IDs without @falsification_id tags in tests/:
python scripts/validate_methodology.py --check-tags
```

---

## Identifier conventions

| Prefix | Example | Meaning |
|---|---|---|
| `F-NNN` | `F-001` | Falsification test (platform invariants, PR #28) |
| `F-DOMAIN-NNN` | `F-GRAPHICS-001` | Domain-specific falsification test |
| `OI-NNN` | `OI-002` | Ontological issue (legacy, PR #26) |
| `OI-DOMAIN-NNN` | `OI-CRYPTO-001` | Domain-specific ontological issue |
| `CS-DOMAIN-NNN` | `CS-CRYPTO-002` | Case study |
| `D-NAME` | `D-CRYPTO` | Domain identifier |
| `RCS-NAME` | `RCS-TIMING` | Root-cause signal |

---

## How to register a new domain

1. Add an entry to `ontology/search_lens.json` → `domains[]`:
   ```json
   {"id": "D-MYDOM", "name": "My Domain", "description": "..."}
   ```
2. Add a domain entry to `ontology/ontology.json` → `domains[]` with
   `invariants`, `example_falsification_test`, `example_ontological_issue`.
3. Run `python scripts/validate_methodology.py` — it should pass.

---

## How to register a new case study

1. Add an entry to `ontology/case_studies.json` → `cases[]`:
   ```json
   {
     "id": "CS-MYDOM-001",
     "title": "...",
     "source": "https://...",
     "domain": "D-MYDOM",
     "root_cause_signals": ["RCS-NONDETERMINISM"],
     "description": "...",
     "assumptions_violated": ["..."],
     "falsification_tests": ["F-MYDOM-001"],
     "ontological_issues": ["OI-MYDOM-001"],
     "lessons": ["..."],
     "methodology_components": ["..."]
   }
   ```
2. Ensure all referenced F-IDs and OI-IDs exist in their respective registries.
3. Run `python scripts/validate_methodology.py`.

---

## How to register a new falsification test

1. Add an entry to `ontology/falsification_tests.json` → `falsification_tests[]`:
   ```json
   {
     "id": "F-MYDOM-001",
     "title": "...",
     "domain": "D-MYDOM",
     "assumption": "...",
     "falsifying_observation": "...",
     "strategy": "...",
     "status": "placeholder",
     "test_file": "TODO: tests/test_mydom.py::test_f_mydom_001",
     "ontological_issues": ["OI-MYDOM-001"],
     "case_studies": ["CS-MYDOM-001"]
   }
   ```
2. Implement the test in `tests/test_mydom.py` and add the tag comment:
   ```python
   # @falsification_id: F-MYDOM-001
   ```
3. Change `"status"` from `"placeholder"` to `"active"` and update `"test_file"`.

---

## How to register a new ontological issue

1. Add an entry to `ontology/ontology.json` → `issues[]`:
   ```json
   {
     "id": "OI-MYDOM-001",
     "title": "...",
     "domain": "D-MYDOM",
     "category": "...",
     "severity": "high",
     "status": "Open",
     "description": "...",
     "assumptions_violated": ["..."],
     "related_cases": [],
     "falsification_tests": ["F-MYDOM-001"],
     "resolution_notes": "..."
   }
   ```
2. Run `python scripts/validate_methodology.py`.

---

## Tagging test files

Add a tag comment near the top of any test file that implements a falsification
test from the registry:

```python
# @falsification_id: F-GRAPHICS-001
```

Multiple tags are allowed:

```python
# @falsification_id: F-001
# @falsification_id: F-002
```

The `--check-tags` flag of `validate_methodology.py` will report F-IDs that
have no corresponding tag in `tests/`. This is reported as a **warning**, not an
error, to allow incremental adoption.

---

## Connection to UVM / axiomatic / Peano / witness architecture

| Methodology concept | Monorepo counterpart |
|---|---|
| **Axiomatic substrate** | Environmental assumptions documented in `pr26_ontological_issues.json` and enforced by F-001..F-005 |
| **Peano kernel** | Core arithmetic invariants tested in `tests/test_peano_axioms.py` and `tests/test_axioms.py` |
| **Falsification tests** | F-IDs in `ontology/falsification_tests.json`, implemented in `tests/test_falsification*.py` |
| **Ontological issue registry** | OI-IDs in `ontology/ontology.json` and `ontology/pr26_ontological_issues.json` |
| **Witness layer** | CI jobs that record sha256 hashes of artifacts (Merkle root witness in `tests/test_global_merkle.py`) |
| **UVM (Universal Virtual Machine)** | Python-level deterministic memory model; all weight generation uses `hashlib.sha256` not `os.urandom` |
| **Search lens** | `ontology/search_lens.json` — domains, artifact types, root-cause signals for triage |
| **Case studies** | `ontology/case_studies.json` — real-world grounding for each falsification test |

### Immune system analogy

- **Domains** = tissues (each with specific invariants)
- **Ontological issues** = pathogens (named, tracked, with known resolution)
- **Falsification tests** = antibodies (designed to detect a specific violation)
- **Case studies** = historical infection records (teach the immune system what to watch for)
- **CI workflow** = immune response (automatically triggers on every PR)

---

## CI workflow

The workflow `.github/workflows/deepseek-methodology.yml` runs on every push/PR
that touches `ontology/`, `scripts/validate_methodology.py`, or `tests/`:

1. **Validate JSON syntax** — all `ontology/*.json` files must parse.
2. **Schema cross-reference validation** — all F-ID, OI-ID, domain, and case-study
   references must resolve correctly.
3. **Tag-coverage check** — reports (non-blocking) F-IDs without `@falsification_id`
   tags in `tests/`.
4. **Existing falsification tests** — `tests/test_falsification.py` (F-001..F-005)
   must pass on ubuntu-latest.

---

## Adding a new domain (end-to-end example)

Suppose you want to add a **Robotics** domain:

1. `ontology/search_lens.json` → add `{"id": "D-ROBOTICS", "name": "Robotics", "description": "..."}`
2. `ontology/ontology.json` → add domain entry with invariants and example IDs
3. `ontology/ontology.json` → add `OI-ROBOTICS-001` issue entry
4. `ontology/falsification_tests.json` → add `F-ROBOTICS-001` entry (`status: "placeholder"`)
5. `ontology/case_studies.json` → add `CS-ROBOTICS-001` if there is a real-world case
6. Run `python scripts/validate_methodology.py` — must pass
7. Implement `tests/test_robotics.py` with `# @falsification_id: F-ROBOTICS-001`
8. Change `F-ROBOTICS-001` status to `"active"` and update `test_file`

---

*TODO: deeper integration with UVM cycle_count witness layer and Peano proof
obligations will be addressed in a future PR once the formal interface between
the ontology registry and the UVM state machine is specified.*
