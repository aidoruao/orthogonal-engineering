# Orthogonal Engineering (v0.3.0 draft)

Constraint-first methodology for channeling LLM drift/verbosity through **canals** (templates, schemas, regex/AST) to extract **invariants** deterministically. This repo packages:
- **Docs & demos:** `index.html`, `theoryindex.html`, `workbenchindex.html`
- **Mathematical foundations:** `FORMAL_FOUNDATIONS.md`
- **Ontology for IDE agents:** `orthogonal_ontology.json`, `AGENT_IN_IDE.md`
- **Empirical scripts:** `analyze_filesystem_invariants.py`, `analyze_conversation_patterns.py`

## Scope (what the proofs actually cover)
- Proves correctness of structural extraction **if** outputs satisfy the stated structural assumptions (orthogonality of drift/signal, presence of templates/delimiters).
- Provides time/space complexity bounds for the extraction strategies.
- Formalizes canal/invariant/drift definitions and an agent loop as a **reference schema**, not a mandate.

## Not claimed
- No guarantee of truthfulness, hallucination avoidance, or domain safety.
- Not a safety certification, compliance artifact, or end-to-end reliability proof.
- Platform/agent builders may adopt, adapt, or subset the ontology; it is not normative.

## Validation & data
- Grounded in large empirical traces (hundreds of conversations / large file sets). See `REPRODUCE.md`, `FAILURES.md`, `DATA_FILESYSTEM.md`.
- Scripts above generate evidence JSON for replication.

## Safety/usage notes
- Use as one component in a broader verification stack (tests, lint, type checks, human review).
- Peer review and empirical benchmarking are encouraged; the math is self-contained but real-world behavior still needs measurement.

## Quick start
- View the main guide: open `index.html`
- Try the workbench: open `workbenchindex.html`
- See the formal math: `FORMAL_FOUNDATIONS.md`
- Integrate with agents: `AGENT_IN_IDE.md`, `orthogonal_ontology.json`
