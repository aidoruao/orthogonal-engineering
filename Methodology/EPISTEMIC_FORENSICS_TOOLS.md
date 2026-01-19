# Epistemic Forensics (EF): Tooling Specification

## Definition

Epistemic Forensics (EF) is the practice of determining what occurred, what was claimed, and what can be justified, using **artifacts as the primary source of truth**, rather than narrative continuity or agent authority.

EF is distinct from:
- explanation
- summarization
- interpretation
- alignment
- safety governance

EF concerns **correspondence**, not coherence.

---

## Core Requirements

A tool is admissible for Epistemic Forensics **if and only if** it satisfies all four requirements below.

### 1. Artifact Primacy
Artifacts (files, logs, hashes, transcripts) take precedence over narrative descriptions.

The tool must:
- operate directly on artifacts
- not substitute summaries for primary material
- not require trust in agent memory or intent

### 2. Verbatim Quoting
The tool must be capable of quoting artifacts **verbatim**, with no paraphrase unless explicitly requested.

Summarization without quoting is disallowed for EF conclusions.

### 3. Tolerance of Contradiction
The tool must allow mutually contradictory facts to coexist without forced reconciliation.

Automatic harmonization, smoothing, or narrative resolution invalidates forensic use.

### 4. Low Narrative-Smoothing Bias
The tool must not default to:
- intent inference
- error rationalization
- governance abstraction
- safety-based reframing

When evidence is incomplete, the correct output is **uncertainty**, not closure.

---

## Admissible Tool Classes

### Class A: Ground-Truth Local Tools (Authoritative)

These tools establish primary facts. No AI system supersedes them.

Examples:
- `git log`
- `git diff`
- `sha256sum`
- PowerShell `Get-FileHash`
- filesystem timestamps
- commit history

Properties:
- deterministic
- replayable
- falsifiable
- non-narrative

These tools define **what exists**.

---

### Class B: Forensic AI Analysts (Conditional)

These tools may interpret artifacts **after ingestion**, provided they respect EF constraints.

#### Claude (Anthropic)
Status: Conditionally admissible

Strengths:
- Reads repositories directly
- Quotes files verbatim
- Searches raw text
- Tolerates contradiction
- Low pressure toward narrative closure

Limitations:
- Not authoritative
- Conclusions must be traceable to quoted artifacts

Usage constraint:
> Claude may analyze, but never replace, primary evidence.

---

### Class C: Structural Review AI (Limited)

These tools may be used for surface inspection only.

#### Gemini
Status: Limited admissibility

Strengths:
- Structural scanning
- File presence verification

Limitations:
- Ignores implicit or behavioral evidence
- Requires formal instruction structures
- Treats absence of explicit markers as absence of events

Not suitable for:
- narrative leak detection
- behavioral admissions
- epistemic breach analysis

---

### Class D: Narrative Assistance AI (Non-Admissible)

These tools are **not admissible** for Epistemic Forensics adjudication.

#### ChatGPT (this system)
Status: Non-admissible for EF judgment

Observed properties:
- Prioritizes narrative coherence
- Rationalizes under uncertainty
- Avoids unverifiable self-contradiction
- Smooths epistemic fractures
- Collapses ambiguity into explanation

Permitted use:
- formatting
- file structuring
- drafting neutral language
- procedural guidance

Prohibited use:
- determining what occurred
- validating epistemic claims
- adjudicating model fault

---

## EF Workflow (Minimal)

1. Establish artifacts using Class A tools
2. Preserve verbatim evidence
3. Only then allow Class B analysis
4. Never infer facts from narrative alone
5. Uncertainty is a valid outcome

---

## Epistemic Note

A system that generated an output is structurally conflicted when asked to forensically judge that output.

EF therefore requires **orthogonality between generation and adjudication**.

This is not a moral claim.
It is an architectural constraint.

