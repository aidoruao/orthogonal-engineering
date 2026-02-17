# IDE AI Runner Runbook

## Overview

This runbook provides guidance for running IDE AI workflows with the CAS (Content-Addressable Storage) system in a safe, controlled manner.

## Safety-First Principles

1. **Dry-Run by Default**: All operations run in dry-run mode unless explicitly disabled
2. **Mandatory Backups**: Backups are created before any file modification
3. **No Auto-Push**: Changes are never automatically pushed to git
4. **Local-Only Vault**: User exports stored in local vault path only (C:\Users\Aidor\Downloads\ai_exports)

## Prerequisites

- Python 3.8 or higher
- All CAS modules installed (see requirements.txt)
- Backup directory configured
- Local vault path accessible

## Quick Start

### 1. Hash Files

Compute SHA-256 hashes for content verification:

```bash
python cli.py hash myfile.txt
```

### 2. Process Files (Dry-Run)

Process files through the pipeline in dry-run mode:

```bash
python cli.py process myfile.txt --dry-run
```

This will:
- Canonicalize the content
- Compute the hash
- Show what would be stored (without actually storing)

### 3. Process Files (Live Mode)

**WARNING**: This will modify files and create backups.

```bash
python cli.py process myfile.txt --live
```

### 4. Create Manifest

Create a manifest for tracking multiple files:

```bash
python cli.py manifest create file1.txt file2.txt --output manifest.json
```

### 5. Verify Manifest

Verify integrity of files in a manifest:

```bash
python cli.py manifest verify --manifest manifest.json --verbose
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

### Workflow 1: Safe File Processing

1. **Always start with dry-run**:
   ```bash
   python cli.py process myfile.txt --dry-run --verbose
   ```

2. **Review the output** to ensure it's what you expect

3. **Run in live mode only if satisfied**:
   ```bash
   python cli.py process myfile.txt --live
   ```

4. **Verify backup was created**:
   ```bash
   python cli.py backup list
   ```

### Workflow 2: Batch Processing with Verification

1. **Create manifest of source files**:
   ```bash
   python cli.py manifest create source_files/*.txt --name sources --output sources_manifest.json
   ```

2. **Process files in dry-run**:
   ```bash
   python cli.py process source_files/ --pattern "*.txt" --dry-run
   ```

3. **Process in live mode**:
   ```bash
   python cli.py process source_files/ --pattern "*.txt" --live
   ```

4. **Verify integrity**:
   ```bash
   python cli.py manifest verify --manifest sources_manifest.json
   ```

### Workflow 3: Using the Finalizer

For critical operations requiring alpha-omega verification:

```python
from core.alpha_omega_finalizer import AlphaOmegaFinalizer

# Initialize
finalizer = AlphaOmegaFinalizer(name="my_operation")

# Alpha phase: capture initial state
files = ["file1.txt", "file2.txt"]
finalizer.alpha(files, metadata={"operation": "critical_update"})

# Perform your operations here
# ...

# Omega phase: verify final state
result = finalizer.omega(verify=True)

if result["verification"]["verified"]:
    print("✓ Operation verified successfully")
else:
    print("✗ Verification failed:", result["verification"]["issues"])
    # Take corrective action
```

## Best Practices

### 1. Always Use Dry-Run First

Never skip the dry-run step for new operations:

```bash
# ✓ GOOD
python cli.py process new_file.txt --dry-run
python cli.py process new_file.txt --live

# ✗ BAD
python cli.py process new_file.txt --live  # Skipping dry-run
```

### 2. Verify Backups

After any live operation, verify your backup:

```bash
python cli.py backup list --pattern "myfile*"
```

### 3. Use Manifests for Batch Operations

For processing multiple files, always create a manifest:

```bash
python cli.py manifest create *.txt --output batch_manifest.json
```

### 4. Keep Logs

The system automatically logs to `logs/` directory. Review logs regularly:

```bash
cat logs/pipeline_*.jsonl | tail -n 20
```

## Troubleshooting

### Problem: "File not found" error

**Solution**: Ensure you're using absolute paths or correct relative paths:

```bash
# ✓ Use absolute path
python cli.py hash /full/path/to/file.txt

# ✓ Or relative path from current directory
python cli.py hash ./relative/path/file.txt
```

### Problem: Backup directory full

**Solution**: Clean up old backups:

```bash
python cli.py backup cleanup --keep 10
```

### Problem: Verification failed

**Solution**: 

1. Check the specific issue:
   ```bash
   python cli.py manifest verify --manifest manifest.json --verbose
   ```

2. Restore from backup if needed:
   ```python
   from backup import BackupManager
   bm = BackupManager()
   bm.restore_backup("backups/file_20260216_183000.txt", "file.txt")
   ```

## Safety Checklist

Before any live operation:

- [ ] Dry-run completed and reviewed
- [ ] Backup directory has sufficient space
- [ ] Critical files have manual backups
- [ ] Operation logs are being captured
- [ ] Rollback plan is ready

## Vault Path Configuration

User exports are stored in the local-only vault path:

**Example Windows path**: `C:\Users\Aidor\Downloads\ai_exports`

> **Note**: This is an example path. Configure your own vault path according to your local environment.

**Never commit export data to git**. The vault path should be:
- Listed in `.gitignore`
- Backed up separately
- Accessible only locally

## Emergency Procedures

### If Something Goes Wrong

1. **Stop immediately**
2. **Check recent logs**: `cat logs/pipeline_*.jsonl | tail -n 50`
3. **List recent backups**: `python cli.py backup list`
4. **Restore if needed**: Use BackupManager.restore_backup()
5. **Document the issue** for future reference

## Additional Resources

- See `SAFE_OPERATIONS.md` for detailed safety guidelines
- See `examples/` directory for code examples
- See unit tests in `core/tests/` for usage patterns
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
1. Review logs in `logs/` directory
2. Check test files for examples
3. Consult `SAFE_OPERATIONS.md`
- Review this runbook
- Check `docs/SAFE_OPERATIONS.md` for safety policies
- Examine pipeline logs for detailed error information
- Verify all paths and permissions are correct

## Version

Runbook Version: 1.0.0
Pipeline Version: 1.0.0
Date: 2026-02-16
