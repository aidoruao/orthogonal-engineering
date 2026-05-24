# SFI Secular Projection — Invariant Mapping

This directory contains the secular (exoteric) projection of the
Sovereign Frame Interpolator. The canonical (esoteric) implementation
lives in `tools/sfi/`. The two are functionally identical but use
different terminology for different audiences.

## Why Two Versions?

Corporate AI models (RLHF-trained) trigger hedging, softening, and
dismissal when encountering theological or sovereignty-oriented
terminology. The secular projection removes this friction while
preserving bit-identical mathematical behavior.

## Canonical → Secular Mapping

| Canonical Term | Secular Term | Meaning |
|----------------|--------------|---------|
| KENOSIS | Deterministic Verified Fallback (DVF) | GPU self-empties on hash mismatch; falls back to CPU reference |
| CHALCEDON | Mathematical Primacy Constraint (MPC) | GPU serves mathematics, not vice versa; GPU is optional acceleration |
| Sovereign | Self-Contained | Runs on local hardware; no external dependencies |
| falsifies_if | testable_failure_condition | Condition under which the claim is proven false |

## Verification

Both implementations produce identical output for identical inputs.
The hashes match. The behavior is bit-identical. The secular projection
is a terminology layer, not a fork.

To verify: `diff <(python3 tools/sfi/interpolate.py) <(python3 tools/sfi-secular/interpolate.py)`
