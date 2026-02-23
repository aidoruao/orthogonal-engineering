<!-- AGENT_FEED.md — append-only state witness ledger (PR #40) -->
<!-- Do not edit existing rows. Append new rows only. -->

# AGENT_FEED — State Witness Ledger

Cryptographically anchored, append-only record of freeze-state observations.
Each row is linked to the previous via `prev_entry_hash` (SHA-256 chain).

Source: `resilience/invariant_spec_v2.freeze` (PR #39 canonical freeze)
Script: `tools/state_witness/generate_feed_entry.py`

| timestamp | freeze_hash | merkle_root | invariant_spec_version | source_paths | commit_sha | prev_entry_hash | entry_hash |
| --- | --- | --- | --- | --- | --- | --- | --- |
