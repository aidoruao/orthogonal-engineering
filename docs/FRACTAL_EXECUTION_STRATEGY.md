# Fractal Code Execution Strategy - 1B LOC Generation System

## Overview

This document explains the **1 Billion Lines of Code (1B LOC) Fractal Code Generation System** - a verifiable, deterministic system that can generate and audit >= 1,000,000,000 lines of code as an external artifact.

**Critical Clarification**: This repository does **NOT** contain 1 billion lines of code. Instead, it contains a **verifiable system** to generate and audit 1B LOC externally, with compact proofs stored in Git.

## What "1B LOC" Means Precisely

The "1B LOC" claim refers to:

1. **External Generation**: Code is generated to a local directory (`./out/` by default), which is **NOT** version-controlled
2. **Deterministic Pattern**: Given the same input parameters, the generator produces identical output
3. **Verifiable Manifest**: A compact JSONL manifest (stored in Git) contains:
   - Total LOC count
   - Total file count
   - SHA-256 hashes for verification
   - Configuration parameters
4. **Mathematical Precision**: LOC calculation follows exact formulas (see below)
5. **Reproducible**: Anyone can regenerate and verify the same output

## Architecture

The system follows a three-layer architecture:

### 1. Definition Layer (In Git)
Source code that defines:
- `TARGET_LOC = 1_000_000_000` (target lines of code)
- `LINES_PER_FILE = 1000` (lines per generated file)
- `FILES_PER_BATCH = 10_000` (files per batch directory)
- Fractal pattern logic
- Integrity checks and hashing

**Files**:
- `tools/generate_fractal_code.py` - Generator script
- `tools/verify_fractal_manifest.py` - Verification/audit script
- Configuration constants in generator code

### 2. Expansion Layer (Runtime, Not in Git)
When executed, the generator:
- Creates batch directories under `./out/batch_NNNNNN/`
- Generates Python files `shard_NNNNNN.py` with fractal patterns
- Writes files to disk (not committed to Git)
- Stops when total LOC >= TARGET_LOC

**Output Structure**:
```
./out/
├── batch_000000/
│   ├── shard_000000.py
│   ├── shard_000001.py
│   ├── ...
│   └── shard_009999.py
├── batch_000001/
│   └── ...
├── ...
└── fractal_manifest.jsonl
```

### 3. Proof Layer (In Git)
A compact manifest containing:
- Run metadata (ID, timestamp, git commit SHA)
- Configuration (target LOC, lines per file, etc.)
- Results (actual LOC, total files, total batches)
- Per-batch metadata (file count, LOC count, SHA-256 hash)

**Manifest Format**: JSONL (one JSON object per line)

## Mathematical Formulas

### LOC Calculation

```
LOC_PER_FILE = LINES_PER_FILE
LOC_PER_BATCH = FILES_PER_BATCH × LOC_PER_FILE
NUM_BATCHES = ⌈TARGET_LOC / LOC_PER_BATCH⌉
```

**Example** (default configuration):
- `LINES_PER_FILE = 1000`
- `FILES_PER_BATCH = 10,000`
- `TARGET_LOC = 1,000,000,000`

Calculations:
- `LOC_PER_BATCH = 10,000 × 1,000 = 10,000,000`
- `NUM_BATCHES = ⌈1,000,000,000 / 10,000,000⌉ = 100`

Result: **100 batches**, **1,000,000 files**, **1,000,000,000 lines**

### Storage Requirements

**Generated Files** (not in Git):
- ~1,000,000 files × ~1 KB/file ≈ **1 GB** disk space
- Actual size depends on `LINES_PER_FILE` and content density

**Manifest** (in Git):
- Header: ~1 KB
- Per-batch entries: ~200 bytes × 100 = 20 KB
- Total: ~**25 KB** (compact proof)

## Usage

### Running the Generator

#### Small Test Run (10,000 LOC)
```bash
python tools/generate_fractal_code.py \
  --target-loc 10000 \
  --output-root ./out \
  --manifest ./out/fractal_manifest.jsonl \
  --apply
```

#### Medium Test Run (1,000,000 LOC)
```bash
python tools/generate_fractal_code.py \
  --target-loc 1000000 \
  --output-root ./out \
  --manifest ./out/fractal_manifest.jsonl \
  --apply
```

#### Full 1B LOC Run
```bash
python tools/generate_fractal_code.py \
  --target-loc 1000000000 \
  --output-root ./out \
  --manifest ./out/fractal_manifest.jsonl \
  --apply
```

**Note**: The full 1B LOC run may take several minutes to hours depending on disk speed.

