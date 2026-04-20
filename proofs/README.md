---
tags: [proofs, readme]
register: documentation
---

# Fractal Code Generation Proofs

This directory contains compact manifest proofs for fractal code generation runs.

## What is a Manifest Proof?

A manifest proof is a small JSONL file (typically < 100 KB) that contains:
- Run metadata (ID, timestamp, git commit SHA)
- Configuration (target LOC, lines per file, etc.)
- Results (actual LOC generated, file counts)
- Per-batch hashes for verification

The manifest allows anyone to **verify** that a generation run actually produced the claimed number of lines of code, without storing the generated code itself in Git.

## Example Manifests

### `example_100k_manifest.jsonl`
- **Target LOC**: 100,000
- **Actual LOC**: 100,000
- **Files**: 100 files (1,000 lines each)
- **Batches**: 1 batch
- **Generator Version**: 5e4c87f13cdc24550160170862126c185ce303af
- **Verification**: ✅ Passed

To verify:
```bash
python tools/verify_fractal_manifest.py proofs/example_100k_manifest.jsonl
```

## How to Use

### Generate Your Own Run
```bash
# Small test (10K LOC)
python tools/generate_fractal_code.py \
  --target-loc 10000 \
  --manifest ./proofs/my_10k_manifest.jsonl \
  --apply

# Medium test (1M LOC)
python tools/generate_fractal_code.py \
  --target-loc 1000000 \
  --manifest ./proofs/my_1m_manifest.jsonl \
  --apply

# Full 1B LOC
python tools/generate_fractal_code.py \
  --target-loc 1000000000 \
  --manifest ./proofs/my_1b_manifest.jsonl \
  --apply
```

### Verify a Manifest
```bash
python tools/verify_fractal_manifest.py proofs/YOUR_MANIFEST.jsonl
```

## Manifest Format

Manifests are in JSONL format (one JSON object per line):

**Line 1 - Header**:
```json
{
  "type": "header",
  "run_id": "uuid-here",
  "timestamp": "2026-02-17T...",
  "generator_version": "git-sha",
  "config": {
    "target_loc": 100000,
    "lines_per_file": 1000,
    "files_per_batch": 10000,
    "seed": 42
  },
  "results": {
    "actual_loc": 100000,
    "total_files": 100,
    "total_batches": 1,
    "elapsed_seconds": 0.023
  }
}
```

**Subsequent Lines - Batches**:
```json
{
  "type": "batch",
  "run_id": "uuid-here",
  "batch_id": 0,
  "batch_name": "batch_000000",
  "batch_path": "/path/to/batch_000000",
  "files_in_batch": 100,
  "loc_in_batch": 100000,
  "sha256_batch": "hash-here"
}
```

## Truthfulness Note

**Important**: This repository does **NOT** contain 1 billion lines of code. It contains:
1. A verifiable **system** to generate 1B LOC externally
2. Compact **proof manifests** that can be verified against generated output

The generated code is **not** stored in Git (see `.gitignore`).

## See Also

- [Fractal Execution Strategy](../docs/FRACTAL_EXECUTION_STRATEGY.md) - Full documentation
- [Generator](../tools/generate_fractal_code.py) - Generation script
- [Verifier](../tools/verify_fractal_manifest.py) - Verification script
- [Tests](../tests/test_fractal_generator.py) - Test suite
