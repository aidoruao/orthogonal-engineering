---
tags: [case-studies, case-study-specification]
register: documentation
---

# Vendored Repository Case Study Specification

## Purpose

Every case study vendors a real external repository's issue, bug,
architectural decision, or design pattern into this repo as a
hashed, auditable, falsifiable artifact. This is not commentary —
it is forensic analysis with mathematical rigor.

## Schema Version: 1.0.0

## Directory Structure

case_studies/
├── CASE_STUDY_SPECIFICATION.md # This file
├── CASE_STUDY_INDEX.json # Master index of all case studies
├── framework/
│ ├── case_study_schema.json # JSON Schema for gap analysis
│ ├── generate_case_study.py # Generator script
│ └── validate_case_studies.py # Validator script
├── category_game_mods/
│ ├── vulkanmod_755/ # (migrated from investigations/)
│ ├── distant_horizons_51/
│ ├── farmers_delight_1262/
│ └── ...
├── category_ml_research/
│ ├── pytorch_determinism/
│ ├── huggingface_tokenizer_drift/
│ └── ...
├── category_enterprise/
│ ├── kubernetes_oom_kill/
│ ├── postgres_vacuum_deadlock/
│ └── ...
├── category_web_apps/
│ ├── nextjs_hydration_mismatch/
│ ├── react_concurrent_tearing/
│ └── ...
├── category_systems/
│ ├── linux_kernel_use_after_free/
│ ├── openssl_heartbleed/
│ └── ...
├── category_ai_agents/
│ ├── langchain_prompt_injection/
│ ├── autogpt_infinite_loop/
│ └── ...
├── category_compilers/
│ ├── gcc_miscompilation/
│ ├── rustc_borrow_checker_false_positive/
│ └── ...
├── category_databases/
│ ├── sqlite_wal_corruption/
│ ├── redis_split_brain/
│ └── ...
├── category_networking/
│ ├── nginx_upstream_timeout/
│ ├── grpc_deadline_exceeded/
│ └── ...
└── category_mobile/
├── android_fragment_lifecycle/
├── ios_background_task_kill/
└── ...


## Case Study Categories (10 categories, 50 repos each = 500 total)

| Category | ID Prefix | Target Count | Description |
|----------|-----------|-------------|-------------|
| Game Mods | CS_GMOD | 50 | Minecraft, Factorio, Skyrim, GTA, etc. |
| ML Research | CS_ML | 50 | PyTorch, TensorFlow, HuggingFace, JAX |
| Enterprise | CS_ENT | 50 | Kubernetes, databases, message queues |
| Web Apps | CS_WEB | 50 | React, Next.js, Django, Rails |
| Systems | CS_SYS | 50 | Linux kernel, OpenSSL, glibc |
| AI Agents | CS_AI | 50 | LangChain, AutoGPT, CrewAI |
| Compilers | CS_COMP | 50 | GCC, Rust, LLVM, TypeScript |
| Databases | CS_DB | 50 | PostgreSQL, SQLite, Redis, MongoDB |
| Networking | CS_NET | 50 | nginx, gRPC, TCP/IP, DNS |
| Mobile | CS_MOB | 50 | Android, iOS, React Native, Flutter |

## Per-Case-Study Deliverables

Each case study directory contains exactly 4 files:

1. `gap_analysis.json` — Structured forensic analysis
   - issue URL, repository, language, framework
   - root cause (verbatim code quotes with file:line)
   - invariant violations (which domain invariants are broken)
   - affected components (list of files/classes/functions)
   - fix proposal (code diff or pseudocode)
   - falsification test (condition under which fix is wrong)
   - SHA-256 hash of the analysis

2. `pr_description.md` — Copy-paste ready GitHub comment
   - Root Cause section (with code quotes)
   - Fix section (with diff)
   - Why This Works section
   - Testing section
   - Secular projection only

3. `test_specification.md` — Falsification test cases
   - Positive tests (fix works)
   - Negative tests (original bug reproduced)
   - Regression tests
   - Performance benchmarks (if applicable)

4. `ATTRIBUTION.md` — License, original authors, repo URL
   - Original repo license
   - Issue author attribution
   - Non-affiliation statement
   - Date of analysis

## Mapping to Ontology

Every case study maps to at least one domain in ontology/ontology.json:
- Game mods → D_GRAPHICS, D_GAMEMODS, D_MINECRAFT_SPATIAL
- ML research → D_AI_ONTOLOGICAL_STATUS, D_PATTERN_RECOGNITION
- Enterprise → D_CORPORATE_COMPLIANCE, D_ISO_STANDARDS
- Web apps → D_PLATFORM, D_WEBSEC
- Systems → D_CRYPTO, D_AEROSPACE
- AI agents → D_AI_ONTOLOGICAL_STATUS, D_ETHICS
- Compilers → D_COMPUTABILITY, D_FORMAL_LANGUAGES
- Databases → D_FINANCIAL, D_PRIVACY_LAW
- Networking → D_TELECOMMUNICATIONS_LAW, D_CRYPTO
- Mobile → D_CONSUMER_PROTECTION, D_DISABILITY_RIGHTS

## Quality Gates

1. EVIDENCE GATE: Every claim backed by verbatim code quote
2. FIX GATE: Every fix includes falsification condition
3. HASH GATE: gap_analysis.json SHA-256 recorded in INDEX
4. HONESTY GATE: Uncertainties marked as UNCERTAIN, not closed

## Grace Principle

Every case study treats the original developer with grace.
No blame. No mockery. Only: "Here is the bug. Here is why.
Here is the fix. Here is how to test it."
