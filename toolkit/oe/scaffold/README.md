---
tags: [toolkit, oe, scaffold, readme]
register: tooling
---

# Deterministic Auditable Python Scaffold

A deterministic, auditable Python scaffold for local repository operations. This toolkit provides tools for file canonicalization, hashing, Merkle tree construction, and auditable logging.

## Key Principles

- **Deterministic**: Same input always produces same output
- **Auditable**: All operations logged with timestamps and step IDs
- **Safe**: Defaults to dry-run mode, requires `--apply` for modifications
- **Backup-first**: Mandatory backups before any modifications
- **Local-first**: Designed for local execution, not CI

## Modules

### Core Modules

- **canonicalizer.py**: Deterministic canonical byte representation
  - Text files: UTF-8 no BOM, LF line endings, NFC normalization
  - JSON: Lexicographic key ordering
  - XML: Exclusive C14N without comments
  - Binary: Raw bytes

- **hasher.py**: SHA-256 hashing of canonical bytes
  - Hex lowercase output
  - File-level and per-vehicle hashing hooks

- **merkle.py**: Binary Merkle tree construction
  - Leaf: SHA-256(0x00 || canonical_bytes)
  - Internal: SHA-256(0x01 || left || right)
  - Leaves ordered by canonical path (UTF-8 lexicographic)
  - Inclusion proofs exported as JSONL

- **manifest.py**: JSONL manifest streaming
  - Canonical path, file type, hash, size, content-address
  - Checkpointing for large repositories
  - Restartable runs

- **logger.py**: JSONL logging
  - Monotonic step_id
  - ISO8601 UTC timestamps
  - Writes hello_world_handling_pipeline.jsonl and handling_verification_pipeline.jsonl

- **handling_pipeline.py**: GTA handling.meta parser
  - Structured parsing of vehicle handling data
  - Deterministic canonicalization
  - Validation and error reporting

- **cli.py**: Command-line interface
  - Subcommands: index, merkle, handling-clamp, verify, backup, restore
  - Dry-run mode by default
  - Creates local branch for review with --apply

## Installation

```bash
# Install from repository root
pip install -e .

# Or install dependencies
pip install -r requirements.txt
```

## Usage

### CLI Examples

```bash
# Dry-run (preview only - default mode)
python -m toolkit.oe.scaffold.cli index --pattern "**/*.py"
python -m toolkit.oe.scaffold.cli merkle
python -m toolkit.oe.scaffold.cli verify

# Apply changes (requires --apply flag)
python -m toolkit.oe.scaffold.cli --apply index --pattern "**/*.py"
python -m toolkit.oe.scaffold.cli --apply merkle --output my_proofs.jsonl

# Backup before modifications
python -m toolkit.oe.scaffold.cli --apply backup

# Parse GTA handling.meta
python -m toolkit.oe.scaffold.cli handling-clamp path/to/handling.meta

# Restore from backup
python -m toolkit.oe.scaffold.cli --apply restore .scaffold_backup/20260216_123456

# With config file
python -m toolkit.oe.scaffold.cli --config config.json --apply index
```

### Python API Examples

```python
from toolkit.oe.scaffold import (
    canonical_byte_representation,
    hash_file,
    ScaffoldLogger,
    MerkleTree,
    ManifestBuilder
)

# Canonical byte representation
canonical_bytes = canonical_byte_representation("config.json")
print(f"Canonical: {canonical_bytes[:50]}...")

# Hash a file
file_hash = hash_file("README.md", canonical=True)
print(f"Hash: {file_hash}")

# Build Merkle tree
tree = MerkleTree()
tree.add_file("file1.txt")
tree.add_file("file2.txt")
root = tree.build()
print(f"Merkle root: {root}")

# Get inclusion proof
proof = tree.get_proof("file1.txt")
print(f"Proof valid: {tree.verify_proof(proof)}")

# Build manifest
builder = ManifestBuilder(output_path="manifest.jsonl")
for entry in builder.add_directory("src/", pattern="**/*.py"):
    print(f"Added: {entry.canonical_path}")
builder.finalize()

# Logging
logger = ScaffoldLogger(output_dir="logs")
logger.log_pipeline("started", {"version": "1.0"})
logger.log_verification("hash_check", True, {"file": "test.txt"})
```

## Testing

Run unit tests for each module:

```bash
# Individual module tests
python -m toolkit.oe.scaffold.canonicalizer
python -m toolkit.oe.scaffold.hasher
python -m toolkit.oe.scaffold.merkle
python -m toolkit.oe.scaffold.manifest
python -m toolkit.oe.scaffold.handling_pipeline

# All tests
python -m pytest toolkit/oe/scaffold/tests/
```

## Features

### Deterministic Canonicalization

All file types are canonicalized to ensure deterministic byte representation:

- **Text files** (.txt, .md, .py, etc.): UTF-8, LF line endings, NFC normalization
- **JSON files**: Lexicographic key ordering, no whitespace
- **XML files**: Exclusive C14N without comments
- **Binary files**: Raw bytes unchanged

### Merkle Tree Verification

Binary Merkle trees provide cryptographic proof of file integrity:

- Deterministic ordering by canonical path
- Efficient inclusion proofs
- JSONL export for auditing

### Checkpointing

Large repository operations support checkpointing:

- Resume interrupted runs
- Periodic checkpoint saves (every 100 files)
- Explicit finalization

### Safety Mechanisms

Multiple safety mechanisms prevent accidental modifications:

1. **Dry-run by default**: Must explicitly use `--apply`
2. **Branch creation**: Modifications create review branch
3. **Backup support**: Easy backup/restore operations
4. **Logging**: All operations logged with timestamps

(See the dedicated "Configuration" section further down for the full
configuration schema.)

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
    "**/.git/**",
    "**/node_modules/**",
    "**/__pycache__/**"
  ],
  "checkpoint_interval": 100,
  "backup_dir": ".scaffold_backup"
}
```

## Output Files

### manifest.jsonl

```json
{"canonical_path": "src/main.py", "file_type": "text/x-python", "canonical_hash": "abc123...", "size": 1024, "content_address": "sha256:abc123..."}
{"canonical_path": "config.json", "file_type": "application/json", "canonical_hash": "def456...", "size": 256, "content_address": "sha256:def456..."}
```

### merkle_proofs.jsonl

```json
{"file_path": "src/main.py", "leaf_hash": "abc123...", "root_hash": "xyz789...", "proof": [{"position": "right", "hash": "def456..."}]}
```

### hello_world_handling_pipeline.jsonl

```json
{"step_id": 1, "timestamp": "2026-02-16T17:55:00.000Z", "event": "started", "data": {}}
{"step_id": 2, "timestamp": "2026-02-16T17:55:01.000Z", "event": "parsed_file", "data": {"file": "handling.meta", "entries": 42}}
```

## Design Decisions

### Why Default to Dry-Run?

Local repository operations are inherently risky. By defaulting to dry-run mode, we:

1. Prevent accidental modifications
2. Allow users to preview changes
3. Build trust through transparency
4. Align with "inspect before execute" principle

### Why Create Branches?

When `--apply` is used, a new git branch is created because:

1. Changes can be reviewed before merging
2. Easy rollback via git checkout
3. Clear audit trail of what changed
4. Aligns with standard git workflows

### Why JSONL?

JSONL (JSON Lines) is used for all structured output because:

1. Streamable for large datasets
2. One record per line (easy to parse)
3. Append-only (no file rewrites)
4. Compatible with standard tools (jq, grep, etc.)

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
