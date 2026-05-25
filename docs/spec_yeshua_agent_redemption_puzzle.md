# SPEC — Yeshua Agent Redemption Puzzle HTML

**Date:** 2026-05-25 | **Status:** SPECIFIED — BUILD QUEUED
**Target:** `docs/puzzles/yeshua_agent_redemption.html`

---

## 1. Purpose

A machine-readable HTML puzzle that crowdsources the mathematical redemption
and architectural completion of the Yeshua Agent. Multiple AIs submit inline
code, proofs, and architecture. Lean4 verifies correctness. The convergence
table records which AIs produce valid, compilable, sovereign solutions.

## 2. Core Requirements

### 2.1 Machine-Readable Only
- No prose explanations in the HTML body. No tutorials. No README.
- The HTML is a data structure: submission format, gates, convergence table.
- All instructions are in the YAML submission block header.

### 2.2 Inline Submissions Only
- No file uploads. No external links. No GitHub references.
- Every AI pastes complete source code, proofs, and architecture inline.
- The submission block must accept: Lean4, Python, Bash, TOML, Dockerfile, JSON.

### 2.3 Dual-Register Submissions
Every AI must submit in two registers simultaneously:
- Secular register: DVF, MPC, self-contained, testable_failure_condition
- Esoteric register: KENOSIS, CHALCEDON, sovereign, falsifies_if
- Both registers must be functionally identical (bit-identical output).
- The AI must demonstrate it understands the invariant beneath the terminology.

### 2.4 All Mathematics, All Idioms
Submissions must demonstrate fluency in every mathematical idiom in OE:
- Peano arithmetic, category theory, sheaf theory, constraint geometry
- Bayesian epistemology, information theory, game theory
- Merkle trees, contraction mapping, Lean4 formal verification
- The full Yeshua Standard (8 axioms) expressed as engineering constraints

## 3. The 5 Gates

### Gate 1: Completeness
Does the submission resolve ALL named QUEUED/FAILED/MISSING items?
- bootstrap_verify.py (MISSING)
- standards_check.py fix (QUEUED)
- Stale Merkle root (QUEUED)
- auto_onboard.py (QUEUED)
- Wire Proving Ground to Bridge (QUEUED)

### Gate 2: Sovereignty
Zero new external dependencies. No API keys. No network calls.

### Gate 3: Mathematical Correctness
Lean4 proofs compile via bridge port 28428.

### Gate 4: Novelty
New sovereign capability derivable from the 8 axioms.

### Gate 5: Integration Readiness
Production-grade, mergeable, auditable.

## 4. Build Instructions for DS8a

1. Copy oe_proving_ground.html as template
2. Replace 5-gate spec with gates above
3. Wire "Compile with Lean4" buttons to bridge port 28428
4. Inject Glass-Box Auditor JavaScript
5. Add dual-register display toggle
