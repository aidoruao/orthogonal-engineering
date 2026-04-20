---
tags: [scaffold-quickstart]
register: documentation
---

# Scaffold Quick Start Guide

The deterministic auditable Python scaffold has been added to the repository at `scaffold/`.

## What is the Scaffold?

A local-run, dry-run-default tool for auditable file processing with:
- Canonical byte representation (deterministic across platforms)
- SHA-256 hashing
- Merkle tree verification
- JSONL logging
- Manifest generation
- Mandatory backups

## Quick Start

### 1. Run Tests

```bash
# Run all tests (62 tests)
python -m unittest discover -s scaffold/tests -p "test_*.py" -v
```

### 2. Run Examples

```bash
# Set PYTHONPATH to include the repository root
export PYTHONPATH=.

# Basic usage
python scaffold/examples/basic_usage.py

# Merkle tree verification
python scaffold/examples/merkle_verification.py

# Manifest generation
python scaffold/examples/manifest_generation.py
```

### 3. Use the CLI

```bash
# Generate manifest (dry-run mode by default)
python -m scaffold.cli index

# Generate manifest and save (requires --apply)
python -m scaffold.cli --apply index

# Build Merkle tree
python -m scaffold.cli --apply merkle

# Verify integrity
python -m scaffold.cli verify

# Create backup
python -m scaffold.cli backup

# See all options
python -m scaffold.cli --help
# Deterministic Auditable Scaffold - Quick Start Guide

## What is This?

The Deterministic Auditable Scaffold is a comprehensive Python toolkit for repository-wide integrity verification, canonicalization, and auditable processing. It's designed to run **locally** on your clone (not in CI) and defaults to **dry-run mode** for safety.

## Location

All scaffold code is in: `toolkit/oe/scaffold/`

## Quick Examples

### 1. Preview Repository Index (Dry-run)

```bash
python -m toolkit.oe.scaffold.cli dry-run /path/to/repo
```

### 2. Generate Manifest

```bash
# Dry-run first (safe)
python -m toolkit.oe.scaffold.cli index /path/to/repo

# Apply changes
python -m toolkit.oe.scaffold.cli index /path/to/repo --apply --output manifest.jsonl
```

### 3. Build Merkle Tree

```bash
python -m toolkit.oe.scaffold.cli merkle /path/to/repo --apply --output proofs.jsonl
```

### 4. Verify Integrity

```bash
python -m toolkit.oe.scaffold.cli verify manifest.jsonl --repo-path /path/to/repo
```

### 5. Process GTA handling.meta

```bash
# Dry-run to see what would change
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta

# Apply clamps
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta --apply
```

### 6. Backup Before Operations

```bash
python -m toolkit.oe.scaffold.cli backup /path/to/repo --output /path/to/backup
```

## Try the Examples

```bash
# Basic usage
python examples/scaffold/basic_usage.py

# Merkle tree verification
python examples/scaffold/merkle_verification.py

# GTA handling.meta processing
python examples/scaffold/handling_processing.py
```

## Run the Tests

```bash
python tests/scaffold/test_scaffold.py
```

## Key Features

### Dry-Run Default
All commands run in dry-run mode by default. Use `--apply` to actually make changes:

```bash
# Safe - just shows what would happen
python -m scaffold.cli index

# Actually generates manifest
python -m scaffold.cli --apply index
```

### Mandatory Backups
Before any modifications, backups are automatically created in `.scaffold_backups/`:

```bash
# Create backup
python -m scaffold.cli backup

