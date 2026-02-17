# Canonicalization Scaffold

A deterministic, auditable Python scaffold for repository-wide canonicalization, SHA-256 hashing, manifest generation, Merkle/DAG construction, and GTA handling.meta clamp pipeline.

## Overview

This scaffold provides tools for:
- **Canonicalization**: Normalize files (text, JSON, XML, binary) to canonical byte representation
- **Hashing**: SHA-256 hashing of canonical bytes
- **Manifests**: JSONL manifest generation with checkpointing support
- **Merkle Trees**: Binary Merkle tree construction with inclusion proofs
- **Verification**: Verify repository integrity against manifests and Merkle proofs
- **GTA Handling**: Parse and clamp GTA handling.meta files (stub implementation)

## Key Features

✅ **Dry-run by default**: All operations default to dry-run mode  
✅ **Mandatory backups**: Backup creation before modifications  
✅ **Deterministic**: Same input always produces same output  
✅ **Auditable**: JSONL logging with ISO8601 timestamps  
✅ **Streaming**: Handles large repositories with checkpointing  
✅ **Local execution**: Designed for local use, not CI/CD  

## Installation

No installation required - this is a standalone Python module. Simply ensure you have Python 3.8+ installed.

```bash
# Test the installation
cd /path/to/orthogonal-engineering
python3 -m unittest discover -s canonicalization_scaffold/tests
```

## Quick Start

### 1. Generate a Manifest

```bash
# Dry-run (preview only)
python3 -m canonicalization_scaffold.cli --repo-path . index

# Actually generate manifest
python3 -m canonicalization_scaffold.cli --repo-path . --apply index
```

### 2. Build Merkle Tree

```bash
# Generate Merkle tree with inclusion proofs
python3 -m canonicalization_scaffold.cli --repo-path . --apply merkle
```

### 3. Verify Repository

```bash
# Verify files against manifest
python3 -m canonicalization_scaffold.cli --repo-path . verify --manifest ./canonical_output/manifest.jsonl
```

### 4. Create Backup

```bash
# Create backup before modifications
python3 -m canonicalization_scaffold.cli --repo-path . --apply backup
```

## CLI Usage

### Global Options

```
--repo-path PATH       Repository path (default: current directory)
--config FILE          Configuration file (JSON)
--output-dir DIR       Output directory (default: ./canonical_output)
--apply                Apply modifications (required for non-dry-run)
--verbose              Verbose output
```

### Commands

#### `index` - Generate Manifest

```bash
python3 -m canonicalization_scaffold.cli index [--exclude PATTERN ...]
```

Generates a JSONL manifest listing all files with:
- Canonical path
- File type (text, json, xml, binary)
- SHA-256 hash of canonical bytes
- File size
- Content-addressed reference

**Example:**
```bash
python3 -m canonicalization_scaffold.cli --apply index --exclude .git __pycache__ node_modules
```

#### `merkle` - Build Merkle Tree

```bash
python3 -m canonicalization_scaffold.cli merkle [--manifest FILE]
```

Builds a binary Merkle tree using:
- Leaf nodes: `SHA-256(0x00 || canonical_bytes)`
- Internal nodes: `SHA-256(0x01 || left_hash || right_hash)`

Exports inclusion proofs to JSONL.

**Example:**
```bash
python3 -m canonicalization_scaffold.cli --apply merkle
```

#### `handling-clamp` - Process GTA Handling Files

```bash
python3 -m canonicalization_scaffold.cli handling-clamp --input FILE [--clamp-rules FILE]
```

Parse and clamp GTA handling.meta XML files.

**Example:**
```bash
python3 -m canonicalization_scaffold.cli --apply handling-clamp --input handling.meta
```

#### `verify` - Verify Integrity

```bash
python3 -m canonicalization_scaffold.cli verify --manifest FILE
python3 -m canonicalization_scaffold.cli verify --proofs FILE
```

Verify repository integrity against manifest or Merkle proofs.

**Example:**
```bash
python3 -m canonicalization_scaffold.cli verify --manifest ./canonical_output/manifest.jsonl
```

#### `backup` - Create Backup

```bash
python3 -m canonicalization_scaffold.cli backup [--backup-dir DIR]
```

Create a backup of the repository.

**Example:**
```bash
python3 -m canonicalization_scaffold.cli --apply backup
```

#### `restore` - Restore from Backup

```bash
python3 -m canonicalization_scaffold.cli restore --backup-dir DIR
```

Restore repository from a backup (requires confirmation).

**Example:**
```bash
python3 -m canonicalization_scaffold.cli --apply restore --backup-dir /path/to/backup
```

## Python API

### Canonicalizer

```python
from canonicalization_scaffold.canonicalizer import canonical_byte_representation

# Get canonical bytes for a file
canonical_bytes = canonical_byte_representation("path/to/file.txt")
```

### Hasher

