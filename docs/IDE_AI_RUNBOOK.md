# IDE AI Runbook - Deterministic Pipeline Operations

This runbook provides operational guidance for using the deterministic pipeline scaffold within IDE and AI-assisted workflows.

## Overview

The deterministic pipeline scaffold provides tools for:
- File indexing and manifest generation
- Merkle tree construction and verification
- GTA handling.meta processing with safety clamps
- Vault finalization with integrity checks

## Safety-First Design

### Default Dry-Run Behavior

**ALL operations default to dry-run mode** and require explicit `--apply` flag for writes.

```bash
# Dry-run (default) - shows what would happen
python cli.py index --repo /path/to/repo

# Apply mode - actually performs writes
python cli.py index --repo /path/to/repo --apply
```

### Mandatory Backups

All destructive operations create timestamped backups automatically:
- Backups stored in `./backups/` by default
- Immutable backup manifest in `backup_manifest.jsonl`
- Each backup includes original hash for verification

## Example Vault Path

**IMPORTANT**: The default example vault path is:
```
C:\Users\Aidor\Downloads\ai_exports
```

This is **EXAMPLE ONLY** and should be customized to your local path. This directory is:
- **NOT included in the repository**
- **NOT committed to version control**
- **For local use only**

To use a different vault path:
```bash
python core/alpha_omega_finalizer.py --vault-dir /your/actual/path --apply
```

## Common Workflows

### 1. Index a Repository

```bash
# Dry-run first
python cli.py index --repo /path/to/repo --out manifest.jsonl

# Review output, then apply
python cli.py index --repo /path/to/repo --out manifest.jsonl --apply
```

### 2. Build Merkle Tree

```bash
# Generate Merkle tree from manifest
python cli.py merkle --manifest manifest.jsonl --apply

# This creates merkle_proofs.jsonl with inclusion proofs
```

### 3. Process Handling Files

```bash
# Process GTA handling.meta (dry-run)
python cli.py handling-clamp --handling-path handling.meta --out ./output

# Apply changes
python cli.py handling-clamp --handling-path handling.meta --out ./output --apply
```

### 4. Finalize Vault

```bash
# Finalize with custom vault path (dry-run)
python core/alpha_omega_finalizer.py --vault-dir /your/path

# Apply finalization
python core/alpha_omega_finalizer.py --vault-dir /your/path --apply
```

### 5. Verify Integrity

```bash
# Verify Merkle proofs
python cli.py verify --manifest merkle_proofs.jsonl

# Verify vault integrity
python core/alpha_omega_finalizer.py --vault-dir /your/path --verify finalization_manifest.jsonl
```

## Pipeline Logs

All operations generate JSONL logs in `./logs/`:
- `indexing_pipeline.jsonl` - File indexing operations
- `merkle_pipeline.jsonl` - Merkle tree operations
- `hello_world_handling_pipeline.jsonl` - Handling processing
- `handling_verification_pipeline.jsonl` - Verification operations

Logs include:
- Monotonic step IDs
- ISO8601 UTC timestamps
- Step names and status
- Detailed operation metadata

## File Types and Canonicalization

The pipeline canonicalizes files based on type:
- **JSON**: Sorted keys, consistent separators (`,` and `:`)
- **XML**: Exclusive canonicalization (C14N) without comments
- **Text**: NFC normalization, LF line endings
- **Binary**: Returned as-is

## Security Notes

### No Network Operations

The pipeline performs **NO** network operations:
- No auto-push to remote repositories
- No auto-merge operations
- No credential usage
- All operations are local-only

### Redaction Hooks

Redaction hooks are present but **DISABLED BY DEFAULT**:
- Users must configure local classifiers for redaction
- No automatic PII detection enabled
- Stub implementations in `core/alpha_omega_finalizer.py`

### Data Safety

- **Never commit** files from `C:\Users\Aidor\Downloads\ai_exports`
- **Never commit** chat exports or sensitive data
- Use `.gitignore` to exclude sensitive directories
- Review all changes before committing

## Checkpointing for Large Operations

For large repositories, manifest generation supports checkpointing:
- Checkpoint files stored as `{manifest}.checkpoint.json`
- Operations can be restarted if interrupted
- Processed files are tracked to avoid re-processing

## Error Handling

If operations fail:
1. Check the pipeline logs in `./logs/`
2. Verify file paths and permissions
3. Ensure required dependencies are installed
4. Review dry-run output for issues

## Advanced Usage

### Subset Processing

Process only specific file patterns:
```bash
python cli.py index --repo /path/to/repo --subset "*.py,*.json" --apply
```

### Parallel Workers

Increase concurrency for large operations:
```bash
# Note: --workers flag would be added to CLI if needed
# Currently uses default ThreadPoolExecutor settings
```

### HMAC Mode

Use HMAC for fingerprinting:
```python
from core.alpha_omega_finalizer import AlphaOmegaFinalizer

finalizer = AlphaOmegaFinalizer(
    vault_dir='/path/to/vault',
    hmac_key=b'your-secret-key'
)
```

## Support

For issues or questions:
- Review this runbook
- Check `docs/SAFE_OPERATIONS.md` for safety policies
- Examine pipeline logs for detailed error information
- Verify all paths and permissions are correct

## Version

Runbook Version: 1.0.0
Pipeline Version: 1.0.0
Date: 2026-02-16
