# Deterministic Auditable Repository Scaffold

A comprehensive toolkit for repository-wide canonicalization, hashing, Merkle tree construction, manifest generation, and GTA handling.meta clamp pipeline processing.

## Overview

This scaffold provides a deterministic, auditable approach to repository analysis with:

- **Canonicalization**: Deterministic byte representation for text, JSON, XML, and binary files
- **Hashing**: SHA-256 hashing with canonical representations
- **Merkle Trees**: Binary Merkle tree construction with JSONL inclusion proofs
- **Manifests**: Streamed JSONL manifest generation with checkpointing
- **Logging**: JSONL logging with monotonic step IDs and ISO8601 timestamps
- **GTA Handling Pipeline**: Parser and validator for GTA handling.meta files

## Features

### Safety by Default

- **Dry-run mode by default**: All operations preview changes without applying them
- **Mandatory backups**: Built-in backup and restore functionality
- **Local execution**: Designed to run on user's local clones, not in CI

### Deterministic Processing

- **Canonical representations**: Files are normalized to ensure identical hashing across systems
- **Merkle tree verification**: Binary Merkle trees with cryptographic proofs
- **Manifest tracking**: Complete file inventory with content addressing

### Auditable Operations

- **JSONL logging**: Every operation logged with timestamps and step IDs
- **Verification pipeline**: Built-in integrity verification
- **Proof generation**: Merkle inclusion proofs for all files

## Installation

The scaffold is part of the `toolkit.oe.scaffold` package.

```bash
# No additional installation needed - part of orthogonal-engineering toolkit
cd /path/to/orthogonal-engineering
```

## Quick Start

### Index Repository (Dry-run)

```bash
python -m toolkit.oe.scaffold.cli index /path/to/repo
```

### Index Repository (Apply)

```bash
python -m toolkit.oe.scaffold.cli index /path/to/repo --apply --output manifest.jsonl
```

### Build Merkle Tree

```bash
python -m toolkit.oe.scaffold.cli merkle /path/to/repo --apply --output merkle_proofs.jsonl
```

### Process GTA handling.meta

```bash
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta --apply --output clamped_handling.meta
```

### Verify Integrity

```bash
python -m toolkit.oe.scaffold.cli verify manifest.jsonl --repo-path /path/to/repo
```

### Create Backup

```bash
python -m toolkit.oe.scaffold.cli backup /path/to/repo --output /path/to/backup
```

### Restore from Backup

```bash
python -m toolkit.oe.scaffold.cli restore /path/to/backup --target /path/to/repo
```

## CLI Reference

### Commands

- **index**: Index repository files and generate manifest
- **merkle**: Build Merkle tree and generate proofs
- **handling-clamp**: Process and validate GTA handling.meta files
- **verify**: Verify file integrity against manifest
- **dry-run**: Preview operations without applying
- **backup**: Create repository backup
- **restore**: Restore from backup

### Common Options

- `--apply`: Enable active mode (default is dry-run)
- `--config PATH`: Path to configuration file
- `--output PATH`: Output file path
- `--exclude PATTERN`: Patterns to exclude from processing

## Module Reference

### Canonicalizer

```python
from toolkit.oe.scaffold.canonicalizer import canonical_byte_representation

# Get canonical bytes for a file
canonical_bytes = canonical_byte_representation("myfile.txt")
```

**Features:**
- UTF-8 no BOM encoding
- LF line endings
- NFC Unicode normalization
- JSON lexicographic key ordering
- XML Exclusive C14N
- Binary passthrough

### Hasher

```python
from toolkit.oe.scaffold.hasher import compute_file_hash

# Compute SHA-256 hash
file_hash = compute_file_hash("myfile.txt")
```

**Features:**
- SHA-256 hashing
- Lowercase hexadecimal output
- Deterministic across systems

### Merkle Tree

```python
from toolkit.oe.scaffold.merkle import build_merkle_tree, write_all_proofs

# Build tree from file list
tree = build_merkle_tree([file1, file2, file3])

# Get root hash
root_hash = tree.get_root_hash()

# Generate proofs
write_all_proofs(tree, "proofs.jsonl")
```

**Features:**
- Binary Merkle tree
- Leaf: SHA-256(0x00 || canonical_bytes)
- Internal: SHA-256(0x01 || left || right)
- Lexicographic path ordering
- JSONL inclusion proofs

