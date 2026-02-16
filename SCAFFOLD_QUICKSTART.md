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
