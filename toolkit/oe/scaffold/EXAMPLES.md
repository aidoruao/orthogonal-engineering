---
tags: [toolkit, oe, scaffold, examples]
register: tooling
---

# Scaffold Usage Examples

This document provides practical examples of using the deterministic auditable scaffold.

## Example 1: Basic File Index

Create an index of all Python files in a project:

```bash
# Dry-run to preview
python -m toolkit.oe.scaffold.cli index --pattern "**/*.py"

# Apply changes
python -m toolkit.oe.scaffold.cli --apply index --pattern "**/*.py"
```

Output: `manifest.jsonl` with entries like:

```json
{"canonical_path": "src/main.py", "file_type": "text/x-python", "canonical_hash": "abc123...", "size": 1024, "content_address": "sha256:abc123..."}
```

## Example 2: Verify Repository Integrity

After creating an index, verify that files haven't changed:

```bash
python -m toolkit.oe.scaffold.cli verify
```

Output:
```
✓ Verified: 42 files
```

## Example 3: Merkle Tree for Cryptographic Proof

Build a Merkle tree to get cryptographic proof of file contents:

```bash
# Build the tree
python -m toolkit.oe.scaffold.cli --apply merkle

# Verify a specific file
# The merkle_proofs.jsonl file contains inclusion proofs
```

Output: `merkle_proofs.jsonl` with cryptographic proofs:

```json
{"file_path": "src/main.py", "leaf_hash": "abc...", "root_hash": "xyz...", "proof": [{"position": "right", "hash": "def..."}]}
```

## Example 4: Backup Before Changes

Always backup before making modifications:

```bash
# Create backup
python -m toolkit.oe.scaffold.cli --apply backup

# Make changes...
# If something goes wrong, restore:
python -m toolkit.oe.scaffold.cli --apply restore .scaffold_backup/20260216_180000
```

## Example 5: Parse GTA Handling.meta

Parse and validate a GTA handling.meta file:

```bash
# Validate handling.meta
python -m toolkit.oe.scaffold.cli handling-clamp path/to/handling.meta --verbose

# Shows:
# ✓ Parsed 42 vehicle handling entries
# ✓ Validation passed
# Vehicles:
#   - ADDER: mass=1400.0, drag=0.35
#   - BULLET: mass=1200.0, drag=0.30
```

## Example 6: Using Configuration File

Create a config file to customize behavior:

```json
{
  "exclude_patterns": [
    "**/.git/**",
    "**/node_modules/**",
    "**/__pycache__/**"
  ],
  "checkpoint_interval": 50,
  "backup_dir": ".backups"
}
```

Use it:

```bash
python -m toolkit.oe.scaffold.cli --config config.json --apply index
```

## Example 7: Python API Usage

Use the scaffold programmatically:

```python
from toolkit.oe.scaffold import (
    canonical_byte_representation,
    hash_file,
    MerkleTree,
    ManifestBuilder,
    ScaffoldLogger
)

# Canonicalize a file
canonical = canonical_byte_representation("config.json")
print(f"Canonical bytes: {canonical[:50]}...")

# Hash it
file_hash = hash_file("config.json", canonical=True)
print(f"SHA-256: {file_hash}")

# Build a manifest
builder = ManifestBuilder("my_manifest.jsonl")
for entry in builder.add_directory("src/", pattern="**/*.py"):
    print(f"Added: {entry.canonical_path}")
builder.finalize()

# Build a Merkle tree
tree = MerkleTree()
tree.add_file("file1.txt")
tree.add_file("file2.txt")
root = tree.build()
print(f"Merkle root: {root}")

# Get and verify proof
proof = tree.get_proof("file1.txt")
if tree.verify_proof(proof):
    print("✓ Proof valid!")

# Log operations
logger = ScaffoldLogger(output_dir="logs")
logger.log_pipeline("index_started", {"files": 42})
logger.log_verification("hash_check", True, {"file": "test.txt"})
```

## Example 8: Checkpointing Large Repositories

For large repositories, checkpointing allows resumable operations:

