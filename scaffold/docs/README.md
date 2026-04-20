---
tags: [scaffold, docs, readme]
register: documentation
---

# Deterministic Auditable Python Scaffold

A local-run, dry-run-default scaffold for auditable file processing with mandatory backups, canonical byte representation, Merkle tree verification, and JSONL logging.

## Overview

This scaffold provides a deterministic and auditable system for processing files with the following key features:

- **Canonical Byte Representation**: Ensures consistent, reproducible byte sequences for files across platforms
- **SHA-256 Hashing**: Cryptographic hashing of canonical bytes
- **Merkle Tree Construction**: Build verifiable Merkle trees with inclusion proofs
- **JSONL Logging**: Structured logging with monotonic step IDs and ISO8601 timestamps
- **Manifest Generation**: Create and verify file manifests with checkpointing
- **Dry-Run Mode**: Default to dry-run with explicit `--apply` flag required for modifications
- **Mandatory Backups**: Automatic backup creation before modifications

## Installation

The scaffold is part of the orthogonal-engineering repository. No additional installation is required beyond the base requirements.

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command Line Interface

The scaffold provides a CLI with several subcommands:

```bash
# Generate manifest (dry-run mode by default)
python -m scaffold.cli index

# Generate manifest and apply changes
python -m scaffold.cli index --apply

# Build Merkle tree
python -m scaffold.cli merkle --apply

# Verify manifest and proofs
python -m scaffold.cli verify

# Create backup
python -m scaffold.cli backup

# Restore from backup
python -m scaffold.cli restore --backup .scaffold_backups/20260216_120000

# Process GTA handling.meta files
python -m scaffold.cli handling-clamp --input ./data --apply
```

### Python API

```python
from scaffold import (
    canonical_byte_representation,
    compute_file_hash,
    ScaffoldLogger,
    ManifestGenerator,
    MerkleTree
)

# Get canonical bytes
canonical_bytes = canonical_byte_representation("file.txt")

# Compute hash
file_hash = compute_file_hash("file.txt", use_canonical=True)

# Initialize logger
logger = ScaffoldLogger()
logger.log_handling_step("process", {"file": "test.txt"})

# Generate manifest
gen = ManifestGenerator("/path/to/repo")
gen.generate()

# Build Merkle tree
tree = MerkleTree()
tree.add_file("file.txt")
tree.build()
root_hash = tree.get_root_hash()
```

## Features

### Canonical Byte Representation

The canonicalizer module provides deterministic byte representations for various file types:

- **Text Files**: UTF-8 encoding, no BOM, LF line endings, NFC normalization
- **JSON Files**: Lexicographically sorted keys, compact representation
- **XML Files**: Exclusive C14N without comments
- **Binary Files**: Raw bytes (no transformation)

### Merkle Tree

Binary Merkle tree implementation with the following specification:

- Leaf nodes: `SHA-256(0x00 || canonical_bytes)`
- Internal nodes: `SHA-256(0x01 || left_hash || right_hash)`
- Leaves ordered by canonical path (UTF-8 lexicographic)
- Per-leaf inclusion proofs exported as JSONL

### JSONL Logging

Structured logging with:

- Monotonic step IDs
- ISO8601 UTC timestamps
- Separate pipelines (handling, verification)
- Machine-readable JSONL format

### Manifest Generation

Stream manifest entries to JSONL with:

- Canonical paths
- File type detection
- SHA-256 hashes of canonical bytes
- File sizes
- Content-addressable references
- Checkpointing support for large repositories

## CLI Commands

### `index`

Generate manifest index for repository.

```bash
python -m scaffold.cli index [--output PATH] [--resume] [--apply]
```

Options:
- `--output PATH`: Output manifest path (default: manifest.jsonl)
- `--resume`: Resume from checkpoint
- `--checkpoint-interval N`: Save checkpoint every N files (default: 100)
- `--apply`: Apply changes (disable dry-run)

### `merkle`

Build Merkle tree and generate inclusion proofs.

```bash
python -m scaffold.cli merkle [--manifest PATH] [--output PATH] [--apply]
```

Options:
- `--manifest PATH`: Input manifest file to use
- `--output PATH`: Output proofs path (default: merkle_proofs.jsonl)
- `--apply`: Apply changes (disable dry-run)

### `verify`

Verify manifest and Merkle proofs.

```bash
python -m scaffold.cli verify [--manifest PATH] [--proofs PATH]
```

Options:
- `--manifest PATH`: Manifest file to verify
- `--proofs PATH`: Merkle proofs file to verify

### `backup`

Create backup of repository or specific files.

```bash
python -m scaffold.cli backup [--files FILE1 FILE2 ...]
```

Options:
- `--files`: Specific files to backup (default: all repository files)

### `restore`

Restore from backup.

```bash
python -m scaffold.cli restore --backup BACKUP_DIR [--apply]
```

Options:
- `--backup`: Backup directory to restore from
- `--apply`: Apply changes (disable dry-run)

### `handling-clamp`

Process GTA handling.meta files.

```bash
python -m scaffold.cli handling-clamp --input PATH [--output DIR] [--apply]
```

Options:
- `--input PATH`: Input file or directory
- `--output DIR`: Output directory for processed files
- `--apply`: Apply changes (disable dry-run)

## Configuration

Create a `config.json` file to customize scaffold behavior:

```json
{
  "checkpoint_interval": 100,
  "backup_retention_days": 30,
  "excluded_patterns": [
    ".git",
    "__pycache__",
    "node_modules",
    ".venv"
  ],
  "file_type_overrides": {
    ".meta": "xml"
  }
}
```

Use with:

```bash
python -m scaffold.cli index --config config.json --apply
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py`: Basic API usage
- `merkle_verification.py`: Merkle tree construction and verification
- `manifest_generation.py`: Manifest generation and verification

Run examples:

```bash
python scaffold/examples/basic_usage.py
python scaffold/examples/merkle_verification.py
python scaffold/examples/manifest_generation.py
```

## Testing

Run unit tests:

```bash
# Run all tests
python -m pytest scaffold/tests/

# Run specific test module
python -m pytest scaffold/tests/test_canonicalizer.py

# Run with coverage
python -m pytest scaffold/tests/ --cov=scaffold --cov-report=html
```

## Architecture

The scaffold is organized into the following modules:

- `canonicalizer.py`: Canonical byte representation
- `hasher.py`: SHA-256 hashing
- `merkle.py`: Merkle tree construction
- `manifest.py`: Manifest generation and verification
- `logger.py`: JSONL logging
- `handling_pipeline.py`: GTA handling.meta processing
- `cli.py`: Command-line interface

See `docs/ARCHITECTURE.md` for detailed architecture documentation.

## Security Considerations

- All modifications default to dry-run mode
- Mandatory backups before applying changes
- Cryptographic hashing with SHA-256
- Deterministic operations for auditability
- JSONL logs for complete operation history

## License

Part of the orthogonal-engineering repository.

## Contributing

This scaffold is designed for local use by repository owners and their IDE AI assistants. Contributions should maintain:

- Determinism: Operations must produce identical results given identical inputs
- Auditability: All operations must be fully logged
- Safety: Dry-run default with explicit apply flag
- Simplicity: Clear, maintainable code
