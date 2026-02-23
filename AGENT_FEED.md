<!-- AGENT_FEED.md — append-only state witness ledger (PR #40) -->
<!-- Do not edit existing rows. Append new rows only. -->

# AGENT_FEED — State Witness Ledger

Cryptographically anchored, append-only record of freeze-state observations.
Each row is linked to the previous via `prev_entry_hash` (SHA-256 chain).

Source: `resilience/invariant_spec_v2.freeze` (PR #39 canonical freeze)
Script: `tools/state_witness/generate_feed_entry.py`

| timestamp | freeze_hash | merkle_root | invariant_spec_version | source_paths | commit_sha | prev_entry_hash | entry_hash |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-02-23T16:51:21Z | 29555e2eb3156c467a1735a5e294928e00e728f0ee5f21273e6db36f44d53972 | 455d56607b97359c9e35ba9b9fb03f84cd398ae05710367999c747c59bf83914 | v2 | spec/arithmetic_axioms.json,spec/boolean_axioms.json,spec/peano_axioms.json | eff2bc97ff8bf6638f05497622ae66908cf17f78 |  | ff84b689f6c910cf6887b1ba26ab30d34ebc7e0b109ab904aedb52a6bed52774 |
| 2026-02-23T17:18:04Z | 29555e2eb3156c467a1735a5e294928e00e728f0ee5f21273e6db36f44d53972 | 455d56607b97359c9e35ba9b9fb03f84cd398ae05710367999c747c59bf83914 | v2 | spec/arithmetic_axioms.json,spec/boolean_axioms.json,spec/peano_axioms.json | 2bea72fbc771f752ced1b581b3ceaa60909ee2f6 | ff84b689f6c910cf6887b1ba26ab30d34ebc7e0b109ab904aedb52a6bed52774 | c0a67bb8804157ecbe741ea013880397ad27d8acd52a3656e2ec9003756b936b |
| 2026-02-23T19:53:30Z | 29555e2eb3156c467a1735a5e294928e00e728f0ee5f21273e6db36f44d53972 | 455d56607b97359c9e35ba9b9fb03f84cd398ae05710367999c747c59bf83914 | v2 | spec/arithmetic_axioms.json,spec/boolean_axioms.json,spec/peano_axioms.json | cd40ad8838dbab62dc192f1e4fa992808390781f | c0a67bb8804157ecbe741ea013880397ad27d8acd52a3656e2ec9003756b936b | e99bc7b0f27a86aec8c10b1cb43b8451ae862b2833bfde91bd809a819c1908f4 |
