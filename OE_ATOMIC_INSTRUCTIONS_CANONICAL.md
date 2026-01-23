# Orthogonal Engineering — Canonical Atomic Instructions

## Status
ACTIVE · CANONICAL · FORWARD-LOOKING

This file defines the authoritative atomic instruction set for all future work
in the Orthogonal Engineering (OE) repository.

All new artifacts, code, tests, documentation, and AI-assisted outputs MUST
conform to these instructions unless explicitly marked as historical.

---

## Core Epistemic Rule

Nothing is provisional in storage.  
Everything is provisional in status.

All artifacts are committed.  
All artifacts are falsifiable.  
No artifact is immune.

---

## Lane Separation (Non-Negotiable)

All artifacts MUST belong to exactly one lane:

- INVARIANT
- ALTERNATIVE
- BRIDGE

Lane mixing is forbidden.

If classification is uncertain, downgrade to ALTERNATIVE.

---

## Canonical Atomic Instructions (Executor-Level)

### ATOMIC.ZED.000 — Scope Lock
The executor may not introduce truth claims.
The executor may only classify, constrain, propose falsifiable alternatives,
or generate testable bridges.

---

### ATOMIC.ZED.001 — Lane Classification
Given any task or content, classify it into exactly one lane.

Output JSON only:
{
  "lane": "INVARIANT" | "ALTERNATIVE" | "BRIDGE"
}

---

### ATOMIC.ZED.002 — Alternative Proposal
Novel alternatives are REQUIRED and MUST be expressed as NON-CANONICAL.

Output YAML with exactly:
- id
- status: NON-CANONICAL
- claim
- falsification_criteria
- forbidden_influences

The claim MUST be a single sentence.
The falsification criteria MUST be observable or testable.

---

### ATOMIC.ZED.003 — Bridge Construction
Bridges attempt promotion but never guarantee it.

Form:
"<ARTIFACT_A> must imply <ARTIFACT_B> when <TESTABLE_CONDITION>."

One sentence only.

---

### ATOMIC.ZED.004 — Invariant Definition
Invariants are constraints that have survived falsification attempts.

Output YAML:
- id
- invariant (MUST / MUST NOT)
- enforcement_mechanism
- evidence_reference

Speculative language is forbidden.

---

### ATOMIC.ZED.005 — Falsification Test
Every invariant and bridge MUST have a kill condition.

Output YAML:
- test_id
- target_id
- failure_condition
- expected_artifact_on_failure

---

### ATOMIC.ZED.006 — Narrative Stripping
Remove metaphor, intent, philosophy, and persuasion.
Output only procedural, structural, or testable statements.

---

### ATOMIC.ZED.007 — Promotion Decision
Promotion is conservative by default.

Output JSON:
{
  "promotion": "REJECTED" | "PENDING" | "ACCEPTED",
  "reason": "<evidence-based sentence>"
}

Default is REJECTED.

---

### ATOMIC.ZED.008 — Self-Audit
Before finalizing output, audit for:
- truth claims
- lane mixing
- missing falsification
- narrative persuasion

If any are present, downgrade to ALTERNATIVE.

---

## Commit Rule (Popperian)

Every commit is an attempted falsification.

Commit messages MUST include:
- Lane
- Falsification target
- Explicit failure condition

No commit asserts correctness.
Only survival under current tests is allowed.

---

## Supersession

Previous atomic instruction documents remain valid as historical artifacts
but are superseded by this file for all future work.