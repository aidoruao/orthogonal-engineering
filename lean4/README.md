---
tags: [lean4, readme]
register: documentation
---

# Lean4 Formal Verification Bridge

This directory contains Lean4 formalizations of the mathematical claims made in the Python axiom modules and SAL types.

## Philosophy

The Python implementations are the operational source of truth.  
The Lean4 proofs are the formal verification layer. If they disagree, investigate — do not silently override either.

## Status

| Python Module | Lean4 File | Status |
|---------------|------------|--------|
| axioms/peano.py | Axioms/Peano.lean | Formalized (P1-P5, +,-,× properties) |
| axioms/number_theory.py | Axioms/NumberTheory.lean | Partial (Euclid's infinite primes, division algorithm) |
| src/sal/SAL_SPECIFICATION.md | SAL/Basic.lean | Stub (Adjoint triple structure) |
| src/sal/yoneda_embedding.py | SAL/Yoneda.lean | Stub (Yoneda lemma formalization) |

## Building

```bash
cd lean4
lake build
```

## Structure

```
lean4/
├── lakefile.lean          # Lean4 project configuration
├── README.md              # This file
├── SAL/                   # SAL type formalizations
│   ├── Basic.lean         # SAL Types 3-9 (Adjoint Triple)
│   └── Yoneda.lean        # SAL Type 10 (Yoneda embedding)
└── Axioms/                # Axiom module formalizations
    ├── Peano.lean         # Peano axioms P1-P5
    └── NumberTheory.lean  # Euclid, Bézout, Fermat
```

## Adding New Formalizations

1. Create new .lean file in appropriate subdirectory
2. Follow existing naming conventions
3. Add entry to status table above
4. Update lakefile.lean if new dependencies needed
5. Run `lake build` to verify

## Cross-Repository Connection

The Lean4 bridge is part of the cross-repo Merkle tree:
- This `lean4/` directory contributes to the overall repository hash
- Changes here must be reflected in the Merkle root computation
- See `automation/cross_repo_merkle.py` for details
