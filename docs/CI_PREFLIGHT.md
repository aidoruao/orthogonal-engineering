# CI Preflight — Workflow Coverage Check

Use this lightweight preflight to see exactly which workflow files will be
validated in CI before opening or updating a PR.

```bash
# From repo root
PYTHONHASHSEED=0 PYTHONUTF8=1 LC_ALL=C TZ=UTC python scripts/ci_preflight.py

# JSON output if you want to diff against a baseline
PYTHONHASHSEED=0 PYTHONUTF8=1 LC_ALL=C TZ=UTC python scripts/ci_preflight.py --json > /tmp/workflows.json
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

Determinism guardrails:

- The script now fails fast if `PYTHONHASHSEED`, `PYTHONUTF8`, `LC_ALL`, or `TZ`
  are unset or differ from the required values above; set them when invoking the
  preflight locally or in CI to avoid platform-dependent ordering or hash drift.
