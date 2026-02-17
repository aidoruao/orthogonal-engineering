# Canonicalization Examples

This directory contains example configurations and usage patterns for the canonicalization and Merkle tree tools.

## Configuration Files

### canon_config.json

Example configuration for GTA handling.meta clamp pipeline. Defines rules for clamping vehicle parameters to safe ranges.

Usage:
```bash
python -m toolkit.oe.canon_cli handling-clamp handling.meta --config examples/canon_config.json
```

## Quick Start Examples

### 1. Index a Repository

Generate a manifest of all files in a repository:

```bash
python -m toolkit.oe.canon_cli index /path/to/repo \
    --output-dir ./canon_output \
    --exclude ".git,__pycache__,*.pyc"
```

### 2. Build Merkle Tree

Build a Merkle tree from a manifest:

```bash
python -m toolkit.oe.canon_cli merkle /path/to/repo \
    --output-dir ./canon_output \
    --manifest ./canon_output/manifest.jsonl
```

### 3. Verify Files

Verify file hashes against a manifest:

```bash
python -m toolkit.oe.canon_cli verify /path/to/repo \
    --manifest ./canon_output/manifest.jsonl \
    --output-dir ./logs
```

### 4. Process handling.meta (Dry Run)

Preview changes to a handling.meta file:

```bash
python -m toolkit.oe.canon_cli dry-run handling.meta \
    --config examples/canon_config.json \
    --output-dir ./logs
```

### 5. Apply Clamps to handling.meta

Apply clamps with automatic backup:

```bash
python -m toolkit.oe.canon_cli handling-clamp handling.meta \
    --config examples/canon_config.json \
    --output-dir ./logs
```

### 6. Restore from Backup

Restore a handling.meta file from backup:

```bash
python -m toolkit.oe.canon_cli restore handling.meta
```

## Python API Examples

See `docs/CANONICALIZATION_GUIDE.md` for detailed Python API examples.
# Merkle-Rooted Pipeline Examples

This directory contains examples demonstrating how to use the deterministic Merkle-rooted pipeline scaffold.

## Examples

### 1. Basic Merkle Pipeline (`merkle_pipeline_example.py`)

Demonstrates the complete workflow:
- Generate a manifest for a directory
- Build a Merkle tree from the manifest
- Export inclusion proofs
- Verify proofs

**Usage:**
```bash
python examples/merkle_pipeline_example.py
```

**Output:**
- `output/manifest.jsonl` - File manifest with hashes
- `output/merkle_root.txt` - Merkle tree root hash
- `output/merkle_proofs.jsonl` - Inclusion proofs for all files
- `logs/example_pipeline.jsonl` - Execution log

### 2. Canonicalizer Example (`canonicalizer_example.py`)

Shows how canonical byte representations ensure deterministic hashing across different file formats:
- Text files with different line endings produce the same hash
- JSON files with different formatting produce the same hash
- XML files with different attribute order produce the same hash
- Binary files are unchanged

**Usage:**
```bash
python examples/canonicalizer_example.py
```

## CLI Usage

The toolkit provides a CLI for the complete pipeline:

### Index Repository

```bash
python -m toolkit.oe.cli index --repo /path/to/repo --out output --apply
```

Generates `manifest.jsonl` with canonical hashes for all files.

### Build Merkle Tree

```bash
python -m toolkit.oe.cli merkle --manifest output/manifest.jsonl --out output --apply
```

Builds Merkle tree and generates:
- `merkle_root.txt` - Root hash
- `merkle_proofs.jsonl` - Inclusion proofs

### Verify Proofs

```bash
python -m toolkit.oe.cli verify-merkle --out output
```

Verifies all inclusion proofs against the root hash.

### Parse Handling File

```bash
python -m toolkit.oe.cli handling-clamp --handling-path file.meta --out output --apply
```

Parses GTA handling.meta files and outputs JSON.

### Backup/Restore

```bash
# Create backup
python -m toolkit.oe.cli backup --out output

# List backups and restore
python -m toolkit.oe.cli restore
```

## Dry-Run Mode

By default, all commands run in dry-run mode. Use `--apply` to actually write files:

```bash
# Dry-run (shows what would happen)
python -m toolkit.oe.cli index --repo .

# Actually write files
python -m toolkit.oe.cli index --repo . --apply
```

## Module Documentation

### Canonicalizer (`toolkit/oe/canonicalizer.py`)

Provides deterministic canonical byte representation:
- **Text files**: UTF-8 no BOM, LF line endings, NFC Unicode normalization
- **JSON files**: Sorted keys, compact format, UTF-8
- **XML files**: Canonical XML (C14N) with sorted attributes
- **Binary files**: Raw bytes unchanged

### Hasher (`toolkit/oe/hasher.py`)

SHA-256 hashing utilities:
- `compute_sha256(data)` - Hash bytes
- `hash_file(path)` - Hash a file
- `hash_bytes_chunked(path)` - Memory-efficient chunked hashing
- Optional HMAC support

### Merkle (`toolkit/oe/merkle.py`)

Binary Merkle tree implementation:
- Leaf nodes: `SHA-256(0x00 || canonical_bytes_hash)`
- Internal nodes: `SHA-256(0x01 || left_hash || right_hash)`
- Leaves ordered by path (UTF-8 lexicographic)
- Inclusion proof generation and verification

### Manifest (`toolkit/oe/manifest.py`)

Streaming manifest generation:
- JSONL format with path, type, hash, size, content-address
- Checkpoint support for restartable runs
- Large repository support

### Logger (`toolkit/oe/logger.py`)

JSONL structured logging:
- Monotonic step IDs
- ISO8601 UTC timestamps
- Event types: start, complete, error, progress

### Handling Pipeline (`toolkit/oe/handling_pipeline.py`)

GTA handling.meta parser:
- Parses XML vehicle handling data
- Validates required properties
- Exports to JSON

## Testing

Run all tests:

```bash
pytest tests/test_canonicalizer.py -v
pytest tests/test_hasher.py -v
pytest tests/test_merkle.py -v
```

## Architecture

The pipeline follows this flow:

```
Repository Files
    ↓
Canonicalizer (normalize content)
    ↓
Hasher (SHA-256)
    ↓
Manifest (JSONL with hashes)
    ↓
Merkle Tree Builder
    ↓
Root Hash + Inclusion Proofs
    ↓
Verification
```

All steps are:
- **Deterministic**: Same input always produces same output
- **Resumable**: Checkpointing allows restart after failures
- **Logged**: All operations logged to JSONL
- **Verifiable**: Inclusion proofs allow verification
