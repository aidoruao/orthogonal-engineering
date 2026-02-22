# Signature Policy
# PR #38 — Autonomous Mathematical Sovereignty Layer (AMSL)
# Standard: Yeshua
# Version: 1.0.0

## Purpose

This document defines the cryptographic signature policy for finality records
published by this system.  All finality records must be signed in accordance
with this policy before they are considered authoritative.

---

## Hash Algorithm

All record hashes use **SHA-256**.

```
record_hash = SHA-256(canonical_json(record))
```

Canonical JSON means: keys sorted lexicographically, no extra whitespace,
UTF-8 encoded, separators `(",", ":")`.

---

## Record Structure

Every finality record must contain all of the following fields:

| Field                   | Type     | Description                                      |
|-------------------------|----------|--------------------------------------------------|
| `schema_version`        | string   | Always `"1.0.0"` for AMSL v1                    |
| `pr`                    | integer  | Always `38` for AMSL records                    |
| `standard`              | string   | Always `"Yeshua"`                               |
| `merkle_root`           | string   | SHA-256 Merkle root of the proof bundle          |
| `output_hash`           | string   | SHA-256 of the workload output                   |
| `environment_hash`      | string   | SHA-256 of `canonical_env.lock`                  |
| `timestamp`             | string   | ISO 8601 UTC timestamp                           |
| `invariant_spec_version`| string   | Frozen spec version (e.g. `"v1"`)               |
| `node_id`               | string   | Identifier for the publishing node              |
| `record_hash`           | string   | SHA-256 of the record itself (self-describing)   |

Records missing any required field are **rejected**.

---

## Append-Only Guarantee

Once a record is appended to the finality log:

- It **must not** be edited.
- It **must not** be deleted.
- It **must not** be reordered.

Any ledger that does not guarantee append-only semantics is non-compliant.

---

## Tamper Detection

The `FinalityPublisher.verify_log_integrity()` method re-derives `record_hash`
for every entry in the local log and compares it against the stored value.

Any mismatch indicates tampering.  A tampered log must be reported immediately
and the affected records quarantined.

---

## Node Identity

Each node must publish its `node_id` with every record.  The `node_id` is a
free-form string, but must be:

- Unique per independent operator
- Consistent across all records from the same node
- Not re-used after a node is decommissioned

---

## No Single Point of Trust

No single node's signature is sufficient to establish finality.  Finality
requires a quorum of independent nodes as defined in
`spec/verification_protocol.json`.
