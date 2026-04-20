---
tags: [dvcl, cross-node-protocol]
register: documentation
---

# Cross-Node Verification Protocol (CNVP)
# PR #37 — Distributed Verifiable Compute Layer
# Standard: Yeshua
# Version: 1.0.0

## Purpose

Every workload must be independently re-executed by at least one additional
node before its output is trusted.  Hash divergence is never tolerated.

## Protocol Steps

1. **Node A** executes the workload under the deterministic execution spec.
2. **Node A** generates a proof bundle:
   - `input.hash` — SHA-256 of canonical serialised input
   - `env.hash` — SHA-256 of `canonical_env.lock`
   - `trace.hash` — SHA-256 of the deterministic execution trace
   - `output.hash` — SHA-256 of canonical serialised output
   - `merkle_root.hash` — Merkle root over all four hashes
   - `verification.json` — Structured verification report
3. **Node B** receives the proof bundle and re-executes the workload
   independently using the same `execution_spec.yaml` and `canonical_env.lock`.
4. **Node B** recomputes:
   - `output.hash`
   - `trace.hash`
   - `merkle_root.hash`
5. **Verification**: Node B compares its computed hashes to Node A's bundle.
   - If identical → workload is **verified**.
   - If any hash diverges → workload is **rejected**; delta is logged.
6. **Merge gate**: CI blocks merge until at least 2 independent nodes agree.

## Divergence Handling

On divergence:
- Record the delta between Node A and Node B outputs.
- Log divergence to `dvcl/divergence_log.jsonl`.
- Reject the proof bundle.
- Trigger root-cause investigation before re-submission.

## Minimum Node Requirements

- Minimum: 2 independent nodes required before merge.
- Nodes must run on distinct hardware to satisfy the cross-platform invariant.
- The pure-path node must run on a commodity CPU (no accelerators).

## Invariants

- A node may NOT trust its own output without cross-node verification.
- Speed is irrelevant; only hash agreement determines validity.
- The pure-path result is the authoritative reference.
