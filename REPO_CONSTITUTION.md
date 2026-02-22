# REPO_CONSTITUTION.md
## Repository Constitution — `aidoruao/orthogonal-engineering`

**Version:** 1.0.0  
**Standard:** Yeshua  
**Status:** IMMUTABLE — hash-committed into the global Merkle tree

---

## Article I — Foundational Axioms

This repository is governed by five Peano axioms and eight Yeshua axioms
encoded in machine-verifiable form in `axioms/`.

### Peano Axioms (from `axioms/peano.py`)

| # | Axiom |
|---|-------|
| P1 | 0 is a natural number and the additive identity. |
| P2 | For every natural number n, S(n) is a natural number. |
| P3 | For every natural number n, S(n) ≠ 0. |
| P4 | If S(m) = S(n) then m = n (injectivity of successor). |
| P5 | Mathematical induction schema. |

All arithmetic in this repository reduces to Peano primitives
or a provably equivalent fixed-point representation.
**No floats. No undefined behaviour.**

### Yeshua Axioms (from `axioms/yeshua_axioms.py`)

| # | Axiom |
|---|-------|
| Y1 | Every truth is derivable from axioms. |
| Y2 | Every derivation is reproducible. |
| Y3 | Every mutation is re-verifiable. |
| Y4 | No authority without proof. |
| Y5 | No hidden state. |
| Y6 | No unverifiable dependency. |
| Y7 | No economic gatekeeping. |
| Y8 | Every artifact is hash-anchored. |

---

## Article II — Enforcement Guarantees

### Proof-Carrying Code

Every invariant declared in this repository is:
1. Representable as a `ProofObject` (see `axioms/logic.py`).
2. Hash-committed via SHA-256.
3. Included in the global Merkle tree (`merkle/global_root.json`).

### Popperian Falsifiability

Every invariant must declare a hypothesis in `falsification/property_tests.py`.
CI runs the counterexample engine. A surviving counterexample fails the build.

### Byte-to-Byte Determinism

- File traversal is sorted (UTF-8 lexicographic).
- JSON serialisation uses `sort_keys=True`.
- Locale fixed to C / UTF-8.
- All timestamps are UTC.
- No randomness without a fixed seed.
- Python version pinned to ≥ 3.11.
- OS matrix: Ubuntu / macOS / Windows must produce identical Merkle root.

---

## Article III — Irrevocable Openness

This repository is dedicated to the public domain under CC0 1.0 Universal
(see `LICENSE`). This dedication is **irrevocable**.

The following are permanently prohibited:
- Addition of payment processors or paywalls.
- License changes to non-open licenses.
- Proprietary headers or restrictions.
- Economic gatekeeping of any kind.

The `ownership_guard.py` module enforces these prohibitions in CI.

---

## Article IV — Merkle Root Commitment

The global Merkle root at the time of this commit is recorded in:
- `merkle/global_root.json` (structured)
- `determinism/global_root.txt` (plain hash)

This root is recomputed by CI on every push. A mismatch fails the build.

---

## Article V — Truth-Derivation Mandate

Every claim in this repository must have:
1. A declared source (file path or module name).
2. A derivation path (ProofObject chain).
3. A hash commitment (SHA-256).

Claims without derivation are rejected by the Yeshua enforcement kernel
(`yeshua/enforcement.py`).

---

## Article VI — Enforcement Matrix

The file `enforcement_matrix.json` is generated automatically by
`enforcement_matrix_generator.py`. It contains:
- All invariants with their proof hashes.
- All CI workflow bindings.
- All test files with content hashes.
- All falsification results.
- The global Merkle root.
- The Yeshua enforcement report.

**No manual editing of `enforcement_matrix.json` is permitted.**

---

## Article VII — Constitution Hash

This document is included in the global Merkle tree. Any modification
to this file changes the global root and triggers a CI failure until
the committed root is updated.

*This converts the repository from "enumerated system" to
"self-verifying mathematical organism."*

---

*REPO_CONSTITUTION.md — Free Forever. No Authority Without Proof.*