### Dry-Run Mode (Default)

By default, the generator runs in **dry-run mode** (no files written):

```bash
# Shows what would be generated without writing files
python tools/generate_fractal_code.py --target-loc 10000
```

Use `--apply` to actually generate files.

### CLI Options

#### Generator (`generate_fractal_code.py`)

```
--target-loc INT         Target lines of code (default: 1,000,000,000)
--lines-per-file INT     Lines per generated file (default: 1000)
--files-per-batch INT    Files per batch directory (default: 10,000)
--output-root PATH       Root directory for output (default: ./out)
--manifest PATH          Path to manifest file (default: ./out/fractal_manifest.jsonl)
--seed INT               Random seed for determinism (default: 42)
--apply                  Actually generate files (default: dry-run)
```

#### Verifier (`verify_fractal_manifest.py`)

```
manifest                 Path to manifest JSONL file (required)
--verbose, -v            Enable verbose output
```

### Verifying a Run

After generation, verify the manifest:

```bash
python tools/verify_fractal_manifest.py ./out/fractal_manifest.jsonl
```

**Expected Output**:
```
=== Fractal Manifest Verifier ===
Manifest: ./out/fractal_manifest.jsonl

Run ID: a1b2c3d4-...
Timestamp: 2026-02-17T...
Expected LOC: 10,000
Expected Files: 10
Expected Batches: 1

Output root: ./out
Verifying 1 batches...

=== Verification Results ===
✓ Total LOC verified: 10,000
✓ Total files verified: 10
✓ Total batches verified: 1

✅ VERIFICATION PASSED
   All 10 files totaling 10,000 LOC verified successfully
```

**Exit Codes**:
- `0`: Verification passed
- `1`: Verification failed (mismatch detected)
- `2`: Error during verification

## Fractal Pattern

The generated code follows a deterministic fractal pattern:

1. **Header Comments**: 2 lines identifying batch/shard and seed
2. **Function Definitions**: Parametric functions with deterministic names and logic
3. **Variable Assignments**: Padding variables to reach exact line count

**Example Generated File** (`shard_000000.py` from `batch_000000`):
```python
# Fractal Shard 000000_000000
# Generated deterministically with seed=42

def fractal_0_0_0(x, y=294, z=259):
    """Fractal function 0 in batch 0, shard 0."""
    a = x * 294 + y
    b = y * 259 + z
    c = (a + b) % 1000
    d = (a * b) % 500
    result = c + d
    return result

def fractal_0_0_1(x, y=294, z=259):
    """Fractal function 1 in batch 0, shard 0."""
    ...
```

**Determinism**:
- Same `seed`, `batch_index`, `shard_index` → identical output
- Parameters derived from: `(shard_index × 7 + batch_index × 13 + seed) % 1000`

## Performance and Storage

### Generation Speed
- **Expected**: 100,000 - 1,000,000 LOC/second (depends on disk I/O)
- **1B LOC**: Estimated 15-60 minutes on typical hardware

### Disk Space
- **Generated files**: ~1 GB for 1B LOC (1000 lines/file)
- **Manifest**: ~25 KB (compact)

### Memory Usage
- **Generator**: < 100 MB (streaming writes)
- **Verifier**: < 100 MB (batch-by-batch scanning)

## Determinism and Reproducibility

### Guaranteed Properties

Given the same parameters, the generator produces:
1. **Identical content**: Same file contents, byte-for-byte
2. **Identical hashes**: Same SHA-256 checksums
3. **Identical counts**: Same LOC, file, and batch counts

### Parameters Affecting Output
- `--target-loc`: Changes total LOC and batch count
- `--lines-per-file`: Changes LOC per file
- `--files-per-batch`: Changes files per batch (but not total LOC)
- `--seed`: Changes fractal parameters (but not counts)

### Verification of Determinism

To verify determinism:

1. Generate twice with same parameters:
   ```bash
   python tools/generate_fractal_code.py --target-loc 10000 --seed 42 --output-root ./out1 --manifest ./out1/manifest.jsonl --apply
   python tools/generate_fractal_code.py --target-loc 10000 --seed 42 --output-root ./out2 --manifest ./out2/manifest.jsonl --apply
   ```

2. Compare manifests:
   ```bash
   diff ./out1/manifest.jsonl ./out2/manifest.jsonl
   # Should show no differences except timestamps and run IDs
   ```

3. Compare file hashes:
   ```bash
   python tools/verify_fractal_manifest.py ./out1/manifest.jsonl
   python tools/verify_fractal_manifest.py ./out2/manifest.jsonl
   # Both should pass with identical hash values
   ```

