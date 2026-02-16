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
