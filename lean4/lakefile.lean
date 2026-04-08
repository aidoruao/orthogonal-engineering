-- Lean4 project for formal verification of SAL Types 3-9
-- This is a BRIDGE: Python implementations are the source of truth,
-- Lean4 proofs verify the mathematical claims.

import Lake
open Lake DSL

package «SAL» where
  -- Settings applied to both builds and interactive editing
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩, -- pretty-prints `fun a ↦ b`
    ⟨`pp.proofs.withType, false⟩
  ]
  -- add any package configuration options here

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

@[default_target]
lean_lib «SAL» where
  -- add any library configuration options here

lean_lib «Axioms» where
  -- Axiom formalizations