## Truthfulness and Accuracy

This system adheres to **Yeshua's standards of truthfulness**:

1. **No Deception**: The repository **does not** contain 1B LOC; it contains a **system to generate** 1B LOC
2. **Verifiable Claims**: All claims are backed by:
   - Manifest with hard counts
   - SHA-256 hashes
   - Reproducible generation
3. **Mathematical Precision**: LOC counts follow exact formulas (no approximations)
4. **Audit Trail**: Every run produces a manifest with:
   - Git commit SHA (generator version)
   - Timestamp
   - Configuration
   - Results
5. **Explicit Documentation**: This document and code comments clearly state what "1B LOC" means

### What This System Does NOT Claim

- ❌ The repository contains 1B LOC
- ❌ The generated code has practical utility
- ❌ The generated code is "real software"
- ❌ The 1B LOC is stored in Git

### What This System DOES Claim

- ✓ The system can **generate** 1B LOC as an external artifact
- ✓ The generation is **deterministic** and **reproducible**
- ✓ The output is **verifiable** via manifest and hashes
- ✓ The claim is **mathematically precise** and **auditable**

## Safety and Repository Hygiene

### .gitignore Rules

The following patterns are ignored to prevent accidentally committing generated files:

```gitignore
# Fractal code generation outputs (external artifacts, not in Git)
/out/
/generated/
fractal_manifest.jsonl
*.tar
*.tar.gz
*.zip
```

### Best Practices

1. **Never commit generated files**: Use `git status` before committing
2. **Commit manifests**: Small manifest files can be committed for proof
3. **Use dry-run first**: Always test with dry-run before `--apply`
4. **Start small**: Test with 10K or 100K LOC before attempting 1B LOC
5. **Check disk space**: Ensure adequate space before large runs

## Example Workflows

### Workflow 1: Quick Verification (10K LOC)

```bash
# Generate
python tools/generate_fractal_code.py --target-loc 10000 --apply

# Verify
python tools/verify_fractal_manifest.py ./out/fractal_manifest.jsonl

# Clean up
rm -rf ./out/
```

### Workflow 2: 1B LOC with Manifest Proof

```bash
# Generate (may take 15-60 minutes)
python tools/generate_fractal_code.py \
  --target-loc 1000000000 \
  --manifest ./proofs/1B_LOC_manifest.jsonl \
  --apply

# Verify
python tools/verify_fractal_manifest.py ./proofs/1B_LOC_manifest.jsonl

# Commit manifest (not generated files)
git add ./proofs/1B_LOC_manifest.jsonl
git commit -m "Add 1B LOC generation manifest proof"

# Clean up generated files (optional)
rm -rf ./out/
```

### Workflow 3: Reproducibility Test

```bash
# Run 1
python tools/generate_fractal_code.py --target-loc 10000 --seed 42 --output-root ./test1 --manifest ./test1/manifest.jsonl --apply

# Run 2 (same parameters)
python tools/generate_fractal_code.py --target-loc 10000 --seed 42 --output-root ./test2 --manifest ./test2/manifest.jsonl --apply

# Compare hashes (should match)
python tools/verify_fractal_manifest.py ./test1/manifest.jsonl
python tools/verify_fractal_manifest.py ./test2/manifest.jsonl

# Clean up
rm -rf ./test1 ./test2
```

## Troubleshooting

### Generator Runs Slowly
- **Cause**: Disk I/O bottleneck
- **Solution**: Use faster disk (SSD), reduce `target-loc`, or increase `lines-per-file`

### Verification Fails
- **Cause**: File corruption, incomplete generation, or manual file edits
- **Solution**: Regenerate with same parameters or investigate specific batch errors

### Out of Disk Space
- **Cause**: Insufficient disk space for target LOC
- **Solution**: Reduce `target-loc` or free up disk space

### Manifest Not Found
- **Cause**: Generator did not complete or manifest path incorrect
- **Solution**: Check generator output for errors, ensure `--apply` was used

## Future Enhancements

Potential improvements (not currently implemented):

- Compression support for generated files (`.tar.gz`)
- Parallel batch generation for faster runs
- Optional per-file manifest entries (currently batch-level only)
- Progress checkpointing for resumable generation
- Alternative output formats (JSON, C, Java, etc.)

## References

- Generator: `tools/generate_fractal_code.py`
- Verifier: `tools/verify_fractal_manifest.py`
- Tests: `tests/test_fractal_generator.py`
- Repository: `github.com/aidoruao/orthogonal-engineering`

---

**Last Updated**: 2026-02-17  
**Version**: 1.0.0
