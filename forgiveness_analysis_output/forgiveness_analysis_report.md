---
tags: [forgiveness-analysis-output, forgiveness-analysis-report]
register: documentation
---

# Forgiveness Analysis — Report

This file is the canonical landing page for the `forgiveness_analysis_output/`
artifact bundle. The bundle is regenerated whenever a forgiveness-class
invariant (see `kernel/commonwealth/` and `pr47_stewardship/`) is re-run
against a new witness set; each regeneration appends a dated section below
and leaves all prior sections in place (append-only, per the Stewardship
behavioural constraint).

## Contents

- `README.md` — high-level human-readable pointer (this file).
- `*.jsonl` — machine-readable witness streams keyed by run timestamp.
- `*.proof.json` — ProofObject exports for every forgiveness-class check
  executed during a run.

## Reading order

1. Start with the most recent dated section below (top-first when present).
2. Open the matching `*.jsonl` stream for the run to inspect the individual
   ProofObjects.
3. Cross-reference against `pr47_stewardship/witness/consent_log.jsonl` to
   verify the run was authorised.

## Current state

No forgiveness-class runs have been materialised in this working tree yet;
the frontmatter block above is sufficient to satisfy the repository-wide
YAML frontmatter invariant while the bundle is empty.
