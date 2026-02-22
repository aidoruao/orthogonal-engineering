# Tensor Identity Enforcement Specification (TIE)
# PR #37 — Distributed Verifiable Compute Layer
# Standard: Yeshua
# Version: 1.0.0

## Purpose

For AI/ML workloads, tensor operations must be deterministic across machines.
Identical inputs must always produce identical outputs, verified by hash.

## Requirements

### Canonical Graph Serialisation
- All tensor graphs must be serialised in a canonical, platform-independent
  format before hashing.
- Serialisation must be deterministic: same graph → same bytes → same hash.

### Precision Lock Policy
- Floating-point precision must be explicitly declared.
- Mixed-precision operations require explicit bounds proofs.
- Where floats are used, error bounds must be formally stated.
- An integer fallback equivalence path must exist.

### Seed-Anchored Initialisation
- All tensor initialisations must use a declared, canonical seed.
- The seed value must appear in `execution_spec.yaml`.
- Random initialisation without a declared seed is forbidden.

### Deterministic Inference Path
- Inference must be reproducible across hardware.
- CUDA ops that are non-deterministic by default must be replaced with
  deterministic equivalents or cross-validated against the pure path.

### Full Tensor Graph Hash
- After inference, the complete output tensor graph must be hashed.
- Hash must be included in the proof bundle (`output.hash`).

## Cross-Machine Identity Invariant

```
hash(canonical_serialise(input)) == hash(canonical_serialise(input))  # always
hash(canonical_serialise(output_A)) == hash(canonical_serialise(output_B))  # mandatory
```

Any probabilistic tolerance must be:
1. Formally bounded (explicit epsilon stated).
2. Proven to not affect the canonical output hash.
3. Documented in `verification.json`.

## Dual-Path Validation for Tensors

- Fast path (GPU) must produce bitwise-identical output to pure path (CPU).
- If fast path diverges from pure path, fast path is invalidated.
- Pure path runs on commodity CPU with deterministic arithmetic core.
