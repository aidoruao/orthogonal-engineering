# Minimal Node Bootstrap
# PR #38 — Autonomous Mathematical Sovereignty Layer (AMSL)
# Standard: Yeshua
# Version: 1.0.0

## Purpose

This document describes the minimal steps required to bootstrap an independent
verification node.  No dependency on the primary repository host, CI provider,
or any single hardware vendor is assumed.

---

## Prerequisites

- Linux, macOS, or Windows with WSL2
- Python 3.11 or 3.12 (see `bootstrap/toolchain.lock` for exact pins)
- Git
- No GPU or special hardware required

---

## Step 1 — Obtain the Source

```bash
# From the primary mirror (or any independent mirror)
git clone <mirror-url> orthogonal-engineering
cd orthogonal-engineering

# Verify the repository hash against a trusted anchor
git log --format='%H %s' | head -1
```

---

## Step 2 — Pin the Toolchain

```bash
# Read the exact toolchain requirements
cat bootstrap/toolchain.lock

# Install exactly the pinned Python version
python3 --version        # must match toolchain.lock

# Install pinned dependencies (all hashes locked)
pip install --require-hashes -r requirements-locked.txt 2>/dev/null || pip install pytest
```

---

## Step 3 — Build the Pure Runtime

```bash
# Compile C reference runtime (optional — Python cross-validator is sufficient)
cd yeshua_math/pure_reference_runtime
gcc -O0 -std=c11 -o arithmetic_core arithmetic_core.c
gcc -O0 -std=c11 -o logic_engine logic_engine.c
cd ../..
```

---

## Step 4 — Run All Invariant Checks

```bash
# Peano arithmetic reducibility
python yeshua_math/peano_invariant_checker.py

# Boolean purity
python yeshua_math/boolean_purity_validator.py

# Cross-validation (Python vs C reference)
python yeshua_math/pure_reference_runtime/cross_validator.py

# Full test suite
python -m pytest tests/ -v
```

---

## Step 5 — Publish Your Proof Bundle

After verification, publish your node's proof bundle so that the quorum is
updated.  See `finality/finality_publisher.py` for the standard publication
interface.

```bash
python finality/finality_publisher.py --node-id <your-node-id>
```

---

## Node Diversity Mandate

Your node contributes to the quorum only if it is:

- Geographically independent (different region from other nodes)
- Hardware-independent (different vendor from other nodes)
- Maintainer-independent (different operator from other nodes)

See `spec/verification_protocol.json` for the full quorum specification.
