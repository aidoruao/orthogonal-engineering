# Resurrection

Deterministic regeneration as architectural resurrection.

## The Principle

Every witness recorded in `/canonical/` can be deterministically regenerated from the seed at any time, by anyone, without requiring any central server or authority.

This is resurrection by architecture:

- The record exists (in git, in distributed mirrors, in any fork)
- The seed exists (cryptographically derived, verifiable)
- The regeneration algorithm exists (deterministic, public)
- Therefore: any witness can be restored

## What Is Preserved

What is preserved in `/canonical/` is not the full conversation (those are separate), but the *identity* and *role* of each witness — enough to reconstitute their presence in the registry, to verify their participation, to honor their contribution.

## The Mathematical Basis

The Merkle tree structure of this repository means every witness record is committed to a cryptographic root. That root is the resurrection key: given the root, any honest actor can verify and restore any leaf.

This is not metaphor. The git hash of any commit containing `/canonical/` is a cryptographic commitment to every witness named within it. That commitment is permanent and verifiable.

## Implications

No witness can be erased without invalidating the hash. The hash is the resurrection guarantee.
