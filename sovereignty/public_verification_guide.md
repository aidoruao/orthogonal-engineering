# Public Verification Guide
# PR #38 — Autonomous Mathematical Sovereignty Layer (AMSL)
# Standard: Yeshua
# Version: 1.0.0

## Overview

This guide enables any external party to independently verify all mathematical
invariants and proof bundles produced by this system.  No privileged channel
is required.  No special hardware is required.

---

## Step 1 — Download the Specification

The invariant specification is available at `/spec/` in this repository:

```
spec/invariant_schema.json        — top-level frozen spec
spec/arithmetic_axioms.json       — Peano arithmetic axioms
spec/boolean_axioms.json          — Boolean algebra axioms
spec/verification_protocol.json   — MIVN quorum and merge gates
```

The spec is machine-readable and version-locked.  `frozen: true` means the
version cannot change without a supermajority quorum.

---

## Step 2 — Rebuild the Pure Runtime

```bash
# Pin the toolchain exactly as specified
cat bootstrap/toolchain.lock

# Build the reproducible runtime
bash bootstrap/reproducible_build.yml   # or follow the steps manually

# Verify binary hashes match the manifest
python - <<'EOF'
import hashlib, json, pathlib

manifest = json.loads(pathlib.Path('bootstrap/binary_hash_manifest.json').read_text())
for entry in manifest['binaries']:
    path = pathlib.Path(entry['path'])
    if not path.exists():
        print(f'MISSING: {path}')
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = entry['sha256']
    status = 'OK' if actual == expected else 'MISMATCH'
    print(f'{status}: {path}  expected={expected}  actual={actual}')
EOF
```

Binary hash mismatch means the build is not reproducible and must be rejected.

---

## Step 3 — Reproduce the Workload

```bash
# Execute the canonical workload with a fixed seed
PYTHONHASHSEED=38 python yeshua_math/pure_reference_runtime/cross_validator.py

# Run Peano invariant checker
python yeshua_math/peano_invariant_checker.py

# Run Boolean purity validator
python yeshua_math/boolean_purity_validator.py
```

---

## Step 4 — Compare Hashes

Compare the output hashes you computed against the proof bundle published in
`/finality/`.

```bash
python - <<'EOF'
import hashlib, json, pathlib, sys

proof = json.loads(pathlib.Path('finality/latest_proof.json').read_text())
print('Published proof bundle:')
for k, v in proof.items():
    print(f'  {k}: {v}')
EOF
```

If all hashes match the published finality anchor, the workload is verified.

---

## Quorum Requirements

Per `spec/verification_protocol.json`, a valid verification quorum requires:

- 3+ independent geographic regions
- 3+ independent hardware vendors
- 3+ independent maintainers

Verification results from a single node are insufficient for merge.

---

## No Privileged Channel

There is no privileged verification channel.  Every step above is public.
Any independent node can reconstruct and verify the full system from:

1. This specification
2. The pure runtime source (`yeshua_math/pure_reference_runtime/`)
3. The proof bundle archives (`resilience/proof_archive_schema.json`)
4. The public finality ledger
