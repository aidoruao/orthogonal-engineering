---
tags: [scaffold-quickstart]
register: documentation
---

# Deterministic Auditable Scaffold — Quick Start Guide

The Deterministic Auditable Scaffold is a comprehensive Python toolkit for
repository-wide integrity verification, canonicalization, and auditable
processing. It is designed to run **locally** on your clone (not in CI) and
defaults to **dry-run mode** for safety.

## Location

All scaffold code lives at `toolkit/oe/scaffold/`. The legacy `scaffold/`
package is retained for backward compatibility only; new callers should
use `toolkit.oe.scaffold` exclusively.

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

All commands run in dry-run mode by default. Use `--apply` to actually
make changes:

```bash
# Safe - just shows what would happen
python -m toolkit.oe.scaffold.cli index /path/to/repo

# Actually generates manifest
python -m toolkit.oe.scaffold.cli index /path/to/repo --apply
```

### Mandatory Backups

Before any modifications, backups are automatically created in
`.scaffold_backups/`:

```bash
# Create backup
python -m toolkit.oe.scaffold.cli backup /path/to/repo

# Restore from backup
python -m toolkit.oe.scaffold.cli restore .scaffold_backups/20260216_120000 \
    --target /path/to/repo --apply
```

### Deterministic Operations

Same input always produces same output:

- Text files: UTF-8, LF line endings, NFC normalization
- JSON files: Sorted keys, compact format
- XML files: Canonical C14N
- Binary files: Raw bytes

### Complete Logging

All operations are logged to JSONL files under `logs/` with monotonic
step IDs and ISO8601 timestamps.

## Documentation

- **Full README**: `toolkit/oe/scaffold/README.md`
- **Module docs**: See individual Python files in `toolkit/oe/scaffold/`
- **Examples**: `examples/scaffold/`
- **Tests**: `tests/scaffold/test_scaffold.py`

## Safety Features

1. **Dry-run default**: all commands preview changes first.
2. **Explicit apply**: `--apply` flag required to mutate state.
3. **Backup command**: create backups before risky operations.
4. **Restore command**: restore from backups if needed.
5. **Verification**: built-in integrity checking.

## Common Workflows

### Workflow 1: Repository Integrity Check

```bash
python -m toolkit.oe.scaffold.cli backup /path/to/repo
python -m toolkit.oe.scaffold.cli index /path/to/repo --apply
python -m toolkit.oe.scaffold.cli merkle /path/to/repo --apply
python -m toolkit.oe.scaffold.cli verify manifest.jsonl --repo-path /path/to/repo
```

### Workflow 2: GTA Mod Development

```bash
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta
python -m toolkit.oe.scaffold.cli handling-clamp handling.meta \
    --apply --output fixed_handling.meta
```

### Workflow 3: Pre-Push Verification

```bash
python -m toolkit.oe.scaffold.cli dry-run .
```

## Need Help?

See the full documentation in `toolkit/oe/scaffold/README.md`.

## Version

Current version: **1.0.0** (2026-02-16).
