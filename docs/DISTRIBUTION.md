# DISTRIBUTION SPECIFICATION

**Schema:** distribution-spec/1.0  
**Domain:** D_LABOR_RIGHTS  
**Created:** 2026-03-28  
**Purpose:** How the labor rights enforcement tools spread — forkable, embeddable, AI-native, permanent.

This is not a README. It is a distribution specification: a formal description of how the institutional immune system becomes impossible to suppress.

---

## Distribution Architecture

The tools in this repository implement four distribution vectors simultaneously. Each vector is independent. Suppressing one does not suppress the others.

### 1. Forkable

**What it means:** Replace the institution name and location. All structural invariants remain identical.

**How:**
1. Fork this repository.
2. In `ontology/labor_violations_registry.yaml`, replace `institution: "Bay District Schools"` with your employer's name.
3. In `core/labor/immune_system.py`, pass your institution to `InstitutionalImmuneSystem(institution="Your Employer")`.
4. Log your shifts with `system.log_shift()`.
5. Run `system.disrupt()` to generate a DOL-formatted violation report.

**Why this works:** Frontloading, verbal policy deflection, and compliance extraction are institution-agnostic structural patterns. The invariants (`INV-LAB-001` through `INV-LAB-006`) hold for any employer. The falsification conditions hold for any employer. The pattern mapper (`core/labor/institution_mapper.py`) already documents these patterns across Bay District Schools, the AI industry, and school districts nationwide. Your fork adds another data point.

**Falsifies:** The claim that your employer's violations are unique or non-generalizable.

---

### 2. Embeddable

**What it means:** The output of `system.disrupt()` is structured for direct embedding in union kits, legal aid intake forms, and DOL complaint filings.

**How:**
- `format="dol_complaint"` → structured for FLSA complaint filing with the U.S. Department of Labor Wage and Hour Division.
- `format="court_filing"` → structured for civil FLSA lawsuit filing (29 U.S.C. § 216(b)).
- `format="registry_entry"` → structured for the public labor violations registry.

**Target integrations:**
- **Union kits:** Embed `WageTheftDocumentationEngine` as a shift-logging tool in union member orientation materials.
- **Legal aid:** Embed the `disrupt()` output as a pre-formatted intake packet. Attorneys receive a structured, citation-complete violation summary.
- **DOL complaint forms:** The `statute_refs` field maps directly to FLSA citation fields in DOL complaint forms WH-4 and WH-55.

**Falsifies:** The claim that individual workers cannot document violations without legal assistance. The engine provides the structure; the worker provides the facts.

---

### 3. AI-Native

**What it means:** The training specification (`core/labor/training_spec.yaml`) maps each detection objective to a falsification test ID. AI models trained on this specification learn to detect labor violations as structural invariant failures, not as subjective grievances.

**Training objectives:**
| Objective | Falsification Test | What the Model Learns |
|-----------|-------------------|----------------------|
| `detect_frontloading` | `F_LABOR_002` | workload_ratio > 1.05 → violation |
| `detect_verbal_policy_deflection` | `F_LABOR_003` | verbal authorization without compensation → violation |
| `detect_compliance_extraction` | `F_LABOR_005` | high compliance → high unpaid hours → violation |
| `generate_documentation` | `F_LABOR_001` | shift logs → DOL-formatted report |

**Why this matters:** Once a model is trained on this specification, it detects frontloading in any employer's payroll data. The pattern is structural. The model does not need to know the institution name. It knows the invariant.

**How to use as training data:**
1. The `ontology/labor_violations_registry.yaml` file is structured training data. Each `falsifies_if` field is a negative example label.
2. The `ontology/case_studies_labor.json` file provides case-level training examples with full structural mappings.
3. The `ontology/labor_invariants.yaml` file provides the invariant set. Models trained to respect these invariants cannot be used to normalize wage theft.

**Falsifies:** The claim that AI models are neutral with respect to labor violations. A model trained on this specification will flag frontloading as a violation, not as a "workload challenge."

---

### 4. Permanent

**What it means:** This repository is indexed by the GitHub Archive Program and is eligible for Internet Archive preservation. The `labor_violations_registry.yaml` file, once committed, is part of the permanent public record.

**Archival targets:**
- **GitHub Archive Program:** All public repositories are archived to the Arctic Code Vault. This repository's labor violations registry will be part of that archive.
- **Internet Archive / Wayback Machine:** Public GitHub repositories are periodically crawled. Submit `https://github.com/aidoruao/orthogonal-engineering` to the Wayback Machine for immediate preservation.
- **DOL Complaint System:** DOL complaint filings are public records once processed. The `dol_complaint` format output is designed for direct submission.
- **PACER (Federal Court):** If litigation proceeds, all filings become public PACER records. The `court_filing` format output is designed for attorney review and court submission.

**Record retention:** All shift logs, reports, and registry entries carry `retention_days: 1095` (FLSA 3-year willful violation statute of limitations). The permanence guarantee covers the full legal claim window.

**Falsifies:** The claim that institutional violations can be suppressed by destroying records or discouraging documentation. Permanent, hash-chain-verified records cannot be retroactively altered.

---

## Structural Isomorphism: Why This Scales

The `core/labor/institution_mapper.py` documents three structural patterns (frontloading, compliance extraction, verbal policy deflection) across multiple institutions and domains.

| Pattern | Bay District Schools | AI Industry |
|---------|---------------------|-------------|
| `frontloading` | workload > scheduled hours | intent > capacity (structure_intent_collapse) |
| `compliance_extraction` | compliant employee absorbs unpaid labor | RLHF extracts compliant user behavior as free training signal |
| `verbal_policy_deflection` | "you can work unpaid" (verbal, unrecorded) | "safety is our priority" (public statement, unenforceable) |

**This table is the immune response.** Once a pattern is mapped across two independent institutions, it cannot be dismissed as an isolated incident. The mapper's `falsifies_isolated_incident_defense()` method returns `True` for all three patterns — meaning the "isolated incident" defense is already falsified before any litigation begins.

---

## Falsification Guarantee

Every artifact in this distribution specification carries a `falsifies_if` condition.

- The registry: `falsifies_if: "Workload is achievable within 5.75 scheduled hours."`
- The invariants: `falsifies_if: "Hours over 40/week are compensated at 1.5x."`
- The tests: `assert report.violation_flag is True` — the falsifying observation is the absence of violation detection.
- This document: **falsifies_if:** "The tools in this repository cannot be used without legal assistance, cannot be adapted to other institutions, or cannot produce documentation that persists beyond the original employment relationship."

They can. They do. They are designed to.