```python
from toolkit.oe.scaffold import ManifestBuilder

# Initial run (processes some files)
builder = ManifestBuilder(
    output_path="manifest.jsonl",
    checkpoint_path=".checkpoint.json"
)

# Process files (checkpoints every 100 files)
list(builder.add_directory("large_repo/", pattern="**/*"))
builder.finalize()

# If interrupted, resume from checkpoint
# The builder automatically loads .checkpoint.json and skips processed files
builder2 = ManifestBuilder(
    output_path="manifest.jsonl",
    checkpoint_path=".checkpoint.json"
)
list(builder2.add_directory("large_repo/", pattern="**/*"))
builder2.finalize()
```

## Example 9: Custom Hashing Hooks

Apply transformations before hashing:

```python
from toolkit.oe.scaffold import hash_file, HashingHooks

# Hash with uppercase transformation
hash1 = hash_file("test.txt", hook=HashingHooks.uppercase_hook)

# Hash with whitespace stripped
hash2 = hash_file("test.txt", hook=HashingHooks.strip_whitespace_hook)

# Custom hook
def custom_hook(data: bytes) -> bytes:
    return data.replace(b"old", b"new")

hash3 = hash_file("test.txt", hook=custom_hook)
```

## Example 10: Comprehensive Workflow

Complete workflow for repository audit:

```bash
#!/bin/bash

# 1. Backup first
echo "Creating backup..."
python -m toolkit.oe.scaffold.cli --apply backup

# 2. Index all files
echo "Building index..."
python -m toolkit.oe.scaffold.cli --apply index --pattern "**/*"

# 3. Build Merkle tree
echo "Building Merkle tree..."
python -m toolkit.oe.scaffold.cli --apply merkle

# 4. Verify integrity
echo "Verifying integrity..."
python -m toolkit.oe.scaffold.cli verify

# 5. Check logs
echo "Review logs:"
ls -la .scaffold_logs/

echo "✓ Audit complete!"
echo "  - Manifest: manifest.jsonl"
echo "  - Merkle proofs: merkle_proofs.jsonl"
echo "  - Logs: .scaffold_logs/"
echo "  - Backup: .scaffold_backup/"
```

## Example 11: IDE Integration

The scaffold is designed to work with IDE AI assistants:

```python
# In your IDE, you can ask the AI to:

# 1. "Hash this file deterministically"
from toolkit.oe.scaffold import hash_file
print(hash_file("myfile.txt", canonical=True))

# 2. "Verify these files match the manifest"
from toolkit.oe.scaffold.cli import ScaffoldCLI
cli = ScaffoldCLI()
cli.verify()

# 3. "Create a Merkle proof for this file"
from toolkit.oe.scaffold import MerkleTree
tree = MerkleTree()
# ... add files ...
tree.build()
proof = tree.get_proof("important.txt")
```

## Tips and Best Practices

1. **Always use dry-run first**: Preview changes before applying
2. **Backup before modifications**: Use `--apply backup` first
3. **Use configuration files**: Customize behavior per project
4. **Enable verbose mode**: Use `-v` for detailed output
5. **Review logs**: Check `.scaffold_logs/` for operation history
6. **Verify checksums**: Run `verify` periodically
7. **Commit manifest**: Track `manifest.jsonl` in git for auditing
8. **Use branches**: All `--apply` operations create review branches

## Troubleshooting

### "File not found" errors

Ensure you're in the correct directory or use `--repo-path`:

```bash
python -m toolkit.oe.scaffold.cli --repo-path /path/to/repo index
```

### Checkpoint corruption

Delete checkpoint and restart:

```bash
rm .scaffold_checkpoint.json
python -m toolkit.oe.scaffold.cli --apply index
```

### Branch creation fails

Ensure you're in a git repository with proper permissions.

### Large file warnings

For very large files, consider using patterns to exclude them:

```bash
python -m toolkit.oe.scaffold.cli index --pattern "**/*.py" --pattern "!**/large_files/**"
```

## Security Considerations

1. **Deterministic hashing**: Same content always produces same hash
2. **No secrets in manifests**: Hashes are one-way functions
3. **Backup safety**: Backups exclude .git to avoid duplication
4. **Log privacy**: Logs contain file paths and hashes only
5. **Local execution**: No network calls, all operations local
6. **Git integration**: Branch creation for audit trail

## Performance

Expected performance on typical hardware:

- **Hashing**: ~100 MB/s per file
- **Indexing**: ~1000 files/s (small files)
- **Merkle tree**: ~10000 files/s
- **Checkpointing**: Every 100 files (configurable)

For large repositories (>10000 files), use checkpointing and consider splitting into subdirectories.
