---
tags: [covenant, yaai, standards, documentation]
register: documentation
---

# YAAI COVENANT — Eighteen Axioms, Classified by What Actually Enforces Them

**Source:** `aidoruao/Fiduciary-Yeshua-Agentic-Local-Model`, the 18-axiom list
in its README (2026-07-23). A refined 10-axiom "covenant" version appears
later in the same file; where the two differ, this document follows the 18.

**Purpose:** to state, one axiom at a time, whether a mechanism enforces it
here, or whether it is framing. The failure mode this document prevents is the
one YAAI itself commits: an axiom list that nothing checks.

**Classification:**
- **ENFORCED** — a gate fails the build when the axiom is violated.
- **PARTIAL** — a mechanism exists but does not cover the whole axiom.
- **NOT ENFORCED** — no mechanism; stated honestly rather than implied.

Legend for mechanisms: gates 1–10 are in `ledger/verify.sh`; Lean modules are
`L1_LEDGER.lean`, `L1_SELECTION.lean`, `L1_GATES.lean`.

---

## The classification

### 1. No authority without proof — **ENFORCED**

`admit()` rejects any claim lacking a source hash, page cite, verbatim quote,
evidence tier, or nature. `L1_LEDGER.lean` makes the adjudication rule a proof
field, so a `finding` on an unverified tier cannot be constructed. Gate 2.

### 2. No hidden state — **PARTIAL**

The custody check enumerates every file held locally and compares it to the
published manifest: mismatch, missing, unlisted, malformed. Gate 6. The lineage
census enumerates every trained adapter across two filesystems. Gate 10's
sibling command.

*Not covered:* live process state, open network connections, or anything
outside the scanned roots. The claim is "the artifacts we know about are
enumerated," not "nothing is hidden."

### 3. Structural fixes over UI patches — **PARTIAL**

Stated as a design preference; no mechanism can distinguish a structural fix
from a patch. Partially served by the negative controls, which require every
invariant to have a failing case.

### 4. Territory is the only valid map — **ENFORCED**

`census declarations` parses a README's declared tree and checks each path
against the filesystem. Gate 10. This axiom is what caught YAAI's own 35/36
divergence.

### 5. Anti-documentation theater — **PARTIAL**

The compliance check refuses `TODO`, `FIXME`, and unimplemented placeholders in
shipping sources. Gate 9, check `no-stubs`.

*Not covered:* code-to-documentation ratio. A comment-heavy file with no logic
still passes.

### 6. Anti-RLHF — **NOT ENFORCED**

This constrains model selection, not the ledger. It cannot be satisfied by any
agent reached through a managed API, including this one. Stated plainly rather
than claimed.

### 7. Anti-corporate incentive — **NOT ENFORCED**

A structural stance about who controls the model. No gate can check it.

### 8. Anti-statistical stochasticism — **PARTIAL**

Verification is deterministic: sorted traversal, canonical JSON, fixed seeds,
pinned dependencies, byte-identical re-runs required. Gates 1–2 and 9.

*Not covered:* the model's own sampling. The gates are deterministic; the
proposer is not. That is the honest split, and it is why subagent output is
treated as a proposal and never as proof.

### 9. Anti-private equity — **NOT ENFORCED**

Out of scope for a ledger. No mechanism.

### 10. Anti-black box — **PARTIAL**

Every gate is a readable file with a falsifier. Gates 1–10 are open code in
`ledger/`.

*Not covered:* the model itself. An LLM is a black box; the response is to put
it outside the trusted path, not to pretend otherwise.

### 11. Anti-hubris — **PARTIAL**

The five negative controls force the system to be able to fail, and every
Scope section states what is *not* proved. Gate 4.

*Not covered:* hubris in prose. Nothing stops an overclaim in a document.

### 12. Anti-arrogance — **PARTIAL**

Same mechanism as 11. Additionally, `L1_GATES.lean` proves that adding a gate
is only *weakly* dominant — never worse, not always better — which is a
deliberately modest claim.

### 13. Anti-disorganization — **ENFORCED**

Ten gates, deterministic ordering, sorted violation output, canonical
serialization, one command (`./verify.sh`) that runs all of it. A violation
report is identical across runs.

### 14. Glass box enforcement — **ENFORCED**

Every gate is open source in this repository, and CI runs the same script a
human runs. Gate 9 checks that no gate has been quietly reduced to a stub.

### 15. Anti-structural-theater — **ENFORCED BY THEOREM**

This is the strongest claim in this document, and it is a theorem rather than
an assertion:

- `vacuous_gate_adds_nothing` — a gate that admits everything changes nothing.
- `duplicate_gate_adds_nothing` — repeating a gate changes nothing.
- `redundant_gate_adds_nothing` — a gate already present adds nothing.
- `strict_gain_needs_rejection` — a gate helps only if it rejects something.

Five negative controls must fail to compile on every run. Gate 4 verifies that
they do.

### 16. Anti-false witness — **ENFORCED**

The citation audit caught a paraphrase published as a quotation in
`L3_FETCHED.lean`. Gate 8 exits non-zero on any cite that is neither verbatim
nor a marked elision. Commit messages are checkable against `git show`.

*Residual risk:* commit messages are not automatically verified. The YAAI
"restore all 8 test files" commit is the counterexample, and nothing in this
gate chain would catch its like.

### 17. Anti-profane architecture — **NOT ENFORCED**

A judgement about what a system is built on. No gate.

### 18. Invariants enforced at compile time — **ENFORCED**

Three Lean modules carry invariants as proof fields, so violating them is a
type error rather than a policy breach: `Record.adjudicated_requires_fetched`,
`Selection.total`, `Selection.reasons`. Five negative controls confirm the
proof fields are inhabited only by valid records.

---

## Tally

| Class | Count | Axioms |
| :--- | ---: | :--- |
| ENFORCED | 7 | 1, 4, 13, 14, 15, 16, 18 |
| PARTIAL | 7 | 2, 3, 5, 8, 10, 11, 12 |
| NOT ENFORCED | 4 | 6, 7, 9, 17 |

Seven of eighteen are enforced by a gate that fails the build. That is the honest
number, and it is the number this document exists to publish.

---

## What this document refuses to do

It refuses to claim the covenant is satisfied. Four axioms have no mechanism
and eight have partial coverage. A document that claimed eighteen of eighteen
would be the exact artifact axiom 15 names — structural theatre — and it would
be the fifth failure in `LESSONS_LEARNED.md`, not a solution to it.

The useful reading is the other direction: **the six enforced axioms are the
ones a reader can check for themselves**, by running one command. The twelve
others are commitments, and commitments are worth exactly what the next
session makes of them.

---

## The one axiom to add

YAAI has no axiom for the failure it actually died of at the commit level: a
message asserting work that did not happen.

Proposed, and not yet enforced:

> **19. A commit message is a claim.** It carries the same evidential burden as
> any other: if it says files were restored, the diff shows them; if it says a
> test passes, the run is cited.

Nothing currently checks this. It is recorded here so that the next session
knows it is the largest remaining gap between what this project says and what
it does.
