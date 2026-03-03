# CI Preflight — Workflow Coverage Check

Use this lightweight preflight to see exactly which workflow files will be
validated in CI before opening or updating a PR.

```bash
# From repo root
python scripts/ci_preflight.py

# JSON output if you want to diff against a baseline
python scripts/ci_preflight.py --json > /tmp/workflows.json
```

The preflight enumerates:

- GitHub Actions workflows under `.github/workflows/`
- Auxiliary workflow specs under `workflows/`

It prints the total count, relative paths, and SHA-256 hash for each file, so
you can compare the set against the expected workflow inventory. If the set
changes (added/removed/renamed workflows), update any downstream baselines
that pin workflow paths or hashes before merging. This avoids surprises in the
full CI run (e.g., compare-roots, deterministic/Merkle checks, or hash-based
guards).