```python
from canonicalization_scaffold.hasher import hash_file, verify_hash

# Hash a file
file_hash = hash_file("path/to/file.txt")

# Verify a hash
is_valid = verify_hash("path/to/file.txt", expected_hash)
```

### Manifest

```python
from canonicalization_scaffold.manifest import generate_manifest, ManifestGenerator

# Generate manifest
count = generate_manifest(
    repo_root="/path/to/repo",
    output_path="manifest.jsonl",
    exclude_patterns={'.git', '__pycache__'}
)

# Verify manifest
results = ManifestGenerator.verify_manifest("manifest.jsonl", "/path/to/repo")
```

### Merkle Tree

```python
from canonicalization_scaffold.merkle import build_merkle_tree
from canonicalization_scaffold.canonicalizer import canonical_byte_representation

# Build tree
file_hashes = {
    "file1.txt": canonical_byte_representation("file1.txt"),
    "file2.txt": canonical_byte_representation("file2.txt")
}
root_hash, tree = build_merkle_tree(file_hashes)

# Get inclusion proof
proof = tree.get_inclusion_proof("file1.txt")

# Verify proof
is_valid = tree.verify_inclusion_proof(
    "file1.txt",
    canonical_byte_representation("file1.txt"),
    proof,
    root_hash
)
```

### Logger

```python
from canonicalization_scaffold.logger import create_hello_world_logger
from pathlib import Path

# Create logger
logger = create_hello_world_logger(Path("./logs"))

# Log operations
step_id = logger.start_operation("my_operation", param="value")
# ... do work ...
logger.complete_operation(step_id, "my_operation", result="success")
```

## Output Formats

### Manifest (JSONL)

Each line contains:
```json
{
  "canonical_path": "path/to/file.txt",
  "file_type": "text",
  "canonical_hash": "abc123...",
  "size": 1234,
  "content_addressed_ref": "sha256:abc123..."
}
```

### Merkle Proofs (JSONL)

Each line contains:
```json
{
  "file_path": "path/to/file.txt",
  "leaf_hash": "def456...",
  "proof": [["right", "hash1"], ["left", "hash2"]],
  "root_hash": "ghi789..."
}
```

### Logs (JSONL)

Each line contains:
```json
{
  "timestamp": "2026-02-16T17:53:05.958Z",
  "session_id": "uuid-here",
  "step_id": "uuid-here",
  "event_type": "start|complete|error",
  "operation": "operation_name",
  ...
}
```

## Canonicalization Rules

### Text Files
- UTF-8 encoding (no BOM)
- LF line endings (Unix-style)
- NFC Unicode normalization

### JSON Files
- Lexicographic key sorting
- Compact formatting (no whitespace)
- UTF-8 encoding

### XML Files
- Simplified C14N (Canonical XML)
- Attribute and element sorting
- Comment removal

### Binary Files
- Raw bytes (no transformation)

## Testing

Run the test suite:

```bash
# Run all tests
python3 -m unittest discover -s canonicalization_scaffold/tests

# Run specific test module
python3 -m unittest canonicalization_scaffold.tests.test_canonicalizer

# Run with verbose output
python3 -m unittest discover -s canonicalization_scaffold/tests -v
```

Test coverage:
- ✅ 72 unit tests
- ✅ Canonicalizer (15 tests)
- ✅ Hasher (13 tests)
- ✅ Merkle Tree (17 tests)
- ✅ Manifest (15 tests)
- ✅ Logger (12 tests)

## Architecture

```
canonicalization_scaffold/
├── __init__.py           # Package initialization
├── cli.py                # CLI entrypoint
├── canonicalizer.py      # File canonicalization
├── hasher.py             # SHA-256 hashing
├── merkle.py             # Merkle tree construction
├── manifest.py           # Manifest generation
├── logger.py             # JSONL logging
├── handling_pipeline.py  # GTA handling.meta parser
└── tests/                # Unit tests
    ├── test_canonicalizer.py
    ├── test_hasher.py
    ├── test_merkle.py
    ├── test_manifest.py
    └── test_logger.py
```

## Security Considerations

- **Deterministic**: All operations are deterministic for auditability
- **No network**: Operates entirely locally
- **Read-only by default**: Requires `--apply` flag for modifications
- **Backups**: Encourages backup creation before changes
- **Logged**: All operations logged to JSONL for audit trail

## Limitations

- **GTA Handling Pipeline**: Stub implementation - needs full GTA schema support
- **XML Canonicalization**: Simplified C14N - not full W3C C14N
- **Large Files**: In-memory processing - may need streaming for very large files

## Future Enhancements

- Full GTA handling.meta schema support
- Streaming mode for large files
- Parallel processing for large repositories
- Web UI for manifest exploration
- Integration with version control systems
- Cryptographic signatures for manifests

## License

This module is part of the Orthogonal Engineering project.

## Contributing

For bugs or feature requests, please file an issue in the main repository.