# Restore from backup
python -m scaffold.cli --apply restore --backup .scaffold_backups/20260216_120000
```

### Deterministic Operations
Same input always produces same output:
- Text files: UTF-8, LF line endings, NFC normalization
- JSON files: Sorted keys, compact format
- XML files: Canonical C14N
- Binary files: Raw bytes

### Complete Logging
All operations are logged to JSONL files in `logs/`:
- `hello_world_handling_pipeline.jsonl`
- `handling_verification_pipeline.jsonl`

## Documentation

See `scaffold/docs/` for complete documentation:
- `README.md` - Full usage guide
- `ARCHITECTURE.md` - Technical architecture

## Configuration

Copy and customize the example config:

```bash
cp scaffold/config.example.json my_config.json
python -m scaffold.cli --config my_config.json --apply index
```

## Use Cases

### Generate File Manifest
```bash
python -m scaffold.cli --apply index
# Creates manifest.jsonl with hashes of all files
```

### Build Merkle Tree
```bash
python -m scaffold.cli --apply merkle
# Creates merkle_proofs.jsonl with inclusion proofs
```

### Verify Repository Integrity
```bash
python -m scaffold.cli verify
# Verifies all hashes match current state
```

### Process GTA Handling Files
```bash
python -m scaffold.cli --apply handling-clamp --input ./data
# Parses handling.meta files and exports to JSON
```

## Testing

All 62 unit tests pass:
- Canonicalizer: Text, JSON, XML, binary
- Hasher: SHA-256, incremental hashing
- Merkle tree: Construction, verification
- Manifest: Generation, checkpointing
- Logger: JSONL, monotonic IDs
- Handling pipeline: XML parsing

## Security

- No security vulnerabilities found (CodeQL scan)
- SHA-256 cryptographic hashing
- Dry-run mode prevents accidents
- Complete audit trail in logs

## Support

For issues or questions, see:
1. `scaffold/docs/README.md` - Full documentation
2. `scaffold/docs/ARCHITECTURE.md` - Technical details
3. `scaffold/examples/` - Working code examples
- ✅ **Dry-run by default** - No changes without `--apply` flag
- ✅ **Deterministic** - Same results across all systems
- ✅ **Auditable** - Complete JSONL logging
- ✅ **Safe** - Built-in backup/restore
- ✅ **Fast** - Streaming processing with checkpointing
- ✅ **Tested** - Comprehensive unit test suite

## Documentation

- **Full README**: `toolkit/oe/scaffold/README.md`
- **Module docs**: See individual Python files in `toolkit/oe/scaffold/`
- **Examples**: `examples/scaffold/`
- **Tests**: `tests/scaffold/test_scaffold.py`

## What Each Module Does

| Module | Purpose |
|--------|---------|
| `canonicalizer.py` | Deterministic byte representation (UTF-8, LF, NFC) |
| `hasher.py` | SHA-256 hashing of canonical representations |
| `merkle.py` | Binary Merkle tree with inclusion proofs |
| `manifest.py` | JSONL manifest generation with checkpointing |
| `logger.py` | JSONL logging with monotonic step IDs |
| `handling_pipeline.py` | GTA handling.meta parser and validator |
| `cli.py` | Command-line interface |

## Safety Features

1. **Dry-run Default**: All commands preview changes first
2. **Explicit Apply**: Must use `--apply` flag to make changes
3. **Backup Command**: Create backups before risky operations
4. **Restore Command**: Restore from backups if needed
5. **Verification**: Built-in integrity checking

## Common Workflows

### Workflow 1: Repository Integrity Check

```bash
# 1. Create backup
python -m toolkit.oe.scaffold.cli backup /path/to/repo

# 2. Generate manifest
python -m toolkit.oe.scaffold.cli index /path/to/repo --apply

# 3. Build Merkle tree
python -m toolkit.oe.scaffold.cli merkle /path/to/repo --apply

# 4. Verify
python -m toolkit.oe.scaffold.cli verify manifest.jsonl --repo-path /path/to/repo
```

### Workflow 2: GTA Mod Development

```bash
# 1. Parse handling.meta
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta

# 2. Review violations and apply fixes
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta --apply --output fixed_handling.meta
```

### Workflow 3: Pre-Push Verification

```bash
# Ensure everything is canonical and verified before push
python -m toolkit.oe.scaffold.cli dry-run .
```

## Need Help?

See the full documentation in `toolkit/oe/scaffold/README.md`

## Version

Current version: **1.0.0** (2026-02-16)
