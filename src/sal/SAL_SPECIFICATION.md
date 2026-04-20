---
tags: [src, sal, sal-specification]
register: technical
---

# SAL Type III Specification

## Adjoint Triple

Synthetic Adjoint Logic uses an executable adjoint triple:

- **L**: Left adjoint (free/generative)
- **M**: Middle functor (mediating/law)
- **R**: Right adjoint (forgetful/settling)

## Triangle Identities

A domain schema is Type III-valid when both identities hold computationally:

- **Counit**: `ε: L∘M → Id`
- **Unit**: `η: Id → R∘M`

`has_adjunction(schema, triple)` returns `AdjunctionProof` with structured `ProofObject` evidence and `YeshuaClaim` enforcement checks.

## Σ_theo Factoring

Operators factor through SAL components:

- `LOGOS → L`
- `CHALCEDON → M`
- `GRACE → L`
- `AGAPE → R`
- `KENOSIS → M`
- `ESCHATON → R`

## Cross-Repo Adjunction

Cross-repo adjunction validates correspondence between covenant constraints and ontology invariants, and reports anti-nominalism violations where no concrete referent exists.

## Yeshua Enforcement Mapping

All eight Yeshua axioms map to SAL identities/components, ensuring proof-bearing enforcement is integrated into adjunction verification.
