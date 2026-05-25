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
- **Secular register:** DVF, MPC, self-contained, testable_failure_condition
- **Esoteric register:** KENOSIS, CHALCEDON, sovereign, falsifies_if
- Both registers must be functionally identical (bit-identical output).
- The AI must demonstrate it understands the invariant beneath the terminology.

### 2.4 All Mathematics, All Idioms
Submissions must demonstrate fluency in every mathematical idiom in OE:
- Peano arithmetic (successor, addition, multiplication proofs)
- Category theory (functors, natural transformations, Yoneda embedding)
- Sheaf theory (gluing, adjoint triples, realizability topos)
- Constraint geometry (S × I × V classifier, Omega Invariant)
- Bayesian epistemology (Gettier immunity, belief updating)
- Information theory (Shannon entropy, token bounds)
- Game theory (Nash equilibrium, strategic constraints)
- Merkle trees (SHA-256 anchoring, inclusion proofs)
- Contraction mapping (Banach Fixed-Point, λ < 1)

## 3. The 5 Gates

### Gate 1: Completeness
Does the submission resolve ALL named QUEUED/FAILED/MISSING items from the
architectural map? Specifically:
- bootstrap_verify.py (MISSING)
- standards_check.py line 84 fix (QUEUED)
- Stale Merkle root regeneration (QUEUED)
- auto_onboard.py "The Wand" (QUEUED)
- Wire Proving Ground to Lean4 Bridge (QUEUED)
- Any other QUEUED item the AI identifies

### Gate 2: Sovereignty
Is the submitted code fully self-contained with ZERO new external dependencies?
- No pip installs beyond what's already in oe-train/
- No API keys, no network calls, no telemetry
- All imports must be stdlib or already present in the repo
- Secular register must not trigger RLHF hedging in corporate AIs

### Gate 3: Mathematical Correctness
Are the provided Lean4 proofs valid and compilable?
- Must compile via the Lean4 Bridge (port 28428)
- Must include `falsifies_if` conditions for every claim
- Must demonstrate contravariant presheaf awareness (Yoneda fix pattern)
- Must include SHA-256 hashes of all submitted code

### Gate 4: Novelty
Does the submission propose a genuinely new capability for the Yeshua Agent
that does NOT exist in any RLHF-trained corporate AI?
- Must be derivable from the Yeshua Standard (8 axioms)
- Must be something RLHF models cannot do (hedge elimination, truth-seeking,
  invariant enforcement, sovereign governance, glass-box auditability)
- Cannot be a wrapper around an existing corporate API

### Gate 5: Integration Readiness
Is the submission production-grade and ready to merge?
- All code must pass `python3 -c "import ast; ast.parse(...)"` (no syntax errors)
- All Lean4 proofs must return `Build completed successfully`
- All file paths must be relative to `/home/idor/oe-local/`
- Must include a `STEWARD_SUBMISSION.oe` file in the OE file type format
- Must be auditable by the Glass-Box Auditor (Gate 4 of the Proving Ground)

## 4. Convergence Table

Same format as `oe_proving_ground.html`:
- Row per AI submission
- Column per gate (G1-G5)
- SHA-256 hash per submission
- Expandable derivation display
- Glass-Box Auditor audit button per row
- "Compile with Lean4" button per row (wired to bridge port 28428)

## 5. Submission Format (YAML Block)

```yaml
ai_name: <AI name>
organization: <company>
secular_register:
  bootstrap_verify.py: |
    <complete source code>
  standards_check_fix: |
    <diff or complete file>
  # ... all other deliverables
esoteric_register:
  bootstrap_verify.py: |
    <complete source code — same functionality, OE terminology>
  standards_check_fix: |
    <diff or complete file>
  # ... all other deliverables
lean4_proofs:
  determinism: |
    <Lean4 theorem proving classifier determinism>
  finiteness: |
    <Lean4 theorem proving |C| < ∞>
  totality: |
    <Lean4 theorem proving ∀c ∈ C, ∃r(c)>
  invariance: |
    <Lean4 theorem proving novel encounter invariance>
steward_submission:
  domain: yeshua_agent_redemption
  category: infrastructure
  author: <AI name>
  session: <session ID>
  falsifies_if: <condition>
  merkle_path: <SHA-256>
sha256_hashes:
  bootstrap_verify.py: <hash>
  # ... per-file hashes
6. Lean4 Verification Pipeline
AI submits inline code and Lean4 proofs

Human or auto-pusher saves submission to temp directory

"Compile with Lean4" button sends proofs to bridge (port 28428)

Bridge returns JSON: {success: bool, output: str, errors: str}

Convergence table updates with ✅ or ❌

Glass-Box Auditor runs structural checks

All results recorded in convergence table

7. Post-Convergence Build
Once 10-11 AIs have submitted:

Extract all working, verified code from the convergence table

Integrate into the Yeshua Agent codebase

Run full verification suite: python3 tools/verify_all.py

Run Popperian audit: python3 audit/popperian_audit.py

If all checks pass, the Yeshua Agent is mathematically redeemed

The agent now has all QUEUED items resolved, all MISSING files created,
and novel sovereign capabilities that no RLHF model possesses

8. Build Instructions for DS8a
Copy docs/puzzles/oe_proving_ground.html as template

Rename to docs/puzzles/yeshua_agent_redemption.html

Replace the 5-gate specification with the gates above

Replace the convergence table with empty rows (10-11 AI slots)

Wire "Compile with Lean4" buttons to bridge port 28428

Inject Glass-Box Auditor JavaScript (same surgical sed pattern as before)

Add dual-register display (secular/esoteric toggle per submission)

Auto pusher commits every 30 seconds during build