### Manifest

```python
from toolkit.oe.scaffold.manifest import generate_manifest

# Generate manifest
count = generate_manifest(
    file_paths=[file1, file2, file3],
    output_path="manifest.jsonl",
    base_path="/repo/root"
)
```

**Features:**
- Streamed JSONL output
- Canonical path tracking
- File type detection
- Content addressing
- Checkpointing for large repos

### Logger

```python
from toolkit.oe.scaffold.logger import ScaffoldLogger

# Create logger
logger = ScaffoldLogger("pipeline.jsonl")

# Log events
logger.log_start("operation", param1="value")
logger.log_complete("operation", result="success")
logger.log_error("operation", "Error message")
```

**Features:**
- JSONL output format
- Monotonic step_id
- ISO8601 UTC timestamps
- Structured event logging

### Handling Pipeline

```python
from toolkit.oe.scaffold.handling_pipeline import (
    HandlingMetaParser,
    HandlingClampPipeline
)

# Parse handling.meta
parser = HandlingMetaParser()
items = parser.parse_file("handling.meta")

# Clamp values
pipeline = HandlingClampPipeline()
results = pipeline.clamp_all(items, apply=False)
```

**Features:**
- GTA handling.meta XML parsing
- CHandlingData Item extraction
- Value clamping/validation
- Violation reporting

## File Formats

### Manifest Format (JSONL)

Each line is a JSON object:

```json
{
  "canonical_path": "src/module.py",
  "file_type": "text",
  "canonical_hash": "abc123...",
  "size": 1024,
  "content_address": "sha256:abc123..."
}
```

### Merkle Proof Format (JSONL)

Each line is a JSON object:

```json
{
  "file_path": "/path/to/file",
  "leaf_hash": "def456...",
  "root_hash": "ghi789...",
  "proof_path": [
    {"position": "right", "sibling_index": 1}
  ]
}
```

### Log Format (JSONL)

Each line is a JSON object:

```json
{
  "step_id": 1,
  "timestamp": "2026-02-16T17:30:00.000000+00:00",
  "event_type": "start",
  "message": "Starting operation",
  "operation": "index"
}
```

## Examples

See `examples/scaffold/` directory for complete examples:

- `basic_usage.py`: Basic scaffold operations
- `merkle_verification.py`: Merkle tree construction and verification
- `handling_processing.py`: GTA handling.meta processing
- `full_pipeline.py`: Complete repository processing pipeline

## Testing

Run the test suite:

```bash
python tests/scaffold/test_scaffold.py
```

All modules include comprehensive unit tests.

## Architecture

### Design Principles

1. **Determinism**: All operations produce identical results across systems
2. **Auditability**: Complete logging of all operations
3. **Safety**: Dry-run by default, mandatory backups
4. **Scalability**: Streaming processing with checkpointing
5. **Transparency**: Clear, documented formats

### Data Flow

```
Files → Canonicalization → Hashing → Merkle Tree
                                   ↓
                              Manifest
                                   ↓
                           Verification
```

## Configuration

Example configuration file (`scaffold.json`):

```json
{
  "exclude_patterns": [
    ".git",
    "__pycache__",
    "*.pyc",
    "node_modules"
  ],
  "checkpoint_interval": 100,
  "output_dir": "./scaffold_output"
}
```

## Troubleshooting

### Common Issues

**Issue**: Files have different hashes on different systems

**Solution**: Ensure all files use LF line endings and UTF-8 encoding. The canonicalizer handles this automatically.

**Issue**: Manifest generation is slow for large repos

**Solution**: Adjust `checkpoint_interval` in configuration. Check logs for progress.

**Issue**: Merkle tree verification fails

**Solution**: Ensure files haven't been modified since tree construction. Use `verify` command to check integrity.

## Version History

- **1.0.0** (2026-02-16): Initial release
  - Canonicalization module
  - Hashing module  
  - Merkle tree module
  - Manifest generation
  - JSONL logging
  - GTA handling pipeline
  - CLI with all subcommands

## License

MIT License - See repository LICENSE file

## Contributing

This scaffold is part of the Orthogonal Engineering methodology. Contributions should maintain:

- Deterministic behavior
- Comprehensive testing
- Clear documentation
- Backward compatibility

## Support

For issues and questions, see the main orthogonal-engineering repository.
